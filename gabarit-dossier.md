# 1. Cahier des charges

## 1.1 Contexte et cas d'usage

Cas attribué : Agriculture. Exploitation de 5 hectares, située
en zone rurale. L'agriculteur souhaite
mesurer l'humidité du sol et la température toutes les 15 minutes afin d'ajuster son irrigation
sans se déplacer.

Priorité de sécurité : Les objets sont isolés exposés aux intempéries et alimentés sur pile.

## 1.2 Objets et contraintes

| Objet | Rôle | Emplacement | CN |
|---|---|---|---|
| Capteur d'humidité | humidité du sol | parcelle | capteur-humidite-01 |
| Capteur de température | température | parcelle | capteur-temperature-01 |
| Broker Mosquitto | reçoit et distribue | bâtiment | broker |
| Superviseur | seuils  et alertes | bâtiment | superviseur |

Contraintes :
- Autonomie : 2 ans sur pile, donc messages courts et peu fréquents.
- Environnement : extérieur, boîtier étanche, pluie.
- Données : peu sensibles (pas de données personnelles).

## 1.3 Choix de protocoles

Réseau (capteur -> passerelle) :

| | Wi-Fi | 4G | LoRaWAN |
|---|---|---|---|
| Portée | ~50 m | bonne (si couverture) | plusieurs km |
| Énergie | élevée | moyenne | très faible |
| Débit | élevé | moyen | très faible (suffisant) |
| Coût | faible | abonnement par objet | faible |
| Sécurité | WPA2/3 | SIM + TLS | AES-128 intégré |
| Verdict | non | possible, coûteux | retenu |

Pour le réseau retenu, nous avons choisi LoRaWAN pour quatre raisons. Sa portée (plusieurs kilomètres) couvre l’exploitation avec une seule passerelle. Sa consommation très faible est compatible avec une alimentation sur pile. Son faible débit est suffisant, puisque chaque capteur n’envoie qu’un message court toutes les 15 minutes. Enfin, il est peu coûteux et intègre un chiffrement AES-128 des échanges.

Applicatif (passerelle -> broker -> superviseur) :

| | HTTP | CoAP | MQTT |
|---|---|---|---|
| Modèle | requête/réponse | requête/réponse (UDP) | publish/subscribe |
| Poids | lourd | léger | léger |
| Sécurité | TLS | DTLS | TLS + mTLS + ACL |
| Verdict | non | possible | retenu |

Pour la couche applicative, nous avons retenu MQTT. Son modèle publish/subscribe découple les capteurs du superviseur : un capteur publie sur son topic sans connaître le destinataire, et le superviseur s’abonne à l’ensemble des topics. Les messages sont très légers (quelques octets d’en-tête), ce qui convient à des capteurs sur pile qui n’envoient qu’une mesure toutes les 15 minutes. MQTT fonctionne sur TLS et permet l’authentification mTLS. HTTP a été écarté car il est plus lourd et fonctionne en requête/réponse, donc moins adapté à des envois périodiques depuis des objets sur pile. CoAP est léger mais ne dispose pas du broker et des ACL par topic de Mosquitto, que nous voulons utiliser.

## 1.4 Dimensionner
- Objets : 2.
- Fréquence 1 message / 15 minutes, soit 96 messages / jour.
- Volume: Un message fais quelque octets, on reste à quelque Ko/jour
- Autonomie: Avec peut de message par jour sur une radio basse consommation la pile peut tenir plusieurs années.

## 1.5 Architecture et limites de confiance

![[Diagramme architecture 2.png]]

## 1.6 Edge Ou Cloud ? 

Nous avons retenu edge car le broker et le superviseur sont hébergés localement. De plus la détection est évalué sur place. Ce choix répond a la priorité de robustesse car il limite l'exposition des données  et évitent un coût d'abonnement pour un volume de donnés très faible.