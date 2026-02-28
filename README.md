# Sudo Air: Air Quality Monitoring Network in the Bary Area

![Air Quality Data Dashboard]()

# Description

This project establishes up the data processing infrastructure.

Technologies and Services used:

| Technology | Purpose |
|---|---|
| **MQTT** | Lightweight messaging protocol for real-time data transmission between air quality nodes and the processing infrastructure |
| **InfluxDB** | Time-series database for storing and querying air quality metrics (PM2.5, PM10, voltage, etc.) with high-performance data retention |
| **Notehub** | Cloud service that aggregates sensor data from distributed nodes and provides APIs for data access and management |
| **Docker** | Containerization platform for deploying consistent, scalable data processing services across environments |

# Air Quality Node Diagram

![Hardware Diagram](hardware-diagram.png)

## Parts

- TODO: Add parts here.

# Data Infrastructure Architecture

The system architecture follows this data flow:

1. **Data Collection**: Air quality nodes send sensor data to Notehub over the LTE network
2. **Event Triggering**: Each data push triggers an event sent to a locally hosted MQTT broker
3. **Data Processing**: A Python script subscribes to the MQTT broker, parses the data, and pushes it to a local InfluxDB database
4. **Visualization**: InfluxDB serves as the data source for a Grafana dashboard hosted on a university server
5. **Exposure**: Cloudflare Tunnels expose both the local services and Grafana dashboard to external access

![Infrastructure Diagram](sudo-air-infrastructure.png)

## Environment Variables

This project requires a `.env` file in the root directory to store sensitive credentials and configuration. The following variables must be configured:

| Variable | Description | Sample Value |
|---|---|---|
| `MQTT_USERNAME` | Username for MQTT broker authentication | `air_quality_user` |
| `MQTT_PASSWORD` | Password for MQTT broker authentication | — |
| `MQTT_LOCAL_BROKER` | Hostname of the local MQTT broker | `localhost` |
| `MQTT_REMOTE_BROKER` | Hostname of the remote MQTT broker | `mqtt.example.com` |
| `MQTT_LOCAL_PORT` | Port for local MQTT connections | `1883` |
| `MQTT_REMOTE_PORT` | Port for remote MQTT connections | `8883` |
| `MQTT_PORT` | Default MQTT port | `1883` |
| `MQTT_WS_PORT` | WebSocket port for MQTT | `8080` |
| `CLOUDFLARE_TUNNEL_TOKEN` | Authentication token from Cloudflare Zero Trust Dashboard | — |
| `INFLUXDB_PORT` | Port for InfluxDB service | `8086` |
| `INFLUXDB_USERNAME` | Username for InfluxDB authentication | `influx_admin` |
| `INFLUXDB_PASSWORD` | Password for InfluxDB authentication | — |
| `INFLUXDB_ORG` | InfluxDB organization name | `sudo-air` |
| `INFLUXDB_BUCKET` | InfluxDB bucket for sensor data storage | `air_quality_metrics` |
| `INFLUXDB_TOKEN` | Authentication token for InfluxDB API access | — |

**⚠️ Security Note:** Never commit the `.env` file to version control. Add it to `.gitignore` to protect sensitive credentials.


# Air Quality Metrics information

Nodes collecting Air Quality Data. Has 2 units:

- 2.5 micron particles (PM2.5) are extremely fine airborne pollutants, smaller than a human hair, that pose significant health risks because they can deeply penetrate lungs and enter the bloodstream, causing respiratory issues, heart problems, and other serious conditions, originating from sources like vehicle exhaust, factories, and wood burning, and are often monitored for air quality alerts.

- 10 micron (µm) particles, known as PM10, are a significant air pollutant: coarse dust, pollen, and mold that are inhalable (under 10 µm) but typically get trapped in the nose/throat, causing irritation, though larger ones (2.5-10 µm) can enter the lungs, affecting those with heart/lung conditions; they're a mix from industry, vehicles, dust, etc., and while less harmful than smaller PM2.5, they still pose health risks, with good masks helping filter them.

Also has data:
- location (closest cell tower)
- voltage (battery life?)
- capture time

all of the nodes publish their data here
- https://notehub.io/project/app:b524d40a-52fc-4acd-a198-571298759ff3/devices

to see my specific node data go to events and filter

# Information on AQI levels
https://atmotube.com/blog/particulate-matter-pm-levels-and-aqi
