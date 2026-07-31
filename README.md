# OSC Shop

OSC Shop est une application web de démonstration pour OpenSecureCloud.

## Ce qui a été fait

- structure Flask propre avec blueprints, services, modèles et formulaires
- catalogue produits, recherche, panier, commandes fictives et avis
- inscription, connexion, déconnexion et profil utilisateur
- tableau de bord administrateur
- API REST simple
- base de données SQLite avec données de test automatiques
- logs structurés pour faciliter l’analyse avec Wazuh
- mode démo prévu via `demo_config.py` pour activer des scénarios de sécurité plus tard

## Démarrer l’application

### En local

```bash
copy .env.example .env
pip install -r requirements.txt
python run.py
```

L’application sera accessible sur `http://127.0.0.1:5000`.

### Avec Docker

```bash
docker compose up --build
```

## Comptes de démonstration

- `admin / Admin123!`
- `user1` à `user5` / `User123!`

## Mode démo

Les scénarios vulnérables ne sont pas actifs par défaut.  
Ils pourront être activés uniquement dans un environnement de laboratoire via `demo_config.py`.
