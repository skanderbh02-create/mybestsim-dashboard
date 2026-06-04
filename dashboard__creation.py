import re
import sys
import html
import math
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from pathlib import Path
from datetime import date

INDEX_URL = "https://pub-96a05b89dc7b47979a5940f679f79728.r2.dev/index.html"
OUTPUT_FILE = "dashboard.html"
TIMEOUT = 30

def get_csv_urls(index_url: str) -> list[str]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MyBestSim-Dashboard/1.0)"}
    r = requests.get(index_url, timeout=TIMEOUT, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    base = index_url.rsplit("/", 1)[0]
    urls = []
    for a in soup.find_all("a"):
        href = a.get("href", "").strip()
        if not href.endswith(".csv"):
            continue
        if href.startswith("http"):
            urls.append(href)
        else:
            urls.append(f"{base}/{href.lstrip('/')}")
    return sorted(set(urls))

def parse_price(value):
    if pd.isna(value):
        return math.nan
    txt = str(value).strip().lower().replace(",", ".")
    txt = re.sub(r"[^0-9.]", "", txt)
    if not txt:
        return math.nan
    try:
        return float(txt)
    except ValueError:
        return math.nan

def parse_data_gb(value):
    if pd.isna(value):
        return math.nan
    txt = str(value).strip().lower()
    if any(k in txt for k in ["unlimited", "illimité", "illimite", "∞"]):
        return math.nan
    m = re.search(r"([0-9]+(?:[.,][0-9]+)?)", txt)
    if not m:
        return math.nan
    num = float(m.group(1).replace(",", "."))
    if "mb" in txt and "gb" not in txt and "go" not in txt:
        return num / 1024.0
    return num

def parse_validity_days(value):
    if pd.isna(value):
        return math.nan
    txt = str(value).strip().lower()
    m = re.search(r"([0-9]+)", txt)
    if not m:
        return math.nan
    return float(m.group(1))

def find_column(columns, candidates):
    norm = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        for low, original in norm.items():
            if cand in low:
                return original
    return None

def load_catalog(csv_urls: list[str]) -> pd.DataFrame:
    frames = []
    for url in csv_urls:
        provider_guess = Path(url).stem.replace("-", " ").replace("_", " ").title()
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; MyBestSim-Dashboard/1.0)"}
            r = requests.get(url, timeout=TIMEOUT, headers=headers)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text))
            df["provider"] = df.get("provider", provider_guess)
            df["source_url"] = url

            price_col    = find_column(df.columns, ["price", "prix", "amount", "eur", "cost"])
            data_col     = find_column(df.columns, ["data", "gb", "go", "volume"])
            validity_col = find_column(df.columns, ["validity", "validité", "days", "jours"])
            name_col     = find_column(df.columns, ["name", "title", "product", "plan"])

            df["price_eur"]    = df[price_col].apply(parse_price) if price_col else math.nan
            df["data_gb"]      = df[data_col].apply(parse_data_gb) if data_col else math.nan
            df["validity_days"]= df[validity_col].apply(parse_validity_days) if validity_col else math.nan
            df["product_name"] = (df[name_col].astype(str).str.strip() if name_col else provider_guess + " plan")

            frames.append(df)
            print(f"  ✓ {provider_guess} — {len(df)} produits")
        except Exception as e:
            print(f"  ✗ {provider_guess}: {e}", file=sys.stderr)

    if not frames:
        return pd.DataFrame(columns=["provider","source_url","price_eur","data_gb","validity_days","product_name"])
    return pd.concat(frames, ignore_index=True)

def fmt_eur(v):
    return "-" if pd.isna(v) else f"{float(v):.2f} €"

def fmt_num(v, decimals=1):
    return "-" if pd.isna(v) else f"{float(v):.{decimals}f}"

def build_table(rows, headers):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    trs = "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in r)}</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"

