from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Bienvenue sur Immoscout Analytics !</h1><p>Le serveur Flask fonctionne.</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
