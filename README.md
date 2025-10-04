Vigilo (AlerteCompteur) API
Vigilo est une application web complète conçue pour les agences immobilières, leur permettant de surveiller les biens de leurs clients en se basant sur les données des compteurs intelligents. L'application gère l'authentification des utilisateurs, la gestion des biens, un parcours de consentement sécurisé pour les locataires/propriétaires, et la simulation d'alertes avec notifications par email.

🚀 Fonctionnalités Principales
Authentification Sécurisée : Inscription et connexion basées sur des tokens JWT.

Gestion des Biens : CRUD complet pour les propriétés (limité à 3 par utilisateur).

Parcours de Consentement : Système d'invitation unique et sécurisé pour obtenir l'autorisation des titulaires de contrat.

Simulation d'Alertes : Déclenchement d'événements (ex: coupure de courant) avec envoi d'email de notification.

Interface utilisateur Interactive : Un tableau de bord complet construit en HTML/CSS/JS pur, permettant de gérer toutes les fonctionnalités sans quitter l'interface.

Notifications Modernes : Système de "toasts" pour un feedback utilisateur non-intrusif.

🛠️ Architecture Technique
Backend : API RESTful construite avec FastAPI, un framework Python moderne et performant.

Base de Données : SQLite via SQLAlchemy pour la persistance des données.

Authentification : Tokens JWT gérés avec python-jose et passlib.

Validation des Données : Modèles Pydantic pour une validation robuste des entrées de l'API.

Frontend : Interface utilisateur légère et responsive, sans framework, utilisant Pico.css pour un design élégant et rapide.

⚙️ Installation et Lancement
Cloner le projet (si ce n'est pas déjà fait).

Créer un environnement virtuel (recommandé) :

python3 -m venv venv
source venv/bin/activate

Installer les dépendances listées dans requirements.txt :

pip install -r requirements.txt

(Optionnel) Configurer les variables d'environnement pour l'envoi d'emails :
Pour que l'envoi d'emails fonctionne, vous devez configurer les variables d'environnement suivantes. Vous pouvez utiliser un service comme Mailtrap pour les tests.

export SMTP_HOST="smtp.mailtrap.io"
export SMTP_PORT="2525"
export SMTP_USER="votre_user_mailtrap"
export SMTP_PASS="votre_pass_mailtrap"

Lancer le serveur de développement :

python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload

L'option --reload est très utile en développement, car elle redémarre le serveur automatiquement à chaque modification du code.

Accéder à l'application :

Interface utilisateur : http://127.0.0.1:8002

Documentation de l'API (Swagger UI) : http://127.0.0.1:8002/docs