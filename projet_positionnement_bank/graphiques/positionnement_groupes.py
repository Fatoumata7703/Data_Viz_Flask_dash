import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def positionnement_groupes_bancaires(df, colonne_metrique, titre_graphique, annee_col='ANNEE', annee_debut=2015, annee_fin=2020, ax=None):
    """
    Calcule et affiche le positionnement des groupes bancaires selon la part de marché et le TCAM.
    
    Paramètres:
    -----------
    df : DataFrame
        DataFrame contenant les données bancaires
    colonne_metrique : str
        Nom de la colonne à analyser (ex: 'BILAN', 'EMPLOI', 'RESSOURCES', 'COMPTE')
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
    fig, ax, df_merge : matplotlib figure, axes et DataFrame avec les résultats
    """
    # Filtrer les données pour les années de début et de fin
    df[annee_col] = pd.to_numeric(df[annee_col], errors='coerce')
    df_debut = df[df[annee_col] == annee_debut].copy()
    df_fin = df[df[annee_col] == annee_fin].copy()
    
    # Grouper par groupe bancaire pour chaque année
    groupe_col = 'Goupe_Bancaire'
    
    # Calculer les sommes par groupe pour l'année de début
    df_debut_group = df_debut.groupby(groupe_col)[colonne_metrique].sum().reset_index()
    df_debut_group.columns = [groupe_col, 'valeur_debut']
    
    # Calculer les sommes par groupe pour l'année de fin
    df_fin_group = df_fin.groupby(groupe_col)[colonne_metrique].sum().reset_index()
    df_fin_group.columns = [groupe_col, 'valeur_fin']
    
    # Fusionner les données
    df_merge = pd.merge(df_debut_group, df_fin_group, on=groupe_col, how='inner')
    
    # Filtrer les groupes qui ont des valeurs valides pour les deux années
    df_merge = df_merge[(df_merge['valeur_debut'] > 0) & (df_merge['valeur_fin'] > 0)]
    
    # Calculer le TCAM (Taux de Croissance Annuel Moyen)
    # TCAM = ((valeur_finale / valeur_initiale)^(1/n) - 1) * 100
    n = annee_fin - annee_debut
    df_merge['tcam'] = ((df_merge['valeur_fin'] / df_merge['valeur_debut']) ** (1/n) - 1) * 100
    
    # Calculer la part de marché 2020
    total_fin = df_merge['valeur_fin'].sum()
    df_merge['part_marche'] = (df_merge['valeur_fin'] / total_fin) * 100
    
    # Créer le graphique si ax n'est pas fourni
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure
    
    # Couleurs pour chaque groupe
    couleurs = {
        'Groupes Locaux': '#065f46',
        'Groupes Régionaux': '#d97706',
        'Groupes Internationnaux': '#9333ea',
        'Groupes Continentaux': '#0891b2'
    }
    
    # Calculer les offsets pour les labels (pour les placer bien à côté des points, pas dessus)
    x_max = df_merge['part_marche'].max()
    y_max = df_merge['tcam'].max()
    y_min = df_merge['tcam'].min()
    
    # Utiliser des offsets en coordonnées de données, plus grands pour éviter tout chevauchement
    x_offset_data = x_max * 0.1  # 10% de la valeur max en x
    y_offset_data = max(abs(y_max - y_min) * 0.12, 3) if len(df_merge) > 1 else max(abs(y_max) * 0.12, 3)  # 12% de la plage ou 3 unités
    
    # Tracer d'abord tous les points
    for groupe in df_merge[groupe_col].unique():
        df_groupe = df_merge[df_merge[groupe_col] == groupe]
        couleur = couleurs.get(groupe, '#757575')
        
        ax.scatter(df_groupe['part_marche'], df_groupe['tcam'], 
                  s=200, color=couleur, alpha=0.7, edgecolors='white', linewidth=2, zorder=3)
    
    # Ensuite ajouter les labels bien séparés des points
    for groupe in df_merge[groupe_col].unique():
        df_groupe = df_merge[df_merge[groupe_col] == groupe]
        couleur = couleurs.get(groupe, '#757575')
        
        # Ajouter les labels à côté des points (bien séparés, pas dessus)
        for idx, row in df_groupe.iterrows():
            # Positionner le label à droite et au-dessus du point
            label_x = row['part_marche'] + x_offset_data
            label_y = row['tcam'] + y_offset_data
            
            # Mettre en évidence "Groupes Locaux" avec un fond gris
            if groupe == 'Groupes Locaux':
                ax.text(label_x, label_y, groupe, 
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#424242', 
                                edgecolor='none', alpha=0.8),
                       color='white', ha='left', va='bottom', zorder=4)
            else:
                ax.text(label_x, label_y, groupe, 
                       fontsize=9, fontweight='bold',
                       color=couleur, ha='left', va='bottom', zorder=4)
    
    # Labels des axes
    ax.set_xlabel('Part de marché 2020 (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('TCAM 2015-2020 (%)', fontsize=12, fontweight='bold')
    ax.set_title(titre_graphique, fontsize=14, fontweight='bold', pad=15)
    
    # Grille
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Ajuster les limites des axes avec plus de marge pour les labels
    x_margin = df_merge['part_marche'].max() * 0.15  # Augmenté pour laisser de l'espace aux labels
    y_margin = abs(df_merge['tcam'].max() - df_merge['tcam'].min()) * 0.15 if len(df_merge) > 1 else abs(df_merge['tcam'].max()) * 0.15
    ax.set_xlim(left=0, right=df_merge['part_marche'].max() + x_margin)
    ax.set_ylim(bottom=min(0, df_merge['tcam'].min() - y_margin), 
                top=df_merge['tcam'].max() + y_margin)
    
    # Ne pas appeler tight_layout ni show si ax est fourni (pour intégration dans subplot)
    if ax is None:
        plt.tight_layout()
        plt.show()
    
    return fig, ax, df_merge
