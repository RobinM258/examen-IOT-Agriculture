# Rapport de tests — Agriculture IoT sécurisée

## 1. Objectif

Valider le fonctionnement de la chaîne IoT composée de deux capteurs simulés,
d'un broker MQTT Mosquitto et d'un superviseur.

Environnement : Linux et Docker Compose.
Port MQTT TLS : 8883.
Les journaux ont montré des connexions utilisant TLS 1.3.

## 2. Résultats des tests

| ID | Scénario | Résultat observé | Statut |
|---|---|---|---|
| T01 | Validation Docker Compose | La configuration a été validée | Réussi |
| T02 | Démarrage des services | Les quatre conteneurs sont actifs | Réussi |
| T03 | Publication du capteur 1 | Mesures reçues par le superviseur | Réussi |
| T04 | Publication du capteur 2 | Mesures reçues par le superviseur | Réussi |
| T05 | Alerte humidité | 22 %, seuil d'alerte à 25 % | Réussi |
| T06 | Alerte température | 37 °C, seuil d'alerte à 35 °C | Réussi |
| T07 | Connexion sans certificat client | Le broker a rejeté la connexion TLS | Réussi |
| T08 | Publication sur le topic d'un autre capteur | Le broker a journalisé `Denied PUBLISH` | Réussi |
| T09 | Détection d'un capteur inconnu | Scénario de test temporaire réalisé | À documenter avec une preuve dédiée |
| T10 | Nettoyage après les tests | ACL d'origine restaurée et fichiers temporaires supprimés | Réussi |

## 3. Commandes de vérification

--bash
docker-compose config --quiet
docker-compose ps
docker-compose logs --since=5m supervisor
docker-compose logs --since=5m broker
### Connexion sans certificat

Le broker a rejeté une connexion TLS sans certificat client.

### Refus par ACL

Le journal du broker a signalé `Denied PUBLISH` lors d'une tentative de publication sur le topic d'un autre capteur.

### Alertes métier

Le superviseur a signalé une humidité de 22 % et une température de 37 °C, conformément aux seuils pédagogiques.

## 5. Limites et travaux complémentaires

- Conserver des captures horodatées des tests.
- Tester les certificats expirés, révoqués ou signés par une autorité inconnue.
- Tester la rotation des certificats.
- Automatiser le test de détection d'un capteur inconnu.
- Revoir les permissions, dépendances et images Docker avant un usage réel.

## 6. Conclusion

Les tests réalisés démontrent le fonctionnement de la communication MQTT sécurisée, le rejet d'une connexion sans certificat, l'application des ACL et la génération d'alertes de seuil. Ils ne constituent pas une certification de sécurité ou de conformité.
