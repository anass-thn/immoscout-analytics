# Immoscout Analytics 🏠

Application web d'analyse de données immobilières françaises permettant de repérer des biens potentiellement sous-évalués ("pépites") à partir des transactions officielles DVF.

🔗 **Application en ligne :** https://immoscout-analytics.onrender.com  
*(Note : hébergée sur le plan gratuit Render, le premier chargement peut prendre ~30 secondes si le serveur sort de veille.)*

## Données utilisées

- **DVF (Demandes de Valeurs Foncières 2025)** : transactions immobilières réelles en France.
- **Carte des loyers (DHUP)** : estimations de loyers au m² par commune.

## Qu'est-ce qu'une "pépite" dans ce projet ?

Après nettoyage des doublons et des valeurs aberrantes (`100 € <= prix/m² <= 30 000 €`), un bien (appartement ou maison) est retenu s'il respecte ces critères :

- **Décote** entre **15 % et 40 %** par rapport au prix médian au m² de sa commune (pour le même type de bien)
- **Rendement locatif brut estimé** entre **7 % et 15 %**
- **Surface habitable** d'au moins **15 m²**
- **Liquidité du marché** : au moins **10 ventes** sur la commune pour ce type de bien

## Structure du projet

- `src/enrich_data.py` : pipeline ETL (chargement, nettoyage, enrichissement avec les loyers, calcul des indicateurs et détection des pépites)
- `data/processed/pepites.csv` : jeu de données final généré par le pipeline
- `src/web/app.py` : application Flask qui charge les données et gère la recherche par ville
- `src/web/templates/index.html` : interface web (Bootstrap)

## Lancer en local

```bash
pip install -r requirements.txt
python src/web/app.py
```

Puis ouvrir `http://127.0.0.1:5000` dans le navigateur.
