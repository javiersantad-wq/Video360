# CFMOTO 300NK BLE Scanner

Reverse engineering del protocolo BLE de la CFMOTO 300NK (2025 Mexico).

## Hardware encontrado

| Dispositivo | MAC | RSSI | Notas |
|-------------|-----|------|-------|
| CFMOTO-LE-8C472C | DD:0D:30:8C:47:2C | -55 dBm | Servicio BLE 34fb |
| CFMOTO-5F2C | 03:FF:01:04:5F:2C | -63 dBm | Servicio BLE 34fb |

## Servicio BLE

**UUID:** `0000fea1-0000-1000-8000-00805f9b34fb` (Nordic UART Service - NUS)

Este es el mismo perfil que usa la app oficial. Parece ser un canal de configuracion/pairing,
no el canal principal de datos.

## Protocolo (del APK de CFMOTO RIDE)

Archivos `.proto` encontrados en el APK:
- `bluetooth.proto` - Protocolo principal
- `Meter.proto` - Datos del tablero
- `messaging_event.proto` - Eventos messaging
- `messaging_event_extension.proto` - Extensiones

### Flujo de autenticacion
```
App → AuthPackage(Info=SN_encriptado)
T-box → TboxRandomNum(codec=SN_desencriptado?)
App → RandomNum(sn=respuesta)
T-box → TboxAuthResult(result=0/1)
```

### Datos de la moto (Bluetooth message)
- `speed` (m/s), `mileage` (m total), `powerPer` (%)
- `BatTmp` (°C), `TransGearPos`, `InverterActTemp`, `MotorActTemp`
- `ActTorq`, `ActHV_Cur`, `ActHV_Volt`, `BattCurr`, `BattVolt`, `BattSOH`
- `Longitude`, `Latitude`, `GPSRxLev` (satelites), `Altitude`
- `vin` (numero de serie MCU)

### Comandos remotos (Operate4g)
- 1 = lock/unlock
- 2 = headlight
- 3 = horn (loudspeaker)
- 4 = double flashers
- 0x10000001+ = comandos extendidos

### Arquitectura de comunicacion
- **BLE (servicio fea1):** Pairing/autenticacion
- **WiFi Direct:** Datos locales entre app y moto
- **MQTT:** Comandos remotos a distancia (4G/5G del celular → cloud → T-box)

## App Android

**Ubicacion del codigo:** `android_app/`

### Funcionalidades
1. **Scanner BLE** - Escanea dispositivos CFMOTO por nombre/MAC/servicio
2. **GATT Explorer** - Conecta y explora services/characteristics
3. **Sniffer Mode** - Servicio en foreground que captura todo el trafico BLE

### Construir
```bash
cd android_app
./gradlew assembleDebug
```

### Instalar
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Archivos de referencia

- `cfmoto_ble_scanner.py` - Scanner CLI en Python
- `cfmoto_scan_2026-05-09_11-17-19.json` - Scan captura
- `cfmoto_devices_2026-05-09_11-19-32.json` - Devices conectados
- `cfmoto_ride_base.apk` - APK de CFMOTO RIDE (extraido)
- `cfmoto_ride_extracted/` - Contenido del APK
- `bluetooth.proto`, `Meter.proto` - Protocolo documentado

## siguiente paso

1. Con la moto cerca, usar el Sniffer para capturar el handshake de autenticacion
2. Analizar los bytes capturados para revertir el cipher
3. Con el cipher, implementar comandos remotos propios sin la app oficial