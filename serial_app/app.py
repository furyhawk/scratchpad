from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import serial as pyserial
import asyncio
import os
from sqlmodel import create_engine, Session, SQLModel
from datetime import datetime
from pydantic import BaseModel

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

# Serial port configuration - can be modified based on system
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200


def is_serial_port_available():
    return os.path.exists(SERIAL_PORT)


async def read_serial_data():
    # Initialize ser variable before the try block
    ser = None

    if not is_serial_port_available():
        print(f"Serial port {SERIAL_PORT} not found")
        yield f'{{"error": "Serial port {SERIAL_PORT} not found"}}'
        return  # Early return if port not available

    try:
        ser = pyserial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Successfully connected to {SERIAL_PORT}")
    except pyserial.SerialException as e:
        error_msg = f"Error opening serial port: {e}"
        print(error_msg)
        yield f'{{"error": "{error_msg}"}}'
        return  # Early return if we can't open the port

    # Only continue if we have a valid serial connection
    while True:
        try:
            data = ser.readline()
            if data:
                print(f"Raw data from serial: {data}")
                print(f"Payload Length: {len(data)}")
                ser_obj = s_models.Serial.from_payload(data)
                print(f"Serial object: {ser_obj}")

                # Get JSON from the original object first
                json_data = ser_obj.json() if ser_obj is not None else None

                if ser_obj is not None:  # Check if ser_obj is not None
                    try:
                        # Create a copy of the object before adding to the session
                        db_obj = ser_obj.model_copy(deep=True)

                        # Check if required fields are populated
                        if db_obj.header is None:
                            print(
                                "Warning: header field is NULL, setting default value"
                            )
                            db_obj.header = (
                                "DEFAULT"  # Set a default value or appropriate fallback
                            )

                        # Add additional validation for other required fields if needed
                        # if db_obj.some_other_required_field is None:
                        #     db_obj.some_other_required_field = default_value

                        session.add(db_obj)
                        session.commit()
                        print(f"Successfully saved to database")
                    except Exception as e:
                        # Rollback the session in case of any error
                        session.rollback()
                        print(f"Database error, transaction rolled back: {e}")
                        # Continue processing even if DB save fails

                    print(f"Serial object JSON: {json_data}")
                    yield json_data
                else:
                    # Handle case where serial object couldn't be created
                    if len(data) < 34:
                        yield f'{{"info": "Handshake data received", "data": "{data.decode("utf-8", errors="replace")}", "hex": "{data.hex()}"}}'
                    else:
                        yield f'{{"warning": "Received malformed data", "data_length": {len(data)}, "hex": "{data.hex()}"}}'
            await asyncio.sleep(0.1)  # Small delay to prevent CPU hogging
        except pyserial.SerialException as e:
            error_msg = f"Error reading from serial port: {e}"
            print(error_msg)
            yield f'{{"error": "{error_msg}"}}'
            break
        except Exception as e:
            error_msg = f"Unexpected error processing serial data: {e}"
            print(error_msg)
            yield f'{{"error": "{error_msg}"}}'
            # Don't break the loop for other exceptions


@app.get("/status")
async def status():
    """Enhanced endpoint to check server status and provide detailed information"""
    port_available = is_serial_port_available()

    # Check if we can actually open the serial port
    port_openable = False
    error_message = None
    if port_available:
        try:
            ser = pyserial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            port_openable = True
            ser.close()
        except pyserial.SerialException as e:
            error_message = str(e)

    # Get recent connection statistics
    try:
        with Session(engine) as db_session:
            recent_records_count = db_session.query(s_models.Serial).count()
            latest_record = (
                db_session.query(s_models.Serial)
                .order_by(s_models.Serial.timestamp.desc())
                .first()
            )
            latest_timestamp = latest_record.timestamp if latest_record else None
    except Exception as e:
        recent_records_count = 0
        latest_timestamp = None

    return {
        "status": "online",
        "serial_port": SERIAL_PORT,
        "baud_rate": BAUD_RATE,
        "port_available": port_available,
        "port_openable": port_openable,
        "error": error_message,
        "database": {
            "recent_records_count": recent_records_count,
            "latest_record_timestamp": latest_timestamp,
        },
        "server_time": datetime.now().isoformat(),
    }


@app.get("/history")
async def get_history(limit: int = 10):
    """Endpoint to retrieve recent data records"""
    try:
        with Session(engine) as db_session:
            records = (
                db_session.query(s_models.Serial)
                .order_by(s_models.Serial.timestamp.desc())
                .limit(limit)
                .all()
            )

            return {"records": [record.dict() for record in records]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.websocket("/serial-data")
async def serial_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        async for data in read_serial_data():
            try:
                print(
                    f"Sending data to client: {data!r}"
                )  # Use !r to show raw representation
                await websocket.send_text(data)
            except WebSocketDisconnect:
                break
        # If we exit the loop without an exception, it means the serial port is not available
        if not is_serial_port_available():
            # Truncate close reason to prevent protocol error
            close_reason = f"Serial port {SERIAL_PORT} not available"
            await websocket.close(1008, close_reason[:100])
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"Error in WebSocket handler: {e}")
        # Truncate error message to prevent protocol error
        error_msg = f"Server error: {str(e)}"
        await websocket.close(1011, error_msg[:100])


@app.get("/test-handshake")
async def test_handshake():
    try:
        ser = pyserial.Serial("/dev/ttyUSB0", 115200, timeout=2)
        # Send the handshake test string
        ser.write(b"$<")

        # Wait for two lines of response
        response1 = ser.readline()
        response2 = ser.readline()
        ser.close()

        if response1 or response2:
            return {
                "status": "success",
                "response1": (
                    response1.decode("utf-8", errors="replace") if response1 else ""
                ),
                "response2": (
                    response2.decode("utf-8", errors="replace") if response2 else ""
                ),
            }
        else:
            return {"status": "error", "message": "No response received from device"}

    except pyserial.SerialException as e:
        return {"status": "error", "message": f"Serial port error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


class CommandRequest(BaseModel):
    command: str


@app.post("/send-command")
async def send_command(request: CommandRequest):
    if not is_serial_port_available():
        raise HTTPException(
            status_code=400, detail=f"Serial port {SERIAL_PORT} not available"
        )

    try:
        ser = pyserial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # Send the command
        ser.write(request.command.encode("utf-8"))

        # Read multiple responses (up to a reasonable limit)
        responses = []
        max_responses = 50  # Safety limit to prevent infinite loops
        timeout_duration = 2  # Seconds to wait for all responses

        # Set a shorter timeout for individual reads
        ser.timeout = 0.1

        start_time = datetime.now()
        while len(responses) < max_responses:
            response = ser.readline()
            if response:
                responses.append(
                    {
                        "raw": response.decode("utf-8", errors="replace"),
                        "hex": response.hex(),
                    }
                )
            else:
                # If there's no more data and we've waited at least a bit or got some responses, break
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout_duration or (len(responses) > 0 and elapsed > 0.2):
                    break

        ser.close()

        return {"status": "success", "responses": responses, "count": len(responses)}
    except pyserial.SerialException as e:
        raise HTTPException(status_code=500, detail=f"Serial port error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
