# Présentation
Scrapper pour le site showroomprivé qui permet de récupérer la liste de ses commandes et des articles liés.


# Récupération du projet

```bash
git clone https://github.com/nclsvsn/srp-connector.git
```

# Création de l'environnement virtuel
```bash
cd srp-connector
python3 -m venv .venv
```

# Installation de dépendances
```bash
. .venv/bin/activate
pip install -r requirements.txt
```

# Ajout des credentials 
Modifiez le fichier ".env" pour y renseigner vos identifiants showroow.


# Lancement du script
```bash
python3 showroom.py
```