def generate_stats(df: pd.DataFrame):
    stats = {}
    if df.empty:
        stats.update({
            "total_products": 0, "products_over_100": 0,
            "min_price": math.nan, "max_price": math.nan,
            "avg_data": math.nan, "avg_price": math.nan,
            "providers_counts": pd.Series(dtype=int),
            "top_eur_per_gb": pd.DataFrame(),
            "avg_validity": pd.Series(dtype=float),
            "unlimited_count": 0,
            "price_buckets": {},
            "top_providers_avg_price": pd.Series(dtype=float),
        })
        return stats

    for col in ["price_eur", "data_gb", "validity_days", "product_name", "provider"]:
        if col not in df.columns:
            df[col] = math.nan

    finite_price = df[df["price_eur"].notna()]
    finite_data  = df[df["data_gb"].notna() & (df["data_gb"] > 0)]
    df_both = df[df["price_eur"].notna() & df["data_gb"].notna() & (df["data_gb"] > 0)].copy()

    if not df_both.empty:
        df_both["eur_per_gb"] = df_both["price_eur"] / df_both["data_gb"]
        stats["top_eur_per_gb"] = df_both.sort_values("eur_per_gb").head(10)
    else:
        stats["top_eur_per_gb"] = pd.DataFrame()

    # KPIs de base
    stats["total_products"]    = len(df)
    stats["products_over_100"] = int((df["price_eur"] > 100).sum(skipna=True))
    stats["min_price"]         = finite_price["price_eur"].min(skipna=True)
    stats["max_price"]         = finite_price["price_eur"].max(skipna=True)
    stats["avg_data"]          = finite_data["data_gb"].mean(skipna=True)
    stats["avg_price"]         = finite_price["price_eur"].mean(skipna=True)
    stats["providers_counts"]  = df.groupby("provider").size().sort_values(ascending=False)
    stats["avg_validity"]      = (df.groupby("provider")["validity_days"]
                                    .mean(numeric_only=True).dropna()
                                    .sort_values(ascending=False).head(5))
    stats["unlimited_count"]   = int(df["data_gb"].isna().sum())

    # BONUS — répartition par tranche de prix
    bins   = [0, 10, 25, 50, 100, float("inf")]
    labels = ["< 10 €", "10–25 €", "25–50 €", "50–100 €", "> 100 €"]
    if not finite_price.empty:
        buckets = pd.cut(finite_price["price_eur"], bins=bins, labels=labels, right=False)
        stats["price_buckets"] = buckets.value_counts().reindex(labels, fill_value=0).to_dict()
    else:
        stats["price_buckets"] = {l: 0 for l in labels}

    # BONUS — prix moyen par fournisseur (top 8)
    stats["top_providers_avg_price"] = (finite_price.groupby("provider")["price_eur"]
                                        .mean().sort_values().head(8))

    return stats

def json_series(s):
    """Sérialise un dict ou Series en listes JS pour Chart.js."""
    if isinstance(s, pd.Series):
        labels = list(s.index)
        values = [round(float(v), 2) for v in s.values]
    else:
        labels = list(s.keys())
        values = [int(v) for v in s.values()]
    return labels, values

