# Analyse STRIDE — Agriculture IoT sécurisée

## 1. Objectif

STRIDE est une méthode d'identification des menaces couvrant l'usurpation
d'identité, la falsification, la répudiation, la divulgation d'informations,
le déni de service et l'élévation de privilèges.

## 2. Analyse des menaces

| Menace | Exemple dans le projet | Protection existante | Risque résiduel |
|---|---|---|---|
| Spoofing — usurpation | Un faux capteur tente de se connecter | Certificats clients X.509 et mTLS | Un certificat valide compromis reste exploitable |
| Tampering — falsification | Un client tente de publier sur le topic d'un autre capteur | ACL MQTT et contrôle de cohérence du topic | Une mesure mensongère d'un capteur autorisé reste possible |
| Repudiation — répudiation | Un acteur conteste une publication | Journaux du broker et du superviseur | Les logs ne constituent pas une preuve infalsifiable |
| Information Disclosure — divulgation | Un tiers tente d'écouter les mesures | TLS et réseaux Docker segmentés | Une compromission d'un conteneur reste possible |
| Denial of Service — déni de service | Multiplication des connexions ou publications | Segmentation réseau et services isolés | Les quotas et mécanismes anti-saturation doivent être renforcés |
| Elevation of Privilege — élévation de privilèges | Un service tente d'accéder à des ressources non autorisées | Conteneurs non-root, lecture seule et no-new-privileges | Une mauvaise configuration Docker reste un risque |

## 3. Mesures de défense observées

- Authentification mutuelle par certificats X.509.
- Vérification du certificat du broker par les clients.
- Refus des connexions sans certificat client.
- ACL limitant les publications aux topics autorisés.
- Réseaux Docker séparés entre clients et superviseur.
- Détection applicative des identifiants de capteurs inconnus.
- Alertes lorsque les mesures dépassent les seuils pédagogiques.

## 4. Améliorations recommandées

- Prévoir une procédure effective de révocation et de rotation des certificats.
- Protéger et sauvegarder la clé privée de l'autorité de certification.
- Ajouter des limites de débit et des quotas de connexions.
- Centraliser les journaux et surveiller les tentatives répétées d'accès refusé.
- Ajouter des tests automatisés de sécurité.
- Étudier la sécurisation du démarrage et des mises à jour des équipements physiques.

## 5. Conclusion

L'architecture réduit plusieurs risques grâce au mTLS, aux ACL et à la
segmentation réseau. Les protections restent partielles : ce prototype
nécessite des contrôles complémentaires avant un déploiement réel.
