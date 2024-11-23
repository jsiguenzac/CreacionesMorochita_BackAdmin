from datetime import datetime, timezone
import time
import pytz

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
    """
    Convierte un timestamp (en milisegundos) a una fecha en la zona horaria de Perú.
    :param timestamp: El timestamp en milisegundos.
    :return: Fecha en formato date en la zona horaria de Perú, o -1 si hay un error.
    """
    try:
        # Validar si el timestamp es inválido
        if timestamp == -1 or not isinstance(timestamp, int):
            return -1
        
        # Convertir timestamp (milisegundos) a segundos
        timestamp_sec = timestamp / 1000

        # Convertir a datetime en UTC
        dt_utc = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)

        # Convertir a la zona horaria de Perú
        peru_tz = pytz.timezone('America/Lima')
        dt_peru = dt_utc.astimezone(peru_tz)
        print("Fecha en Perú:", dt_peru)

        return dt_peru
    except Exception as e:
        # Otros errores inesperados
        print("Error al convertir timestamp a fecha:", e)
        return -1
# END REGION

# Método para obtener la fecha y hora actual en Perú
def get_peru_datetime():
    """
    Obtiene la fecha y hora actual en la zona horaria de Perú.
    :return: Objeto datetime con la hora y fecha actual en Perú.
    """
    peru_tz = pytz.timezone('America/Lima')
    return datetime.now(peru_tz)

# Método para obtener solo la fecha actual en Perú
def get_peru_date():
    """
    Obtiene la fecha actual en la zona horaria de Perú.
    :return: Objeto date con la fecha actual en Perú.
    """
    return get_peru_datetime().date()

# Método para obtener solo la hora actual en Perú
def get_peru_time():
    """
    Obtiene la hora actual en la zona horaria de Perú.
    :return: Objeto time con la hora actual en Perú.
    """
    return get_peru_datetime().time()

# REGION: Método para exportar reporte de ventas a Excel
import pandas as pd
from io import BytesIO
import os
from typing import List, Dict

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

# REGION: Método para generar boleta de venta en PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

def generate_sales_receipt_pdf(sale: dict, logo_path: str):
    try:
        # Crear un buffer en memoria para el archivo PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Configuración de dimensiones
        width, height = letter
        margin = 3 * cm
        
        # Añadir fondo (color claro)
        pdf.setFillColorRGB(0.95, 0.95, 0.95)  # Fondo gris claro
        pdf.rect(0, 0, width, height, fill=True, stroke=False)
        
        # Añadir el logo centrado
        logo_width = 8 * cm
        logo_height = 5 * cm

        # Calcular la posición x para centrar el logo
        logo_x_position = (width - logo_width) / 2
        logo_y_position = height - logo_height - margin  # Mantiene la posición vertical

        pdf.drawImage(logo_path, logo_x_position, logo_y_position, width=logo_width, height=logo_height, preserveAspectRatio=True)

        # Título de la boleta
        pdf.setFont("Courier-Bold", 18)
        pdf.setFillColor(colors.darkblue)
        pdf.drawCentredString(width / 2, height - margin - logo_height - 1.5 * cm, "Creaciones Morochita")
        pdf.drawCentredString(width / 2, height - margin - logo_height - 2.5 * cm, "Boleta de Venta")

        # Datos de la venta en dos columnas
        pdf.setFont("Helvetica", 12)
        data_left = [
            f"Vendedor: {sale['name_seller']}",
            f"Cliente: {sale['name_client']}",
            f"DNI Cliente: {sale.get('dni_client', 'N/A') if sale['dni_client'] else 'N/A'}",
        ]
        data_right = [
            f"Fecha: {sale['date_sale']}",
            f"Hora: {sale['hour_sale']}",
            f"Método de Pago: {sale['name_payment']}",
        ]
        
        x_left = margin
        x_right = width / 2
        y = height - logo_height - margin - 4.5 * cm
        line_spacing = 18

        for line in data_left:
            pdf.drawString(x_left, y, line)
            y -= line_spacing
        
        y = height - logo_height - margin - 4.5 * cm
        for line in data_right:
            pdf.drawString(x_right, y, line)
            y -= line_spacing

        # Detalle de productos
        # Crear y configurar la tabla
        table_data = [["Producto", "Talla", "Cantidad", "Subtotal"]]
        for product in sale["products"]:
            table_data.append([
                product["name_product"],
                str(product["talla"]),
                str(product["quantity"]),
                f"S/ {product['subtotal']:.2f}"
            ])

        table = Table(table_data, colWidths=[8 * cm, 2 * cm, 2 * cm, 3 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Obtener las dimensiones de la tabla
        table_width, table_height = table.wrapOn(pdf, width, height)

        # Dibujar la tabla en la posición calculada
        table_y_position = y - table_height - 40  # Ajusta este valor para bajar la tabla
        table.drawOn(pdf, margin, table_y_position)

        # Total de la venta alineado a la derecha
        total_text = f"Total: S/ {sale['total']:.2f}"
        pdf.setFont("Helvetica-Bold", 12)

        # Posición dinámica debajo de la tabla
        total_y_position = table_y_position - 20  # Ajusta para separar el total de la tabla
        pdf.drawRightString(width - margin, total_y_position, total_text)

        # Guardar el PDF
        pdf.save()
        buffer.seek(0)

        # Nombre del archivo
        date_time_current = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        file_name = f"Boleta_Venta_{date_time_current}.pdf"
        return buffer, file_name
    except Exception as e:
        print("Error al generar el PDF:", e)
        return None, None
# END REGION