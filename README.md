# 📊 eSIM Analytics Dashboard — MyBestSim

> Automated ETL pipeline that scrapes 18 eSIM providers, processes 5 000+ products and generates a self-contained interactive HTML dashboard — built for the MyBestSim technical test.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Dashboard-Live-brightgreen)

---

## 🚀 Live Demos

| Livrable | Lien |
|---|---|
| 📊 Dashboard Data | [skanderbh02-create.github.io/.../dashboard.html](https://skanderbh02-create.github.io/mybestsim-dashboard/dashboard.html) |
| ✍️ Article SEO | [skanderbh02-create.github.io/.../article.html](https://skanderbh02-create.github.io/mybestsim-dashboard/article.html) |

> Données en temps réel — Pipeline ETL exécuté le 04 Juin 2026.

---

## 📸 Key Metrics

| Indicateur | Valeur |
|---|---|
| Total produits | **5 056** |
| Fournisseurs analysés | **18** |
| Prix le plus bas | **5,36 €** |
| Prix le plus haut | **154,63 €** |
| Prix moyen global | **29,30 €** |
| Volume moyen | **14,5 Go** |
| Produits > 100 € | **56** |
| Offres illimitées | **653 (12,9 %)** |
| Meilleur ratio €/Go | **0,91 €/Go** |

---

## 🧠 Pipeline Architecture

```
index.html (R2 Storage)
        │
        ▼
  get_csv_urls()          → Scrape la liste des 18 fichiers CSV fournisseurs
        │
        ▼
  load_catalog()          → Télécharge & parse chaque CSV
  parse_price()           → Normalise les prix (texte libre → float €)
  parse_data_gb()         → Normalise les volumes (MB/GB/illimité)
  parse_validity_days()   → Extrait la validité en jours
        │
        ▼
  generate_stats()        → Calcule les KPIs et indicateurs métier
        │
        ▼
  generate_html()         → Dashboard HTML self-contained (Chart.js)
```

---

## 🛠️ Installation & lancement

### Prérequis
- Python 3.10+
- Connexion internet (le pipeline scrape les CSV en live)

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/skanderbh02-create/mybestsim-dashboard.git
cd mybestsim-dashboard

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le pipeline ETL
python dashboard__creation.py

# 4. Ouvrir le dashboard généré
open dashboard.html        # macOS
xdg-open dashboard.html    # Linux
start dashboard.html       # Windows
```

**Output attendu :**
```
MyBestSim Dashboard — démarrage pipeline ETL
→ Récupération de l'index CSV...
  18 fichiers trouvés
→ Chargement des catalogues fournisseurs...
  ✓ Airalo — 722 produits
  ✓ Ubigi — 562 produits
  ...
✅ Dashboard généré : dashboard.html
```

---

## 📁 Structure du projet

```
mybestsim-dashboard/
│
├── dashboard__creation.py   # Pipeline ETL complet
├── dashboard.html           # Dashboard interactif (généré)
├── article.html             # Article SEO Mexique (Partie 1)
├── requirements.txt         # Dépendances Python
└── README.md
```

---

## 🏗️ Tech Stack

| Composant | Technologie |
|---|---|
| Langage | Python 3.10+ |
| Data processing | Pandas, re, math |
| Scraping | Requests, BeautifulSoup4 |
| Visualisation | Chart.js (injecté dans le HTML) |
| Dashboard | HTML/CSS self-contained |
| Source données | Cloudflare R2 — CSV publics MyBestSim |

---

## 👤 Author

**Mohamed Skander Ben Hamida** — Data / Growth enthusiast  
[GitHub](https://github.com/skanderbh02-create)

---

*Développé dans le cadre du test technique MyBestSim — Juin 2026*



