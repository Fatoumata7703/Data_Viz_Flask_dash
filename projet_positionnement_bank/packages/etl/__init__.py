# -*- coding: utf-8 -*-
"""
ETL : Extract (bank.banque dev) -> Transform (nettoyage) -> Load (bank_prod.prod).
Base de données prod propre pour le dashboard et les rapports.
"""
from .extract import extract_from_dev
from .transform import transform_clean
from .load import load_to_prod
from .pipeline import run_etl
from .anomalies import quality_report, detect_iqr_outliers, plot_boxplots, select_best_boxplot_columns

__all__ = [
    "extract_from_dev",
    "transform_clean",
    "load_to_prod",
    "run_etl",
    "quality_report",
    "detect_iqr_outliers",
    "plot_boxplots",
    "select_best_boxplot_columns",
]
