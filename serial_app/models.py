from datetime import datetime
import uuid
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text


class Serial(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default=datetime.now())
    header: str
    payload_length: str = Field(sa_column=Column(Text))
    gid: str
    did: str
    latitude_int: str = Field(sa_column=Column(Text))
    latitude_frac: str = Field(sa_column=Column(Text))
    longitude_int: str = Field(sa_column=Column(Text))
    longitude_frac: str = Field(sa_column=Column(Text))
    latitude: float
    longitude: float
    time_hour: str = Field(sa_column=Column(Text))
    time_minute: str = Field(sa_column=Column(Text))
    time_second: str = Field(sa_column=Column(Text))
    time: str
    mode: str = Field(sa_column=Column(Text))
    gps_quality: str = Field(sa_column=Column(Text))
    battery_percent: str = Field(sa_column=Column(Text))
    device_to_host_rssi: str = Field(sa_column=Column(Text))
    host_to_device_rssi: str = Field(sa_column=Column(Text))
    heart_rate: str = Field(sa_column=Column(Text))
    blood_oxygen: str = Field(sa_column=Column(Text))
    stress: str = Field(sa_column=Column(Text))
    step: str = Field(sa_column=Column(Text))
    distance: str = Field(sa_column=Column(Text))
    calorie: str = Field(sa_column=Column(Text))

    # Contructor to create a new instance of the Serial class from serial data payload
    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) == 22:
            # No watch data available in the payload.
            payload = payload[:22] + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

        # If payload is less than 34 bytes, this is handshake data
        if len(payload) < 34:
            print(f"Handshake data: {payload.decode('utf-8', errors='replace')}")
            print(f"Handshake data (hex): {payload.hex()}")
            return
        header = payload[:2].hex()
        payload_length = str(payload[2])
        gid = hex(payload[3])
        did = hex(payload[4])
        latitude_int = str(int.from_bytes(payload[5:7], "big"))
        latitude_frac = str(int.from_bytes(payload[7:9], "big"))
        longitude_int = str(int.from_bytes(payload[9:11], "big"))
        longitude_frac = str(int.from_bytes(payload[11:13], "big"))
        time_hour = str(payload[13])
        time_minute = str(payload[14])
        time_second = str(payload[15])
        time = f"{payload[13]}:{payload[14]}:{payload[15]}"
        mode = str(payload[16])
        # Add GPS quality - using a default value since exact location in payload is unclear
        gps_quality = "0"  # Default value
        latitude_msb_bit = (payload[16] & 0b10000000) >> 7
        longitude_msb_bit = (payload[16] & 0b01000000) >> 6
        rsvd_bit = (payload[16] & 0b00100000) >> 5
        gps_quality = str((payload[16] & 0b00011100) >> 2)

        # Fix latitude and longitude calculation
        latitude_int_val = int(latitude_int)
        latitude_frac_val = int(latitude_frac) + (latitude_msb_bit * 0x10000)
        # Format latitude_int_val with up to 4 leading zeros
        latitude_int_str = str(latitude_int_val).zfill(4)
        # Convert to proper decimal degrees
        latitude_val_str = f"{latitude_int_str}.{latitude_frac_val}"
        # fix the signifcant digit to 4 fixed digits
        latitude = float(latitude_val_str[:2]) + float(latitude_val_str[2:]) / 60.0

        longitude_int_val = int(longitude_int)
        longitude_frac_val = int(longitude_frac) + (longitude_msb_bit * 0x10000)
        # Convert to proper decimal degrees
        longitude_val_str = f"{longitude_int_val}.{longitude_frac_val}"
        # fix the signifcant digit to 4 fixed digits
        longitude = float(longitude_val_str[:3]) + float(longitude_val_str[3:]) / 60.0

        battery_percent = str(payload[17])
        device_to_host_rssi = str(int.from_bytes(payload[18:20], "big", signed=True))
        host_to_device_rssi = str(int.from_bytes(payload[20:22], "big", signed=True))
        heart_rate = str(payload[22])
        blood_oxygen = str(payload[23])
        stress = str(payload[24])
        step = str(int.from_bytes(payload[25:28], "big"))
        distance = str(int.from_bytes(payload[28:31], "big"))
        calorie = str(int.from_bytes(payload[31:34], "big"))

        return cls(
            header=header,
            payload_length=payload_length,
            gid=gid,
            did=did,
            latitude_int=latitude_int,
            latitude_frac=latitude_frac,
            longitude_int=longitude_int,
            longitude_frac=longitude_frac,
            latitude=latitude,
            longitude=longitude,
            time_hour=time_hour,
            time_minute=time_minute,
            time_second=time_second,
            time=time,
            mode=mode,
            gps_quality=gps_quality,  # Add this parameter
            battery_percent=battery_percent,
            device_to_host_rssi=device_to_host_rssi,
            host_to_device_rssi=host_to_device_rssi,
            heart_rate=heart_rate,
            blood_oxygen=blood_oxygen,
            stress=stress,
            step=step,
            distance=distance,
            calorie=calorie,
        )
