# Inventaire Exhaustif des Captures et Preuves Visuelles StockFlow

**Document de référence :** `Screenshots_Results.pdf` (Document de 18 pages d'évaluation préliminaire)  
**Date d'inventaire :** 20 novembre 2026  
**Statut :** Analyse systématique page par page  

---

## 1. Tableau Synoptique de l'Inventaire

| Page PDF | Élément Visuel / Titre | Couche de Test / Périmètre | Exigence Référencée | Nature de la Preuve | Statut de Conformité | Emplacement dans Rapport | Action Requise |
|---|---|---|---|---|---|---|---|
| **Page 1** | Build Docker E2E & Démarrage Playwright | Couche 4 (E2E) & 12 (Portabilité) | EF-03, QS-6.1, QS-6.8 | Log de conteneurisation | Information / Début d'exécution | Annexe E & Rapport Preuves § 2.1 | Documenter comme contexte de lancement. |
| **Page 2** | Analyse SAST Bandit (Python 3.12.16) | Couche 7 (SAST) | QS-6.6 (Sécurité) | Preuve de réussite | **Conforme** (0 faille / 523 LOC) | Rapport ISO § 4.7 & Annexe C | Conserver comme preuve définitive. |
| **Page 3** | Synthèse d'exécution Newman (Tests 12 à 16) | Couche 3 (Tests API) | EF-01, EF-04, EF-06, QS-6.1 | Preuve de réussite | **Conforme** (16 req, 17 assertions, 0 fail) | Rapport ISO § 3.3 & Preuves § 2.2 | Conserver comme preuve clé API. |
| **Page 4** | Tableau récapitulatif Newman (Vue agrandie) | Couche 3 (Tests API) | QS-6.1 (Aptitude fonctionnelle) | Preuve de réussite (Doublon) | **Conforme** | Rapport de Preuves § 2.2 | Conserver en complément zoomé. |
| **Page 5** | Requêtes Newman 04 à 12 (Workflow & Métier) | Couche 3 (Tests API) | EF-02, EF-03, RM-01 à RM-08 | Preuve de réussite | **Conforme** (Codes HTTP 200, 201, 409) | Rapport ISO § 3.3 & Preuves § 2.2 | Preuve des règles de transition et stock. |
| **Page 6** | Requêtes Newman 01 à 06 (Auth & CRUD initial) | Couche 3 (Tests API) | EF-01, EF-02, QS-6.6 | Preuve de réussite | **Conforme** (Login admin, création client/produit) | Rapport ISO § 3.3 & Preuves § 2.2 | Preuve de démarrage API. |
| **Page 7** | Analyse SAST Bandit (Rapport détaillé) | Couche 7 (SAST) | QS-6.6 (Sécurité), QS-6.7 | Preuve de réussite | **Conforme** (0 vulnérabilité / 532 LOC) | Rapport ISO § 4.7 & Preuves § 2.3 | Preuve formelle SAST. |
| **Page 8** | Rapport de couverture Pytest (Total 90%) | Couche 1 & 10 (Couverture / Qualité) | QS-6.7 (Maintenabilité) | Preuve de réussite | **Conforme** (Cible 70% dépassée : 90%) | Rapport ISO § 4.8 & Annexe A | Preuve maîtresse de couverture de code. |
| **Page 9** | Linter Ruff ("All checks passed!") & Pytest | Couche 10 (Maintenabilité) | QS-6.7 (Maintenabilité) | Preuve de réussite | **Conforme** (Formatage et linter OK) | Rapport ISO § 3.3 & Preuves § 2.4 | Preuve de maintenabilité du code. |
| **Page 10** | Test de charge Locust (20 utilisateurs, 10s) | Couche 5 (Performance) | QS-6.2 (Performance) | Preuve de test avec écart | **Partiellement Conforme** (p95 1 100 ms > 500 ms) | Rapport ISO § 4.3 & Annexe B | Documenter l'impact du hachage Bcrypt. |
| **Page 11** | Échec Playwright (Trace et attachements) | Couche 4 (E2E) | EF-03, QS-6.1 | Preuve d'anomalie (Défaut) | **Non Conforme** (1 failed sur Chromium) | Rapport de Preuves § 2.5 | Classifier comme preuve de bug identifié. |
| **Page 12** | Échec Playwright (Code source de l'assertion) | Couche 4 (E2E) | EF-03, QS-6.1 | Preuve d'anomalie (Défaut) | **Non Conforme** (Ligne 10 en échec) | Rapport de Preuves § 2.5 | Classifier comme preuve du défaut d'origine. |
| **Page 13** | Échec Playwright (Détail de timeout locator) | Couche 4 (E2E) | EF-03, QS-6.1 | Preuve d'anomalie (Défaut) | **Non Conforme** (Timeout 5000ms locator row) | Rapport de Preuves § 2.5 | Classifier comme preuve du défaut d'origine. |
| **Page 14** | Échec Playwright (Dump console de la section) | Couche 4 (E2E) | EF-03, QS-6.1 | Log de diagnostic | Preuve de diagnostic | Rapport de Preuves § 2.5 | Montre la liste des options sans le tableau. |
| **Page 15** | Grille d'évaluation préliminaire (Partie 1) | Synthèse Qualité | Cahier des Charges § 4 | Évaluation intermédiaire | Document d'analyse de l'équipe | Rapport ISO § 4.1 & INITIAL_AUDIT | Référence d'état des lieux initial. |
| **Page 16** | Grille d'évaluation préliminaire (Partie 2) | Synthèse Qualité | Cahier des Charges § 4 & 6 | Évaluation intermédiaire | Document d'analyse de l'équipe | Rapport ISO § 4.1 & INITIAL_AUDIT | Référence d'état des lieux initial. |
| **Page 17** | Grille d'évaluation préliminaire (Partie 3) | Synthèse Qualité | Cahier des Charges § 6 | Évaluation intermédiaire | Document d'analyse de l'équipe | Rapport ISO § 4.1 & INITIAL_AUDIT | Référence d'état des lieux initial. |
| **Page 18** | Grille d'évaluation préliminaire (Partie 4) | Synthèse Qualité | Cahier des Charges § 8 | Évaluation intermédiaire | Document d'analyse de l'équipe | Rapport ISO § 4.1 & INITIAL_AUDIT | Priorités d'actions du collègue. |

---

## 2. Distinction Stricte : Preuves de Réussite vs Preuves d'Anomalies

Conformément à la règle d'or du cahier des charges et aux consignes explicites :
1. **Ne pas travestir un échec en succès :** Les pages 11 à 14 constituent des preuves réelles de la présence d'un **bogue de synchronisation et de binding UI**, et non des preuves de conformité du parcours E2E.
2. **Preuves valides de conformité :**
   - **Page 2 & 7 :** Bandit SAST (0 problème).
   - **Page 3, 5, 6 :** Newman API Acceptance (100% succès sur 16 requêtes).
   - **Page 8 :** Couverture de code 90% (largement au-dessus des 70% requis).
   - **Page 9 :** Linter Ruff sans anomalie.
3. **Preuves de limites / écarts réels :**
   - **Page 10 :** Locust met en lumière un goulot d'étranglement CPU sur l'algorithme Bcrypt lors des requêtes d'obtention de token sous forte charge concurrente.

---

## 3. Inventaire des Captures d'Interface et Éléments Manquants

Pour le rapport Word principal et la soutenance, les captures suivantes de l'interface graphique sont définies :
1. `01-dashboard-sales.png` : Tableau de bord commercial (KPIs et filtres d'état).
2. `02-products.png` : Gestion des produits (formulaire d'ajout/édition, tableau des stocks).
3. `03-customers.png` : Gestion des clients (formulaire, recherche indexée, liste).
4. `04-orders.png` : Gestion des commandes, lignes de commandes et boutons de transition de statut.
5. `05-audit-admin.png` : Journal d'audit accessible uniquement sous le profil administrateur.
6. `06-playwright-chromium-pass.png` : Exécution réussie des scénarios E2E sur Chromium après correction.
7. `07-playwright-firefox-pass.png` : Exécution des scénarios E2E sur Firefox.
8. `08-pip-audit-sca.png` : Rapport d'analyse de vulnérabilités des dépendances Python.
9. `09-owasp-zap-dast.png` : Rapport d'analyse dynamique applicative.
