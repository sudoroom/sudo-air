# Deployment Instructions

Before we begin we'll need to setup our cloudflare account and setup a cloudflare tunnel. It's free.
Please follow these instructions: [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)

The next thing we'll need to do is buy a cheap domain that we'll use to expose our internal services to
the outside world. Follow this [namcheap guide](https://www.youtube.com/watch?v=MoePjwotTUE) you can buy the cheapest.

Next thing we'll want to do is setup our cloudflare tunnels to use our namecheap domain. Follow this guide for help: [How to set up DNS records for your domain in a Cloudflare account](https://www.namecheap.com/support/knowledgebase/article.aspx/9607/2210/how-to-set-up-dns-records-for-your-domain-in-a-cloudflare-account/)

Once we have our domain setup with our cloudflare tunnel, we need to configure our tunnel. We're going to need 2 tunnels. One for the incoming MQTT messages and one for the outgoing InfluxDB connection.

The domains should be something like:

- influxdb.domain.com
- mosquitto.domain.com

![tunnel setup](figures/tunnel_screenshot.png)

# Required Software

We use docker to stand up our infrastructure in the same host. You'll want to install docker by running

```bash
sudo chmod +x install_docker.sh
./install_docker.sh
```

Once you have that setup you'll want to clone the repository:

```bash
git clone git@github.com:sudoroom/sudo-air.git
```

# Initial Setup

## Mosquitto

We'll need to create a password and a config for the mosquitto mqtt broker.

```bash

# create directories necessary
cd sudo-air
mkdir mosquitto/config
touch mosquitto/config/password.txt
touch mosquitto/config/mosquitto.conf

# setup the password
docker run --rm -v "$PWD/mosquitto/config:/mosquitto/config" eclipse-mosquitto mosquitto_passwd -b /mosquitto/config/password.txt [USERNAME] [PASSWORD]
```

# Token Generation

# Edit .env file
