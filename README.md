# Chaîne de supervision IoT sécurisée (cas Agriculture)

Capteurs simulés -> MQTT sur mTLS -> broker Mosquitto -> superviseur.

## Prérequis
Docker (avec Compose) et openssl.

## Lancer
    bash gen-certs.sh
    docker compose up --build
    docker compose logs -f supervisor

Les certificats sont générés localement (aucun secret dans le dépôt).

## Ce que fait chaque service
- broker : Mosquitto, mTLS obligatoire, ACL par topic, non publié sur l'hôte
- sensor_01 / sensor_02 : humidité du sol et température simulées
- supervisor : seuils, détection de panne (silence), détection d'objet inconnu

## Paramètres
INTERVAL (s) : 900 en nominal (15 min), 10 pour la démo.
SILENCE_TIMEOUT (s) : délai avant alerte de panne.

## Preuves
Voir le dossier `preuves/` et la section 4 du dossier.
