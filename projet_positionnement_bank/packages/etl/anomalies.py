# -*- coding: utf-8 -*-
"""
Détection des anomalies sur les données brutes (après harmonisation des colonnes).
Utilisé dans transform avant nettoyage et imputation.
"""
import pandas as pd


def detect_anomalies(df):
    """
    Détecte les anomalies sur le DataFrame (colonnes sigle, annee, bilan attendues).

    Retourne un dict avec:
    - duplicates: nombre de paires (sigle, annee) en double, et exemples
    - missing: {colonne: nombre} pour les colonnes avec manquants
    - invalid_sigle: nombre de lignes sans sigle valide
    - invalid_annee: nombre de lignes sans année valide (ou hors plage 1990-2030)
    - invalid_bilan: nombre de lignes avec bilan manquant ou <= 0 (si colonne présente)
    """
    if df is None or len(df) == 0:
        return {}

    out = {}
    # Doublons (sigle, annee)
    if "sigle" in df.columns and "annee" in df.columns:
        dup = df.duplicated(subset=["sigle", "annee"], keep=False)
        n_dup = dup.sum()
        n_pairs = df.duplicated(subset=["sigle", "annee"]).sum()
        out["duplicates"] = {
            "lignes_concernees": int(n_dup),
            "paires_en_double": int(n_pairs),
            "exemples": (
                df.loc[dup, ["sigle", "annee"]].drop_duplicates().head(5).to_dict("records")
                if n_dup > 0 else []
            ),
        }
    # Manquants par colonne
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        out["missing"] = missing.astype(int).to_dict()
    # Sigle invalide (vide ou NaN)
    if "sigle" in df.columns:
        inv_sigle = (df["sigle"].isna()) | (df["sigle"].astype(str).str.strip() == "")
        out["invalid_sigle"] = int(inv_sigle.sum())
    # Année invalide (NaN ou hors plage)
    if "annee" in df.columns:
        annee_num = pd.to_numeric(df["annee"], errors="coerce")
        inv_annee = annee_num.isna() | (annee_num < 1990) | (annee_num > 2030)
        out["invalid_annee"] = int(inv_annee.sum())
    # Bilan invalide (manquant, <= 0 ou aberrant > 1e15, ex. erreurs PDF)
    if "bilan" in df.columns:
        bilan_num = pd.to_numeric(df["bilan"], errors="coerce")
        out["invalid_bilan"] = int((bilan_num.isna() | (bilan_num <= 0)).sum())
        out["bilan_aberrant"] = int((bilan_num.gt(1e15)).sum())
    return out


def get_numeric_columns_for_quality(df):
    """Liste des colonnes numériques utilisables pour outliers/boxplots."""
    if df is None or len(df) == 0:
        return []
    cols = []
    for col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() > 0:
            cols.append(col)
    return cols


def select_best_boxplot_columns(df, n=4, exclude=None, min_non_null_ratio=0.4, min_unique=6):
    """
    Sélectionne automatiquement les meilleures colonnes pour boxplots.

    Critères:
    - numérique
    - taux de non-null suffisant
    - variabilité (nombre de valeurs uniques + dispersion IQR)
    """
    if df is None or len(df) == 0:
        return []

    excluded = {"annee", "ANNEE"}
    if exclude:
        excluded.update(set(exclude))

    candidates = []
    total = len(df)
    for col in df.columns:
        if col in excluded:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        non_null = int(s.notna().sum())
        if non_null == 0:
            continue
        ratio = non_null / total if total else 0
        if ratio < min_non_null_ratio:
            continue

        s_non_null = s.dropna()
        uniq = int(s_non_null.nunique())
        if uniq < min_unique:
            continue

        q1 = s_non_null.quantile(0.25)
        q3 = s_non_null.quantile(0.75)
        iqr = float(q3 - q1)
        # Score: privilégie données présentes + variabilité robuste
        score = (ratio * 100.0) + min(uniq, 50) + min(iqr if iqr > 0 else 0, 1e7) / 1e6
        candidates.append((score, col))

    candidates.sort(reverse=True)
    return [c for _, c in candidates[:n]]


def detect_iqr_outliers(df, columns=None):
    """
    Détecte les outliers via IQR (1.5 * IQR).
    Retour: {col: {"outliers": n, "lower": x, "upper": y}}
    """
    if df is None or len(df) == 0:
        return {}
    if columns is None:
        columns = get_numeric_columns_for_quality(df)

    out = {}
    for col in columns:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_out = int(((s < lower) | (s > upper)).sum())
        out[col] = {"outliers": n_out, "lower": float(lower), "upper": float(upper)}
    return out


def quality_report(df, boxplot_columns=None):
    """Rapport consolidé anomalies + outliers (pour le notebook ETL)."""
    return {
        "anomalies": detect_anomalies(df),
        "outliers_iqr": detect_iqr_outliers(df, columns=boxplot_columns),
    }


def plot_boxplots(df, columns=None, max_cols=6):
    """
    Trace des boxplots (retourne fig, axes, columns_plot).
    """
    if df is None or len(df) == 0:
        return None, None, []

    if columns is None:
        columns = get_numeric_columns_for_quality(df)
    columns = [c for c in columns if c in df.columns][:max_cols]
    if not columns:
        return None, None, []

    import matplotlib.pyplot as plt

    n = len(columns)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, columns):
        s = pd.to_numeric(df[col], errors="coerce")
        ax.boxplot(s.dropna())
        ax.set_title(col)
        ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig, axes, columns
