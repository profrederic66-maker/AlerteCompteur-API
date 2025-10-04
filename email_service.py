# /email_service.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

def send_alert_email(recipient_email: str, property_label: str, event_type: str) -> bool:
    """
    Envoie un email d'alerte en utilisant les identifiants SMTP configurés.
    """
    subject = f"⚡️ Alerte AlerteCompteur : {event_type} sur '{property_label}'"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = config.EMAIL_FROM
    message["To"] = recipient_email

    html = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2>Alerte AlerteCompteur</h2>
        <p>Une alerte a été détectée pour le bien : <strong>{property_label}</strong></p>
        <p>Type d'événement : <strong>{event_type}</strong></p>
      </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))
    
    server = None
    try:
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASS)
        server.sendmail(config.EMAIL_FROM, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"--- ERREUR EMAIL: {e} ---")
        return False
    finally:
        if server:
            server.quit()

def send_consent_invitation_email(recipient_email: str, owner_email: str, property_label: str) -> bool:
    """
    Envoie un email d'invitation pour un consentement.
    """
    subject = f"📧 Invitation à consulter les données de '{property_label}'"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = config.EMAIL_FROM
    message["To"] = recipient_email

    html = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2>Invitation de la part de {owner_email}</h2>
        <p>L'utilisateur {owner_email} vous a invité à consulter les données du bien : <strong>{property_label}</strong>.</p>
        <a href="#" style="background-color: #2dd4bf; color: #111827; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accepter l'invitation</a>
      </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))
    
    server = None
    try:
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASS)
        server.sendmail(config.EMAIL_FROM, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"--- ERREUR EMAIL: {e} ---")
        return False
    finally:
        if server:
            server.quit()