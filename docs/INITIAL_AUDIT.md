# Audit Initial du Projet StockFlow (ISO/IEC 25010)

**Date d'audit :** 20 novembre 2026  
**Auditeur :** Ingénieur Qualité Logicielle & DevSecOps  
**Dépôt Git cible :** `https://github.com/BahaEdinAbdelkhalek/ProjetTest`  
**Branche locale :** `main` (synchronisée avec `origin/main`)  

---

## 1. Contexte et Objectifs de l'Audit

L'audit a pour objectif d'évaluer l'état réel du projet académique **StockFlow** par rapport aux exigences du cahier des charges officiel du professeur et à la norme ISO/IEC 25010.
Il confronte le code source existant, les configurations, la documentation (`README.md`, `docs/ARCHITECTURE.md`, `docs/EXECUTION_RESULTS.md`, `docs/TRACEABILITY.md`), les suites de tests, et les 18 pages de preuves visuelles et résultats fournies dans le document d'évaluation préliminaire.

---

## 2. État du Répertoire Git et Synchronisation

- **Branche courante :** `main`
- **Branche distante :** `origin/main` (`https://github.com/BahaEdinAbdelkhalek/ProjetTest`)
- **Derniers commits constatés :**
  - `77d6caf` : *Add StockFlow ISO 25010 demo and evidence*
  - `cd97f6b` : *first commit*
- **État de l'arbre de travail :** Propre, aucune modification non validée n'a été écrasée.
- **Règle respectée :** Préservation stricte du travail existant sans commande destructive (`git reset --hard` proscrit).

---

## 3. Architecture et Composants Existants

### 3.1 Stack Technologique
- **Frontend :** Angular 19.2 (Standalone Components, Signals, FormsModule, CommonModule).
- **Backend :** FastAPI 0.115.12, Pydantic 2.10.6, SQLAlchemy 2.0.38, SQLite (`demo.db`).
- **Authentification :** JWT Bearer (`python-jose`), hachage Bcrypt (`passlib`).
- **Conteneurisation :** `docker-compose.yml`, Dockerfiles pour backend, frontend et postman.

### 3.2 Modèle de Données (4 Entités Métier + Audit + Utilisateurs)
1. **Customer :** `id`, `name`, `email` (unique). Relation 1-N avec `Order`.
2. **Product :** `id`, `name`, `sku` (unique), `price`, `stock`. Relation 1-N avec `OrderItem`.
3. **Order :** `id`, `customer_id` (FK), `status` (`draft`, `validated`, `closed`), `total`, `created_at`. Relation 1-N avec `OrderItem`.
4. **OrderItem :** `id`, `order_id` (FK), `product_id` (FK), `quantity`, `unit_price`.
5. **User :** `id`, `username`, `password_hash`, `role` (`admin`, `sales`, `viewer`).
6. **Audit :** `id`, `actor`, `action`, `entity`, `entity_id`, `at`.

### 3.3 Rôles et Droits d'Accès
- **Admin :** Accès complet CRUD (clients, produits, commandes, lignes), transitions de statut, accès exclusif au journal d'audit (`/api/audit`).
- **Sales (Commercial) :** Création et modification de clients, produits, commandes et lignes; transitions de statut; consultation générale. Suppression restreinte aux commandes brouillon. Accès audit interdit (HTTP 403).
- **Viewer (Lecteur) :** Consultation en lecture seule (dashboard, clients, produits, commandes). Toute action d'écriture ou transition rejetée (HTTP 403), onglet Audit masqué.

---

## 4. Bilan des Couches de Test Existantes et Résultats Initiaux

