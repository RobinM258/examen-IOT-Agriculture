# 1. Cahier des charges

## 1.1 Contexte et cas d'usage

Cas attribué : Agriculture. Exploitation de 5 hectares, située
en zone rurale L'agriculteur souhaite
mesurer l'humidité du sol et la température afin d'ajuster son irrigation
sans se déplacer.

Priorité de sécurité : Les objets sont isolés exposés aux intempéries et alimentés sur pile.

## 1.2 Objets et contraintes

| Objet | Rôle | Emplacement | CN |

| Capteur d'humidité | humidité du sol | parcelle | capteur-humidite-01 |
| Capteur de température | température | parcelle | capteur-temperature-01 |
| Broker  | reçoit et distribue | bâtiment | broker |
| Superviseur | seuils et alertes | bâtiment | superviseur |


Contraintes :
- Autonomie : [X] ans sur pile, donc messages courts et peu fréquents.
- Environnement : extérieur, boîtier étanche, pluie.
- Données : peu sensibles (pas de données personnelles).

## 1.3 Choix de protocoles


