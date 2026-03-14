# -*- coding: utf-8 -*-
"""
Extraction des données des PDF BCEAO et chargement dans MongoDB (collection banque).

BASE_SENEGAL (Excel) est déjà en base (données jusqu’à 2020). Ce script n’insère
que les documents issus des PDF. On utilise 3 PDF : 2022, 2023 et 2024 (bilan_umoa_2022.pdf, etc.) avec les mêmes 31 colonnes normalisées que l’Excel : sigle, groupe_bancaire, annee, emploi, bilan, ressources,
fonds_propre, effectif, agence, compte, ... resultat_net, source.

- Les noms de colonnes sont exactement ceux de BASE_SENEGAL (lu depuis l’Excel
  ou liste fallback), plus source = "bceao_pdf".
- Chaque document PDF a donc 31 clés ; les valeurs non présentes dans le PDF
  restent à None.
- On remplace uniquement les documents bceao_pdf pour l’année traitée (Excel inchangé).

Usage: python -m scripts.extract_pdf_to_mongo [--verbose] [--force] [--sanitize] [--no-ocr]
  Par défaut : extraction par OCR (Tesseract). Utilisez --no-ocr pour pdfplumber uniquement.
  --force   : ré-extraire même si l'année est déjà en base (supprime puis ré-insère).
  --sanitize : à l'insertion, mettre à None les valeurs <=0 ou >1e15.
  --no-ocr  : ne pas utiliser l'OCR, extraire avec pdfplumber uniquement.
"""
import os
import re
import sys
import unicodedata

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv
FORCE_REEXTRACT = "--force" in sys.argv
# Par défaut : garder les valeurs brutes du PDF ; nettoyage dans l'ETL.
SANITIZE_VALUES = "--sanitize" in sys.argv
# Par défaut : OCR (Tesseract). --no-ocr pour utiliser uniquement pdfplumber.
USE_OCR = "--no-ocr" not in sys.argv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pymongo import MongoClient
from config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_BANQUES,
    PDF_DOWNLOAD_DIR,
    EXCEL_FILE,
)

# Sigles Sénégal (alignés sur BASE_SENEGAL2.xlsx)
SIGLES_SENEGAL = [
    "BAS", "BCIM", "BDK", "BGFI", "BICIS", "BIS", "BNDE", "BOA", "BSIC",
    "CBAO", "CDS", "CISA", "CITIBANK", "LBA", "CBI", "ECOBANK", "FBNBANK",
    "NSIA Banque", "ORABANK", "SGBS", "UBA", "LBO", "BRM", "BHS",
]

# Mapping libellés PDF / titre page -> Sigle (Sénégal)
MAP_NOM_TO_SIGLE = {
    "société générale": "SGBS",
    "societe generale": "SGBS",
    "sgbs": "SGBS",
    "bicis": "BICIS",
    "banque internationale pour le commerce": "BICIS",
    "cbao": "CBAO",
    "compagnie bancaire": "CBAO",
    "attijariwafa": "CBAO",
    "crédit du sénégal": "CDS",
    "credit du senegal": "CDS",
    "banque de l'habitat": "BHS",
    "bhs": "BHS",
    "citibank": "CITIBANK",
    "citi": "CITIBANK",
    "banque agricole": "LBA",
    "lba": "LBA",
    "cncas": "LBA",
    "banque islamique": "BIS",
    "bis": "BIS",
    "ecobank": "ECOBANK",
    "orabank": "ORABANK",
    "bank of africa": "BOA",
    "boa": "BOA",
    "bsic": "BSIC",
    "sahélo-saharienne": "BSIC",
    "sabelo-saharienne": "BSIC",
    "bimao": "BIMAO",  # hors liste Excel, on peut ignorer ou ajouter
    "banque atlantique": "BAS",
    "atlantique": "BAS",
    "bas": "BAS",
    "brm": "BRM",
    "régionale des marchés": "BRM",
    "uba": "UBA",
    "united bank": "UBA",
    "fbnbank": "FBNBANK",
    "fbn": "FBNBANK",
    "crédit international": "CISA",
    "credit international": "CISA",
    "cis": "CISA",
    "cisa": "CISA",
    "bnde": "BNDE",
    "nationale pour le développement": "BNDE",
    "nsia": "NSIA Banque",
    "bdk": "BDK",
    "dakar": "BDK",
    "banque de dakar": "BDK",
    "bgfi": "BGFI",
    "bci-mali": "CBI",
    "commerce et industrie": "CBI",
    "cbi": "CBI",
    "lbo": "LBO",
    "outarde": "LBO",
    "coris": "CBI",
    "coris bank": "CBI",
    "bridge bank": "CBI",
}


