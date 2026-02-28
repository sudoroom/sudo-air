import datetime
import json
import os
import sys

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from loguru import logger

load_dotenv()

# Configure loguru: remove default handler and add structured one
logger.remove()
logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# MQTT broker settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "/devices/#")

# InfluxDB settings
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", "8086"))
INFLUXDB_URL = os.getenv("INFLUXDB_URL", f"http://localhost:{INFLUXDB_PORT}")


def _validate_env() -> None:
    """Validate that all required environment variables are set."""
    required = {
        "MQTT_USERNAME": MQTT_USERNAME,
        "MQTT_PASSWORD": MQTT_PASSWORD,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_ORG": INFLUXDB_ORG,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        logger.error("Missing required environment variables: {}", ", ".join(missing))
        sys.exit(1)


def _create_influxdb_client() -> InfluxDBClient:
    """Create and return an InfluxDB client."""
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    logger.info("InfluxDB client created for {}", INFLUXDB_URL)
    return client


def on_connect(client, userdata, flags, rc, properties=None) -> None:
    """Callback for when the MQTT client connects to the broker."""
    if rc == 0:
        logger.info("Connected to MQTT broker successfully")
        client.subscribe(MQTT_TOPIC)
        logger.info("Subscribed to topic: {}", MQTT_TOPIC)
    else:
        logger.error("Failed to connect to MQTT broker, return code: {}", rc)


def on_disconnect(client, userdata, flags, rc, properties=None) -> None:
    """Callback for when the MQTT client disconnects from the broker."""
    if rc != 0:
        logger.warning("Unexpected disconnection from MQTT broker (rc={})", rc)
    else:
        logger.info("Disconnected from MQTT broker")


def on_message(client, userdata, msg) -> None:
    """Callback for when a message is received from the MQTT broker."""
    try:
        raw_message = msg.payload.decode()
        logger.debug("Received message on topic '{}': {}", msg.topic, raw_message)

        point = json.loads(raw_message)

        if point.get("file") != "data.qo":
            logger.debug("Ignoring non-data.qo message (file={})", point.get("file"))
            return

        body = point.get("body", {})
        dt = datetime.datetime.fromtimestamp(point["when"], tz=datetime.timezone.utc)

        p = (
            Point("aqi")
            .tag("device", point["device"])
            .field("best_lat", point["best_lat"])
            .field("best_lon", point["best_lon"])
            .field("pm02_5", body["pm02_5"])
            .field("pm10_0", body["pm10_0"])
            .field("temperature", int(body["temperature"]))
            .field("voltage", body["voltage"])
            .time(dt)
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)
        logger.info(
            "Wrote data point for device '{}' at {}", point["device"], dt.isoformat()
        )

    except json.JSONDecodeError:
        logger.error("Failed to parse message as JSON: {}", msg.payload.decode())
    except KeyError as e:
        logger.error("Missing required field in message: {}", e)
    except Exception:
        logger.exception("Unexpected error processing message on topic '{}'", msg.topic)


def main() -> None:
    """Entry point for the MQTT-to-InfluxDB bridge."""
    _validate_env()

    global write_api
    influx_client = _create_influxdb_client()
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    logger.info("Connecting to MQTT broker at {}:{}...", MQTT_BROKER, MQTT_PORT)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception:
        logger.exception("Fatal error in MQTT client")
    finally:
        client.disconnect()
        influx_client.close()
        logger.info("Cleanup complete")


if __name__ == "__main__":
    main()
