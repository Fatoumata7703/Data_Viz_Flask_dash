# -*- coding: utf-8 -*-
"""
Transform : nettoyage et normalisation des données pour la base prod.

Sources en entrée (collection banque) :
- Excel BASE_SENEGAL : colonnes complètes (sigle, annee, bilan, groupe_bancaire,
  emploi, ressources, fonds_propre, effectif, …). source=excel.
- PDF BCEAO : souvent sigle, annee, bilan, groupe_bancaire, source=bceao_pdf.
  Autres colonnes absentes → NaN. Bilan peut être aberrant (erreur d’extraction).

Règles :
- Harmonisation des noms de colonnes (Excel/PDF) vers noms canoniques.
- Lignes sans sigle ou sans année → supprimées.
- Bilan aberrant (≤ 0 ou > 1e15) → mis à NaN puis imputation par sigle si possible.
- Doublons (sigle, annee) : suppression en priorité source=excel.
- Manquants : categoriales = mode ; numeriques = mean ou median selon distribution
  (asymetrie/outliers), puis imputation par sigle.
- Rapport optionnel : anomalies + manquants/imputés par colonne.
"""
import pandas as pd

from .anomalies import detect_anomalies

# Colonnes numériques à traiter pour les manquants (noms normalisés, minuscules)
# On matche par mot-clé dans le nom de la colonne après normalisation
NUMERIC_KEYWORDS = [
    "bilan",
    "emploi",
    "ressources",
    "fonds_propre", "fonds propre",
    "effectif",
    "agence",
    "compte",
    "interet", "interets",
    "commission",
    "resultat",
    "produit", "charge",
    "capital", "reserve",
]


def _normalize_column_name(c):
    """Une seule forme normalisée pour les noms de colonnes (minuscules, _)."""
    s = str(c).strip().lower().replace(" ", "_").replace(".", "_")
    # Réduire les séquences de _ et supprimer accents courants
    while "__" in s:
        s = s.replace("__", "_")
    return s


def _is_numeric_key_column(col_name):
    """True si la colonne est une métrique numérique à gérer (bilan, fonds propres, etc.)."""
    n = _normalize_column_name(col_name)
    for kw in NUMERIC_KEYWORDS:
        if kw.replace(" ", "_") in n or kw in n:
            return True
    return False


def _harmonize_columns(df):
    """Harmonise les noms de colonnes (sigle, annee, bilan, groupe_bancaire + autres)."""
    col_map = {}
    for c in df.columns:
        n = _normalize_column_name(c)
        if "sigle" in n:
            col_map[c] = "sigle"
        elif "annee" in n or "année" in n:
            col_map[c] = "annee"
        elif "bilan" in n:
            col_map[c] = "bilan"
        elif "goupe" in n or "groupe" in n:
            col_map[c] = "groupe_bancaire"
        elif "emploi" in n and "effectif" not in n:
            col_map[c] = "emploi"
        elif "ressources" in n:
            col_map[c] = "ressources"
        elif "fonds" in n and "propre" in n:
            col_map[c] = "fonds_propres"
        elif "effectif" in n:
            col_map[c] = "effectif"
        elif "agence" in n:
            col_map[c] = "agence"
        elif "compte" in n and "commis" not in n:
            col_map[c] = "compte"
        elif "interet" in n and "produit" in n:
            col_map[c] = "interets_produits"
        elif "interet" in n and "charge" in n:
            col_map[c] = "interets_charges"
        elif "commission" in n and "produit" in n:
            col_map[c] = "commissions_produits"
        elif "commission" in n and "charge" in n:
            col_map[c] = "commissions_charges"
        elif "resultat" in n and "net" in n:
            col_map[c] = "resultat_net"
        elif "resultat" in n and "brut" in n:
            col_map[c] = "resultat_brut"
    df = df.rename(columns={k: v for k, v in col_map.items() if k != v})
    return df


def _impute_numeric_by_sigle(df, col):
    """Compat: imputation numerique par mediane (ancienne logique)."""
    return _impute_numeric_by_sigle_with_method(df, col, method="median")


