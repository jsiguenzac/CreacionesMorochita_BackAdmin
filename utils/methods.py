# REGION: Formato JSON para salida de todos los endpoints
from schemas.exit_api.BaseOut import BaseM, Salida

def exit_json(state, data):
    if state < 0 or state > 1:
        raise Exception("El estado de salida debe ser 1 o 0")
    msg = "success" if state == 1 else "error"
    exit_json = Salida(state=state, msg= msg)
    exit_json.data = data
    salida_model = BaseM(**exit_json.__dict__)
    return salida_model
# END REGION

# REGION: Método para generar clave aleatoria
import random
import string

def generate_random_password(string_length=10):
    letdigs = string.ascii_letters + string.digits
    return ''.join(random.choice(letdigs) for i in range(string_length))
# END REGION

# REGION: Método para envio de correo electrónico
import os
import ssl
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email: str, subject: str, body: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg.add_alternative(body, subtype='html')
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
        
def EmailServiceEnv():
    # Cargar las variables de entorno del archivo .env
    load_dotenv()

    # Obtener las variables de entorno
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT'))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    # Inicializa el servicio de correo electrónico con las variables de entorno
    email_service = EmailService(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        sender_email=EMAIL_ADDRESS,
        sender_password=EMAIL_PASSWORD
    )
    return email_service
# END REGION

# REGION: Método para convertir long a datetime UTC
from datetime import datetime, timezone

def long_to_date(timestamp: int):
    if timestamp == -1:
        return timestamp
    # Convertir timestamp (milisegundos) a segundos
    timestamp_sec = timestamp / 1000
    # Convertir a datetime en UTC
    dt_utc = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
    return dt_utc.date()
# END REGION