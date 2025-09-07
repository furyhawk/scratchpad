"""
CircuitPython MiniMQTT subscriber for environment topics.

Subscribes to the topics:
  - temperature
  - pressure
  - humidity

Configuration via settings.toml on CIRCUITPY drive (preferred) or env vars:
  CIRCUITPY_WIFI_SSID="..."
  CIRCUITPY_WIFI_PASSWORD="..."
  MQTT_BROKER="broker.example.com"
  MQTT_PORT="1883"          # optional; defaults 1883 or 8883 if TLS
  MQTT_USERNAME="user"       # optional
  MQTT_PASSWORD="pass"       # optional
  MQTT_TLS="false"           # "true" to enable TLS

This file is intended to live on the CIRCUITPY drive with lib/
containing adafruit_minimqtt and dependencies.
"""

import os
import time

try:
    import wifi  # type: ignore
    import socketpool  # type: ignore
    import ssl as ssl_module  # type: ignore
except ImportError:
    # When run off-board (e.g. on your PC), these won't exist.
    wifi = None  # type: ignore
    socketpool = None  # type: ignore
    ssl_module = None  # type: ignore

try:
    # CircuitPython MiniMQTT (available on the board's CIRCUITPY lib path)
    from adafruit_minimqtt.adafruit_minimqtt import MQTT  # type: ignore[reportMissingImports]
except Exception as e:  # pragma: no cover - helpful message on import failure
    raise RuntimeError(
        "MiniMQTT not found. Ensure lib/adafruit_minimqtt is on the CIRCUITPY drive"
    ) from e


# --- Helpers -----------------------------------------------------------------


def _getenv_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def _wifi_credentials():
    ssid = os.getenv("CIRCUITPY_WIFI_SSID") or os.getenv("WIFI_SSID")
    pwd = os.getenv("CIRCUITPY_WIFI_PASSWORD") or os.getenv("WIFI_PASSWORD")
    return ssid, pwd


def connect_wifi(timeout: float = 20.0):
    if wifi is None:
        print("Wi‑Fi module not available in this runtime.")
        return False, "wifi module missing"

    if getattr(wifi.radio, "connected", False):
        try:
            print("Wi‑Fi already connected:", wifi.radio.ipv4_address)
        except Exception:
            print("Wi‑Fi already connected.")
        return True, "ok"

    ssid, pwd = _wifi_credentials()
    if not ssid or not pwd:
        return False, "Missing Wi‑Fi credentials in settings.toml or env"

    print("Connecting Wi‑Fi to:", ssid)
    start = time.monotonic()
    last_err = None
    while time.monotonic() - start < timeout:
        try:
            wifi.radio.connect(ssid, pwd)  # type: ignore[arg-type]
            print("Wi‑Fi connected, IP:", wifi.radio.ipv4_address)
            return True, "ok"
        except Exception as e:
            last_err = e
            time.sleep(1.0)
    return False, f"Wi‑Fi failed: {repr(last_err)}"


def _mqtt_config():
    host = os.getenv("MQTT_BROKER") or "test.mosquitto.org"
    tls = _getenv_bool("MQTT_TLS", False)
    try:
        port = int(os.getenv("MQTT_PORT") or (8883 if tls else 1883))
    except Exception:
        port = 8883 if tls else 1883
    user = os.getenv("MQTT_USERNAME")
    pwd = os.getenv("MQTT_PASSWORD")
    return host, port, tls, user, pwd


# --- Topic callbacks ----------------------------------------------------------


def _print_kv(client, topic, message):
    # client.user_data can be used to share state across callbacks
    ts = time.monotonic()
    try:
        # Try to decode bytes and/or cast to float nicely
        if isinstance(message, (bytes, bytearray)):
            s = message.decode("utf-8", errors="ignore").strip()
        else:
            s = str(message).strip()
        val = float(s)
        s_fmt = f"{val:g}"
    except Exception:
        s_fmt = s  # leave as-is
    print(f"[{ts:8.1f}] {topic}: {s_fmt}")


def main():
    ok, info = connect_wifi()
    if not ok:
        print("Wi‑Fi not connected:", info)
        # We still continue; broker might be on a non-Wi‑Fi interface on some boards

    if socketpool is None:
        raise RuntimeError("socketpool module not available")

    host, port, use_tls, user, pwd = _mqtt_config()
    print("MQTT broker:", host, "port:", port, "TLS:", use_tls)

    pool = socketpool.SocketPool(wifi.radio) if wifi else None
    ssl_ctx = None
    if use_tls:
        if ssl_module is None:
            raise RuntimeError("TLS requested but ssl module not available")
        try:
            ssl_ctx = ssl_module.create_default_context()
        except Exception:
            # Some CircuitPython builds use an ssl shim that does not expose context creation
            ssl_ctx = None

    # Create MQTT client
    client = MQTT(
        broker=host,
        port=port,
        username=user,
        password=pwd,
        is_ssl=use_tls,
        socket_pool=pool,
        ssl_context=ssl_ctx,
        keep_alive=60,
        socket_timeout=1,
        connect_retries=5,
        user_data={},
    )

    # Optional general callbacks
    def _on_connect(mqtt_client, user_data, flags, rc):  # signature used by MiniMQTT
        print("Connected to MQTT, result code:", rc)

    def _on_disconnect(mqtt_client, user_data, rc):
        print("Disconnected from MQTT, rc:", rc)

    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect

    # Per-topic callbacks
    client.add_topic_callback("temperature", _print_kv)
    client.add_topic_callback("pressure", _print_kv)
    client.add_topic_callback("humidity", _print_kv)

    # Connect and subscribe
    try:
        client.connect(clean_session=True)
        client.subscribe([("temperature", 0), ("pressure", 0), ("humidity", 0)])
    except Exception as e:
        print("MQTT connect/subscribe failed:", repr(e))

    last_ping = time.monotonic()
    while True:
        try:
            # Non-blocking loop; returns list of packet types or None
            client.loop(timeout=1.0)
            # Keep-alive ping once in a while (defensive)
            now = time.monotonic()
            if now - last_ping > 30:
                try:
                    client.ping()
                except Exception:
                    pass
                last_ping = now
        except Exception as e:
            print("MQTT error:", repr(e))
            try:
                client.reconnect(resub_topics=True)
            except Exception as re:
                print("Reconnect failed:", repr(re))
                time.sleep(2.0)


if __name__ == "__main__":
    main()
