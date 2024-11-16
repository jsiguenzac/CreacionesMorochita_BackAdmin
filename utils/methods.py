from datetime import datetime, timezone

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
def long_to_date(timestamp: int):
    try:
        if timestamp == -1:
            return timestamp
        # Convertir timestamp (milisegundos) a segundos
        timestamp_sec = timestamp / 1000
        # Convertir a datetime en UTC
        dt_utc = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        return dt_utc.date()
    except Exception as e:
        print("Error al convertir timestamp a fecha:", e)
        return -1
# END REGION

# REGION: Método para exportar reporte de ventas a Excel
import pandas as pd
from io import BytesIO
import os
from typing import List

def export_sales_report_to_excel(sales: List[dict]):
    try:
        # Crear un DataFrame vacío con las columnas requeridas
        columns = [
            "Vendedor", "Cliente", "DNI Cliente", "Fecha Venta",
            "Hora Venta", "Método de Pago", "Estado Venta",
            "Total", "Detalle de Productos"
        ]
        df = pd.DataFrame(columns=columns)
        
        # Preparar las filas de ventas
        rows = []
        for sale in sales:
            # Concatenar detalles de productos en un solo string con saltos de línea
            products_details = '\n'.join(
                [f"Producto: {product['name_product']} / "
                f"Talla: {product['talla']} / Precio: {product['price']} / "
                f"Cantidad: {product['quantity']} / Subtotal: {product['subtotal']}"
                for product in sale["products"]
                ]
            )
            
            # Crear una fila con los datos de la venta
            row = [
                sale["name_seller"],
                sale["name_client"],
                sale.get("dni_client", "N/A") if sale["dni_client"] else "N/A",
                sale["date_sale"],
                sale["hour_sale"],
                sale["name_payment"],
                sale["name_status"],
                sale["total"],
                products_details
            ]
            rows.append(row)
        
        # Crear el archivo Excel en memoria (en lugar de en el disco)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as excel_writer:
            # Escribir el DataFrame vacío para la estructura inicial
            df.to_excel(excel_writer, index=False, sheet_name="Reporte de Ventas")

            # Obtener el libro y la hoja activa
            workbook  = excel_writer.book
            worksheet = workbook.get_worksheet_by_name("Reporte de Ventas")

            # Formato para el título (texto grande y centrado)
            header_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9EAD3'})
            worksheet.merge_range('A1:I1', 'Reporte de Ventas Morochita', header_format)

            # Configurar las cabeceras de las columnas
            header_cells_format = workbook.add_format({'bold': True, 'bg_color': '#B6D7A8', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            worksheet.write_row('A3', df.columns, header_cells_format)

            # Formato de las celdas de datos
            data_cells_format = workbook.add_format({'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
            
            # Escribir las filas de ventas
            for i, row in enumerate(rows, start=4):  # Empezar desde la fila 4
                worksheet.write_row(f'A{i}', row, data_cells_format)

            # Ajustar el alto de las filas para los saltos de línea en el detalle de productos
            worksheet.set_row(3, None, None, {'text_wrap': True})  # Ajuste para cabecera
            for i in range(4, len(rows) + 4):
                worksheet.set_row(i, 30)  # Ajuste de altura para las filas con detalles de productos

            # Ajustar el ancho de las columnas
            worksheet.set_column('A:A', 20) # Ajuste para la columna de vendedor
            worksheet.set_column('B:B', 20) # Ajuste para la columna de cliente
            worksheet.set_column('C:C', 15) # Ajuste para la columna de DNI
            worksheet.set_column('D:D', 15) # Ajuste para la columna de fecha
            worksheet.set_column('E:E', 10) # Ajuste para la columna de hora
            worksheet.set_column('F:F', 15) # Ajuste para la columna de método de pago
            worksheet.set_column('G:G', 15) # Ajuste para la columna de estado
            worksheet.set_column('H:H', 10) # Ajuste para la columna de total
            worksheet.set_column('I:I', 80) # Ajuste para la columna de detalle de productos
        
        # Movemos el puntero de BytesIO al inicio
        output.seek(0)
        
        date_time_current = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        name_file = f'Reporte_Ventas_{date_time_current}.xlsx'
        # Devolver el archivo Excel generado como una respuesta de StreamingResponse
        return (output, name_file)
    except Exception as e:
        print("Error al crear el archivo Excel:", e)
        return (None, None)
# END REGION