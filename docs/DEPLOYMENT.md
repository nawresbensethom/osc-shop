# OSC Shop — Guide de déploiement

Ce document décrit un déploiement type d’OSC Shop derrière une chaîne de sécurité composée de :

- `HAProxy`
- `Nginx`
- `OAuth2 Proxy`
- `Keycloak`
- `Coraza WAF` avec `OWASP CRS`
- `Wazuh`
- `Falco`

L’objectif est de fournir une base claire pour les démonstrations de cybersécurité, sans activer de vulnérabilités par défaut.

## 1. Architecture cible

Schéma recommandé :

`Internet -> HAProxy -> Nginx -> OAuth2 Proxy -> OSC Shop`

Selon ton environnement, `Coraza WAF` peut être placé :

- dans `Nginx` via intégration WAF compatible,
- ou sur une couche intermédiaire dédiée avant l’application.

`Wazuh` récupère les journaux applicatifs et les logs des proxies.
`Falco` surveille les conteneurs, les accès fichiers et les comportements anormaux.

## 2. Prérequis

- Docker et Docker Compose
- Python 3.12 si lancement local
- un serveur `Keycloak`
- une instance `Wazuh` déjà opérationnelle
- un environnement de test isolé

## 3. Variables d’environnement

Créer un fichier `.env` à partir de `.env.example` :

```bash
copy .env.example .env
```

Variables importantes :

- `SECRET_KEY`
- `DATABASE_URL`
- `AUTH_MODE`
- `APP_NAME`
- `ENABLE_SQLI`
- `ENABLE_XSS`
- `ENABLE_IDOR`
- `ENABLE_UPLOAD`
- `ENABLE_BRUTE_FORCE`
- `ENABLE_DEBUG_ERRORS`
- `ENABLE_ENUMERATION`
- `ENABLE_RATE_LIMITING`
- `ENABLE_CSRF`
- `ENABLE_INSECURE_COOKIES`
- `ENABLE_WEAK_HEADERS`

## 4. Déploiement de l’application

### Lancement local

```bash
pip install -r requirements.txt
python run.py
```

### Lancement Docker

```bash
docker compose up --build
```

Le service web écoute sur le port `5000` dans le `docker-compose.yml`.

## 5. Configuration Nginx

Exemple de reverse proxy :

```nginx
server {
    listen 80;
    server_name osc-shop.example.local;

    location / {
        proxy_pass http://haproxy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Bonnes pratiques :

- activer TLS en production
- bloquer les en-têtes inutiles
- journaliser les accès
- faire remonter `X-Forwarded-*` vers l’application

## 6. Configuration HAProxy

Exemple simplifié :

```haproxy
frontend http_in
    bind *:80
    default_backend nginx_back

backend nginx_back
    server nginx nginx:80 check
```

Pour une démo sécurité, HAProxy peut aussi :

- répartir la charge,
- simuler une première couche de protection,
- imposer des règles de base de rate limiting.

## 7. Intégration Keycloak + OAuth2 Proxy

OSC Shop supporte deux modes :

- `AUTH_MODE=local` : authentification locale pour les tests
- `AUTH_MODE=proxy` : identité fournie par un proxy d’authentification

### Flux recommandé

1. L’utilisateur s’authentifie via `Keycloak`
2. `OAuth2 Proxy` valide la session
3. `OAuth2 Proxy` transmet l’identité à OSC Shop via en-têtes HTTP
4. OSC Shop lit ces en-têtes sans recompiler l’application

### En-têtes attendus

- `X-Forwarded-User`
- `X-Forwarded-Email`
- `X-Forwarded-Name`
- `X-Forwarded-Role`

### Exemple de principe

```bash
AUTH_MODE=proxy
```

## 8. Coraza WAF / OWASP CRS

Le but est d’observer comment le WAF réagit aux scénarios contrôlés.

Conseils :

- garder les vulnérabilités désactivées par défaut
- activer un seul scénario de démo à la fois
- corréler les logs WAF avec les logs applicatifs
- tester SQLi, XSS, traversal, IDOR et brute force dans un environnement isolé

Exemples de signaux à surveiller :

- requêtes bloquées
- motifs CRS déclenchés
- règles répétées sur la même IP
- erreurs 403 / 406 / 429

## 9. Logs pour Wazuh

OSC Shop écrit des logs structurés dans `instance/logs/osc_shop.log`.

Événements utiles :

- connexion
- déconnexion
- échec de connexion
- inscription
- ajout au panier
- commande
- recherche
- suppression produit
- message contact
- erreur serveur
- exception

Recommandation :

- remonter les logs applicatifs
- remonter les logs Nginx et HAProxy
- normaliser les champs IP, user-agent, route et niveau de sévérité

## 10. Falco

Falco peut surveiller :

- accès anormal aux fichiers de configuration
- exécution de commandes inattendues dans les conteneurs
- accès aux répertoires `instance/` et `uploads/`
- comportements de type shell ou privilege escalation

Conseil :

- monter le répertoire `instance/` de façon explicite
- surveiller les événements sur le conteneur applicatif

## 11. Données de test

Au premier démarrage, l’application crée automatiquement :

- 1 administrateur
- 5 utilisateurs
- 20 produits
- 10 commandes

Comptes :

- `admin / Admin123!`
- `user1` à `user5` / `User123!`

## 12. Vérifications rapides

### Vérifier que Python compile

```bash
python -m compileall .
```

### Vérifier que l’application démarre

```bash
python run.py
```

### Vérifier les endpoints principaux

```bash
python -c "from app import create_app; app = create_app('testing'); print(len(list(app.url_map.iter_rules())))"
```

### Vérifier l’API

```bash
@'
from app import create_app
app = create_app('testing')
client = app.test_client()
print(client.get('/api/health').status_code)
print(client.get('/api/products').status_code)
print(client.post('/api/login', json={'username':'admin','password':'Admin123!'}).status_code)
'@ | python -
```

## 13. Mode démo

Les scénarios vulnérables restent désactivés par défaut dans `demo_config.py`.

À activer uniquement dans un laboratoire :

- `ENABLE_SQLI`
- `ENABLE_XSS`
- `ENABLE_IDOR`
- `ENABLE_UPLOAD`
- `ENABLE_BRUTE_FORCE`
- `ENABLE_DEBUG_ERRORS`
- `ENABLE_ENUMERATION`
- `ENABLE_RATE_LIMITING`
- `ENABLE_CSRF`
- `ENABLE_INSECURE_COOKIES`
- `ENABLE_WEAK_HEADERS`

## 14. Notes de sécurité

- ne jamais activer les flags de vulnérabilité en production
- garder `AUTH_MODE=local` ou `proxy` selon le scénario
- isoler le laboratoire réseau
- surveiller les journaux WAF, proxy et applicatifs ensemble

