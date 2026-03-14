import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

def graphique_tcam(df, colonne_metrique, titre_graphique, annee_col='ANNEE', annee_debut=2015, annee_fin=2020):
    """
    Crée un graphique en barres avec les années en abscisse et la valeur en ordonnée,
    avec le TCAM affiché dans une petite bande jaune en haut à gauche.
    
    Paramètres:
    -----------
    df : DataFrame
        DataFrame contenant les données bancaires
    colonne_metrique : str
        Nom de la colonne à analyser (ex: 'BILAN', 'FONDS.PROPRE', 'EMPLOI', 'RESSOURCES')
    titre_graphique : str
        Titre du graphique
    annee_col : str
        Nom de la colonne contenant les années (défaut: 'ANNEE')
    annee_debut : int
        Année de début pour le calcul du TCAM (défaut: 2015)
    annee_fin : int
        Année de fin pour le calcul du TCAM (défaut: 2020)
    
    Retourne:
    ---------
    fig, ax : matplotlib figure et axes
    """
    # Filtrer les données pour les années
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    df_filtered = df[(df[annee_col] >= annee_debut) & (df[annee_col] <= annee_fin)].copy()
    df_filtered = df_filtered.sort_values(by=annee_col)
    
    # Grouper par année et sommer
    df_agg = df_filtered.groupby(annee_col)[colonne_metrique].sum().reset_index()
    df_agg = df_agg.sort_values(by=annee_col)
    
    # Calculer le TCAM
    valeur_initiale = df_agg[df_agg[annee_col] == annee_debut][colonne_metrique].values[0]
    valeur_finale = df_agg[df_agg[annee_col] == annee_fin][colonne_metrique].values[0]
    
    n = annee_fin - annee_debut
    if valeur_initiale > 0:
        tcam = ((valeur_finale / valeur_initiale) ** (1/n) - 1) * 100
    else:
        tcam = 0
    
    # Déterminer l'unité et convertir si nécessaire
    valeur_max = df_agg[colonne_metrique].max()
    if valeur_max >= 1000000:  # Si > 1 million, convertir en milliards
        df_agg['valeur_affichage'] = df_agg[colonne_metrique] / 1000
        unite = 'Milliards FCFA'
        ylabel = f'{titre_graphique.split("(")[0].strip()} ({unite})'
    else:
        df_agg['valeur_affichage'] = df_agg[colonne_metrique]
        unite = 'Millions FCFA'
        ylabel = f'{titre_graphique.split("(")[0].strip()} ({unite})'
    
    # Thème rapport : chocolat / orange BCEAO
    couleur_fonce = '#5C3317'   # header
    couleur_medium = '#9C4A1F'  # primary
    couleur_claire = '#b87333'  # primary-light
    couleur_creme = '#e5d5c8'   # contour
    couleur_texte = '#3d2914'
    couleur_tcam_bg = '#d4a84b' # ambre/or pour bande TCAM

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(12, 7.5))
    fig.patch.set_facecolor('#fefbf7')

    # Dégradé chocolat → orange (thème rapport BCEAO)
    n_bars = len(df_agg)
    try:
        from matplotlib.colors import LinearSegmentedColormap
        cmap_custom = LinearSegmentedColormap.from_list('chocolat', ['#e5d5c8', '#b87333', '#9C4A1F', '#5C3317'], N=max(n_bars, 4))
        colors_bar = cmap_custom(np.linspace(0.15, 0.92, n_bars))
    except Exception:
        colors_bar = plt.cm.Oranges(np.linspace(0.35, 0.9, n_bars))

    # Créer les barres (facecolor via color pour éviter conflit)
    bars = ax.bar(df_agg[annee_col].astype(str), df_agg['valeur_affichage'],
                  color=colors_bar, alpha=0.92, edgecolor='white', linewidth=1.5, width=0.72)

    # Valeurs sur les barres
    for i, (annee, valeur) in enumerate(zip(df_agg[annee_col], df_agg['valeur_affichage'])):
        ax.text(i, valeur, f'{valeur:,.0f}',
                ha='center', va='bottom', fontsize=10, fontweight='600', color=couleur_texte)

    # Titre et axes (thème rapport)
    ax.set_xlabel('Année', fontsize=12, fontweight='600', color=couleur_texte)
    ax.set_ylabel(ylabel, fontsize=12, fontweight='600', color=couleur_texte)
    ax.set_title(titre_graphique, fontsize=15, fontweight='bold', pad=16, color=couleur_fonce)

    # Grille discrète
    ax.grid(axis='y', alpha=0.35, linestyle='--', linewidth=0.7, color=couleur_creme)
    ax.set_axisbelow(True)
    ax.set_facecolor('#fefbf7')

    # Cadre épuré
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(couleur_creme)
    ax.spines['bottom'].set_color(couleur_creme)
    ax.tick_params(colors=couleur_texte, labelsize=10)

    # Limites Y
    ax.set_ylim(bottom=0, top=df_agg['valeur_affichage'].max() * 1.08)

    # Bande TCAM (facecolor uniquement pour éviter le warning)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    bande_width = (xlim[1] - xlim[0]) * 0.14
    bande_height = (ylim[1] - ylim[0]) * 0.06
    x_pos = xlim[0] + (xlim[1] - xlim[0]) * 0.02
    y_pos = ylim[0] + (ylim[1] - ylim[0]) * 0.88
    bande = Rectangle((x_pos, y_pos), bande_width, bande_height,
                      facecolor=couleur_tcam_bg, alpha=0.95, zorder=10, edgecolor=couleur_medium, linewidth=1)
    ax.add_patch(bande)
    text_x = x_pos + bande_width / 2
    text_y = y_pos + bande_height / 2
    ax.text(text_x, text_y, f'TCAM {tcam:.1f}%',
            ha='center', va='center', fontsize=10, fontweight='bold', color=couleur_texte, zorder=11)
    
    plt.tight_layout()
    plt.show()
    
    return fig, ax
