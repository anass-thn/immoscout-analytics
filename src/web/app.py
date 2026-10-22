import pandas as pd
from flask import Flask,render_template,request

app = Flask(__name__)
df_pepites = pd.read_csv('data/processed/pepites.csv')

@app.route('/', methods=['GET', 'POST'])
def home():
    total_global = len(df_pepites)
    top_pepites = df_pepites.head(10).to_dict('records')
    ville = request.args.get('ville', '')
    if ville:
        df_ville = df_pepites[df_pepites['Commune'].str.contains(ville,case=False)].to_dict('records')
        total_recherche = len(df_ville)
        df_ville = df_ville[:20]
        return render_template('index.html', total_pepites=total_global, pepites=df_ville, total_recherche=total_recherche,ville=ville)
    return render_template('index.html', total_pepites=total_global, pepites=top_pepites,total_recherche=total_global,ville=ville)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
