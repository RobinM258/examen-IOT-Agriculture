import json
import os
import ssl

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "broker")
BROKER_PORT = int(os.getenv("BROKER_PORT", "8883"))

CERT_DIR = "/app/certs"
CA_CERT = os.path.join(CERT_DIR, "ca.crt")
CLIENT_CERT = os.path.join(CERT_DIR, "supervisor.crt")
CLIENT_KEY = os.path.join(CERT_DIR, "supervisor.key")

# Liste d'autorisation indépendante des données reçues.
AUTHORIZED_SENSORS = {"sensor_01", "sensor_02"}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[SUPERVISEUR] Connexion mTLS établie.", flush=True)
        client.subscribe("agriculture/+/mesures", qos=1)
        print("[SUPERVISEUR] Abonné aux mesures des capteurs.", flush=True)
    else:
        print(f"[SUPERVISEUR] Connexion refusée : {reason_code}", flush=True)


def on_message(client, userdata, message):
    topic_parts = message.topic.split("/")

    if len(topic_parts) != 3 or topic_parts[0] != "agriculture":
        print(f"[SÉCURITÉ] Topic inattendu : {message.topic}", flush=True)
        return

    sensor_from_topic = topic_parts[1]

    if sensor_from_topic not in AUTHORIZED_SENSORS:
        print(
            f"[INTRUSION] Capteur inconnu détecté dans le topic : "
            f"{sensor_from_topic}",
            flush=True,
        )
        return

    try:
        data = json.loads(message.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print(f"[SÉCURITÉ] Message JSON invalide sur {message.topic}", flush=True)
        return

    if data.get("capteur") != sensor_from_topic:
        print(
            f"[SÉCURITÉ] Incohérence identité/topic : {message.topic}",
            flush=True,
        )
        return

    print(f"[MESURE] {message.topic} : {data}", flush=True)

    if sensor_from_topic == "sensor_01":
        humidity = data.get("humidite_sol")
        if isinstance(humidity, (int, float)) and humidity < 25:
            print(
                f"[ALERTE] Humidité du sol basse : {humidity}% "
                f"(seuil pédagogique : 25%).",
                flush=True,
            )

    elif sensor_from_topic == "sensor_02":
        temperature = data.get("temperature")
        if isinstance(temperature, (int, float)) and temperature > 35:
            print(
                f"[ALERTE] Température élevée : {temperature}°C "
                f"(seuil pédagogique : 35°C).",
                flush=True,
            )


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="supervisor",
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )
    client.tls_insecure_set(False)

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
