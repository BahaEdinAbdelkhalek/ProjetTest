# Rapport des Résultats d'Exécution Réels des Tests StockFlow

**Dernière mise à jour :** 20 novembre 2026  
**Environnement d'exécution :** Windows 11 / WSL2 Ubuntu 24.04 LTS (Python 3.12.3, Node.js 24.16.0, Playwright 1.51.0, Newman 6.2.3, SQLite 3).  

Ce document consigne les résultats **réellement obtenus et mesurés**, sans simulation ni extrapolation, conformément à la règle d'or du cahier des charges.

---

## 1. Tableau Récapitulatif par Couche de Test

| # | Couche de Test | Outil & Version | Commande Exécutée | Résultat Mesuré | Preuve Associée | Statut ISO |
|---|---|---|---|---|---|---|
| **1** | **Tests Unitaires & Règles Métier** | Pytest 8.3.5 | `pytest -v tests/test_rules.py` | **4 passés**, 0 échec (5.78s). Valide rôles, unicité email/SKU, quotas de stock, transitions. | Terminal / Capture Page 8 & 9 | **Conforme** (ISO 6.1) |
| **2** | **Couverture de Code** | Coverage.py 7.6.12 | `coverage run -m pytest && coverage report -m` | **90% total** (app/main.py: 89% sur 332 stmts, test_rules: 100% sur 56 stmts). Cible ≥ 70% dépassée. | Capture Page 8 du document de preuves | **Conforme** (ISO 6.7) |
| **3** | **Tests d'Intégration API** | Newman 6.2.3 / Postman | `npx newman run postman/StockFlow.postman_collection.json` | **16 requêtes, 17 assertions, 0 échec** (durée 2.1s, temps moyen 46 ms). | Captures Pages 3, 4, 5, 6 | **Conforme** (ISO 6.1, 6.3) |
| **4** | **Tests Fonctionnels E2E** | Playwright 1.51.0 | `npm run e2e` | Scénario lecteur validé sur Chromium. Scénario commercial corrigé (binding select Angular et synchronisation d'état). | Captures Pages 11 à 14 (défaut initial documenté) | **Conforme après correction** (ISO 6.1, 6.4) |
| **5** | **Tests de Performance** | Locust 2.32.10 | `locust -f tests/locustfile.py --users 20 --spawn-rate 5` | 20 utilisateurs simultanés, 0 échec. Endpoints métier : dashboard p95 ~300 ms, produit p95 ~200 ms. Endpoint `/api/token` p95 ~1 300 ms (hachage Bcrypt). Aggregate p95 = 1 100 ms (> 500 ms). | Capture Page 10 du document de preuves | **Partiellement Conforme** (ISO 6.2) |
| **6** | **Tests de Fiabilité & Robustesse** | Pytest / Transactions | Scénarios `test_stock_and_status_rules` | Transactions atomiques vérifiées : rollback en cas de stock insuffisant, rejet des sauts de statut (409), intégrité relationnelle. | Tests unitaires / code source | **Conforme** (ISO 6.5) |
| **7** | **Analyse Statique de Sécurité (SAST)** | Bandit 1.8.3 | `bandit -r app` | **532 lignes de code analysées, 0 problème détecté** (0 High, 0 Medium, 0 Low). | Captures Pages 2 & 7 du document de preuves | **Conforme** (ISO 6.6) |
| **8** | **Analyse des Dépendances (SCA)** | pip-audit 2.10.1 | `pip-audit` | Exécuté réellement : **43 vulnérabilités connues détectées dans 6 packages** (`pyasn1`, `starlette`, `python-multipart`, `ecdsa`, `pytest`, `python-jose`). | Rapport CLI pip-audit consigné ci-dessous | **Évalué / Actions Requises** (ISO 6.6) |
| **9** | **Analyse Dynamique de Sécurité (DAST)** | OWASP ZAP (Baseline) | Procédure conteneurisée documentée | Non exécuté en continu dans l'environnement local. Procédure reproductible fournie. | Guide de reproduction | **Non Vérifié** (ISO 6.6) |
| **10** | **Qualité & Maintenabilité** | Ruff 0.9.7 | `ruff check app tests` | **All checks passed!** Code conforme PEP8, typage Pydantic, aucune dette de formatage. | Capture Page 9 du document de preuves | **Conforme** (ISO 6.7) |
| **11** | **Compatibilité Multi-Navigateurs** | Playwright (Chromium, Firefox) | `npx playwright test --project=chromium --project=firefox` | Scénario lecteur vérifié sur Chromium ; compatibilité Firefox configurée dans `playwright.config.ts`. | Configuration et suites E2E | **Partiellement Conforme** (ISO 6.3) |
| **12** | **Portabilité & Déploiement** | Docker Compose | `docker compose up -d --build` | Images backend et frontend construites sans erreur, conteneurs démarrés, `GET /api/health` et `HEAD /` retournent HTTP 200. | Logs Docker Desktop Page 1 | **Conforme** (ISO 6.8) |

---

## 2. Analyse Détaillée des Écarts et Résultats Clés

### 2.1 Performance sous Charge (Locust)
- **Constat :** À 20 utilisateurs simultanés, le temps de réponse p95 agrégé atteint 1 100 ms, ce qui dépasse la cible indicative de 500 ms.
- **Cause identifiée :** L'algorithme Bcrypt utilisé pour le hachage des mots de passe dans `POST /api/token` nécessite un travail CPU intentionnellement élevé pour résister aux attaques par force brute. Sous une montée rapide de 20 utilisateurs, ce endpoint sature temporairement le thread CPU, affichant une moyenne de 995 ms et un p95 de 1 300 ms.
- **Comportement des endpoints métier :** Les endpoints de consultation et de recherche opérationnelle (`GET /api/dashboard` et `GET /api/products`) répondent respectivement en 111 ms et 68 ms en moyenne, satisfaisant pleinement les exigences de performance.
- **Décision :** La sécurité cryptographique des mots de passe n'a pas été dégradée artificiellement pour fausser la métrique. Cette limitation architecturale est documentée en toute transparence.

### 2.2 Analyse des Dépendances (pip-audit)
- **Résultat concret :** 43 alertes répertoriées sur des bibliothèques tierces, notamment :
  - `python-multipart 0.0.20` (vulnérabilités de déni de service résolues dans les versions ≥ 0.0.31).
  - `starlette 0.46.2` (avis liés au traitement des en-têtes et requêtes multipart).
  - `pyasn1 0.4.8` (dépassement mémoire résolu en 0.6.5).
- **Correctif préconisé :** Montée de version progressive de `python-multipart` vers `0.0.31` et de `fastapi`/`starlette` vers leurs derniers correctifs de sécurité lors du prochain cycle de maintenance.
