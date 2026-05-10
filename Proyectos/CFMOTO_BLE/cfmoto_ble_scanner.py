#!/usr/bin/env python3
"""
CFMOTO BLE Scanner - Captura dispositivos Bluetooth cerca de la moto
para analizar el protocolo de comunicación.

Uso:
    python cfmoto_ble_scanner.py

Requiere: bleak (pip install bleak)
"""

import asyncio
import struct
import datetime
import json
import sys
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import ScannerConstants

# Configuración
SCAN_TIMEOUT = 30  # segundos
OUTPUT_DIR = r"C:\Users\ed\.openclaw\workspace\Proyectos\CFMOTO_BLE"
DEVICE_NAME_FILTER = ["CFMOTO", "CFM", "cfmoto", "CF", "Niu", "NIU", "VOG", "BT"]
MANUFACTURER_ID_CFMOTO = 0x0D85  # CFMOTO过的manufacturer ID (确认)

class CFmotoBLEScanner:
    def __init__(self):
        self.devices_found = []
        self.raw_advertisements = []
        self.cfmoto_devices = []

    async def on_detection(self, device: BLEDevice, advertisement_data):
        """Callback invoked for every BLE advertisement received."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Extraer datos crudos
        rssi = advertisement_data.rssi
        name = device.name or advertisement_data.local_name or "Unknown"
        address = device.address
        
        # Parse manufacturer data
        manufacturer_data = {}
        if advertisement_data.manufacturer_data:
            for mfg_id, mfg_data in advertisement_data.manufacturer_data.items():
                raw_bytes = bytes(mfg_data)
                manufacturer_data[mfg_id] = raw_bytes.hex()
        
        entry = {
            "timestamp": timestamp,
            "address": address,
            "name": name,
            "rssi": rssi,
            "manufacturer_data": manufacturer_data,
            "service_uuids": advertisement_data.service_uuids,
            "service_data": advertisement_data.service_data,
            "tx_power": advertisement_data.tx_power,
            "platform": device.details.get("platform", "unknown")
        }
        
        self.devices_found.append(entry)
        
        # Filtrar por nombre para可能被识别
        name_upper = name.upper()
        is_cfmoto = any(f in name_upper for f in DEVICE_NAME_FILTER)
        
        if is_cfmoto:
            self.cfmoto_devices.append(entry)
            print(f"[CFMOTO DEVICE] {name} | {address} | RSSI: {rssi} dBm")
            print(f"  Manufacturer IDs: {list(manufacturer_data.keys())}")
            print(f"  Services: {advertisement_data.service_uuids}")
        
        # Mostrar todos los dispositivos con buena señal
        if rssi > -70:
            print(f"[{timestamp}] {name} ({address}) RSSI: {rssi} dBm")

    async def scan(self, duration=SCAN_TIMEOUT):
        """Escanea dispositivos BLE durante N segundos."""
        print("=" * 60)
        print("CFMOTO BLE Scanner - Iniciando...")
        print(f"Duración: {duration}s | Filtro nombres: {DEVICE_NAME_FILTER}")
        print("=" * 60)
        
        try:
            scanner = BleakScanner(detection_callback=self.on_detection)
            await scanner.start()
            print("[*] Escaneando... presiona Ctrl+C para detener temprano\n")
            
            await asyncio.sleep(duration)
            
        except Exception as e:
            print(f"Error durante escaneo: {e}")
        finally:
            await scanner.stop()
            print("\n[*] Escaneo detenido.")
        
        return self.devices_found

    async def connect_and_explore(self, address):
        """Conecta a un dispositivo y explora sus servicios/características."""
        print(f"\n[*] Conectando a {address}...")
        
        try:
            async with BleakClient(address, timeout=20) as client:
                print(f"[+] Conectado a {address}")
                print(f"    Services: {client.services}")
                
                for service in client.services:
                    print(f"\n  [Service] {service.uuid}: {service.description}")
                    for char in service.characteristics:
                        props = ",".join(char.properties)
                        print(f"    [Char] {char.uuid} ({props})")
                        
                        # Leer si es legible
                        if "READ" in char.properties:
                            try:
                                value = await client.read_gatt_char(char.uuid)
                                print(f"        Value: {value.hex()}")
                            except Exception as e:
                                print(f"        Read error: {e}")
                
                # Intentar escribir en características escribibles
                print("\n[*] Probando escribir en características escribibles...")
                for service in client.services:
                    for char in service.characteristics:
                        if "WRITE" in char.properties or "WRITE_WITHOUT_RESPONSE" in char.properties:
                            print(f"  [Writable] {char.uuid} - intentando escribir...")
                            try:
                                # Enviar ping genérico
                                test_data = bytes([0x01, 0x03, 0x00])
                                await client.write_gatt_char(char.uuid, test_data, response=True)
                                print(f"    -> Escritura exitosa")
                            except Exception as e:
                                print(f"    -> Error: {e}")
                                
        except Exception as e:
            print(f"[-] Error conectando: {e}")
            return None

    def save_results(self):
        """Guarda los resultados del escaneo."""
        import os
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        scan_file = os.path.join(OUTPUT_DIR, f"scan_{timestamp_str}.json")
        
        results = {
            "scan_time": datetime.datetime.now().isoformat(),
            "duration_seconds": SCAN_TIMEOUT,
            "total_devices": len(self.devices_found),
            "cfmoto_candidates": len(self.cfmoto_devices),
            "devices": self.devices_found,
            "cfmoto_devices": self.cfmoto_devices
        }
        
        with open(scan_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[+] Resultados guardados: {scan_file}")
        return scan_file

async def interactive_scan():
    """Modo interactivo: escanear y permitir conexión a dispositivos."""
    scanner = CFmotoBLEScanner()
    
    print("\n1. Escanear 30 segundos")
    print("2. Escanear 60 segundos")
    print("3. Escanear hasta Ctrl+C")
    print("4. Escanear 30s + modo verbose (todos los paquetes)")
    
    choice = input("\nOpción (1-4): ").strip()
    
    duration = 30
    verbose = False
    
    if choice == "2":
        duration = 60
    elif choice == "3":
        duration = 9999
    elif choice == "4":
        duration = 30
        verbose = True
    
    devices = await scanner.scan(duration if duration < 9999 else 30)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {len(devices)} dispositivos encontrados")
    
    if scanner.cfmoto_devices:
        print(f"CANDIDATOS CFMOTO: {len(scanner.cfmoto_devices)}")
        for d in scanner.cfmoto_devices:
            print(f"  - {d['name']} ({d['address']})")
    
    scanner.save_results()
    
    # Preguntar si conectar
    if scanner.cfmoto_devices:
        connect = input("\n¿Conectar a alguno? (s/n): ").strip().lower()
        if connect == "s":
            for i, d in enumerate(scanner.cfmoto_devices):
                print(f"  {i+1}. {d['name']} ({d['address']})")
            idx = input("Número: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(scanner.cfmoto_devices):
                    await scanner.connect_and_explore(scanner.cfmoto_devices[idx]["address"])
            except:
                pass
    
    return scanner

async def quick_scan():
    """Un escaneo rápido guardado automaticamente."""
    scanner = CFmotoBLEScanner()
    await scanner.scan(30)
    
    print(f"\nResumen: {len(scanner.devices_found)} dispositivos")
    scanner.save_results()
    
    return scanner

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║       CFMOTO BLE Protocol Scanner v1.0               ║
    ║                                                      ║
    ║  Escanea dispositivos Bluetooth Low Energy para      ║
    ║  encontrar y analizar el protocolo de la moto.       ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        # Modo CLI: python cfmoto_ble_scanner.py [address]
        if sys.argv[1] == "--help":
            print("Uso: python cfmoto_ble_scanner.py [address]")
            print("  Sin args: modo interactivo")
            print("  Con address: conecta directo")
        elif len(sys.argv) >= 2:
            asyncio.run(CFmotoBLEScanner().connect_and_explore(sys.argv[1]))
    else:
        asyncio.run(interactive_scan())