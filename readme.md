## *Es necesario crear un entorno virtual y activarlo.

# Activar entorno virtual: fastapi-env\Scripts\activate
## Desactivar:  deactivate
## Para instalar las librerias usadas usar: pip install -r requirements.txt
## ejecutar server: uvicorn main:app --reload
### Para envio de correo:
Debe generar su clave unica en gmail: https://myaccount.google.com/u/0/apppasswords
Luego generar un archivo .env en la raiz del proyecto y colocar:

SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="465"
EMAIL_ADDRESS="TU_CORREO_GMAIL"
EMAIL_PASSWORD="TU_CLAVE_UNICA"

## Inicio Rapido: fastapi-env\Scripts\activate && uvicorn main:app --reload