from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import serial
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_serial_data():
    try:
        ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    ser.write(b"$<")
    while True:
        try:
            data = ser.readline()
            if data:
                yield f"{data.hex()} : {data.decode('utf-8', errors='ignore')}"
        except serial.SerialException as e:
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
