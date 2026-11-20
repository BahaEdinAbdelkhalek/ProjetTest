# Guide de Reproduction des Captures et Preuves StockFlow

Ce guide fournit des instructions pas à pas permettant à tout évaluateur, enseignant ou étudiant de reproduire fidèlement l'intégralité des captures d'écran et rapports de test requis pour le projet StockFlow (ISO/IEC 25010).

---

## 1. Prérequis d'Environnement

Avant de procéder aux captures, assurez-vous d'avoir lancé l'application :

```powershell
# Option 1 : Via Docker Compose (recommandé en production/évaluation)
docker compose up -d --build

# Option 2 : Lancement local sans Docker
# Backend :
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend :
cd frontend
npm install
npm start
```

- **URL de l'application :** `http://localhost:4200`
- **URL de l'API / Documentation interactive :** `http://localhost:8000/docs`
- **Comptes de démonstration configurés :**
  - **Administrateur :** `admin` / `Admin123!` (Rôle : `admin`)
  - **Commercial :** `sales` / `Sales123!` (Rôle : `sales`)
  - **Lecteur :** `viewer` / `View123!` (Rôle : `viewer`)

---

## 2. Captures d'Interface Applicative (UI)

### Capture 01 : Tableau de bord commercial
- **Fichier cible :** `docs/screenshots/01-dashboard-sales.png`
- **Objectif :** Démontrer l'affichage des KPIs agrégés (clients, produits, commandes, chiffre d'affaires clôturé) et le filtre de statut.
- **Compte :** `sales` / `Sales123!`
- **Actions :**
  1. Accéder à `http://localhost:4200`.
  2. Saisir `sales` et `Sales123!`, puis cliquer sur **Sign in**.
  3. Vérifier la présence du message `Signed in as sales (sales)`.
  4. Sélectionner `All statuses` ou `Draft` dans la liste déroulante du filtre de statut.
  5. Capturer l'écran complet ou la zone principale avec les 4 cartes de KPIs.
- **Résultat attendu :** Les 4 indicateurs affichent des valeurs numériques positives, le filtre est positionné, le rôle `sales` est visible dans le bandeau supérieur.

---

### Capture 02 : Gestion et recherche des produits
- **Fichier cible :** `docs/screenshots/02-products.png`
- **Objectif :** Valider le formulaire de création de produit, la saisie des prix/stocks et le tableau avec recherche indexée.
- **Compte :** `sales` / `Sales123!`
- **Actions :**
  1. Cliquer sur le bouton de navigation **Products**.
  2. Dans le formulaire, renseigner :
     - Name : `Widget Démonstration`
     - SKU : `WD-DEMO-01`
     - Price : `19.99`
     - Stock : `50`
  3. Cliquer sur **Add product**.
  4. Saisir `Widget` dans le champ **Search**.
  5. Prendre la capture d'écran montrant le produit créé dans le tableau.
- **Résultat attendu :** Message `Product saved` affiché, produit visible avec son SKU, son prix formaté en devise et son stock initial.

---

### Capture 03 : Gestion et recherche des clients
- **Fichier cible :** `docs/screenshots/03-customers.png`
- **Objectif :** Démontrer la création d'un client et la vérification de l'unicité de son adresse email.
- **Compte :** `sales` / `Sales123!`
- **Actions :**
  1. Cliquer sur le bouton de navigation **Customers**.
  2. Renseigner le formulaire :
     - Name : `Entreprise Dupont SAS`
     - Email : `contact@dupont-sas.fr`
  3. Cliquer sur **Add customer**.
  4. Filtrer la recherche sur `Dupont`.
  5. Capturer l'écran.
- **Résultat attendu :** Message `Customer saved`, le client apparaît dans la table avec son identifiant, son nom et son email.

---

### Capture 04 : Commandes, lignes et workflow à statuts
- **Fichier cible :** `docs/screenshots/04-orders.png`
- **Objectif :** Prouver la création d'une commande brouillon, la visualisation de ses lignes et la transition vers l'état validé puis clôturé.
- **Compte :** `sales` / `Sales123!`
- **Actions :**
  1. Cliquer sur le bouton de navigation **Orders**.
  2. Dans le menu déroulant **Customer**, sélectionner `Entreprise Dupont SAS`.
  3. Dans le menu déroulant **Product**, sélectionner `Widget Démonstration (stock 50)`.
  4. Saisir la quantité : `5`.
  5. Cliquer sur **Create draft order**.
  6. Constater l'apparition de la ligne avec le statut `draft` et le bouton **Validate**.
  7. Cliquer sur **View items** pour afficher les lignes d'articles associées.
  8. Cliquer sur **Validate** : le statut passe à `validated`, le bouton devient **Close**, et le stock produit diminue de 5 unités.
  9. Prendre la capture montrant l'état `validated` ou `closed` avec les lignes déroulées.
