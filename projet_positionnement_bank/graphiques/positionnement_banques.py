# -*- coding: utf-8 -*-
"""
Graphiques de positionnement par BANQUE (pas par groupe) pour le rapport :
- Scatter Part de marché vs TCAM, toutes banques, banque du rapport mise en évidence.
- Scatter positionnement par rapport aux groupes locaux (banques locales uniquement).
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Thème rapport — Slate & Cyan
COULEUR_FONCE = '#0f172a'
COULEUR_MEDIUM = '#0891b2'
COULEUR_CLAIRE = '#22d3ee'
COULEUR_CREME = '#e2e8f0'
COULEUR_TEXTE = '#0f172a'
COULEUR_BANQUE_RAPPORT = '#ef4444'
COULEUR_AUTRES = '#94a3b8'


def _compute_part_marche_tcam_by_bank(df, colonne_metrique, annee_col, banque_col, annee_debut, annee_fin):
    """Calcule part de marché (année fin) et TCAM par banque pour une métrique."""
    df = df.copy()
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    df_debut = df[df[annee_col] == annee_debut].groupby(banque_col)[colonne_metrique].sum().reset_index()
    df_fin = df[df[annee_col] == annee_fin].groupby(banque_col)[colonne_metrique].sum().reset_index()
    df_debut.columns = [banque_col, 'valeur_debut']
    df_fin.columns = [banque_col, 'valeur_fin']
    merge = pd.merge(df_debut, df_fin, on=banque_col, how='inner')
    merge = merge[(merge['valeur_debut'] > 0) & (merge['valeur_fin'] > 0)]
    if len(merge) == 0:
        return merge
    total_fin = merge['valeur_fin'].sum()
    merge['part_marche'] = (merge['valeur_fin'] / total_fin) * 100
    n = annee_fin - annee_debut or 1
    merge['tcam'] = ((merge['valeur_fin'] / merge['valeur_debut']) ** (1 / n) - 1) * 100
    return merge


def scatter_part_marche_tcam_banques(df, banque_rapport, annee_col='ANNEE', banque_col='Sigle',
                                    annee_cible=None, annee_debut=2015, annee_fin=2020,
                                    indicateurs=None, titre_global=None):
    """
    Figure 2x2 : scatter Part de marché (année cible) vs TCAM (période), une point par BANQUE.
    La banque du rapport est mise en évidence (rouge).
    """
    if indicateurs is None:
        indicateurs = [('BILAN', 'TOTAL BILAN'), ('EMPLOI', 'EMPLOIS'), ('RESSOURCES', 'RESSOURCES'), ('COMPTE', 'NOMBRE DE COMPTES')]
    if annee_cible is None:
        annee_cible = annee_fin
    annee_cible = int(annee_cible)
    annee_debut = int(annee_debut)
    annee_fin = int(annee_fin)
    banque_rapport = str(banque_rapport).strip().upper() if banque_rapport else 'BNDE'

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    fig.patch.set_facecolor('#ffffff')
    for ax in axes:
        ax.set_facecolor('#f7f9fc')

    for idx, (col_metrique, label_metrique) in enumerate(indicateurs):
        if col_metrique not in df.columns or idx >= len(axes):
            continue
        ax = axes[idx]
        df_plot = _compute_part_marche_tcam_by_bank(df, col_metrique, annee_col, banque_col, annee_debut, annee_fin)
        if len(df_plot) == 0:
            ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(label_metrique, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
            continue

        for _, row in df_plot.iterrows():
            bank = row[banque_col]
            is_rapport = str(bank).strip().upper() == banque_rapport
            color = COULEUR_BANQUE_RAPPORT if is_rapport else COULEUR_AUTRES
            size = 120 if is_rapport else 60
            z = 5 if is_rapport else 3
            ax.scatter(row['part_marche'], row['tcam'], s=size, color=color, alpha=0.9,
                       edgecolors='white', linewidth=2, zorder=z)
            label = str(bank) if is_rapport else ''
            if label:
                ax.annotate(label, (row['part_marche'], row['tcam']), xytext=(5, 5), textcoords='offset points',
                            fontsize=9, fontweight='bold', color=COULEUR_BANQUE_RAPPORT,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff', edgecolor=COULEUR_BANQUE_RAPPORT))

        ax.set_xlabel(f'Part de marché {annee_cible} (%)', fontsize=10, color=COULEUR_TEXTE)
        ax.set_ylabel(f'TCAM {annee_debut}-{annee_fin} (%)', fontsize=10, color=COULEUR_TEXTE)
        ax.set_title(label_metrique, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
        ax.grid(True, alpha=0.3, linestyle='--', color=COULEUR_CREME)
        ax.set_axisbelow(True)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color(COULEUR_CREME)
        ax.spines['bottom'].set_color(COULEUR_CREME)
        ax.tick_params(colors=COULEUR_TEXTE)

    if titre_global:
        fig.suptitle(titre_global, fontsize=14, fontweight='bold', color=COULEUR_FONCE, y=1.02)
    plt.tight_layout()
    plt.show()
    return fig, axes


def _compute_part_marche_two_years_by_bank(df, colonne_metrique, annee_col, banque_col, annee_prev, annee_cible):
    """Part de marché année N-1 et année N par banque (pour groupes locaux)."""
    df = df.copy()
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    df_prev = df[df[annee_col] == annee_prev].groupby(banque_col)[colonne_metrique].sum().reset_index()
    df_curr = df[df[annee_col] == annee_cible].groupby(banque_col)[colonne_metrique].sum().reset_index()
    df_prev.columns = [banque_col, 'valeur_prev']
    df_curr.columns = [banque_col, 'valeur_curr']
    total_prev = df_prev['valeur_prev'].sum()
    total_curr = df_curr['valeur_curr'].sum()
    if total_prev <= 0 or total_curr <= 0:
        return pd.DataFrame()
    merge = pd.merge(df_prev, df_curr, on=banque_col, how='inner')
    merge = merge[(merge['valeur_prev'] > 0) & (merge['valeur_curr'] > 0)]
    merge['part_prev'] = (merge['valeur_prev'] / total_prev) * 100
    merge['part_curr'] = (merge['valeur_curr'] / total_curr) * 100
    return merge


def scatter_positionnement_groupes_locaux(df, banque_rapport, annee_col='ANNEE', banque_col='Sigle',
                                          groupe_col='Goupe_Bancaire', annee_cible=None,
                                          indicateurs=None, titre_global=None):
    """
    Figure 2x2 : scatter Part de marché année N-1 vs Part de marché année N,
    uniquement pour les banques du groupe « Groupes Locaux ». Banque du rapport mise en évidence.
    """
    if indicateurs is None:
        indicateurs = [('BILAN', 'SUR LE TOTAL BILAN'), ('EMPLOI', 'SUR LES EMPLOIS'),
                      ('RESSOURCES', 'SUR LES RESSOURCES'), ('COMPTE', 'SUR LE NOMBRE DE COMPTES')]
    if annee_cible is None:
        annee_cible = int(df[annee_col].max()) if annee_col in df.columns else 2020
    annee_cible = int(annee_cible)
    annee_prev = annee_cible - 1
    banque_rapport = str(banque_rapport).strip().upper() if banque_rapport else 'BNDE'

    df = df.copy()
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    if groupe_col not in df.columns:
        groupe_col = 'Groupe_Bancaire' if 'Groupe_Bancaire' in df.columns else groupe_col
    if groupe_col not in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, 'Colonne groupe bancaire manquante', ha='center', va='center', transform=ax.transAxes)
        plt.show()
        return fig, ax

    # Restreindre aux groupes locaux (toutes banques qui sont dans un groupe contenant "Local")
    groupes = df[groupe_col].dropna().astype(str).unique()
    groupe_local = None
    for g in groupes:
        if 'local' in g.lower() or 'Local' in g:
            groupe_local = g
            break
    if groupe_local is None:
        groupe_local = 'Groupes Locaux'
    df_local = df[df[groupe_col].astype(str).str.strip() == groupe_local.strip()].copy()
    if len(df_local) == 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, 'Aucune banque du groupe « Groupes Locaux »', ha='center', va='center', transform=ax.transAxes)
        plt.show()
        return fig, ax

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    fig.patch.set_facecolor('#ffffff')
    for ax in axes:
        ax.set_facecolor('#f7f9fc')

    for idx, (col_metrique, label_metrique) in enumerate(indicateurs):
        if col_metrique not in df.columns or idx >= len(axes):
            continue
        ax = axes[idx]
        full = _compute_part_marche_two_years_by_bank(df, col_metrique, annee_col, banque_col, annee_prev, annee_cible)
        if len(full) == 0:
            ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(label_metrique, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
            continue
        banks_local = df_local[banque_col].dropna().astype(str).str.strip().str.upper().unique()
        df_plot = full[full[banque_col].astype(str).str.strip().str.upper().isin(banks_local)].copy()
        if len(df_plot) == 0:
            ax.text(0.5, 0.5, 'Aucune donnée groupes locaux', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(label_metrique, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
            continue

        for _, row in df_plot.iterrows():
            bank = row[banque_col]
            is_rapport = str(bank).strip().upper() == banque_rapport
            color = COULEUR_BANQUE_RAPPORT if is_rapport else COULEUR_AUTRES
            size = 120 if is_rapport else 70
            z = 5 if is_rapport else 3
            ax.scatter(row['part_prev'], row['part_curr'], s=size, color=color, alpha=0.9,
                       edgecolors='white', linewidth=2, zorder=z)
            ax.annotate(str(bank), (row['part_prev'], row['part_curr']), xytext=(4, 4), textcoords='offset points',
                        fontsize=8, fontweight='bold' if is_rapport else 'normal',
                        color=COULEUR_BANQUE_RAPPORT if is_rapport else COULEUR_TEXTE,
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor=COULEUR_BANQUE_RAPPORT if is_rapport else 'none'))

        ax.set_xlabel(f'Part de marché {annee_prev} (%)', fontsize=10, color=COULEUR_TEXTE)
        ax.set_ylabel(f'Part de marché {annee_cible} (%)', fontsize=10, color=COULEUR_TEXTE)
        ax.set_title(label_metrique, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
        ax.grid(True, alpha=0.3, linestyle='--', color=COULEUR_CREME)
        ax.set_axisbelow(True)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color(COULEUR_CREME)
        ax.spines['bottom'].set_color(COULEUR_CREME)
        ax.tick_params(colors=COULEUR_TEXTE)

    if titre_global:
        fig.suptitle(titre_global, fontsize=14, fontweight='bold', color=COULEUR_FONCE, y=1.02)
    plt.tight_layout()
    plt.show()
    return fig, axes


def evolution_2x2_banque(df_banque, banque_nom, annee_col='ANNEE', annee_debut=2015, annee_fin=2024,
                         indicateurs=None):
    """
    Une figure 2x2 : évolution (barres + courbe de tendance + % croissance) pour la banque choisie.
    indicateurs : liste de (colonne, titre), ex. [('BILAN','Total Bilan'), ('EMPLOI','Emplois'), ...]
    """
    if indicateurs is None:
        indicateurs = [('BILAN', 'TOTAL BILAN'), ('EMPLOI', 'EMPLOIS'), ('RESSOURCES', 'RESSOURCES'), ('COMPTE', 'NOMBRE DE COMPTES')]
    df = df_banque.copy()
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    df = df[(df[annee_col] >= annee_debut) & (df[annee_col] <= annee_fin)].sort_values(annee_col)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    fig.patch.set_facecolor('#ffffff')
    for ax in axes:
        ax.set_facecolor('#f7f9fc')

    for idx, (col, titre) in enumerate(indicateurs):
        if col not in df.columns or idx >= len(axes):
            continue
        ax = axes[idx]
        agg = df.groupby(annee_col)[col].sum().reset_index()
        if len(agg) < 2:
            ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(titre, fontsize=12, fontweight='bold', color=COULEUR_FONCE)
            continue
        x = agg[annee_col].values
        y = agg[col].values
        # Unité : milliards si > 1e6
        if y.max() >= 1e6:
            y_plot = y / 1000
            unite = 'Milliards FCFA'
        else:
            y_plot = y
            unite = 'Millions FCFA'
        bars = ax.bar(x.astype(str), y_plot, color=COULEUR_CLAIRE, alpha=0.9, edgecolor='white', linewidth=1)
        # Tendance linéaire
        z = np.polyfit(np.arange(len(x)), y_plot, 1)
        p = np.poly1d(z)
        ax.plot(x.astype(str), p(np.arange(len(x))), color=COULEUR_MEDIUM, linewidth=2.5, label='Tendance')
        # Croissance globale %
        v0, v1 = y[0], y[-1]
        if v0 > 0:
            n = len(x) - 1
            tcam = ((v1 / v0) ** (1 / n) - 1) * 100
        else:
            tcam = 0
        ax.text(0.02, 0.98, f'{tcam:+.1f}%', transform=ax.transAxes, fontsize=11, fontweight='bold',
                color=COULEUR_MEDIUM, va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffff', edgecolor=COULEUR_MEDIUM))
        ax.set_ylabel(unite, fontsize=10, color=COULEUR_TEXTE)
        ax.set_title(f'{titre} — {banque_nom}', fontsize=11, fontweight='bold', color=COULEUR_FONCE)
        ax.grid(axis='y', alpha=0.3, linestyle='--', color=COULEUR_CREME)
        ax.set_axisbelow(True)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color(COULEUR_CREME)
        ax.spines['bottom'].set_color(COULEUR_CREME)
        ax.tick_params(colors=COULEUR_TEXTE)

    fig.suptitle(f'Évolution des indicateurs — {banque_nom} ({annee_debut}-{annee_fin})', fontsize=13, fontweight='bold', color=COULEUR_FONCE, y=1.02)
    plt.tight_layout()
    plt.show()
    return fig, axes