def generate_html(df: pd.DataFrame, stats, csv_urls):
    today = date.today().strftime("%d %B %Y")

    provider_rows = build_table(
        [(html.escape(p), int(c)) for p, c in stats["providers_counts"].items()],
        ["Fournisseur", "Nombre de cartes"]
    ) if stats["total_products"] > 0 else "<p>Aucune donnée.</p>"

    top_rows = build_table(
        [(html.escape(str(r["product_name"])), html.escape(str(r["provider"])),
          f'{fmt_num(r["data_gb"])} Go', fmt_eur(r["price_eur"]), fmt_eur(r["eur_per_gb"]))
         for _, r in stats["top_eur_per_gb"].iterrows()],
        ["Produit", "Fournisseur", "Data", "Prix", "€/Go"]
    ) if not stats["top_eur_per_gb"].empty else "<p>Pas de données comparables.</p>"

    validity_rows = build_table(
        [(html.escape(p), f'{fmt_num(v,1)} jours') for p, v in stats["avg_validity"].items()],
        ["Fournisseur", "Validité moy."]
    ) if not stats["avg_validity"].empty else "<p>Validité moyenne indisponible.</p>"

    # Données graphiques JSON
    prov_labels, prov_vals   = json_series(stats["providers_counts"])
    bucket_labels, bucket_vals = json_series(stats["price_buckets"])
    avg_labels, avg_vals     = json_series(stats["top_providers_avg_price"])

    unlimited_pct = (round(stats["unlimited_count"] / stats["total_products"] * 100, 1)
                     if stats["total_products"] > 0 else 0)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>MyBestSim — eSIM Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&display=swap');
  :root {{
    --bg:#0f1117; --surface:#1a1d27; --surface2:#22263a;
    --border:#2e3148; --accent:#6366f1; --accent2:#34d399;
    --text:#f1f5f9; --muted:#8b91a8; --radius:14px;
    --shadow:0 4px 24px rgba(0,0,0,.4);
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);font-size:15px;line-height:1.6}}
  .top-bar{{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 32px;display:flex;align-items:center;gap:12px}}
  .logo{{font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;color:var(--accent)}}
  .logo span{{color:var(--text)}}
  .badge{{background:var(--accent);color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px;margin-left:auto}}
  .container{{max-width:1200px;margin:0 auto;padding:32px 24px}}
  h1{{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;margin-bottom:4px}}
  .subtitle{{color:var(--muted);margin-bottom:32px;font-size:14px}}

  /* KPI GRID */
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:36px}}
  .kpi{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;position:relative;overflow:hidden}}
  .kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent)}}
  .kpi.green::before{{background:var(--accent2)}}
  .kpi-label{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin-bottom:8px}}
  .kpi-value{{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:var(--text)}}
  .kpi-sub{{font-size:12px;color:var(--muted);margin-top:4px}}

  /* CHARTS GRID */
  .charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:36px}}
  .chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px}}
  .chart-card.wide{{grid-column:1/-1}}
  .chart-title{{font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;margin-bottom:18px;color:var(--text)}}
  canvas{{max-height:260px}}

  /* TABLES */
  .section{{margin-bottom:32px}}
  .section h2{{font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;margin-bottom:14px;color:var(--text)}}
  table{{width:100%;border-collapse:collapse;background:var(--surface);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}}
  th,td{{padding:12px 16px;border-bottom:1px solid var(--border);text-align:left;font-size:13.5px}}
  th{{background:var(--surface2);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.07em;font-weight:700}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:var(--surface2)}}

  .note{{color:var(--muted);font-size:12px;margin-top:32px;border-top:1px solid var(--border);padding-top:16px}}
  @media(max-width:680px){{.charts-grid{{grid-template-columns:1fr}}.chart-card.wide{{grid-column:auto}}}}
</style>
</head>
<body>

<div class="top-bar">
  <div class="logo">MyBest<span>Sim</span></div>
  <span style="color:var(--muted);font-size:13px">eSIM Analytics Dashboard</span>
  <span class="badge">LIVE · {today}</span>
</div>

<main class="container">
  <h1>Analyse catalogue eSIM</h1>
  <p class="subtitle">{len(csv_urls)} fournisseurs analysés · Pipeline ETL automatisé · Mis à jour le {today}</p>

  <!-- KPIs -->
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">Total produits</div>
      <div class="kpi-value">{stats["total_products"]}</div>
      <div class="kpi-sub">cartes eSIM référencées</div>
    </div>
    <div class="kpi green">
      <div class="kpi-label">Prix le plus bas</div>
      <div class="kpi-value">{fmt_eur(stats["min_price"])}</div>
      <div class="kpi-sub">entrée de gamme catalogue</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Prix le plus haut</div>
      <div class="kpi-value">{fmt_eur(stats["max_price"])}</div>
      <div class="kpi-sub">haut de gamme catalogue</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Prix moyen global</div>
      <div class="kpi-value">{fmt_eur(stats["avg_price"])}</div>
      <div class="kpi-sub">tous fournisseurs confondus</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Data moyenne</div>
      <div class="kpi-value">{fmt_num(stats["avg_data"])} Go</div>
      <div class="kpi-sub">hors offres illimitées</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Produits > 100 €</div>
      <div class="kpi-value">{stats["products_over_100"]}</div>
      <div class="kpi-sub">offres premium</div>
    </div>
    <div class="kpi green">
      <div class="kpi-label">Offres illimitées</div>
      <div class="kpi-value">{stats["unlimited_count"]}</div>
      <div class="kpi-sub">{unlimited_pct}% du catalogue</div>
    </div>
  </div>

  <!-- GRAPHIQUES -->
  <div class="charts-grid">

    <div class="chart-card">
      <div class="chart-title">📦 Produits par fournisseur</div>
      <canvas id="chartProviders"></canvas>
    </div>

    <div class="chart-card">
      <div class="chart-title">💶 Répartition par tranche de prix</div>
      <canvas id="chartBuckets"></canvas>
    </div>

    <div class="chart-card wide">
      <div class="chart-title">📊 Prix moyen par fournisseur (Top 8 les moins chers)</div>
      <canvas id="chartAvgPrice"></canvas>
    </div>

  </div>

  <!-- TABLES -->
  <div class="section">
    <h2>🏆 Meilleur rapport €/Go — Top 10</h2>
    {top_rows}
  </div>

  <div class="section">
    <h2>📋 Répartition complète par fournisseur</h2>
    {provider_rows}
  </div>

  <div class="section">
    <h2>⏱️ Validité moyenne par fournisseur (Top 5)</h2>
    {validity_rows}
  </div>

  <p class="note">
    Dashboard analytique développé dans le cadre du test technique MyBestSim · Pipeline ETL Python/Pandas pour l’agrégation de catalogues eSIM multi-fournisseurs, harmonisation des données, calcul d’indicateurs métier et génération automatisée d’un tableau de bord interactif.<br>
    Sources : {len(csv_urls)} fichiers CSV · {stats["total_products"]} produits · {today}