def get_base_senegal_columns():
    """
    Retourne les 30 colonnes de BASE_SENEGAL (Excel). Seules 4 sont renommees dans la boucle ci-dessous
    qu’en base (sigle, annee, bilan, groupe_bancaire) ; les 26 autres gardent leur nom.
    """
    if not os.path.isfile(EXCEL_FILE):
        return _BASE_SENEGAL_COLUMNS_FALLBACK
    df = pd.read_excel(EXCEL_FILE, nrows=0)
    cols = [str(c).strip().replace(" ", "_").replace(".", "_").lower() for c in df.columns]
    col_map = {}
    for c in cols:
        if "sigle" in c:
            col_map[c] = "sigle"
        elif "annee" in c or "année" in c:
            col_map[c] = "annee"
        elif "bilan" in c:
            col_map[c] = "bilan"
        elif "goupe" in c or "groupe" in c:
            col_map[c] = "groupe_bancaire"
        else:
            col_map[c] = c  # les 26 autres colonnes (emploi, ressources, ...) inchangées
    return [col_map.get(c, c) for c in cols]  # 30 colonnes au total


# Fallback si Excel absent : colonnes BASE_SENEGAL (mêmes noms qu’en base)
_BASE_SENEGAL_COLUMNS_FALLBACK = [
    "sigle", "groupe_bancaire", "annee", "emploi", "bilan", "ressources",
    "fonds_propre", "effectif", "agence", "compte",
    "interets_et_produits_assimiles", "interets_et_charges_assimilees",
    "revenus_des_titres_a_revenu_variable", "commissions_(produits)", "commissions_(charges)",
    "gains_ou_pertes_nets_sur_operations_des_portefeuilles_de_negociation",
    "gains_ou_pertes_nets_sur_operations_des_portefeuilles_de_placement_et_assimiles",
    "autres_produits_d_exploitation_bancaire", "autres_charges_d_exploitation_bancaire",
    "produit_net_bancaire", "subventions_d_investissement", "charges_generales_d_exploitation",
    "dotations_aux_amortissements_et_aux_depreciations_des_immobilisations_incorporelles_et_corporelles",
    "resultat_brut_d_exploitation", "cout_du_risque", "resultat_d_exploitation",
    "gains_ou_pertes_nets_sur_actifs_immobilises", "resultat_avant_impot",
    "impots_sur_les_benefices", "resultat_net",
]