- **Résultat attendu :** Statut reflété fidèlement, transition interdite sautée impossible, décrémentation du stock vérifiée.

---

### Capture 05 : Journal d'audit réservé à l'administrateur
- **Fichier cible :** `docs/screenshots/05-audit-admin.png`
- **Objectif :** Valider la traçabilité des opérations sensibles (acteur, action, entité, date) et l'exclusivité du rôle admin.
- **Compte :** `admin` / `Admin123!`
- **Actions :**
  1. Dans le bandeau supérieur, saisir `admin` et `Admin123!`, puis cliquer sur **Sign in**.
  2. Constater l'apparition du bouton **Audit** dans la barre de navigation.
  3. Cliquer sur **Audit**.
  4. Capturer le tableau d'audit listant les créations, mises à jour et transitions récentes.
- **Résultat attendu :** Tableau avec colonnes `When`, `Actor` (`admin`, `sales`), `Action` (`create`, `update`, `transition`), `Entity`.

---

## 3. Captures des Résultats de Tests Automatisés

### Capture 06 : Exécution des tests API Newman / Postman
- **Fichier cible :** `docs/screenshots/06-newman-api.png`
- **Commande à exécuter :**
  ```powershell
  npx newman run postman/StockFlow.postman_collection.json --env-var baseUrl=http://localhost:8000/api
  ```
- **Résultat attendu :** 16 requêtes exécutées, 17 assertions réussies, 0 échec. Durée environ 2 secondes.

---

### Capture 07 : Exécution des tests unitaires et intégration Pytest avec couverture
- **Fichier cible :** `docs/screenshots/07-pytest-coverage.png`
- **Commande à exécuter :**
  ```powershell
  cd backend
  coverage run -m pytest tests/test_rules.py -v
  coverage report -m
  ```
- **Résultat attendu :** 4 tests passés (`test_health_and_auth_roles`, `test_customer_uniqueness_and_audit`, `test_stock_and_status_rules`, `test_customer_product_order_item_crud_and_dashboard_filter`), couverture globale de 90%.

---

### Capture 08 : Analyse de sécurité statique Bandit (SAST)
- **Fichier cible :** `docs/screenshots/08-bandit-sast.png`
- **Commande à exécuter :**
  ```powershell
  cd backend
  bandit -r app
  ```
- **Résultat attendu :** `No issues identified`, 0 High, 0 Medium, 0 Low.

---

### Capture 09 : Analyse des dépendances pip-audit (SCA)
- **Fichier cible :** `docs/screenshots/09-pip-audit-sca.png`
- **Commande à exécuter :**
  ```powershell
  cd backend
  pip-audit
  ```
- **Résultat attendu :** Rapport d'audit listant les dépendances scannées et signalant les avis de sécurité connus pour `pyasn1`, `starlette` et `python-multipart`.

---

### Capture 10 : Analyse dynamique de sécurité OWASP ZAP (DAST)
- **Fichier cible :** `docs/screenshots/10-owasp-zap-dast.png`
- **Commande à exécuter :**
  ```powershell
  docker run -t --rm zaproxy/zap-stable zap-baseline.py -t http://host.docker.internal:8000/docs -r zap_report.html
  ```
- **Résultat attendu :** Rapport HTML identifiant les en-têtes de sécurité manquants (ex. CSP, X-Content-Type-Options) et absence d'injection critique.

---

### Capture 11 : Tests de charge Locust (Performance)
- **Fichier cible :** `docs/screenshots/11-locust-performance.png`
- **Commande à exécuter :**
  ```powershell
  cd backend
  locust -f tests/locustfile.py --host http://localhost:8000 --users 20 --spawn-rate 5 --run-time 30s --headless
  ```
- **Résultat attendu :** 20 utilisateurs simultanés, 0 requête échouée, tableau récapitulatif par endpoint distinguant le coût d'authentification (`/api/token`) des requêtes métier (`/api/dashboard` et `/api/products`).

---

### Capture 12 : Tests E2E Playwright Multi-Navigateurs (Chromium & Firefox)
- **Fichier cible :** `docs/screenshots/12-playwright-e2e.png`
- **Commande à exécuter :**
  ```powershell
  cd frontend
  npm run e2e
  ```
- **Résultat attendu :** Scénarios `sales user completes product, customer and order workflow` et `viewer cannot create records and audit tab is hidden` exécutés avec succès.

---

## 4. Script Automatique de Génération des Captures UI

Pour générer automatiquement les 5 captures d'interface en une seule commande :

```powershell
node frontend/capture-screenshots.cjs
```
Les captures seront enregistrées directement dans le dossier `docs/screenshots/`.
