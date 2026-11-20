# StockFlow — Application Métier Conforme ISO/IEC 25010

Application web de gestion commerciale et d'inventaire développée dans le cadre du projet étudiant d'ingénierie logicielle et qualité logicielle (**ISO/IEC 25010**).

Le système gère l'intégralité du cycle commercial (clients, produits, commandes, lignes de commande), applique un contrôle d'accès basé sur les rôles (**RBAC** avec JWT), un workflow à statuts strict (`draft → validated → closed`), des règles métier d'intégrité de stock, un tableau de bord d'indicateurs agrégés et un journal d'audit réservé à l'administrateur.

---

## 1. Stack Technologique et Architecture

- **Frontend :** Angular 19.2 (Standalone components, Signals, formulaires réactifs).
- **Backend :** Python 3.12, FastAPI 0.115.12, Pydantic 2.10.6, SQLAlchemy 2.0.38.
- **Base de Données :** SQLite (embarqué, transactions ACID avec intégrité relationnelle).
- **Authentification :** JWT Bearer Tokens (expiration 2h), hachage Bcrypt.
- **Conteneurisation :** Docker et Docker Compose.

---

## 2. Démarrage Rapide

### Option A : Déploiement Conteneurisé (Recommandé)

Assurez-vous que Docker Desktop est lancé, puis exécutez à la racine du dépôt :

```powershell
docker compose up -d --build
```

- **Interface Frontend :** `http://localhost:4200`
- **Documentation API Interactive (Swagger) :** `http://localhost:8000/docs`

### Option B : Lancement en Développement Local

**1. Backend :**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**2. Frontend :**
```powershell
cd frontend
npm install
npm start
```

---

## 3. Comptes de Démonstration

L'application est initialisée avec 3 comptes prédéfinis aux droits différenciés :

| Rôle | Nom d'utilisateur | Mot de passe | Droits Principaux |
|---|---|---|---|
| **Administrateur** | `admin` | `Admin123!` | CRUD complet sur toutes les entités, transitions de statut, accès exclusif au journal d'audit. |
| **Commercial** | `sales` | `Sales123!` | Création/mise à jour clients, produits, commandes, lignes de commande et transitions. Suppression restreinte aux brouillons. Accès audit interdit. |
| **Lecteur** | `viewer` | `View123!` | Consultation en lecture seule (dashboard, clients, produits, commandes). Toute écriture ou transition refusée (HTTP 403). |

---

## 4. Exécution des 12 Couches de Test et Qualité

| Couche de Test | Commande à Exécuter | Outil & Objectif |
|---|---|---|
| **1. Tests Unitaires & Métier** | `cd backend; pytest -v tests/test_rules.py` | Pytest 8.3.5 — Validation des règles métier isolées. |
| **2. Couverture de Code** | `cd backend; coverage run -m pytest tests/test_rules.py && coverage report -m` | Coverage.py — Mesure de la couverture (résultat mesuré : 90%). |
| **3. Tests API Contractuels** | `npx newman run postman/StockFlow.postman_collection.json --env-var baseUrl=http://localhost:8000/api` | Newman / Postman — 16 requêtes, 17 assertions validées. |
| **4. Tests Fonctionnels E2E** | `cd frontend; npm run e2e` | Playwright — Parcours utilisateur réels multi-navigateurs. |
| **5. Tests de Performance** | `cd backend; locust -f tests/locustfile.py --host http://localhost:8000 --users 20 --spawn-rate 5 --run-time 30s --headless` | Locust — Mesure des temps de réponse sous charge de 20 utilisateurs. |
| **6. Tests de Fiabilité** | `cd backend; pytest -v -k "rules or crud"` | Pytest — Vérification du rollback en cas de stock insuffisant et rejet des sauts de statut. |
| **7. Analyse SAST (Sécurité)** | `cd backend; bandit -r app` | Bandit — Détection statique des vulnérabilités (0 faille détectée). |
| **8. Analyse SCA (Dépendances)** | `cd backend; pip-audit` | pip-audit — Détection des CVE connues sur les bibliothèques utilisées. |
| **9. Analyse DAST (Dynamique)** | `docker run -t --rm zaproxy/zap-stable zap-baseline.py -t http://host.docker.internal:8000/docs -r zap_report.html` | OWASP ZAP — Scan dynamique de sécurité applicative. |
| **10. Qualité & Formatage** | `cd backend; ruff check app tests` | Ruff — Respect des standards PEP8 et complexité. |
| **11. Compatibilité Navigateurs** | `cd frontend; npx playwright test --project=chromium --project=firefox` | Playwright — Validation sur Chromium et Firefox. |
| **12. Portabilité & Déploiement** | `docker compose config && docker compose build` | Docker Compose — Reproductibilité de l'installation. |

---

## 5. Génération Automatique des Captures et Rapports

- **Génération des captures d'écran :**
  ```powershell
  node frontend/capture-screenshots.cjs
  ```
- **Documentation et Rapports associés :**
  - [Architecture et Conception](docs/ARCHITECTURE.md)
  - [Résultats d'Exécution Réels](docs/EXECUTION_RESULTS.md)
  - [Matrice de Traçabilité ISO 25010](docs/TRACEABILITY.md)
  - [Audit Initial du Projet](docs/INITIAL_AUDIT.md)
  - [Inventaire des Preuves Visuelles](docs/SCREENSHOT_INVENTORY.md)
  - [Guide de Reproduction des Captures](docs/SCREENSHOT_REPRODUCTION_GUIDE.md)
  - `Rapport_Projet_ISO25010_StockFlow_FINAL.docx` (Rapport académique complet)
  - `Rapport_Captures_et_Preuvres_StockFlow.docx` (Dossier séparé de preuves visuelles)
