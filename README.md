# Générateur de Calendrier

Ce projet est une application de planification basée sur Django, conçue pour gérer les affectations des enseignants et les emplois du temps des séances. Il comprend des fonctionnalités d'importation de données depuis des fichiers Excel, d'exécution d'algorithmes de planification, et d'exportation des emplois du temps en fichiers Excel ou PDF.

## Fonctionnalités

- Importation des données des enseignants et des séances via des fichiers Excel.
- Exécution d’un algorithme de planification pour affecter les enseignants aux séances.
- Exportation des emplois du temps au format Excel ou en PDF pour chaque enseignant.
- Tableau de bord administrateur avec gestion des fichiers et liste des enseignants.
- Téléchargement des emplois du temps individuels depuis le tableau de bord.

## Installation

1. Créer et activer un environnement virtuel Python 

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2.Installer les dépendances:

```bash
pip install -r requirements.txt
```

3. Appliquer les migrations:

```bash
python manage.py migrate
```

4. Lancer le serveur de développement:

```bash
python manage.py runserver
```

5. Accéder au tableau de bord administrateur à l’adresse : http://127.0.0.1:8000/dashboard/.

## Utilisation:
Utilisez le tableau de bord pour téléverser les fichiers Excel des enseignants et des séances.

Générez et téléchargez les emplois du temps.

Affichez et téléchargez les emplois du temps individuels des enseignants.

## Remarques:
Assurez-vous d’avoir installé les packages Python requis (voir requirements.txt).

L’intégration frontend se fait via des appels API — voir frontend-integration.md pour plus de détails.

Vous pouvez personnaliser les modèles et styles du tableau de bord admin selon vos besoins.

## Licence
Ce projet est sous licence MIT.
