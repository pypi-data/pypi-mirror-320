# webservices-enedis

**webservices-enedis** est une API permettant de communiquer avec les webservices d'Enedis via des messages SOAP.

## Table des matières

- [Services disponibles](#services-disponibles)
- [Variables d'environnement](#variables-denvironnement)
- [Connexion avec Imposter](#connexion-avec-imposter)
- [Constantes](#constpy)
- [Certificats](#certificats-enedis)

---

## Services disponibles

Actuellement, neuf services sont disponibles, chacun étant défini dans le projet via une classe dédiée contenant les méthodes nécessaires pour communiquer avec les webservices d'Enedis. Les objets à passer en paramètre des méthodes sont décrits dans le chapitre consacré au sous-module `webservices_enedis_common`.

1. **`ConsulterDonneesTechniquesContractuelles`**  
   Permet de consulter les données techniques d'un point. Utilisez la méthode `consultation_donnees_techniques_contractuelles(point)` en passant un objet de type `Point` en argument.

2. **`ConsulterMesures`**  
   Permet de consulter l'historique des consommations d'un point. Utilisez la méthode `consulter_mesures(donnees_consulter_mesures)` en passant un objet de type `DonneesConsulterMesures` en argument.

3. **`ConsulterMesuresDetaillees`**  
   Permet de consulter les données détaillées d'un point. Utilisez la méthode `consulter_mesures_detaillees(demande)` en passant un objet de type `DemandeConsulterMesuresDetaillees` en argument.

4. **`RecherchePoint`**  
   Permet de rechercher un point dans le système d'Enedis. Utilisez la méthode `recherche_point(criteres)` en passant un objet de type `Criteres` en argument.

5. **`CommanderCollectePublicationMesures`**  
   Permet de collecter des données ou de demander une transmission récurrente de données sur le point concerné. Utilisez la méthode `commander_collecte_publication(demande_collecte)` en passant un objet de type `DemandeCollecte` en argument.

6. **`RechercheServicesSouscritsMesures`**  
   Permet de récupérer les données des services souscrits sur un point. Utilisez la méthode `rechercher_services_souscrit_mesures(prm_id)` en passant une chaîne de caractères de 14 caractères correspondant à l'identifiant PRM du point concerné.

7. **`CommanderArretServiceSouscritMesures`**  
   Permet d'arrêter un service de collecte ou de transmission de mesures récurrente. Utilisez la méthode `commander_arret_service_souscrit_mesures(demande_arret)` en passant un objet de type `DemandeArret` en argument.

8. **`CommandeAccesDonneesMesures`**  
   Permet de demander l'accès à des données de mesures sur un point. Utilisez la méthode `commande_acces_donnees_mesures(demande)` en passant un objet de type `DemandeAccesDonneesMesures` en argument.

9. **`M023InformationsTechniquesEtContractuelles`**  
   Permet de demander les données techniques et contractuelles d'un ou plusieurs sites. Utilisez la méthode `m023(demande)` en passant un objet de type `DemandeInformationsTechniquesEtContractuelles` en argument.

10. **`M023HistoriqueMesuresFines`**  
   Permet de demander les données fines de consommation ou de production. Utilisez la méthode `m023(demande)` en passant un objet de type `DemandeHistoriqueMesuresFines` en argument.

11. **`M023MesuresFacturantes`**  
   Permet de demander les mesures facturantes des sites. Utilisez la méthode `m023(demande)` en passant un objet de type `DemandeHistoriqueDonneesFacturantes` en argument.

---

## Variables d'environnement

Pour fonctionner correctement, le projet nécessite que plusieurs variables d'environnement soient spécifiées :

- `WS_ENEDIS_LOGIN` : Identifiant auprès des webservices d'Enedis. **Ne jamais stocker ou afficher cette information en clair !**
- `WS_ENEDIS_CONTRAT_ID` : Identifiant du contrat entre le Client et Enedis, utilisé pour identifier l'entreprise sur certains webservices. **Ne pas stocker ou afficher cette information en clair !**
- `WS_ENEDIS_URL` : Partie commune de l'URL d'appel aux webservices d'Enedis.
- `PROXY_DB_NAME` : Nom de la base de données utilisée par Django.
- `PROXY_DB_USER` : Nom d'utilisateur pour la base de données. **Ne pas stocker ou afficher cette information en clair !**
- `PROXY_DB_PASSWORD` : Mot de passe pour la base de données. **Ne pas stocker ou afficher cette information en clair !**
- `PROXY_DB_PORT` : Port de communication avec la base de données.
- `PROXY_DB_HOST` : Hôte (nom de domaine) de la base de données.
- `ENVIRONNEMENT_EXECUTION` : Doit contenir soit `dev` pour l'environnement de développement, soit `prod` pour le déploiement en production. Sert à gérer l'activation de Gunicorn.
- `DJANGO_SECRET` : Clé secrète Django. **Ne pas stocker ou afficher cette information en clair !**
- `PYTHONUNBUFFERED` : Doit contenir `"1"` si vous êtes en développement.
- `DJANGO_SETTINGS_MODULE` : Spécifie le module de configuration de Django.
- `DEBUG` : Doit absolument être renseigné à `False` en environnement de production.
- `HOMOLOGATION`: Indiquant si le système est déployé pour l'homologation Enedis (ne rien mettre si c'est la prod)

#### Production only
- `KEY_PRIVATE_CLIENT_CERTIFICATE` : Variable d'env contenant la clé privée du certificat Client 
- `BUCKET_NAME` : Nom du bucket S3 dans lequel est placée la clé publique du client (.crt)
- `KEY_PUBLIC_CLIENT_CERTIFICATE` : Clé S3 du certificat public présent sur S3 (exemple : test/certificat.crt)

---

## Connexion avec Imposter

[Imposter](https://github.com/gatehillsoftware/Imposter) est un outil de simulation qui permet de reproduire le comportement des webservices d'Enedis. Il est utilisé dans ce projet pour disposer d'un environnement de test accessible rapidement et en local.

Pour qu'Imposter simule un service, il faut lui fournir les fichiers `.xsd` et `.wsdl` qui définissent la structure des messages attendus par le service, ainsi qu'un fichier de configuration se terminant par `-config.yaml`.

**Important** : Les fichiers `.wsdl` doivent avoir leur champ `targetNamespace` modifié pour commencer par `http://imposter:8080/`.

Exemple de fichier de configuration :

```yaml
plugin: soap
wsdlFile: RecherchePoint-v2.0.wsdl

resources:
  - binding: RecherchePointBinding
    operation: rechercherPoint
    response:
      content: |
        <!-- Votre réponse SOAP ici -->
```
---
## const.py

Le fichier `const.py` contient l'ensemble des `enum` et des constantes du système.

---
## Certificats Enedis
### Développement
Les certificats doivent être placés dans le dossier :
- `./ressources/certificats/client_public.crt` pour le certificat public
- `./ressources/certificats/server.key` pour le certificat privé
### Production
Le certificat public doit être situé dans le bucket paramètrable via la variable `BUCKET_NAME` et dont la clé est `KEY_PUBLIC_CLIENT_CERTIFICATE`
Le certificat privé doit être injecté via une variable d'env dénommée `KEY_PRIVATE_CLIENT_CERTIFICATE`
