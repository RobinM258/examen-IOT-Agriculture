# Matrice de conformité indicative — Agriculture IoT sécurisée

## 1. Objet

Cette matrice établit une correspondance indicative entre les mesures du
prototype et quelques référentiels de cybersécurité. Elle ne constitue pas
une certification ni une évaluation juridique formelle.

## 2. Matrice

| Référentiel | Domaine concerné | Mesure du projet | État et limites |
|---|---|---|---|
| ETSI EN 303 645 | Communications sécurisées | MQTT avec TLS et authentification mutuelle par certificats | Partiellement couvert ; une évaluation complète reste nécessaire |
| ETSI EN 303 645 | Gestion des vulnérabilités | Dépendances Python et images Docker utilisées | Processus de mises à jour et de divulgation des vulnérabilités à formaliser |
| ETSI EN 303 645 | Protection des identifiants | Clés privées et certificats exclus du dépôt via `.gitignore` | Protection locale à compléter par un stockage sécurisé |
| OWASP IoT Top 10 | Identifiants et authentification | Certificats X.509 et certificat client obligatoire | Couverture partielle ; rotation et révocation à tester |
| OWASP IoT Top 10 | Services réseau | ACL MQTT et segmentation Docker | Couverture partielle ; tests de durcissement complémentaires nécessaires |
| OWASP IoT Top 10 | Confidentialité | TLS pour les communications MQTT | À compléter par une analyse des données stockées et des journaux |
| Cyber Resilience Act (CRA) | Gestion des risques et vulnérabilités | Analyse STRIDE et documentation des tests | Contribution pédagogique ; exigences applicables à évaluer selon le produit et son contexte |
| RGPD | Protection des données personnelles | Projet de supervision agricole simulée | Applicabilité à déterminer selon les données réelles, les personnes concernées et les traitements |

## 3. Actions recommandées

- Formaliser la gestion des vulnérabilités et des mises à jour.
- Documenter la rotation, l'expiration et la révocation des certificats.
- Ajouter une procédure de sauvegarde et de protection de la clé privée de la CA.
- Réaliser une revue des dépendances et des images de conteneurs.
- Définir les durées de conservation des journaux.
- Évaluer les exigences réglementaires applicables avant une commercialisation.

## 4. Conclusion

Le prototype met en œuvre plusieurs mécanismes utiles de cybersécurité, notamment
mTLS, les ACL et la segmentation réseau. La présence de ces mécanismes ne suffit
pas à démontrer une conformité complète aux référentiels ou aux réglementations.
