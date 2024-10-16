FastAPI - API REST Gestión Inventario/Ventas | By: Joel Sigüenza
================================================================

Explicación
-----------
"Creaciones Morochita" maneja actualmente sus operaciones utilizando registros en cuadernos físicos, lo cual resulta ineficiente y propenso a errores. Ante esto, surge la siguiente interrogante: ¿Qué impacto tendría la implementación de un sistema web en la gestión de inventarios y ventas de "Creaciones Morochita" en el año 2024?.

Este proyecto busca implementar un sistema de gestión integral para "Creaciones Morochita", que permitirá optimizar los procesos de la empresa, mejorando la precisión en la gestión de inventarios y ventas, aplicanto la metodología Scrum y el framework de FastApi para la construcción de los servicios web haciendo uso de una base de datos PostgreSQL.

Instalación
-----------

Crear un entorno virtual, activarlo e instalar las dependencias desde el archivo requirements.txt

Usar `Command Prompt` (recomendable)

Crear entorno virtual:

```sh
python -m venv fastapi-env
```

Activar el entorno virtual:

```sh
fastapi-env\Scripts\activate
```

Instalar las dependencias:

```sh
pip install -r requirements.txt
```

Para desactivar el entorno virtual:

```sh
deactivate
```

## Para envio de correo:
------------------------

Debe generar su clave unica en gmail: 

```sh
https://myaccount.google.com/u/0/apppasswords
```

Luego generar un archivo .env en la raiz del proyecto y colocar:

```sh
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="465"
EMAIL_ADDRESS="TU_CORREO_GMAIL"
EMAIL_PASSWORD="TU_CLAVE_UNICA"
```

## Mantener entorno virtual activado para:
------------------------------------------

Iniciar Servidor
----------------

```sh
uvicorn src.main:app --reload
```

`Inicio rápido:`

```sh
fastapi-env\Scripts\activate; uvicorn main:app --reload
```

Ejecutar Test
-------------

```sh
pytest -s
```