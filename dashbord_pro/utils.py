"""
Utilitaires pour le traitement des données hospitalières.
Données : MongoDB Atlas (flash_dash.hospital) ou CSV en secours.
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
try:
    import config_mongo as _cfg
except ImportError:
    _cfg = None

def format_number(value, currency=False, decimals=1):
    """
    Formate un nombre avec des suffixes K, M, etc.
    Exemples: 2500 -> "2,5K", 2500000 -> "2,5M"
    
    Args:
        value: Le nombre à formater
        currency: Si True, ajoute le symbole €
        decimals: Nombre de décimales (défaut: 1)
    
    Returns:
        String formatée (ex: "2,5M €")
    """
    if pd.isna(value) or value == 0:
        return "0 €" if currency else "0"
    
    value = float(value)
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:  # Milliards
        formatted = f"{sign}{abs_value / 1_000_000_000:.{decimals}f}".replace('.', ',')
        suffix = "Md"
    elif abs_value >= 1_000_000:  # Millions
        formatted = f"{sign}{abs_value / 1_000_000:.{decimals}f}".replace('.', ',')
        suffix = "M"
    elif abs_value >= 1_000:  # Milliers
        formatted = f"{sign}{abs_value / 1_000:.{decimals}f}".replace('.', ',')
        suffix = "K"
    else:
        formatted = f"{sign}{abs_value:.{decimals}f}".replace('.', ',')
        suffix = ""
    
    result = f"{formatted}{suffix}"
    if currency:
        result += " €"
    
    return result

def load_data():
    """Charge les données hospitalières (Atlas ou CSV)."""
    df = None
    if _cfg and getattr(_cfg, "MONGO_URI", "").strip() and "mongodb+srv" in getattr(_cfg, "MONGO_URI", ""):
        try:
            from pymongo import MongoClient
            client = MongoClient(_cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
            coll = client[_cfg.FLASH_DASH_DB][_cfg.HOSPITAL_COLLECTION]
            docs = list(coll.find({}))
            client.close()
            if docs:
                for d in docs:
                    d.pop("_id", None)
                df = pd.DataFrame(docs)
        except Exception:
            pass
    if df is None or len(df) == 0:
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'hospital_data (1).csv')
        df = pd.read_csv(data_path, sep=';', encoding='utf-8')

    # Conversion des dates
    df['DateAdmission'] = pd.to_datetime(df['DateAdmission'], format='%d/%m/%Y', errors='coerce')
    df['DateSortie'] = pd.to_datetime(df['DateSortie'], format='%d/%m/%Y', errors='coerce')

    # Calcul du coût par jour
    df['CoutParJour'] = df['Cout'] / df['DureeSejour']

    # Identification des patients à risque (séjour long + coût élevé)
    seuil_duree = df['DureeSejour'].quantile(0.75)
    seuil_cout = df['Cout'].quantile(0.75)
    df['PatientRisque'] = (df['DureeSejour'] > seuil_duree) & (df['Cout'] > seuil_cout)

    # Catégorisation par âge
    df['GroupeAge'] = pd.cut(df['Age'],
                            bins=[0, 18, 35, 50, 65, 100],
                            labels=['Enfant', 'Jeune', 'Adulte', 'Senior', 'Aîné'])

    return df

def calculate_kpis(df):
    """Calcule les indicateurs clés"""
    kpis = {
        'duree_moyenne': df['DureeSejour'].mean(),
        'cout_moyen_patient': df['Cout'].mean(),
        'cout_par_jour': df['CoutParJour'].mean(),
        'total_patients': len(df),
        'patients_risque': df['PatientRisque'].sum(),
        'taux_risque': (df['PatientRisque'].sum() / len(df)) * 100
    }
    return kpis

def get_department_stats(df):
    """Statistiques par département"""
    stats = df.groupby('Departement').agg({
        'Cout': ['sum', 'mean'],
        'DureeSejour': ['mean', 'sum'],
        'PatientID': 'count'
    }).round(2)
    stats.columns = ['CoutTotal', 'CoutMoyen', 'DureeMoyenne', 'DureeTotale', 'NbPatients']
    stats['CoutParJour'] = (stats['CoutTotal'] / stats['DureeTotale']).round(2)
    return stats.reset_index()

def get_pathology_stats(df):
    """Statistiques par pathologie"""
    stats = df.groupby('Maladie').agg({
        'Cout': ['sum', 'mean'],
        'DureeSejour': ['mean', 'sum'],
        'PatientID': 'count'
    }).round(2)
    stats.columns = ['CoutTotal', 'CoutMoyen', 'DureeMoyenne', 'DureeTotale', 'NbPatients']
    stats['CoutParJour'] = (stats['CoutTotal'] / stats['DureeTotale']).round(2)
    return stats.reset_index()

def get_treatment_stats(df):
    """Statistiques par traitement"""
    stats = df.groupby('Traitement').agg({
        'Cout': ['sum', 'mean'],
        'DureeSejour': ['mean'],
        'PatientID': 'count'
    }).round(2)
    stats.columns = ['CoutTotal', 'CoutMoyen', 'DureeMoyenne', 'NbPatients']
    stats['Efficacite'] = (1 / (stats['CoutMoyen'] * stats['DureeMoyenne'] / 1000)).round(4)
    return stats.reset_index()

def get_age_sex_stats(df):
    """Statistiques par âge et sexe"""
    stats = df.groupby(['GroupeAge', 'Sexe']).agg({
        'Cout': 'mean',
        'DureeSejour': 'mean',
        'PatientID': 'count'
    }).round(2)
    stats.columns = ['CoutMoyen', 'DureeMoyenne', 'NbPatients']
    return stats.reset_index()

def get_risk_patients(df, limit=20):
    """Retourne les patients à risque"""
    risk_df = df[df['PatientRisque'] == True].copy()
    risk_df = risk_df.sort_values(['DureeSejour', 'Cout'], ascending=[False, False])
    return risk_df.head(limit)[['PatientID', 'Age', 'Sexe', 'Departement', 'Maladie', 
                                 'DureeSejour', 'Cout', 'CoutParJour', 'Traitement']]

def filter_data(df, departement=None, maladie=None, traitement=None, sexe=None, age_min=None, age_max=None):
    """Filtre les données selon les critères"""
    filtered_df = df.copy()
    
    if departement and len(departement) > 0:
        filtered_df = filtered_df[filtered_df['Departement'].isin(departement)]
    if maladie and len(maladie) > 0:
        filtered_df = filtered_df[filtered_df['Maladie'].isin(maladie)]
    if traitement and len(traitement) > 0:
        filtered_df = filtered_df[filtered_df['Traitement'].isin(traitement)]
    if sexe and len(sexe) > 0:
        filtered_df = filtered_df[filtered_df['Sexe'].isin(sexe)]
    if age_min is not None:
        filtered_df = filtered_df[filtered_df['Age'] >= age_min]
    if age_max is not None:
        filtered_df = filtered_df[filtered_df['Age'] <= age_max]
    
    return filtered_df