def _choose_numeric_method(series):
    """
    Choisit mean ou median selon la distribution:
    - median si asymetrie forte ou outliers marques
    - mean sinon
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 8:
        return "median"

    skew = abs(float(s.skew())) if pd.notna(s.skew()) else 0.0
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if iqr <= 0:
        return "mean"

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_ratio = float(((s < lower) | (s > upper)).mean())
    if skew > 1.0 or outlier_ratio > 0.05:
        return "median"
    return "mean"


def _impute_numeric_by_sigle_with_method(df, col, method):
    """Imputation numerique par sigle avec methode mean/median + fallback global."""
    if col not in df.columns:
        return
    if not pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if int(df[col].isna().sum()) == 0:
        return

    agg = "median" if method == "median" else "mean"
    by_sigle = df.groupby("sigle")[col].transform(agg)
    df[col] = df[col].fillna(by_sigle)

    if df[col].isna().any():
        global_value = df[col].median() if method == "median" else df[col].mean()
        if pd.notna(global_value):
            df[col] = df[col].fillna(global_value)


def _impute_categorical_by_mode(df, col):
    """Imputation categorielle: mode par sigle puis mode global."""
    if col not in df.columns or pd.api.types.is_numeric_dtype(df[col]):
        return
    if int(df[col].isna().sum()) == 0:
        return

    by_sigle_mode = df.groupby("sigle")[col].transform(
        lambda x: x.dropna().mode().iloc[0] if x.notna().any() else None
    )
    df[col] = df[col].fillna(by_sigle_mode)

    if df[col].isna().any():
        mode_global = df[col].dropna().mode()
        if len(mode_global) > 0:
            df[col] = df[col].fillna(mode_global.iloc[0])


def transform_clean(df, return_report=False):
    """
    Nettoie le DataFrame brut (dev) pour une base prod propre.

    - Supprime les lignes sans sigle ou sans année.
    - Harmonise les colonnes (sigle, annee, bilan, groupe_bancaire, emploi, ressources,
      fonds_propres, effectif, agence, compte, intérêts, commissions, résultats...).
    - Déduplique (sigle, annee) en gardant priorité à source=excel.
    - Complète les colonnes categorielles manquantes : mode par sigle (fallback global).
    - Complète les colonnes numériques manquantes : mean/median par sigle selon distribution.

    Si return_report=True, retourne (df_clean, report) où report est un dict avec
    les comptages de manquants par colonne (avant / après imputation).
    """
    if df is None or len(df) == 0:
        return (None, {}) if return_report else None

    df = df.copy()

    # 1) Harmoniser tous les noms de colonnes
    df = _harmonize_columns(df)

    if "sigle" not in df.columns or "annee" not in df.columns:
        return (None, {}) if return_report else None

    # 2) Détection des anomalies (avant suppression)
    report = {} if return_report else None
    if return_report:
        report["anomalies"] = detect_anomalies(df)

    # 3) Supprimer lignes sans sigle ou sans année
    df = df[df["sigle"].notna() & (df["sigle"].astype(str).str.strip() != "")]
    df = df[df["annee"].notna()]

    # 4) Année en int
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    df = df[df["annee"].notna()]

    # 5) Bilan et autres numériques en numérique (colonnes présentes uniquement)
    if "bilan" in df.columns:
        df["bilan"] = pd.to_numeric(df["bilan"], errors="coerce")
        # Bilans aberrants (ex. erreurs d'extraction PDF 1e+43) → NaN pour imputation
        BILAN_MIN, BILAN_MAX = 1.0, 1e15
        mask_bad = (df["bilan"].lt(BILAN_MIN)) | (df["bilan"].gt(BILAN_MAX))
        df.loc[mask_bad, "bilan"] = float("nan")
    for c in list(df.columns):
        if c in ("sigle", "annee", "source") or "groupe" in c:
            continue
        if _is_numeric_key_column(c) or (df[c].dtype == object and df[c].astype(str).str.match(r"^-?[\d\s,\.]+$").any()):
            try:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            except Exception:
                pass

    # 6) Normaliser sigle
    df["sigle"] = df["sigle"].astype(str).str.strip()

    # 7) Dedoublonnage d'abord (sigle, annee) : priorite excel
    n_before_dedup = len(df)
    if "source" in df.columns:
        df["_order"] = df["source"].map({"excel": 0, "bceao_pdf": 1}).fillna(2)
        df = df.sort_values("_order").drop_duplicates(subset=["sigle", "annee"], keep="first")
        df = df.drop(columns=["_order"])
    else:
        df = df.drop_duplicates(subset=["sigle", "annee"], keep="first")
    if return_report:
        report["dedup"] = {
            "before": int(n_before_dedup),
            "after": int(len(df)),
            "removed": int(n_before_dedup - len(df)),
        }

    # 8) Rapport des manquants (avant imputation) — colonnes présentes uniquement
    if return_report:
        for c in df.columns:
            if c in ("sigle", "annee", "source"):
                continue
            n = df[c].isna().sum()
            if n > 0:
                report[c] = {"missing_before": int(n), "imputed": 0, "method": None}

    # 9) Imputation categorielle: mode (par sigle, fallback global)
    for c in list(df.columns):
        if c in ("sigle", "annee", "source"):
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            continue
        before = int(df[c].isna().sum())
        if before == 0:
            continue
        _impute_categorical_by_mode(df, c)
        after = int(df[c].isna().sum())
        if return_report:
            if c in report:
                report[c]["imputed"] = int(before - after)
                report[c]["method"] = "mode"
            else:
                report[c] = {"missing_before": int(before), "imputed": int(before - after), "method": "mode"}

    # 10) Imputation numerique: choix mean/median selon distribution
    for c in list(df.columns):
        if c in ("sigle", "annee", "source") or "groupe" in c:
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            continue
        before = int(df[c].isna().sum())
        if before == 0:
            continue
        method = _choose_numeric_method(df[c])
        _impute_numeric_by_sigle_with_method(df, c, method=method)
        after = int(df[c].isna().sum())
        if return_report:
            if c in report:
                report[c]["imputed"] = int(before - after)
                report[c]["method"] = method
            else:
                report[c] = {"missing_before": int(before), "imputed": int(before - after), "method": method}

    # 11) Renommage pour prod / dashboard (Sigle, ANNEE, BILAN, Goupe_Bancaire)
    rename_prod = {
        "sigle": "Sigle",
        "annee": "ANNEE",
        "bilan": "BILAN",
        "groupe_bancaire": "Goupe_Bancaire",
    }
    for old, new in rename_prod.items():
        if old in df.columns:
            df = df.rename(columns={old: new})

    if return_report:
        return df, report
    return df