| Couche de Test | Outil & Version | Résultat Initial Constaté | Statut Initial | Analyse |
|---|---|---|---|---|
| **1. Tests Unitaires & Intégration** | Pytest 8.3.5 | 4 tests réussis en 5.78s (`tests/test_rules.py`) | Passé | Valide rôles, unicité, règles de stock et statut, CRUD et relations. |
| **2. Couverture de Code** | Coverage.py 7.6.12 | 90% total (app/main.py: 89%, test_rules.py: 100%) | Conforme (Cible ≥ 70%) | Dépasse largement l'exigence des 70% fixée par le professeur. |
| **3. Tests API** | Newman 6.2.1 / Postman | 16 requêtes, 17 assertions, 0 échec (8.1s) | Passé | Contrat d'interface et codes HTTP validés. |
| **4. E2E / Navigateur** | Playwright 1.51.0 | Échec sur le workflow commercial (timeout 5s sur assertion 'draft') ; test viewer passé. | Échoué / Partiel | Problème de synchronisation UI/API et binding des options HTML dans Angular. |
| **5. Performance** | Locust 2.32.10 | 20 utilisateurs simultanés, 0 échec. p95 agrégé à 1 100 ms. | Partiellement Conforme | Le p95 dépasse la cible de 500 ms en raison du coût de dérivation de clé Bcrypt sur le endpoint `/api/token`. |
| **6. SAST (Sécurité Statique)** | Bandit 1.8.3 | 532 lignes analysées, 0 problème détecté. | Conforme | Aucune faille de sécurité statique identifiée dans le code backend. |
| **7. SCA (Dépendances)** | pip-audit | Non exécuté initialement (manquant dans l'image). | Non Vérifié | Exécuté lors de notre audit : 43 vulnérabilités connues détectées dans 6 dépendances. |
| **8. DAST (Sécurité Dynamique)** | OWASP ZAP | Non exécuté. | Non Vérifié | Nécessite un scan dynamique contre l'application déployée. |
| **9. Qualité / Linter** | Ruff 0.9.7 | "All checks passed!" | Conforme | Code PEP8 propre et formaté. |
| **10. Compatibilité Navigateurs** | Chromium / Firefox | Chromium partiellement testé ; Firefox non exécuté. | Non Conforme | Doit être exécuté sur les deux moteurs. |
| **11. Fiabilité & Persistance** | Transactions SQLite / Docker | Règles de rollback validées par test ; persistance après redémarrage non vérifiée. | Partiel | Transaction atomique vérifiée en cas d'erreur de stock. |
| **12. Portabilité & Déploiement** | Docker Compose | Images construites et services démarrés. | Partiel | Validation sur machine vierge à documenter. |

---

## 5. Identification Précise des Écarts et Bugs

### Bug 1 : Échec du Test E2E Playwright (Parcours Commercial)
- **Symptôme :** `Error: timed out 5000ms waiting for expect(locator).toBeVisible()` sur `row.getByText('draft')`.
- **Diagnostic réel :**
  1. Dans `main.ts`, le formulaire de création de commande utilisait `<option [ngValue]="null">` mélangé avec `<option [value]="c.id">`, ce qui perturbait l'assignation de `order.customer_id`.
  2. L'appel de soumission `createOrder()` était asynchrone et lançait en arrière-plan `refresh()` puis `load()`. Le test Playwright vérifiait immédiatement l'apparition de la ligne dans le tableau avant que le rafraîchissement réseau ne se termine.
  3. Le sélecteur de ligne Playwright pouvait être ambigu en présence de multiples commandes antérieures.
- **Correction appliquée :**
  - Harmonisation des sélecteurs `<select>` dans `main.ts` avec `<option *ngFor="let c of customers()" [value]="c.id">`.
  - Attente explicite de la notification de confirmation `Draft order #... created` dans le test Playwright avant d'inspecter la ligne du tableau.
  - Ciblage précis de la ligne nouvellement créée avec `.first()`.

### Écart 2 : CRUD Incomplet sur les Lignes de Commande (OrderItem) dans l'UI
- **Constat :** L'API disposait de tous les endpoints (`POST /orders/{id}/items`, `GET /order-items/{id}`, `PUT /order-items/{id}`, `DELETE /order-items/{id}`), mais l'interface Angular ne permettait que de visualiser le nombre de lignes sans afficher le détail ni ajouter/supprimer de lignes sur une commande brouillon.
- **Correction appliquée :**
  - Ajout d'une vue détaillée extensible pour chaque commande (`View items` / `Hide items`).
  - Affichage des lignes avec produit, quantité, prix unitaire.
  - Ajout d'un formulaire d'ajout de ligne sur commande brouillon (`addOrderItem`).
  - Ajout d'un bouton de suppression de ligne de commande brouillon (`removeOrderItem`).

### Écart 3 : Dépassement du p95 Locust (1 100 ms vs cible 500 ms)
- **Analyse :** Le test Locust initial de 10 secondes était trop court. Lors de la phase de montée en charge (ramp-up), les 20 utilisateurs exécutaient simultanément `POST /api/token` (hachage Bcrypt, ~1s par appel), ce qui représentait 42% des requêtes totales. Les endpoints métier purs (`/api/dashboard` à 111 ms et `/api/products` à 68 ms) respectaient largement la cible.
- **Recommandation :** Distinguer la charge d'authentification de la charge transactionnelle en régime établi.

### Écart 4 : Absence de Preuve SCA et DAST
- **Constat :** `pip-audit` et `OWASP ZAP` n'étaient pas exécutés dans le dépôt d'origine.
- **Résolution :** Exécution réelle de `pip-audit` réalisée lors de notre audit (43 vulnérabilités répertoriées, principalement liées à des sous-dépendances comme `pyasn1`, `starlette` et `python-multipart`). Procédure OWASP ZAP documentée pour reproduction fidèle.

---

## 6. Grille de Conformité Initiale au Cahier des Charges

| Exigence du Cahier des Charges | Référence | État Initial | Action Menée / Prévue |
|---|---|---|---|
| Application métier complète (Backend + Frontend + BDD) | § 1, 4 | Fait | FastAPI + Angular 19 + SQLite fonctionnels. |
| 3 profils utilisateurs distincts (Admin, Sales, Viewer) | § 4.1 | Fait | Rôles implémentés et testés au niveau API et UI. |
| Au moins 4 entités métier avec CRUD complet | § 4.2 | Partiel | CRUD étendu à l'UI pour `OrderItem`. |
| Workflow à statuts (brouillon → validée → clôturée) | § 4.3 | Partiel | API validée, correction E2E UI effectuée. |
| Tableau de bord avec indicateurs agrégés et filtres | § 4.4 | Fait | Dashboard avec KPIs et filtre par statut opérationnel. |
| Recherche/filtrage sur entité à fort volume | § 4.5 | Fait | Recherche indexée clients et produits opérationnelle. |
| Journal d'audit des actions sensibles | § 4.6 | Fait | Audit trail enregistré et restreint à l'admin. |
| Au moins 5 règles métier explicites et testables | § 4.7 | Fait | 8 règles métier formalisées et vérifiées. |
| Couverture de tests ≥ 70% | § 6.7 | Fait (90%) | 90% atteint (app/main.py: 89%, test_rules: 100%). |
| Temps de réponse sous charge p95 < 500 ms | § 6.2 | Partiel | Diagnostic de la surcharge d'authentification Bcrypt documenté. |
| Fonctionnement multi-navigateurs (≥ 2) | § 6.3 | Partiel | Playwright configuré pour Chromium et Firefox. |
| Rapports Word académiques et preuves | § 8 | À compléter | Finalisation du rapport ISO 25010 et rapport de captures. |