def _normalize_label(s):
    """Normalise un libellé pour le matching (minuscule, sans accents)."""
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[\s'_]+", " ", s)
    return s


# Mapping : (mots-clés dans le libellé PDF, nom de colonne BASE_SENEGAL)
# PDF = une ligne par indicateur, colonnes 2020 / 2021 / 2022. Total actif = total passif = bilan.
# Aligné sur les KPI du projet : Bilan, Emploi, Ressources, Fonds propres, Comptes de résultat.
PDF_ROW_LABEL_TO_COLUMN = [
    (["total", "actif"], "bilan"),
    (["total", "passif"], "bilan"),  # même montant que total actif
    (["emploi"], "emploi"),
    (["creances", "sur", "la", "clientele"], "emploi"),  # Créances sur la clientèle (PDF BCEAO)
    (["creances", "clientele"], "emploi"),
    (["creances", "client"], "emploi"),
    (["placements", "clientele"], "emploi"),
    (["ressources"], "ressources"),
    (["dettes", "egard", "clientele"], "ressources"),  # Dettes à l'égard de la clientèle
    (["dettes", "l'egard", "clientele"], "ressources"),
    (["dettes", "clientele"], "ressources"),
    (["dettes", "client"], "ressources"),
    (["depots", "clientele"], "ressources"),
    (["fonds", "propre"], "fonds_propre"),
    (["capitaux", "propres"], "fonds_propre"),  # Capitaux propres et ressources assimilées
    (["capitaux", "propres", "ressources", "assimilees"], "fonds_propre"),
    (["effectif"], "effectif"),
    (["agence"], "agence"),
    (["compte"], "compte"),
    (["interet", "produit"], "interets_et_produits_assimiles"),
    (["interet", "charge"], "interets_et_charges_assimilees"),
    (["revenus", "titres"], "revenus_des_titres_a_revenu_variable"),
    (["commission", "produit"], "commissions_(produits)"),
    (["commission", "charge"], "commissions_(charges)"),
    (["gains", "pertes", "negociation"], "gains_ou_pertes_nets_sur_operations_des_portefeuilles_de_negociation"),
    (["gains", "pertes", "placement"], "gains_ou_pertes_nets_sur_operations_des_portefeuilles_de_placement_et_assimiles"),
    (["autres", "produits", "exploitation"], "autres_produits_d_exploitation_bancaire"),
    (["autres", "charges", "exploitation"], "autres_charges_d_exploitation_bancaire"),
    (["produit", "net", "bancaire"], "produit_net_bancaire"),
    (["subvention"], "subventions_d_investissement"),
    (["charges", "generales", "exploitation"], "charges_generales_d_exploitation"),
    (["dotations", "amortissement"], "dotations_aux_amortissements_et_aux_depreciations_des_immobilisations_incorporelles_et_corporelles"),
    (["resultat", "brut", "exploitation"], "resultat_brut_d_exploitation"),
    (["cout", "risque"], "cout_du_risque"),
    (["coût", "risque"], "cout_du_risque"),
    (["resultat", "exploitation"], "resultat_d_exploitation"),
    (["gains", "pertes", "actifs", "immobilise"], "gains_ou_pertes_nets_sur_actifs_immobilises"),
    (["resultat", "avant", "impot"], "resultat_avant_impot"),
    (["impot", "benefice"], "impots_sur_les_benefices"),
    (["resultat", "net"], "resultat_net"),
    (["resultat", "exercice"], "resultat_net"),  # Résultat de l'exercice (PDF BCEAO)
]


def extract_tables_from_pdf(pdf_path):
    """Extrait les tableaux de chaque page du PDF (pdfplumber)."""
    try:
        import pdfplumber
    except ImportError:
        print("Installer pdfplumber: pip install pdfplumber")
        return []
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            out.append({"page_num": i + 1, "text": text, "tables": tables})
    return out


def _ensure_ocr_site_packages():
    """Ajoute le site-packages du .venv du projet ou du parent (s'il existe) pour trouver pymupdf/pytesseract."""
    if getattr(_ensure_ocr_site_packages, "_done", False):
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    parent_root = os.path.dirname(project_root)
    candidates = []
    for root in (project_root, parent_root):
        for subdir in ("Lib", "lib"):
            venv_site = os.path.join(root, ".venv", subdir, "site-packages")
            if os.path.isdir(venv_site):
                candidates.append(venv_site)
    for venv_site in candidates:
        if venv_site not in sys.path:
            sys.path.insert(0, venv_site)
    _ensure_ocr_site_packages._done = True


def _pdf_pages_to_images(pdf_path, dpi=200):
    """Convertit chaque page du PDF en image (PIL) pour l'OCR. Utilise pdf2image ou PyMuPDF."""
    _ensure_ocr_site_packages()
    # 1) pdf2image (nécessite poppler sur le système)
    try:
        from pdf2image import convert_from_path  # type: ignore[import-untyped]
        return convert_from_path(pdf_path, dpi=dpi)
    except ImportError:
        pass
    # 2) PyMuPDF (peut échouer avec "DLL load failed" sur certains Windows)
    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF
        from PIL import Image
        doc = fitz.open(pdf_path)
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        return images
    except Exception:
        pass
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    raise ImportError(
        "OCR : installer pdf2image+Pillow (et poppler) ou pymupdf+Pillow dans le venv utilisé.\n"
        "  pip install pdf2image Pillow   OU   pip install pymupdf Pillow\n"
        "Puis : python -m scripts.extract_pdf_to_mongo --ocr\n"
        "Projet : %s" % project_root
    )


def _get_tesseract_cmd():
    """Retourne le chemin de tesseract.exe. TESSERACT_CMD est utilisé tel quel si défini."""
    env_cmd = (os.environ.get("TESSERACT_CMD") or "").strip()
    if env_cmd:
        return env_cmd
    if sys.platform != "win32":
        return None
    for path in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if path and os.path.isfile(path):
            return path
    return None


def _ocr_image_to_table(image, lang="fra+eng"):
    """
    Exécute Tesseract OCR sur l'image et reconstruit un tableau (liste de lignes, chaque ligne = liste de cellules).
    Regroupe les mots par ligne (top), puis par colonne (left), pour former des cellules.
    """
    _ensure_ocr_site_packages()
    try:
        import pytesseract  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError("Pour l'OCR, installer pytesseract: pip install pytesseract (et Tesseract sur le système)")
    tesseract_cmd = _get_tesseract_cmd()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    try:
        data = pytesseract.image_to_data(image, lang=lang)
    except pytesseract.pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR n'est pas installé ou pas dans le PATH.\n"
            "1) Téléchargez et installez : https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2) Cochez 'French' si besoin, ou ajoutez le pack 'fra' dans tessdata.\n"
            "3) Soit ajoutez le dossier d'installation au PATH, soit définissez la variable d'environnement :\n"
            "   TESSERACT_CMD = C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        ) from None
    full_text = pytesseract.image_to_string(image, lang=lang)
    if not data or not data.strip():
        return [], full_text
    lines = data.strip().split("\n")
    if len(lines) < 2:
        return [], full_text
    headers = lines[0].split("\t")
    word_list = []
    for line in lines[1:]:
        parts = line.split("\t", len(headers) - 1)
        if len(parts) < len(headers):
            continue
        d = dict(zip(headers, parts))
        text = (d.get("text") or "").strip()
        if not text:
            continue
        try:
            left = int(d.get("left", 0))
            top = int(d.get("top", 0))
            width = int(d.get("width", 0))
            height = int(d.get("height", 0))
        except (ValueError, TypeError):
            continue
        word_list.append({"text": text, "left": left, "top": top, "width": width, "height": height})

    if not word_list:
        return [], full_text

    # Regrouper par ligne (top proche = même ligne)
    word_list.sort(key=lambda w: (w["top"], w["left"]))
    LINE_TOLERANCE = 8
    rows_boxes = []
    current_row = []
    current_top = None
    for w in word_list:
        if current_top is None:
            current_top = w["top"]
        if abs(w["top"] - current_top) <= LINE_TOLERANCE:
            current_row.append(w)
        else:
            if current_row:
                rows_boxes.append(current_row)
            current_row = [w]
            current_top = w["top"]
    if current_row:
        rows_boxes.append(current_row)

    # Pour chaque ligne, regrouper les mots en cellules (colonnes séparées par un gap)
    GAP_COLUMN = 25
    table = []
    for row_words in rows_boxes:
        row_words.sort(key=lambda x: x["left"])
        cells = []
        current_cell = []
        last_right = -100
        for w in row_words:
            if current_cell and (w["left"] - last_right) > GAP_COLUMN:
                cell_text = " ".join(x["text"] for x in current_cell).strip()
                if cell_text:
                    cells.append(cell_text)
                current_cell = []
            current_cell.append(w)
            last_right = w["left"] + w["width"]
        if current_cell:
            cell_text = " ".join(x["text"] for x in current_cell).strip()
            if cell_text:
                cells.append(cell_text)
        if cells:
            table.append(cells)

    return table, full_text


def extract_tables_from_pdf_ocr(pdf_path, dpi=200, lang="fra+eng"):
    """
    Extrait le contenu de chaque page du PDF par OCR (Tesseract), puis reconstruit
    des tableaux au même format que extract_tables_from_pdf (list of {page_num, text, tables}).
    """
    images = _pdf_pages_to_images(pdf_path, dpi=dpi)
    out = []
    for i, img in enumerate(images):
        table, text = _ocr_image_to_table(img, lang=lang)
        # Un seul tableau par page (toute la page OCR)
        tables = [table] if table and len(table) >= 2 else []
        out.append({"page_num": i + 1, "text": text, "tables": tables})
    return out


def find_sigle_in_text(text):
    """
    Détecte un sigle à partir du texte de la page (pays Sénégal + nom banque).
    Accepte les sigles de SIGLES_SENEGAL et aussi ceux de MAP_NOM_TO_SIGLE pour
    prendre en compte les nouvelles banques qui apparaissent dans les PDF.
    """
    if not text:
        return None
    # On ne garde que les pages Sénégal (éviter Bénin, Burkina, etc.)
    text_low = text.lower()
    if "sénégal" not in text_low and "senegal" not in text_low:
        return None
    # D'abord match par nom (MAP) : on accepte le sigle même s'il n'est pas dans SIGLES_SENEGAL (nouveaux documents)
    for nom, sigle in MAP_NOM_TO_SIGLE.items():
        if nom in text_low:
            return sigle
    # Puis match direct par sigle connu (liste Sénégal)
    for sigle in SIGLES_SENEGAL:
        if sigle.lower() in text_low or sigle.replace(" ", "").lower() in text_low.replace(" ", ""):
            return sigle
    return None


def parse_numeric(s):
    """Parse un nombre (espaces, virgule)."""
    if s is None:
        return None
    s = str(s).strip().replace("\xa0", "").replace(" ", "").replace(",", ".")
    s = re.sub(r"[^\d.\-]", "", s)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def get_annee_from_filename(path):
    """Extrait l'année du nom de fichier (ex: bilan_umoa_2022.pdf -> 2022)."""
    m = re.search(r"20\d{2}", os.path.basename(path))
    return int(m.group()) if m else None


def _resolve_to_base_column(col_name, base_columns):
    """
    Retourne la colonne de la base à utiliser. On n'écrit que dans des colonnes
    qui existent dans BASE_SENEGAL (Excel). Si le nom du mapping n'existe pas
    tel quel, on cherche la colonne Excel qui correspond (ex: interet, resultat_brut_exploi).
    """
    base_list = list(base_columns)
    if col_name in base_list:
        return col_name
    col_lower = col_name.lower().replace("'", "_").replace("(", "_").replace(")", "")
    for c in base_list:
        if c in ("sigle", "annee", "source", "groupe_bancaire"):
            continue
        if c == col_lower or col_lower == c:
            return c
        # Excel a des noms plus courts : interet, ressource, commissions, resultat_brut_exploi...
        if c in col_lower or col_lower.startswith(c + "_"):
            return c
        if col_lower.startswith(c) or (len(c) >= 4 and c in col_lower):
            return c
    return None


def _match_row_label_to_column(normalized_label, base_columns):
    """Retourne le nom de colonne BASE_SENEGAL (existant dans la base) si le libellé PDF correspond."""
    for keywords, col_name in PDF_ROW_LABEL_TO_COLUMN:
        if all(k in normalized_label for k in keywords):
            resolved = _resolve_to_base_column(col_name, base_columns)
            if resolved:
                return resolved
    return None


def _find_year_columns_in_header(header):
    """
    Repère les colonnes année (20xx). Si une cellule contient "2020 2021 2022",
    on associe les années aux colonnes consécutives (i, i+1, i+2).
    """
    out = []
    for i, h in enumerate(header):
        s = str(h).strip()
        years_in_cell = re.findall(r"20\d{2}", s)
        if not years_in_cell:
            continue
        for j, yr in enumerate(years_in_cell):
            col_idx = i + j
            out.append((col_idx, int(yr)))
    return out


def extract_full_document_from_page(page_data, base_columns, groupe_by_sigle=None, fallback_sigle=None):
    """
    Extrait les données des tableaux de la page. Les tableaux ont des colonnes 2020, 2021, 2022, etc.
    Retourne une liste de documents : un par (sigle, année) trouvé dans les en-têtes.
    Si la page n'a pas de sigle dans le texte (ex. page "Comptes de résultat" seule), utilise fallback_sigle
    (sigle de la page précédente = même banque).
    """
    sigle = find_sigle_in_text(page_data.get("text") or "") or fallback_sigle
    if not sigle:
        return []

    # Par année : un dict de colonne -> valeur (on remplira sigle, annee, source à la fin)
    year_data = {}

    for table in page_data.get("tables") or []:
        if not table or len(table) < 2:
            continue
        # L'en-tête des années (2020, 2021, 2022) peut être en ligne 0, 1 ou 2 (après "ACTIF" ou "Montant net...")
        header_row_idx = None
        year_columns = []
        for idx in range(min(3, len(table))):
            header = [str(c).strip() if c else "" for c in table[idx]]
            year_columns = _find_year_columns_in_header(header)
            if year_columns:
                header_row_idx = idx
                break
        if not year_columns or header_row_idx is None:
            continue
        for _, year in year_columns:
            if year not in year_data:
                year_data[year] = {c: None for c in base_columns}

        # Valeurs aberrantes (ex. 1e+37) = erreur de lecture. On accepte les négatifs (coût du risque, résultats).
        VALIDE_MAX = 1e15

        def _valeurs_annees_depuis_ligne(row, col_indices):
            """Extrait les valeurs (année -> nombre) depuis une ligne. Ignore les valeurs aberrantes."""
            out = {}
            for col_idx, year in col_indices:
                v = None
                if col_idx < len(row):
                    v = parse_numeric(row[col_idx])
                if v is None and len(row) >= 2:
                    v = parse_numeric(row[-1])
                if v is not None and -VALIDE_MAX <= v <= VALIDE_MAX:
                    out[year] = round(v, 2)
            return out

        data_rows = table[header_row_idx + 1 :]
        for i, row in enumerate(data_rows):
            # Libellé : première cellule, ou concaténation des 2-3 premières (PDF BCEAO souvent coupé)
            label_cell = row[0] if row else None
            if label_cell and len(row) > 1:
                # Concaténer les premières cellules non numériques pour capturer "Créances sur la clientèle", etc.
                parts = []
                for k in range(min(3, len(row))):
                    c = (row[k] or "").strip()
                    if c and parse_numeric(c) is None and not re.match(r"^-?\d[\d\s,.]*$", str(c)):
                        parts.append(c)
                if parts:
                    label_cell = " ".join(parts)
            label_norm = _normalize_label(label_cell or "")
            col_name = _match_row_label_to_column(label_norm, list(base_columns))
            if not col_name or col_name not in base_columns:
                continue
            # Valeurs sur la même ligne, puis sur les 5 lignes suivantes (PDF BCEAO : libellé puis chiffres en dessous)
            valeurs_par_annee = _valeurs_annees_depuis_ligne(row, year_columns)
            if not valeurs_par_annee and col_name:
                candidates = []
                for j in range(i + 1, min(i + 6, len(data_rows))):
                    suiv = data_rows[j]
                    vals = _valeurs_annees_depuis_ligne(suiv, year_columns)
                    if vals:
                        candidates.append(vals)
                if candidates:
                    # Pour bilan et fonds_propre : prendre la ligne avec la plus grande somme (total, pas sous-total)
                    if col_name in ("bilan", "fonds_propre") and len(candidates) > 1:
                        valeurs_par_annee = max(candidates, key=lambda v: sum(v.values()))
                    else:
                        valeurs_par_annee = candidates[0]
            for year, val in valeurs_par_annee.items():
                if year in year_data:
                    year_data[year][col_name] = val

    result = []
    for year, data in year_data.items():
        doc = dict(data)
        doc["sigle"] = sigle
        doc["annee"] = year
        doc["source"] = "bceao_pdf"
        if groupe_by_sigle and sigle in groupe_by_sigle:
            doc["groupe_bancaire"] = groupe_by_sigle[sigle]
        if SANITIZE_VALUES:
            BILAN_MAX = 1e15
            for k in list(doc):
                if k in ("sigle", "annee", "source", "groupe_bancaire"):
                    continue
                v = doc.get(k)
                if isinstance(v, (int, float)) and (v <= 0 or v > BILAN_MAX):
                    doc[k] = None
        result.append(doc)
    return result


def get_groupe_bancaire_from_mongo(coll):
    """
    Récupère sigle -> groupe_bancaire depuis les documents Excel en base
    (dernière année disponible, ex. 2020) pour compléter les docs PDF.
    """
    cursor = coll.find({"source": "excel"}, {"sigle": 1, "annee": 1, "groupe_bancaire": 1})
    by_sigle = {}
    for doc in cursor:
        s, a, g = doc.get("sigle"), doc.get("annee"), doc.get("groupe_bancaire")
        if s and g is not None:
            if s not in by_sigle or (by_sigle[s][0] or 0) < (a or 0):
                by_sigle[s] = (a, g)
    return {s: g for s, (_, g) in by_sigle.items()}


def _merge_docs_by_key(docs_list, base_columns):
    """
    Fusionne les documents qui ont le même (sigle, annee).
    Bilan peut venir d'une page (ACTIF/PASSIF), resultat_net et autres d'une autre (Comptes de résultat).
    """
    by_key = {}
    for doc in docs_list:
        key = (doc["sigle"], doc["annee"])
        if key not in by_key:
            by_key[key] = {c: None for c in base_columns}
            by_key[key]["sigle"] = doc["sigle"]
            by_key[key]["annee"] = doc["annee"]
            by_key[key]["source"] = "bceao_pdf"
            by_key[key]["groupe_bancaire"] = doc.get("groupe_bancaire")
        for k, v in doc.items():
            if k in ("sigle", "annee", "source"):
                continue
            if v is None:
                continue
            if isinstance(v, float) and v != v:  # NaN
                continue
            # Pour le bilan : garder le maximum (TOTAL ACTIF peut donner un sous-total, TOTAL PASSIF le vrai total)
            if k == "bilan" and v is not None:
                existing = by_key[key].get(k)
                if existing is None:
                    by_key[key][k] = v
                else:
                    try:
                        by_key[key][k] = max(existing, v)
                    except TypeError:
                        by_key[key][k] = v
            elif by_key[key].get(k) is None:
                by_key[key][k] = v
    return list(by_key.values())


def extract_documents_from_pdf(pdf_path, groupe_by_sigle=None, base_columns=None, use_ocr=None):
    """
    Parcourt toutes les pages du PDF. Bilan (ACTIF/PASSIF) et Comptes de résultat
    peuvent être sur des pages différentes ; on fusionne par (sigle, année).
    Si use_ocr=True, utilise l'OCR (Tesseract) pour extraire les tableaux au lieu de pdfplumber.
    """
    groupe_by_sigle = groupe_by_sigle or {}
    if base_columns is None:
        base_columns = get_base_senegal_columns()
    if "source" not in base_columns:
        base_columns = list(base_columns) + ["source"]
    if use_ocr is None:
        use_ocr = USE_OCR
    if use_ocr:
        try:
            pages = extract_tables_from_pdf_ocr(pdf_path)
        except (ImportError, RuntimeError) as e:
            if not getattr(extract_documents_from_pdf, "_ocr_fallback_printed", False):
                print("  OCR indisponible (Tesseract non installé ou pas dans le PATH).")
                print("  Retour à l'extraction pdfplumber. Pour utiliser l'OCR : https://github.com/UB-Mannheim/tesseract/wiki")
                extract_documents_from_pdf._ocr_fallback_printed = True
            else:
                print("  OCR indisponible, utilisation de pdfplumber.")
            pages = extract_tables_from_pdf(pdf_path)
    else:
        pages = extract_tables_from_pdf(pdf_path)
    if VERBOSE:
        print(f"    [verbose] {len(pages)} page(s) extraite(s) du PDF")
    all_docs = []
    last_sigle = None  # page "Comptes de résultat" peut ne pas avoir le nom de la banque → on réutilise le sigle précédent

    for p in pages:
        page_num = p.get("page_num", 0)
        page_docs = extract_full_document_from_page(
            p, base_columns, groupe_by_sigle, fallback_sigle=last_sigle
        )
        if not page_docs:
            if VERBOSE:
                text_preview = (p.get("text") or "")[:80].replace("\n", " ")
                print(f"    [verbose] page {page_num}: pas de sigle (texte: {text_preview!r}...)")
            continue
        for doc in page_docs:
            last_sigle = doc["sigle"]
            num_count = sum(
                1 for k in doc
                if k not in ("sigle", "annee", "source")
                and isinstance(doc.get(k), (int, float)) and doc.get(k) is not None
            )
            if VERBOSE:
                print(f"    [verbose] page {page_num}: sigle={doc['sigle']}, annee={doc['annee']}, {num_count} valeur(s)")
        all_docs.extend(page_docs)

    # Fusionner les docs de plusieurs pages (bilan d'une page, resultat_net/cout_risque d'une autre)
    documents = _merge_docs_by_key(all_docs, base_columns)
    return documents


def main():
    if not os.path.isdir(PDF_DOWNLOAD_DIR):
        os.makedirs(PDF_DOWNLOAD_DIR, exist_ok=True)
        print(f"Dossier créé: {PDF_DOWNLOAD_DIR}")
        print("Téléchargez d'abord les PDF depuis le site: python -m scripts.bceao_scraper")
        return

    pdf_files = [
        os.path.join(PDF_DOWNLOAD_DIR, f)
        for f in os.listdir(PDF_DOWNLOAD_DIR)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        print("Aucun fichier PDF dans le dossier. Exécuter: python -m scripts.bceao_scraper")
        return

    # Traiter les PDF dans l'ordre des années (2022, 2023, 2024)
    pdf_files = sorted(pdf_files, key=lambda p: get_annee_from_filename(p) or 0)
    annees_detectees = [get_annee_from_filename(p) for p in pdf_files if get_annee_from_filename(p)]
    print(f"PDF trouvés : {len(pdf_files)} fichier(s) -> années {annees_detectees}")
    if USE_OCR:
        print("Extraction par OCR (Tesseract), puis chargement en base.")
    else:
        print("Extraction par pdfplumber uniquement (--no-ocr).")
    if FORCE_REEXTRACT:
        print("Mode --force : ré-extraction (suppression puis insertion) pour toutes les années.")
    else:
        print("Extraction par année ; si des documents bceao_pdf existent déjà pour une année, celle-ci est ignorée.")

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    coll = db[MONGO_COLLECTION_BANQUES]

    # 31 colonnes = 30 de BASE_SENEGAL (normalisées comme l’Excel) + source
    base_columns = get_base_senegal_columns()
    n_cols = len(base_columns) + 1  # + source
    print(f"Colonnes utilisées : {n_cols} (alignées sur BASE_SENEGAL : sigle, groupe_bancaire, annee, emploi, bilan, ... resultat_net, source)")

    groupe_by_sigle = get_groupe_bancaire_from_mongo(coll)

    total = 0
    for pdf_path in pdf_files:
        print(f"Traitement: {os.path.basename(pdf_path)}")
        docs = extract_documents_from_pdf(pdf_path, groupe_by_sigle, base_columns)
        if not docs:
            print(f"  -> 0 document(s) extrait(s)")
            continue
        annees_dans_docs = sorted(set(d["annee"] for d in docs))
        # Avec OCR ou --force : supprimer les anciennes données PDF et les remplacer
        replace_pdf = FORCE_REEXTRACT or USE_OCR
        if not replace_pdf:
            years_already = set()
            for y in annees_dans_docs:
                if coll.count_documents({"source": "bceao_pdf", "annee": y}) > 0:
                    years_already.add(y)
            docs = [d for d in docs if d["annee"] not in years_already]
            if not docs:
                print(f"  -> années {annees_dans_docs} déjà présentes, extraction ignorée")
                continue
        if replace_pdf and docs:
            for annee in annees_dans_docs:
                coll.delete_many({"source": "bceao_pdf", "annee": annee})
        coll.insert_many(docs)
        total += len(docs)
        print(f"  -> {len(docs)} document(s) inséré(s) (années: {sorted(set(d['annee'] for d in docs))})")
    if total == 0:
        print("Total: 0 document(s) — aucune donnée insérée. Lancer avec --verbose pour diagnostiquer.")
    else:
        print(f"Total: {total} document(s) issus des PDF insérés dans {MONGO_DB_NAME}.{MONGO_COLLECTION_BANQUES}")


if __name__ == "__main__":
    main()
