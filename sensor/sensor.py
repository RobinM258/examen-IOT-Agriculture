import json
import os
import ssl
import random
import time

import paho.mqtt.client as mqtt

SENSOR_ID = os.getenv("SENSOR_ID", "sensor_01")
BROKER_HOST = os.getenv("BROKER_HOST", "broker")
BROKER_PORT = int(os.getenv("BROKER_PORT", "8883"))
INTERVAL = float(os.getenv("INTERVAL", "10"))

CERT_DIR = "/app/certs"
CA_CERT = os.path.join(CERT_DIR, "ca.crt")
CLIENT_CERT = os.path.join(CERT_DIR, f"{SENSOR_ID}.crt")
CLIENT_KEY = os.path.join(CERT_DIR, f"{SENSOR_ID}.key")

TOPIC = f"agriculture/{SENSOR_ID}/mesures"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[{SENSOR_ID}] Connecté au broker avec TLS/mTLS.", flush=True)
    else:
        print(f"[{SENSOR_ID}] Connexion refusée : {reason_code}", flush=True)


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=SENSOR_ID,
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect

    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )
    client.tls_insecure_set(False)

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            # Valeurs simulées pour démontrer les alertes.
            if SENSOR_ID == "sensor_01":
                 measurement = {"humidite_sol": round(random.uniform(18, 45), 1)}
            else:
                 measurement = {"temperature": round(random.uniform(15, 38), 1)}

            payload = {
                "capteur": SENSOR_ID,
                "timestamp": int(time.time()),
                **measurement,
            }

            info = client.publish(
                TOPIC,
                json.dumps(payload),
                qos=1,
            )
            info.wait_for_publish()
            print(f"[{SENSOR_ID}] Publication : {payload}", flush=True)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
