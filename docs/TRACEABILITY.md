# Matrice de Traçabilité Exigences ↔ Tests ↔ Résultats (ISO/IEC 25010)

Ce document assure la traçabilité bidirectionnelle complète entre les exigences fonctionnelles minimales du cahier des charges, les règles métier, les huit caractéristiques de la norme ISO/IEC 25010, les outils de validation et les résultats effectivement constatés.

---

## 1. Traçabilité des Exigences Fonctionnelles (EF)

| ID | Exigence Fonctionnelle | Implémentation dans le Code | Couche de Test | Outil Utilisé | Résultat Obtenu | Statut |
|---|---|---|---|---|---|---|
| **EF-01** | **Authentification & Gestion des Rôles** (Admin, Sales, Viewer avec droits différenciés) | `backend/app/main.py` (`/api/token`, dépendances `require()`), `frontend/src/main.ts` | Tests Unitaires & API | Pytest, Newman (Requêtes 02, 14, 15) | Connexion JWT réussie, rejet des accès non autorisés (HTTP 403), masquage UI pour Viewer. | **Conforme** |
| **EF-02** | **CRUD Complet sur 4 Entités Métier** (Customer, Product, Order, OrderItem) | Modèles SQLAlchemy et routes CRUD dans `main.py`, composants UI étendus dans `main.ts` | Tests API & E2E | Pytest (`test_customer_product_order_item_crud`), Newman (Req. 03 à 08), Playwright | Création, lecture, mise à jour et suppression validées sur toutes les entités, y compris les lignes de commande. | **Conforme** |
| **EF-03** | **Workflow à Statuts** (`draft → validated → closed`) | `PATCH /api/orders/{id}/status`, transitions contrôlées dans `main.py` et boutons UI | Tests API & E2E | Pytest (`test_stock_and_status_rules`), Newman (Req. 09, 10, 11), Playwright | Saut d'état rejeté (409), validation conditionnée au stock, clôture définitive enregistrée. | **Conforme** |
| **EF-04** | **Tableau de Bord** (indicateurs agrégés, filtres de statut) | `GET /api/dashboard`, agrégations SQL (`func.count`, `func.sum`), composant Dashboard | Tests API & E2E | Newman (Requête 12), Playwright | Retourne nombre de clients, produits, commandes, CA clôturé, et filtre par statut opérationnel. | **Conforme** |
| **EF-05** | **Recherche et Filtrage** sur entité à fort volume (Clients et Produits) | `GET /api/customers?q=...`, `GET /api/products?q=...`, clause `ilike`, limite à 100 | Tests API & E2E | Newman (Requête 04), Playwright | Recherche textuelle insensible à la casse opérationnelle et bornée à 100 résultats. | **Conforme** |
| **EF-06** | **Journal d'Audit** des actions sensibles (qui, quoi, quand, entité) | Table `Audit`, fonction utilitaire `audit()`, endpoint `GET /api/audit` | Tests API & Sécurité | Pytest (`test_customer_uniqueness_and_audit`), Newman (Req. 13, 15) | Enregistrement systématique des créations/modifications/transitions. Accès strictement réservé à l'Admin (403 pour Viewer/Sales). | **Conforme** |

---

## 2. Traçabilité des Règles Métier Explicites (RM)

| ID | Règle Métier | Justification & Emplacement | Test Associé | Résultat Obtenu | Statut |
|---|---|---|---|---|---|
| **RM-01** | **Unicité de l'adresse email client** | Contrainte SQL `unique=True` sur `Customer.email`, gestion du conflit HTTP 409 | Pytest (`test_customer_uniqueness_and_audit`), Newman Req. 03 | La tentative de création d'un doublon est rejetée avec un code HTTP 409 Conflict. | **Conforme** |
| **RM-02** | **Unicité du code SKU produit** | Contrainte SQL `unique=True` sur `Product.sku`, gestion du conflit HTTP 409 | Pytest (`test_customer_product_order_item_crud`), Newman Req. 06 | Rejet immédiat de tout produit portant un SKU déjà existant en base. | **Conforme** |
| **RM-03** | **Positivité des prix et des quantités** | Schémas Pydantic `ProductIn` (`price > 0`, `stock >= 0`) et `ItemIn` (`quantity > 0`) | Validation Pydantic & Pytest | Rejet HTTP 422 Unprocessable Entity en cas de valeur négative ou nulle. | **Conforme** |
| **RM-04** | **Cohérence du stock disponible** | Contrôle de la disponibilité lors de la création d'ordre et de la validation | Pytest (`test_stock_and_status_rules`), Newman Req. 07 | Rejet HTTP 409 si la quantité demandée excède le stock magasin. | **Conforme** |
| **RM-05** | **Décrémentation du stock à la validation** | Le stock produit n'est diminué que lors de la transition `draft → validated`, pas lors de la création du brouillon | Pytest (`test_stock_and_status_rules`), Newman Req. 10 | Vérification que le stock reste intact au stade draft et diminue exactement de la quantité commandée à la validation. | **Conforme** |
| **RM-06** | **Invariance et respect du workflow d'état** | Transitions permises : `draft → validated` puis `validated → closed`. Tout saut ou retour en arrière est interdit | Pytest (`test_stock_and_status_rules`), Newman Req. 09 | Le passage direct de `draft` à `closed` déclenche un code HTTP 409 Conflict. | **Conforme** |
| **RM-07** | **Protection contre la suppression d'entités liées** | Un client ayant des commandes ou un produit figurant dans une commande ne peut pas être supprimé | Pytest (`test_stock_and_status_rules`), API routes DELETE | Suppression refusée avec HTTP 409 ("Customer has orders" / "Product is in an order"). | **Conforme** |
| **RM-08** | **Traçabilité des opérations sensibles** | Toute création, modification, suppression ou transition d'état enregistre l'acteur, l'action, l'entité et l'horodatage | Pytest (`test_customer_uniqueness_and_audit`), Newman Req. 13 | Audit vérifié en base après chaque action sensible. | **Conforme** |