</p>
</main>

<script>
const COLORS = ['#6366f1','#34d399','#f59e0b','#f43f5e','#60a5fa','#a78bfa','#fb923c','#2dd4bf','#e879f9','#4ade80'];
const DARK = '#1a1d27';
const MUTED = '#8b91a8';
const TEXT = '#f1f5f9';
const BORDER = '#2e3148';

Chart.defaults.color = MUTED;
Chart.defaults.borderColor = BORDER;
Chart.defaults.font.family = "'DM Sans', sans-serif";

// 1 — Produits par fournisseur (bar horizontal)
new Chart(document.getElementById('chartProviders'), {{
  type: 'bar',
  data: {{
    labels: {prov_labels},
    datasets: [{{ data: {prov_vals}, backgroundColor: COLORS, borderRadius: 6, borderSkipped: false }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ color: BORDER }}, ticks: {{ color: MUTED }} }},
      y: {{ grid: {{ display: false }}, ticks: {{ color: TEXT }} }}
    }}
  }}
}});

// 2 — Répartition par tranche de prix (doughnut)
new Chart(document.getElementById('chartBuckets'), {{
  type: 'doughnut',
  data: {{
    labels: {bucket_labels},
    datasets: [{{ data: {bucket_vals}, backgroundColor: COLORS, borderColor: DARK, borderWidth: 3 }}]
  }},
  options: {{
    responsive: true, cutout: '60%',
    plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 16, boxWidth: 12 }} }} }}
  }}
}});

// 3 — Prix moyen par fournisseur (bar vertical)
new Chart(document.getElementById('chartAvgPrice'), {{
  type: 'bar',
  data: {{
    labels: {avg_labels},
    datasets: [{{
      label: 'Prix moyen (€)',
      data: {avg_vals},
      backgroundColor: COLORS,
      borderRadius: 8,
      borderSkipped: false
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ display: false }}, ticks: {{ color: TEXT }} }},
      y: {{ grid: {{ color: BORDER }}, ticks: {{ color: MUTED, callback: v => v + ' €' }} }}
    }}
  }}
}});
</script>
</body>
</html>
"""

def main():
    print("MyBestSim Dashboard — démarrage pipeline ETL")
    print(f"Source: {INDEX_URL}\n")
    try:
        print("→ Récupération de l'index CSV...")
        csv_urls = get_csv_urls(INDEX_URL)
        print(f"  {len(csv_urls)} fichiers trouvés\n→ Chargement des catalogues fournisseurs...")
        df = load_catalog(csv_urls)
        print(f"\n→ Calcul des statistiques ({len(df)} produits)...")
        stats = generate_stats(df)
        print("→ Génération du dashboard HTML...")
        html_content = generate_html(df, stats, csv_urls)
        Path(OUTPUT_FILE).write_text(html_content, encoding="utf-8")
        print(f"\n✅ Dashboard généré : {OUTPUT_FILE}")
        print(f"   Fournisseurs : {len(stats['providers_counts'])}")
        print(f"   Produits     : {stats['total_products']}")
        print(f"   Prix moyen   : {stats['avg_price']:.2f} €" if not math.isnan(stats['avg_price'] or math.nan) else "   Prix moyen   : -")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
