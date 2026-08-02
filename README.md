# OSC Shop

OSC Shop est une application web de démonstration pour OpenSecureCloud.
Elle sert de support pour tester une chaîne de sécurité composée de Nginx, OAuth2 Proxy, Keycloak, HAProxy, Coraza WAF, Wazuh et Falco.

## Ce qui a été fait

### Architecture
- structure Flask propre avec `blueprints`, `services`, `models`, `forms`, `utils`, `templates` et `static`
- séparation claire entre frontend et backend
- base compatible SQLite par défaut et PostgreSQL plus tard
- configuration centralisée avec `config.py`, `extensions.py` et `demo_config.py`

### Fonctionnalités déjà en place
- page d’accueil
- catalogue produits
- recherche produits
- page détail produit
- inscription, connexion, déconnexion
- profil utilisateur et modification du profil
- panier
- ajout et suppression d’articles du panier
- commande fictive
- historique des commandes
- page contact
- avis produits
- tableau de bord administrateur
- gestion des produits par l’admin
- vue des utilisateurs, commandes et avis
- API REST de base

### Sécurité et observabilité
- authentification locale avec abstraction prévue pour un futur passage à OAuth2 Proxy + Keycloak
- logs structurés avec adresse IP, User-Agent et timestamp
- base saine par défaut, sans vulnérabilité activée
- scénarios de démonstration désactivés par défaut via `demo_config.py`
- préparation de cas de test pour SQLi, XSS, IDOR, brute force, upload, headers faibles, cookies non sécurisés, rate limiting et erreurs debug

### Données de test
- 1 administrateur
- 5 utilisateurs
- 20 produits
- 10 commandes fictives

## Comment démarrer l’application

### 1) En local

```bash
copy .env.example .env
pip install -r requirements.txt
python run.py
```

Puis ouvrir :

```text
http://127.0.0.1:5000
```

### 2) Avec Docker

```bash
docker compose up --build
```

## Documentation de déploiement

Le guide complet de déploiement se trouve dans `docs/DEPLOYMENT.md`.

## Commandes de vérification

### Vérifier la syntaxe Python

```bash
python -m compileall .
```

### Vérifier le démarrage de l’application

```bash
python run.py
```

### Vérifier les routes principales

```bash
python -c "from app import create_app; app = create_app('testing'); print(len(list(app.url_map.iter_rules())))"
```

### Vérifier rapidement les pages et l’API

```bash
@'
from app import create_app
app = create_app('testing')
client = app.test_client()
for path in ['/', '/products/', '/api/products', '/auth/login']:
    resp = client.get(path)
    print(path, resp.status_code)
'@ | python -
```

### Vérifier la connexion API

```bash
@'
from app import create_app
app = create_app('testing')
client = app.test_client()
resp = client.post('/api/login', json={'username': 'admin', 'password': 'Admin123!'})
print(resp.status_code, resp.json)
'@ | python -
```

## Comptes de démonstration

- `admin / Admin123!`
- `user1` à `user5` / `User123!`

## Mode démo

Les scénarios vulnérables ne sont pas actifs par défaut.
Ils doivent rester désactivés en production et ne servir que dans un environnement de laboratoire via `demo_config.py`.

## Arborescence principale

- `app/` : création de l’application Flask
- `routes/` : blueprints des pages et de l’API
- `models/` : modèles SQLAlchemy
- `services/` : logique métier
- `forms/` : formulaires Flask-WTF
- `templates/` : interface Bootstrap
- `static/` : CSS et JavaScript
- `utils/` : helpers techniques
