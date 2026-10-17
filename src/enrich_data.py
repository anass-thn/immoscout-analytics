# pyrefly: ignore [missing-import]

import pandas as pd

def load_dvf(file_path) :
    print("chargement des donnees DVF ...")
    dvf = pd.read_csv(file_path, sep='|',low_memory=False)
    print(f"DVF charge avec succes : {len(dvf)} lignes.")
    return dvf
def load_loyers(file_path):
    print("chargement des donnees de loyers ...")
    loyers = pd.read_csv(file_path, sep=';', encoding="cp1252")
    print(f"Donnees loyers chargees avec succes : {len(loyers)} lignes.")
    return loyers

def clean_dvf(dvf):
    print("Nettoyage des données DVF...")
    
    # 1. Garder les logements (Maisons, Appartements)
    dvf_clean = dvf[dvf['Type local'].isin(['Appartement', 'Maison'])].copy()

    # 2. Convertir prix et surface en nombres
    dvf_clean['Valeur fonciere'] = pd.to_numeric(
        dvf_clean['Valeur fonciere'].astype(str).str.replace(',', '.'),
        errors='coerce'
    )
    dvf_clean['Surface reelle bati'] = pd.to_numeric(
        dvf_clean['Surface reelle bati'].astype(str).str.replace(',', '.'),
        errors='coerce'
    )

    # 3. Garder uniquement les valeurs valides
    dvf_clean = dvf_clean[
        (dvf_clean['Valeur fonciere'] > 0) &
        (dvf_clean['Surface reelle bati'] > 0)
    ]

    # 4. Supprimer les doublons
    dvf_clean = dvf_clean.drop_duplicates(
        subset=['Date mutation', 'Valeur fonciere', 'Code departement', 'Code commune', 'Voie'],
        keep='first'
    )

    # 5. Calculer le prix au m²
    dvf_clean['prix_m2'] = dvf_clean['Valeur fonciere'] / dvf_clean['Surface reelle bati']

    # filtrage sur les valeur 100 et 30000
    dvf_clean = dvf_clean[(dvf_clean['prix_m2'] >= 100) & (dvf_clean['prix_m2'] <= 30000)]
    
    return dvf_clean

    
def dvf_enrichie(dvf_clean,loyers):
    # Créer la clé de jointure (code_insee)
    dvf_clean['code_insee'] = dvf_clean['Code departement'].astype(str).str.zfill(2) + dvf_clean['Code commune'].astype(str).str.zfill(3)
    loyers['code_insee'] = loyers['INSEE_C'].astype(str).str.zfill(5)
    # fusionner dvf avec les loyers
    dvf_enrichie = pd.merge(
        dvf_clean,
        loyers[['code_insee', 'loypredm2']],
        on='code_insee',
        how='inner'
    )

    # Convertir loypredm2 en vrai nombre (float)
    dvf_enrichie['loypredm2'] = pd.to_numeric(
        dvf_enrichie['loypredm2'].astype(str).str.replace(',', '.'),
        errors='coerce'
    )
    # Calculer le Rendement Locatif Brut (%)
    dvf_enrichie['rendement_brut'] = (dvf_enrichie['loypredm2'] * 12/dvf_enrichie['prix_m2'] * 100)
    # calcul d'une médiane par groupe :
    dvf_enrichie['prix_m2_median_commune'] = dvf_enrichie.groupby(['code_insee', 'Type local'])['prix_m2'].transform('median')
    # decote_pct calculé : 
    dvf_enrichie['decote_pct'] = (dvf_enrichie['prix_m2_median_commune'] - dvf_enrichie['prix_m2']) / dvf_enrichie['prix_m2_median_commune'] * 100
    # compter les mutations par an : 
    dvf_enrichie['nb_ventes_commune_type'] = dvf_enrichie.groupby(['code_insee', 'Type local'])['prix_m2'].transform('count')
    print(f"dvf_enrichie: {len(dvf_enrichie)} lignes.")
    return dvf_enrichie

def detect_pepites(dvf_enrichie):
    print("Detection des pepites...")
    pepites = dvf_enrichie[dvf_enrichie['decote_pct'].between(15, 40) & (dvf_enrichie['nb_ventes_commune_type']>= 10) & (dvf_enrichie['rendement_brut'].between(7,15)) & (dvf_enrichie['Surface reelle bati']>=15)].copy()

    print(f"Pepites trouvees : {len(pepites)} lignes.")
    return pepites
def save_pepites(pepites,output_path):
    colonnes_utiles = [
    'Commune','Code postal','Code departement','Voie','code_insee','Date mutation','Type local','Surface reelle bati','Nombre pieces principales','prix_m2','Valeur fonciere','prix_m2_median_commune','decote_pct','nb_ventes_commune_type','rendement_brut'
    ]
    pepites_sauvegardes = pepites[colonnes_utiles].copy()
    pepites_sauvegardes.to_csv(output_path,index = False)
    print(f"Pepites sauvegardees dans : {output_path}")

if __name__ == '__main__':
    dvf = load_dvf('data/raw/ValeursFoncieres-2025.txt')
    loyers = load_loyers('data/raw/pred-app-mef-dhup.csv')
    dvf_clean = clean_dvf(dvf)
    dvf_enrichie = dvf_enrichie(dvf_clean,loyers)
    pepites = detect_pepites(dvf_enrichie)
    save_pepites(pepites, 'data/processed/pepites.csv')
    
    
    
