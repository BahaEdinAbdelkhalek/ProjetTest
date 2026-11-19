"""Append the verified StockFlow progress record to the copied Word template."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "Rapport_Projet_ISO25010_StockFlow.docx"
NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", NS)

def tag(name):
    return f"{{{NS}}}{name}"

def paragraph(body, text, style="Normal"):
    p = ET.SubElement(body, tag("p"))
    ppr = ET.SubElement(p, tag("pPr"))
    ET.SubElement(ppr, tag("pStyle"), {tag("val"): style})
    run = ET.SubElement(p, tag("r"))
    t = ET.SubElement(run, tag("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p

sections = [
    ("Heading1", "Avancement vérifié du projet StockFlow"),
    ("Normal", "Cette section complète le modèle de rapport avec l’état vérifié du prototype réalisé à partir du cahier des charges. Les résultats distinguent les contrôles exécutés de ceux qui restent à faire. Date des mesures : 19 novembre 2026."),
    ("Heading2", "Périmètre et choix techniques"),
    ("Normal", "StockFlow est une application de gestion commerciale destinée à la démonstration : Angular pour l’interface, FastAPI et SQLAlchemy pour l’API, SQLite pour les données et Docker Compose pour le déploiement local. Les entités reliées sont Client, Produit, Commande et Ligne de commande. Les utilisateurs disposent des rôles administrateur, commercial et lecteur."),
    ("Normal", "Les fonctions développées comprennent l’authentification JWT, les permissions par rôle, les API CRUD, la recherche client/produit, un tableau de bord avec filtre d’état, les commandes brouillon → validée → clôturée, le contrôle du stock et un journal d’audit réservé à l’administrateur. L’interface permet de gérer clients et produits et de créer/traiter les commandes. Le modèle de données relie une commande à un client et ses lignes à des produits."),
    ("Heading2", "Règles métier implémentées"),
    ("Normal", "1. L’adresse e-mail client et le SKU produit sont uniques. 2. Le prix et la quantité doivent être positifs ; le stock ne peut pas être négatif. 3. Une commande exige un client et des produits existants. 4. Une quantité supérieure au stock disponible est refusée. 5. Le stock diminue à la validation, pas à la création du brouillon. 6. Les transitions autorisées sont brouillon → validée → clôturée. 7. Un client ou produit référencé ne peut pas être supprimé ; seules les commandes brouillon sont supprimables. 8. Les actions sensibles sont auditées."),
    ("Heading2", "Résultats réellement obtenus"),
    ("Normal", "Tests API avec pytest et FastAPI TestClient : 4 tests réussis. Ils couvrent les rôles, l’unicité, les règles de stock et de statut, les opérations CRUD et les relations de commande. Newman a exécuté la collection Postman : 16 requêtes, 17 assertions, 0 échec. Couverture mesurée : 90 % au total (89 % pour l’API, 100 % pour le fichier de tests). Ruff : toutes les vérifications passent. Bandit : aucun problème de sécurité détecté dans les 532 lignes analysées."),
    ("Normal", "Locust, 20 utilisateurs, 10 secondes : 156 requêtes, 0 échec. Le p95 agrégé est de 1 100 ms et ne respecte donc pas la cible indicative de 500 ms. Le p95 mesuré est de 300 ms pour le tableau de bord, 200 ms pour la recherche produit et 1 300 ms pour l’authentification. Ce test court est un test de charge exploratoire, pas une mesure de charge soutenue."),
    ("Normal", "Le build Docker et le démarrage local ont été vérifiés ; l’API de santé et la page web ont répondu HTTP 200. Le scénario Playwright lecteur a réussi sur Chromium. Le parcours commercial de bout en bout et la validation Firefox restent non concluants : ne pas les présenter comme réussis."),
    ("Heading2", "État des caractéristiques ISO/IEC 25010"),
    ("Normal", "Aptitude fonctionnelle : API testée (4 tests) et collection Postman réussie. Performance : mesurée, cible globale non atteinte. Compatibilité : un scénario lecteur Chromium réussi, parcours complet Chromium/Firefox encore à valider. Utilisabilité : revue manuelle clavier/mobile non réalisée. Fiabilité : stock et transitions vérifiés par test ; la persistance après redémarrage du conteneur reste à vérifier. Sécurité : Bandit réussi ; pip-audit et OWASP ZAP non exécutés. Maintenabilité : Ruff réussi et couverture 90 %. Portabilité : images Docker construites et services lancés ; installation sur une machine propre non vérifiée."),
    ("Heading2", "Captures d’écran à insérer dans le rapport"),
    ("Normal", "Les captures se trouvent dans docs/screenshots/. Remplacer les marqueurs ci-dessous par les images correspondantes dans Word (Insertion → Images) après les avoir générées. Les captures montrent l’état réel de l’interface, sans constituer à elles seules une preuve de test réussi."),
    ("Normal", "[INSÉRER docs/screenshots/01-dashboard-sales.png — Tableau de bord commercial]"),
    ("Normal", "[INSÉRER docs/screenshots/02-products.png — Recherche et gestion des produits]"),
    ("Normal", "[INSÉRER docs/screenshots/03-customers.png — Recherche et gestion des clients]"),
    ("Normal", "[INSÉRER docs/screenshots/04-orders.png — Commandes et workflow à statuts ; cette vue est en cours de validation E2E]"),
    ("Normal", "[INSÉRER docs/screenshots/05-audit-admin.png — Journal d’audit administrateur]"),
    ("Heading2", "Éléments restant à vérifier"),
    ("Normal", "Corriger et réussir le rafraîchissement de la liste des commandes dans l’interface, puis rejouer Playwright sur Chromium et Firefox. Exécuter pip-audit et OWASP ZAP. Vérifier la persistance après redémarrage et faire une revue clavier/mobile. Analyser la latence de connexion et refaire une charge soutenue ; le résultat p95 global actuel dépasse la cible de 500 ms."),
]

with ZipFile(DOCX, "r") as source:
    files = {name: source.read(name) for name in source.namelist()}
root = ET.fromstring(files["word/document.xml"])
body = root.find(tag("body"))
section_properties = body.find(tag("sectPr"))
for style, text in sections:
    p = paragraph(body, text, style)
    if section_properties is not None:
        body.remove(p)
        body.insert(list(body).index(section_properties), p)
files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
with ZipFile(DOCX, "w", ZIP_DEFLATED) as target:
    for name, contents in files.items():
        target.writestr(name, contents)
print(f"Updated {DOCX}")
