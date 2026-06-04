\# 📊 eSIM Analytics Dashboard — MyBestSim



> Automated ETL pipeline that scrapes 18 eSIM providers, processes 5 000+ products and generates a self-contained interactive HTML dashboard — built for the MyBestSim technical test.



!\[Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python\&logoColor=white)

!\[Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas\&logoColor=white)

!\[License](https://img.shields.io/badge/License-MIT-green)

!\[Status](https://img.shields.io/badge/Dashboard-Live-brightgreen)



\---



## 🚀 Live Demo

👉 **[View Live Dashboard](https://skanderbh02-create.github.io/mybestsim-dashboard/dashboard.html)**

Generated automatically from the MyBestSim catalog data.


\---



\## 📸 Aperçu



| KPIs globaux | Répartition par fournisseur |

|---|---|

| 5 056 produits · 18 fournisseurs | Airalo, Ubigi, eSIMX, Saily... |

| Prix : 5,36 € → 154,63 € | Meilleur rapport : \*\*0,91 €/Go\*\* |

| Prix moyen : \*\*29,30 €\*\* | Offres illimitées : \*\*653 (12,9 %)\*\* |



\---



\## 🧠 Fonctionnement du pipeline



```

index.html (R2 Storage)

&#x20;       │

&#x20;       ▼

&#x20; get\_csv\_urls()          → Scrape la liste des 18 fichiers CSV fournisseurs

&#x20;       │

&#x20;       ▼

&#x20; load\_catalog()          → Télécharge \& parse chaque CSV

&#x20; parse\_price()           → Normalise les prix (texte libre → float €)

&#x20; parse\_data\_gb()         → Normalise les volumes (MB/GB/illimité)

&#x20; parse\_validity\_days()   → Extrait la validité en jours

&#x20;       │

&#x20;       ▼

&#x20; generate\_stats()        → Calcule les KPIs et indicateurs métier

&#x20;       │

&#x20;       ▼

&#x20; generate\_html()         → Produit un dashboard HTML self-contained

&#x20;                           avec Chart.js (aucune dépendance externe)

```



\---



\## 📊 Indicateurs générés



| Indicateur | Valeur |

|---|---|

| Total produits | \*\*5 056\*\* |

| Fournisseurs analysés | \*\*18\*\* |

| Prix le plus bas | \*\*5,36 €\*\* |

| Prix le plus haut | \*\*154,63 €\*\* |

| Prix moyen global | \*\*29,30 €\*\* |

| Volume moyen | \*\*14,5 Go\*\* |

| Produits > 100 € | \*\*56\*\* |

| Offres illimitées | \*\*653 (12,9 %)\*\* |

| Meilleur ratio €/Go | \*\*0,91 €/Go\*\* |



\*\*Bonus calculés automatiquement :\*\*

\- Top 10 meilleur rapport €/Go

\- Répartition par tranche de prix (< 10 € / 10–25 € / 25–50 € / 50–100 € / > 100 €)

\- Prix moyen par fournisseur (Top 8 les moins chers)

\- Validité moyenne par fournisseur (Top 5)



\---



\## 🛠️ Installation \& lancement



\### Prérequis

\- Python 3.10+

\- Connexion internet (le pipeline scrape les CSV en live)



\### Étapes



```bash

\# 1. Cloner le repo

git clone https://github.com/skanderbh02-create/mybestsim-dashboard.git

cd mybestsim-dashboard



\# 2. Installer les dépendances

pip install -r requirements.txt



\# 3. Lancer le pipeline ETL

python dashboard\_\_creation.py



\# 4. Ouvrir le dashboard généré

open dashboard.html   # macOS

xdg-open dashboard.html   # Linux

start dashboard.html  # Windows

```



\*\*Output attendu :\*\*

```

MyBestSim Dashboard — démarrage pipeline ETL

→ Récupération de l'index CSV...

&#x20; 18 fichiers trouvés

→ Chargement des catalogues fournisseurs...

&#x20; ✓ Airalo — 722 produits

&#x20; ✓ Ubigi — 562 produits

&#x20; ...

→ Calcul des statistiques (5056 produits)...

→ Génération du dashboard HTML...

✅ Dashboard généré : dashboard.html

```



\---



\## 📁 Structure du projet



```

mybestsim-dashboard/

│

├── dashboard\_\_creation.py   # Pipeline ETL complet (scraping → stats → HTML)

├── dashboard.html           # Dashboard généré (self-contained, no server needed)

├── requirements.txt         # Dépendances Python

└── README.md

```



\---



\## 🏗️ Stack technique



| Composant | Technologie |

|---|---|

| Langage | Python 3.10+ |

| Data processing | Pandas, re, math |

| Scraping HTTP | Requests, BeautifulSoup4 |

| Visualisation | Chart.js (CDN, injecté dans le HTML) |

| Dashboard | HTML/CSS self-contained (aucun serveur requis) |

| Source des données | Cloudflare R2 — CSV publics MyBestSim |



\---



\## 👤 Auteur



\*\*Mohamed Skander Ben Hamida\*\*  

Data / Growth enthusiast  

\[GitHub](https://github.com/skanderbh02-create)



\---



\*Développé dans le cadre du test technique MyBestSim — Juin 2026\*