---

## 3. Traçabilité des 8 Caractéristiques Qualité ISO/IEC 25010

| # | Caractéristique ISO | Exigence Pédagogique | Outil de Test | Commande Exécutée | Résultat Mesuré | Preuve Documentée | Statut ISO |
|---|---|---|---|---|---|---|---|
| **6.1** | **Aptitude fonctionnelle** | 100% des exigences fonctionnelles minimales implémentées et validées | Pytest, Newman, Playwright | `pytest`, `newman run`, `playwright test` | 4 tests Pytest passés, 16 requêtes Newman réussies (17 assertions), scénarios E2E validés. | Captures Pages 3, 5, 6, 8 | **Conforme** |
| **6.2** | **Efficacité de performance** | Temps de réponse mesuré sous charge (cible : p95 < 500 ms à 20 utilisateurs simultanés) | Locust 2.32.10 | `locust --users 20 --spawn-rate 5 --headless` | 20 utilisateurs, 0 erreur. Endpoints métier : dashboard p95 300 ms, produit p95 200 ms. Endpoint token p95 1 300 ms (Bcrypt). Aggregate p95 1 100 ms. | Capture Page 10 du document de preuves | **Partiellement Conforme** |
| **6.3** | **Compatibilité** | Fonctionnement multi-navigateurs (au moins 2 navigateurs) et contrat API standard | Newman (API standard), Playwright (Chromium, Firefox) | `playwright test --project=chromium --project=firefox` | Scénario lecteur passé sur Chromium, scénario commercial corrigé. Configuration Firefox définie. | Configuration et suites de tests | **Partiellement Conforme** |
| **6.4** | **Facilité d'utilisation** | Parcours utilisateurs complets, ergonomie, formulaires réactifs, accessibilité de base | Playwright E2E, Recette visuelle | `capture-screenshots.cjs` | Parcours commercial et lecteur automatisés ; feedback utilisateur visible via messages de statut. | Captures d'écran 01 à 05 | **Conforme** |
| **6.5** | **Fiabilité** | Robustesse aux erreurs, intégrité transactionnelle, aucune corruption de données en cas d'échec | Tests unitaires de rollback, SQLite transactions | `pytest tests/test_rules.py` | Rollback automatique vérifié lors d'échecs de contraintes ou de stock insuffisant. | Suites Pytest | **Conforme** |
| **6.6** | **Sécurité** | Authentification JWT robuste, RBAC strict, absence de vulnérabilités connues (OWASP Top 10) | Bandit (SAST), pip-audit (SCA), OWASP ZAP (DAST) | `bandit -r app`, `pip-audit` | Bandit : 0 problème sur 532 LOC. pip-audit : 43 avis répertoriés sur dépendances tierces. DAST documenté. | Captures Pages 2, 7 & logs pip-audit | **Partiellement Conforme** |
| **6.7** | **Maintenabilité** | Architecture en couches, code structuré, couverture de tests mesurée ≥ 70% | Ruff (Linter), Coverage.py | `ruff check app tests`, `coverage report -m` | Ruff : 100% checks passed. Couverture totale : 90% (largement supérieure au seuil exigé de 70%). | Captures Pages 8 & 9 | **Conforme** |
| **6.8** | **Portabilité** | Déploiement reproductible sur une autre machine via conteneurisation | Docker, Docker Compose | `docker compose up -d --build` | Images backend et frontend construites sans erreur, conteneurs fonctionnels, endpoints HTTP 200. | Logs Docker Page 1 | **Conforme** |
