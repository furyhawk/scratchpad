from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import serial as pyserial
import asyncio
from sqlmodel import create_engine, Session, SQLModel

import models as s_models

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///serial.db")
SQLModel.metadata.create_all(engine)
session = Session(engine)


async def read_serial_data():
    try:
        ser = pyserial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    except pyserial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    while True:
        try:
            data = ser.readline()
            if data:
                print(f"Raw data from serial: {data}")
                ser_obj = s_models.Serial.from_payload(data)
                if ser_obj is not None:  # Check if ser_obj is not None
                    session.add(ser_obj)
                    session.commit()
                    yield ser_obj.json()
        except pyserial.SerialException as e:
            print(f"Error reading from serial port: {e}")
            break


@app.websocket("/serial-data")
async def serial_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        async for data in read_serial_data():
            try:
                await websocket.send_text(data)
            except WebSocketDisconnect:
                break
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"Error in WebSocket handler: {e}")


@app.get("/test-handshake")
async def test_handshake():
    try:
        ser = pyserial.Serial("/dev/ttyUSB0", 115200, timeout=2)
        # Send the handshake test string
        ser.write(b"$<")

        # Wait for response
        response = ser.readline()
        ser.close()

        if response:
            return {
                "status": "success",
                "response": response.decode("utf-8", errors="replace"),
            }
        else:
            return {"status": "error", "message": "No response received from device"}

    except pyserial.SerialException as e:
        return {"status": "error", "message": f"Serial port error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
