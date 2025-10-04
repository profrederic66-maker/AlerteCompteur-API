# create_user.py

import sys
sys.path.append('.') # <-- LA LIGNE MAGIQUE QUI CORRIGE LE PROBLÈME

from database import SessionLocal
import models
import security

def create_test_user():
    """
    Script pour créer un utilisateur de test dans la base de données.
    """
    db = SessionLocal()
    try:
        print("--- Création d'un utilisateur de test ---")
        
        # --- Définissez ici vos identifiants de test ---
        TEST_USER_EMAIL = "test@exemple.com"
        TEST_USER_PASSWORD = "password123"
        # ---------------------------------------------

        # On vérifie si l'utilisateur existe déjà pour ne pas le créer en double
        existing_user = db.query(models.User).filter(models.User.email == TEST_USER_EMAIL).first()
        if existing_user:
            print(f"L'utilisateur '{TEST_USER_EMAIL}' existe déjà. Aucune action n'est nécessaire.")
            return

        # On utilise la fonction de hachage de votre fichier security.py
        hashed_password = security.get_password_hash(TEST_USER_PASSWORD)
        
        # On crée le nouvel utilisateur avec le modèle que vous avez défini
        new_user = models.User(email=TEST_USER_EMAIL, hashed_password=hashed_password)
        
        db.add(new_user)
        db.commit()
        
        print(f"✅ Utilisateur '{TEST_USER_EMAIL}' créé avec succès.")
        print(f"   Mot de passe : '{TEST_USER_PASSWORD}'")

    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()