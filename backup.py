import os
import re
import time
import datetime
from flask import Flask, render_template

class Soumissions:
    def __init__(self, soumission, path, date_limite, projet_principal, days_until_due):
        self.soumission = soumission
        self.path = path
        self.date_limite = date_limite
        self.projet_principal = projet_principal
        self.days_until_due = days_until_due

def list_subfolders(root_folder):
    subfolders = [f.path for f in os.scandir(root_folder) if f.is_dir()]
    return subfolders

def extract_due_date(subfolder):
    for filename in os.listdir(subfolder):
        if filename.endswith('.txt'):
            # Vérifier le format jj-mm-aaaa
            if re.search(r'\d{2}-\d{2}-\d{4}', filename):  
                return filename[:-4]  # Supprimer l'extension .txt

            # Capturer le format jj mois aaaa (ex: 8 mai 2024) et le convertir en format compatible
            match = re.search(r'(\d{1,2}) (\w+) (\d{4})', filename, re.IGNORECASE)
            if match:
                day, month_str, year = match.groups()
                month_dict = {
                    'janvier': '01',
                    'février': '02',
                    'mars': '03',
                    'avril': '04',
                    'mai': '05',
                    'juin': '06',
                    'juillet': '07',
                    'août': '08',
                    'septembre': '09',
                    'octobre': '10',
                    'novembre': '11',
                    'décembre': '12'
                }
                month = month_dict.get(month_str.lower(), None)
                if month:
                    formatted_date = f"{day}-{month}-{year}"
                    return formatted_date

    return None

def main():
    disk_path = 'C:\\2e disque\\Soumissions\\2024\\test'

    # Obtenir la liste des sous-dossiers
    subfolders_list = list_subfolders(disk_path)

    # Créer des objets Soumissions et les stocker dans une liste
    projets = []
    for subfolder in subfolders_list:
        # Vérifier si un fichier texte avec une date existe
        due_date = extract_due_date(subfolder)

        # Calculer le nombre de jours restants jusqu'à la date limite
        if due_date:
            due_date_obj = datetime.datetime.strptime(due_date, "%d-%m-%Y")
            days_until_due = (due_date_obj - datetime.datetime.now()).days
        else:
            days_until_due = None

        # Déterminer le nom du projet
        if due_date:
            projet = Soumissions(os.path.basename(subfolder), subfolder, due_date, os.path.basename(subfolder), days_until_due)
            projets.append(projet)
            continue
        else:
            if len(next(os.walk(subfolder))[1]) == 0:
                projet = Soumissions(os.path.basename(subfolder), subfolder, None, os.path.basename(subfolder), days_until_due)
                projets.append(projet)

            for subfold in list_subfolders(subfolder):
                due_date = extract_due_date(subfold)
                if due_date:
                    due_date_obj = datetime.datetime.strptime(due_date, "%d-%m-%Y")
                    days_until_due = (due_date_obj - datetime.datetime.now()).days
                    projet = Soumissions(os.path.basename(subfold), subfolder, due_date, os.path.basename(subfolder), days_until_due)
                    projets.append(projet)
                else:
                    projet = Soumissions(os.path.basename(subfolder), subfolder, None, os.path.basename(subfolder), days_until_due)
                    projets.append(projet)

    # Trier la liste des projets en fonction du nombre de jours restants jusqu'à la date limite
    projets.sort(key=lambda x: x.days_until_due if x.days_until_due is not None else float('inf'))

    return projets

app = Flask(__name__)

@app.route('/')
def index():
    # Call your main function and store the results in a variable
    results = main()
    return render_template('index.html', results=results)

if __name__ == "__main__":
    app.run(debug=True, host='192.168.2.37')
