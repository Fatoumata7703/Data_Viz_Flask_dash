import os
import re
import sys
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime
from .sommaire import add_toc

REPORT_HTML_HEADER = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --rp-primary: #1e40af;
      --rp-accent: #2563eb;
      --rp-blue: #3b82f6;
      --rp-gold: #f59e0b;
      --rp-gold-light: #fbbf24;
      --rp-text: #334155;
      --rp-muted: #94a3b8;
      --rp-bg: #f0f4f8;
      --rp-card: #ffffff;
      --rp-border: #e2e8f0;
      --rp-shadow: 0 4px 20px rgba(37,99,235,0.06);
      --rp-radius: 16px;
      --rp-radius-sm: 10px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
      color: var(--rp-text);
      background: var(--rp-bg);
      line-height: 1.7;
      font-size: 15px;
      -webkit-font-smoothing: antialiased;
    }}

    /* ─── Wrapper ─── */
    .rapport-wrapper {{
      max-width: 920px;
      margin: 0 auto;
      padding: 40px 32px 48px;
    }}

    /* ─── Header ─── */
    .rapport-header {{
      background: linear-gradient(145deg, #0f172a 0%, #1e293b 35%, #334155 70%, #0891b2 100%);
      color: #fff;
      padding: 48px 44px 42px;
      border-radius: var(--rp-radius);
      margin-bottom: 32px;
      box-shadow: 0 8px 32px rgba(15,23,42,0.25);
      text-align: center;
      position: relative;
      overflow: hidden;
    }}
    .rapport-header::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 4px;
      background: linear-gradient(90deg, var(--rp-gold-light), var(--rp-gold), var(--rp-gold-light));
    }}
    .rapport-header::after {{
      content: '';
      position: absolute;
      bottom: 0; left: 0; right: 0; height: 1px;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    }}
    .rapport-header .badge {{
      display: inline-block;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--rp-accent);
      background: rgba(8,145,178,0.15);
      padding: 5px 14px;
      border-radius: 20px;
      margin-bottom: 18px;
    }}
    .rapport-header h1 {{
      margin: 0 0 12px 0;
      font-size: 1.8rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      line-height: 1.25;
    }}
    .rapport-header .subtitle {{
      font-size: 1rem;
      opacity: 0.85;
      font-weight: 500;
      margin-bottom: 24px;
    }}
    .rapport-header .meta {{
      font-size: 0.85rem;
      opacity: 0.75;
      font-weight: 500;
    }}
    .rapport-header .source {{
      font-size: 0.78rem;
      margin-top: 8px;
      opacity: 0.6;
    }}

    /* ─── TOC ─── */
    #toc.rapport-toc {{
      background: var(--rp-card);
      padding: 24px 28px;
      border-radius: var(--rp-radius);
      margin-bottom: 28px;
      box-shadow: var(--rp-shadow);
      border: 1px solid var(--rp-border);
      position: relative;
    }}
    #toc.rapport-toc::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; bottom: 0; width: 4px;
      background: linear-gradient(180deg, var(--rp-accent), var(--rp-gold));
      border-radius: var(--rp-radius) 0 0 var(--rp-radius);
    }}
    #toc.rapport-toc h2 {{
      margin: 0 0 16px 0;
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--rp-accent);
      letter-spacing: 0.02em;
    }}
    #toc.rapport-toc ul {{ list-style: none; padding-left: 0; margin: 0; }}
    #toc.rapport-toc li {{ margin: 8px 0; line-height: 1.5; }}
    #toc.rapport-toc a {{
      color: var(--rp-text);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      transition: color 0.2s;
    }}
    #toc.rapport-toc a:hover {{ color: var(--rp-gold); }}

    /* ─── Content ─── */
    .rapport-content {{
      background: var(--rp-card);
      padding: 40px 44px;
      border-radius: var(--rp-radius);
      box-shadow: var(--rp-shadow);
      border: 1px solid var(--rp-border);
    }}
    .rapport-content > div {{ margin-bottom: 1.8em; }}
    .rapport-content h1, .rapport-content h2, .rapport-content h3 {{
      color: var(--rp-accent);
      font-weight: 800;
      margin-top: 2em;
      margin-bottom: 0.6em;
      letter-spacing: -0.01em;
    }}
    .rapport-content h1:first-child {{ margin-top: 0; }}
    .rapport-content h1 {{
      font-size: 1.4rem;
      padding-bottom: 10px;
      border-bottom: 3px solid var(--rp-gold);
    }}
    .rapport-content h2 {{
      font-size: 1.2rem;
      padding-left: 14px;
      border-left: 4px solid var(--rp-gold);
    }}
    .rapport-content h3 {{ font-size: 1.05rem; }}
    .rapport-content p {{ margin: 0.8em 0; color: var(--rp-text); }}
    .rapport-content .output_area {{
      margin: 1.5em 0;
      border-radius: var(--rp-radius-sm);
    }}
    .rapport-content img {{
      max-width: 100%;
      height: auto;
      border-radius: var(--rp-radius-sm);
      box-shadow: var(--rp-shadow);
      display: block;
      margin: 1em 0;
    }}

    /* ─── Tables ─── */
    .rapport-content .dataframe, .rapport-content table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      margin: 1.5em 0;
      border-radius: var(--rp-radius-sm);
      overflow: hidden;
      box-shadow: var(--rp-shadow);
    }}
    .rapport-content .dataframe th, .rapport-content table th {{
      background: linear-gradient(135deg, var(--rp-accent), var(--rp-blue));
      color: #fff;
      font-weight: 700;
      font-size: 0.82rem;
      padding: 12px 16px;
      text-align: left;
      letter-spacing: 0.02em;
    }}
    .rapport-content .dataframe td, .rapport-content table td {{
      padding: 10px 16px;
      text-align: left;
      border-bottom: 1px solid var(--rp-border);
      color: var(--rp-text);
    }}
    .rapport-content .dataframe tbody tr:nth-child(even),
    .rapport-content table tbody tr:nth-child(even) {{
      background: rgba(247,249,252,0.6);
    }}
    .rapport-content .dataframe tr:hover,
    .rapport-content table tr:hover {{
      background: rgba(44,82,130,0.04);
    }}

    .rapport-content div.output_subarea {{ max-width: 100%; }}
    .rapport-content div[class*="output"] pre {{
      font-size: 0.85rem;
      line-height: 1.55;
      background: var(--rp-bg);
      padding: 16px 18px;
      border-radius: var(--rp-radius-sm);
      border-left: 4px solid var(--rp-border);
      overflow-x: auto;
    }}
    .rapport-content div[style*="background"] {{
      border-radius: var(--rp-radius-sm);
      overflow: hidden;
    }}

    /* ─── Footer ─── */
    .rapport-footer {{
      margin-top: 40px;
      padding: 24px 20px;
      border-top: 2px solid var(--rp-border);
      font-size: 0.78rem;
      color: var(--rp-muted);
      text-align: center;
      line-height: 1.6;
    }}
    .rapport-footer .line1 {{
      font-weight: 800;
      color: var(--rp-accent);
      font-size: 0.85rem;
      letter-spacing: 0.02em;
    }}
    .rapport-footer .line2 {{ margin-top: 5px; }}
    .rapport-footer .line3 {{
      margin-top: 4px;
      font-size: 0.72rem;
      opacity: 0.7;
    }}

    /* ─── Print ─── */
    @media print {{
      body {{ background: #fff; font-size: 12px; }}
      .rapport-wrapper {{ padding: 12px; max-width: 100%; }}
      .rapport-header {{ box-shadow: none; page-break-after: avoid; }}
      .rapport-content {{ box-shadow: none; border: 1px solid #ddd; }}
      .rapport-content h2 {{ page-break-after: avoid; }}
      .rapport-content .output_area {{ page-break-inside: avoid; }}
      .rapport-content img {{ max-height: 500px; }}
    }}
  </style>
</head>
<body>
  <div class="rapport-wrapper">
  <header class="rapport-header">
    <div class="badge">Document de référence · BCEAO</div>
    <h1>{title}</h1>
    <p class="subtitle">Étude sectorielle · Données bancaires harmonisées</p>
    <div class="meta">Généré le {date}</div>
    <div class="source">Source : base_senegal2 · MongoDB prod</div>
  </header>
  <div class="rapport-content">
"""

REPORT_HTML_FOOTER = """
  </div>
  <footer class="rapport-footer">
    <div class="line1">Rapport de positionnement bancaire — Sénégal</div>
    <div class="line2">BCEAO · Données harmonisées · Généré le {date}</div>
    <div class="line3">Document de travail · Usage institutionnel</div>
  </footer>
  </div>
</body>
</html>
"""


def _clean_notebook_outputs(notebook):
    for cell in notebook.cells:
        if cell.cell_type != "code" or not getattr(cell, "outputs", None):
            continue
        kept = []
        for out in cell.outputs:
            if out.output_type == "stream" and getattr(out, "name", None) == "stderr":
                continue
            if out.output_type == "execute_result":
                data = getattr(out, "data", {}) or {}
                text = "".join(data.get("text/plain", []) or [])
                if re.search(r"<Figure|Axes:|Figure size", text, re.IGNORECASE):
                    continue
            kept.append(out)
        cell.outputs = kept


def _highlight_banque_in_tables(html_str, banque):
    """Met en couleur la ligne de la banque concernée dans tous les tableaux du rapport."""
    if not banque or not html_str:
        return html_str
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_str, "html.parser")
    banque_norm = str(banque).strip().upper()
    # Couleur de surlignage (teal léger, cohérent avec le thème)
    highlight_style = "background-color: rgba(13, 148, 136, 0.18); font-weight: 600;"
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            # Premier cellule = souvent la colonne Banque/Sigle
            first_cell_text = (cells[0].get_text() or "").strip().upper()
            if first_cell_text == banque_norm:
                existing = tr.get("style") or ""
                tr["style"] = existing + ("; " if existing else "") + highlight_style
                break
            # Sinon chercher dans toute la ligne (au cas où l'ordre des colonnes change)
            for cell in cells:
                if (cell.get_text() or "").strip().upper() == banque_norm:
                    existing = tr.get("style") or ""
                    tr["style"] = existing + ("; " if existing else "") + highlight_style
                    break
    return str(soup)


def _clean_html_technical_output(html_str):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_str, "html.parser")
    bad_patterns = [
        re.compile(r"Out\[\d+\]\s*:", re.IGNORECASE),
        re.compile(r"UserWarning|Setting bande|Rectangle\("),
        re.compile(r"Traceback \(most recent|File \".*\.py\""),
        re.compile(r"<Figure size \d+x\d+ with \d+ Axes>"),
    ]
    for tag in list(soup.find_all(["pre", "div"])):
        if tag.find("img"):
            continue
        text = tag.get_text() or ""
        if len(text) > 2500:
            continue
        for pat in bad_patterns:
            if pat.search(text):
                tag.decompose()
                break
    return str(soup)


def notebook_to_html(notebook_path, banque=None, annee=None):
    """
    Convertit un notebook Jupyter (.ipynb) en rapport HTML élégant.

    Parameters
    ----------
    notebook_path : str
        Chemin vers le fichier .ipynb.
    banque : str, optional
        Sigle de la banque (ex: "BNDE").
    annee : int, optional
        Année sélectionnée.

    Returns
    -------
    str
        HTML complet du rapport.
    """
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook_content = f.read()

    notebook = nbformat.reads(notebook_content, as_version=4)
    notebook_dir = os.path.dirname(os.path.abspath(notebook_path))

    cell_cwd = (
        "import os\nimport sys\nimport warnings\nwarnings.filterwarnings('ignore')\n"
        "_rapport_dir = %s\nos.chdir(_rapport_dir)\n"
        "if _rapport_dir not in sys.path:\n    sys.path.insert(0, _rapport_dir)\n"
    ) % repr(notebook_dir)
    notebook.cells.insert(0, nbformat.v4.new_code_cell(cell_cwd))

    idx = 1
    if banque:
        notebook.cells.insert(idx, nbformat.v4.new_code_cell("banque_selectionnee = %s\n" % repr(banque)))
        idx += 1
    if annee is not None:
        notebook.cells.insert(idx, nbformat.v4.new_code_cell("annee_rapport = %s\n" % int(annee)))

    executor = ExecutePreprocessor(timeout=-1)
    executor.preprocess(notebook)

    _clean_notebook_outputs(notebook)

    html_exporter = HTMLExporter(template_name="classic", exclude_input=True)
    resources = {"embed_widgets": True}
    body, _ = html_exporter.from_notebook_node(notebook, resources=resources)

    body = add_toc(body)
    body = _clean_html_technical_output(body)

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    body_tag = soup.find("body")
    if body_tag:
        inner = "".join(str(c) for c in body_tag.children)
    else:
        inner = body

    # Remplacer les variables techniques par les vraies valeurs (nom de banque, année)
    banque_affichage = banque if banque else "Secteur"
    inner = inner.replace("{banque_rapport}", banque_affichage)
    if annee is not None:
        inner = inner.replace("{annee_cible}", str(annee))

    # Mettre en couleur la ligne de la banque concernée dans les tableaux (ex. tableau comparatif détaillé)
    inner = _highlight_banque_in_tables(inner, banque)

    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    title = f"Rapport de positionnement bancaire — {banque}" if banque else "Rapport de positionnement bancaire — Secteur"
    header = REPORT_HTML_HEADER.format(title=title, date=date_str)
    footer = REPORT_HTML_FOOTER.format(date=date_str)

    return header + inner + footer
