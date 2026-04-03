import bluetooth

_SERVICE_UUID = '4fafc201-1fb5-459e-8fcc-c5c9c331914a'                    # UUID of the server
_RX_CHARACTERISTIC_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a6'          # UUID of the characteristic Tx
_TX_CHARACTERISTIC_UUID = 'beb5484a-36e1-4688-b7f5-ea07361b26a6'          # UUID of the characteristic Rx
_BLEDeviceName= "ESP32-S3-GEEK"

_Bluetooth_Mode = 2  # Used to distinguish data sources
_TxCharacteristic = 0
_RxCharacteristic = 0
_ble=0

def connected():
    print("Device connected");

def disconnected():
    global _BLEDeviceName
    print("Device disconnected")
    advertiser(_BLEDeviceName)                                                  # Re-broadcast so that the device can query

def ble_irq(event, data):
    global _ble, _RxCharacteristic,_Bluetooth_Mode
    _rxValue = ""
    if event == 1:
        connected()
    elif event == 2:
        disconnected()
    elif event == 3:  
        _rxValue = _ble.gatts_read(_RxCharacteristic) 
        print(_rxValue)
        _rxValue = ""

def register():
    global _ble,_SERVICE_UUID,_TX_CHARACTERISTIC_UUID,_RX_CHARACTERISTIC_UUID      
    services = (
        (
            bluetooth.UUID(_SERVICE_UUID),
            (
                (bluetooth.UUID(_TX_CHARACTERISTIC_UUID), bluetooth.FLAG_READ),
                (bluetooth.UUID(_RX_CHARACTERISTIC_UUID), bluetooth.FLAG_WRITE),
            )
        ),
    )
    ((TxCharacteristic, RxCharacteristic,), ) = _ble.gatts_register_services(services)
    return (TxCharacteristic, RxCharacteristic)

def send(data):
    global _ble,_TxCharacteristic
    _ble.gatts_write(_TxCharacteristic, data)

def advertiser(name):
    global _ble
    print(name)
    name = bytes(name, 'UTF-8')
    adv_data = bytearray('\x02\x01\x02', 'UTF-8') + bytearray((len(name) + 1, 0x09), 'UTF-8') + name
    _ble.gap_advertise(100, adv_data)

def Bluetooth_Init():
    global _ble,_TxCharacteristic, _RxCharacteristic,_BLEDeviceName
    _ble = bluetooth.BLE()
    _ble.active(True)
    _ble.config(gap_name=_BLEDeviceName)
    _ble.irq(ble_irq)
    _TxCharacteristic, _RxCharacteristic = register()
    advertiser(_BLEDeviceName)
    
Bluetooth_Init()
