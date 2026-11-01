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



# 2. Architecture et limites de confiance

# 2.1 Architecture et limites de confiance

![[Diagramme architecture 2.png]]

## 2.2 Edge Ou Cloud ? 

Nous avons retenu edge car le broker et le superviseur sont hébergés localement. De plus la détection est évalué sur place. Ce choix répond a la priorité de robustesse car il limite l'exposition des données  et évitent un coût d'abonnement pour un volume de donnés très faible.

# 3. Sécurité implémentée

## 3.1 Identité des objets 
Un certificat par objet, signé par l'AC, CN = sensor_01, etc. Le broker exige le certificat et prend le CN comme nom d’utilisateur. Chaque clé est dans un dossier monté en lecture seule dans son conteneur seulement.

## 3.2 PKI et cycle de vie des clés 

gen-certs.sh crée l’AC puis les certificats (825 jours). Le gabarit accepte que ce soit seulement décrit.

## 3.3 Chiffrement 

Le certificat est vérifié des deux côtés, il y n'y a  jamais de tls_insecure. Au repos : clés en mode 640, conteneurs en lecture seule.

## 3.4 Segmentation et moindre privilège

ACL : chaque objet écrit seulement sur agriculture/<son CN>/mesures, seul le superviseur lit tout.

## 3.6 Détection 

Seuils : humidité < 25 %, température > 35 °C. Panne : silence au-delà de 35 sec . Intrusion : topic d’un CN absent de l’allowlist.

## 3.7 Lancer l'infra 

bash gen-certs.sh
docker compose up --build
docker compose logs -f supervisor

# 4. Rapport d'audit

## 4.1 STRIDE

| Menace | Exemple dans le projet | Protection existante | Risque résiduel |
|---|---|---|---|
| Spoofing — usurpation | Un faux capteur tente de se connecter | Certificats clients X.509 et mTLS | Un certificat valide compromis reste exploitable |
| Tampering — falsification | Un client tente de publier sur le topic d'un autre capteur | ACL MQTT et contrôle de cohérence du topic | Une mesure mensongère d'un capteur autorisé reste possible |
| Repudiation — répudiation | Un acteur conteste une publication | Journaux du broker et du superviseur | Les logs ne constituent pas une preuve infalsifiable |
| Information Disclosure — divulgation | Un tiers tente d'écouter les mesures | TLS et réseaux Docker segmentés | Une compromission d'un conteneur reste possible |
| Denial of Service — déni de service | Multiplication des connexions ou publications | Segmentation réseau et services isolés | Les quotas et mécanismes anti-saturation doivent être renforcés |
| Elevation of Privilege — élévation de privilèges | Un service tente d'accéder à des ressources non autorisées | Conteneurs non-root, lecture seule et no-new-privileges | Une mauvaise configuration Docker reste un risque |

## 4.2 Arbre d'attaque

Objectif : une fausse mesure « sol humide » est acceptée

├─ 1. Injecter la mesure depuis un faux objet
│   ├─ 1.1 Se connecter sans certificat ............ bloqué : mTLS (preuve-mtls)
│   ├─ 1.2 Certificat d'une autre AC ............... bloqué : validation de la CA
│   └─ 1.3 Certificat valide mais inconnu .......... détecté : [INTRUSION] (preuve-intrusion)
│
├─ 2. Se faire passer pour un capteur existant
│   └─ 2.1 Publier sur le topic de sensor_02 ....... bloqué : ACL, rc135 (preuve-acl-rc135)
│
├─ 3. Altérer la mesure en transit ................. bloqué : TLS 1.3
│
└─ 4. Faire taire les vrais capteurs
    └─ Brouillage, vol, pile vide .................. détecté : [PANNE] (preuve-panne)

## 4.3 Table menace 

| ID | Menace | Impact | Proba | Priorité | Contre-mesure | Implémentation |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **M1** | Faux capteur injecte des mesures | 3 | 2 | 6 | mTLS + allowlist | `mosquitto.conf`, `supervisor.py` |
| **M2** | Capteur muet (panne, pile, brouillage) | 2 | 3 | 6 | Détection de silence, QoS 1 | `supervisor.py (watchdog)` |
| **M3** | Usurpation du topic d’un autre capteur | 3 | 1 | 3 | ACL pattern avec `%u` | `acl` |
| **M4** | Vol d’un capteur et de sa clé | 3 | 2 | 6 | Révocation (décrite), une clé par objet | `gen-certs.sh`, `docker-compose.yml` |
| **M5** | Écoute du trafic | 1 | 2 | 2 | TLS 1.3, broker non publié | `docker-compose.yml` |
| **M6** | Saturation du broker | 2 | 1 | 2 | Segmentation réseau (limites de débit : amélioration) | `docker-compose.yml` |

## 4.4 Preuves exécutées
- Client sans certificat rejeté (menace M1) preuves/preuve-mtls
- sensor_01 vers le topic de sensor_02 : Denied PUBLISH, rc135 (menace M3) preuves/preuve-acl-rc135
- [INTRUSION] pour intrus-01 (menace M1) preuves/preuves-intrusions
- [PANNE] après 39 s (menace M2) preuves/preuve-panne

# 5. Rapport de conformité

## 5.1 ETSI EN 303 645	

Il n'y a pas de mot de passe chaque objet se connecte avec son certificat  et les connexion anonymes sont refusées 

## 5.2 OWASP IoT Top 10

Un seul port, en TLS, aucun port publié sur l’hôte, ACL
TLS 1.3 en transit
Un certificat par objet, allowlist, révocation décrite

## 5.3 Cyber Resilience Act

mTLS, moindre privilège, aucun secret par défaut, aucun port publié
images Docker reconstruites régulièrement
Un point de contact et une procédure réception d’un signalement, analyse, correction, information des clients

## 5.4 RGPD

Le RGPD conserne les données d'une personne, ici les mesures sont peux sensibles (température, humidité) mais sont rattachés à un exploitant précis. Les messages sont réduit au minimum id + horodatage + mesure. Les données sont stockés dans les journaux des conteneurs  que docker garde sans limite.  vu que les donnés ne sont pas vraiment critique cela ne pose pas de soucis.

# 6. Contributions

Robin Martinez (robin.martinez2600@gmail.com)
gen-certs.sh
