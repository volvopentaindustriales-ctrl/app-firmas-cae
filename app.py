import os
import base64
import hashlib
import datetime
from flask import Flask, render_template, request, redirect, send_file

app = Flask(__name__)

# Lista simulada de trabajadores
TRABAJADORES = {
    "12345678A": {"nombre": "Juan Pérez López", "dni": "12345678A", "firmado": False},
    "87654321B": {"nombre": "Ana Gómez Martín", "dni": "87654321B", "firmado": False}
}

REGISTRO_AUDITORIA = []

@app.route('/')
def inicio():
    return render_template('firmar.html')

@app.route('/firmar', methods=['POST'])
def guardar_firma():
    nombre = request.form.get('nombre')
    dni = request.form.get('dni')
    firma_base64 = request.form.get('firma_img')
    
    # Captura automática de auditoría IP y tiempo
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    fecha_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Hash de seguridad
    cadena_bruta = f"{dni}-{fecha_utc}-{ip_cliente}"
    hash_auditoria = hashlib.sha256(cadena_bruta.encode()).hexdigest()
    
    REGISTRO_AUDITORIA.append({
        "dni": dni,
        "nombre": nombre,
        "fecha": fecha_utc,
        "ip": ip_cliente,
        "user_agent": user_agent,
        "hash": hash_auditoria,
        "firma": firma_base64
    })
    
    return "<h2 style='text-align:center; color:green;'>¡Firma registrada con éxito! Puede cerrar esta pestaña.</h2>"

@app.route('/ver_firmas')
def ver_firmas():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro de Firmas CAE</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background-color: #f8f9fa; }
            h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; background: #fff; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }
            th { background-color: #007bff; color: white; }
            img { max-height: 60px; border: 1px solid #ccc; background: #fff; }
        </style>
    </head>
    <body>
        <h2>Registro de Firmas de Auditoría CAE</h2>
        <table>
            <tr>
                <th>Fecha (UTC)</th>
                <th>Nombre</th>
                <th>DNI</th>
                <th>Firma Trazada</th>
                <th>IP Capturada</th>
                <th>Hash SHA-256</th>
            </tr>
    """
    for reg in REGISTRO_AUDITORIA:
        html += f"""
            <tr>
                <td>{reg['fecha']}</td>
                <td>{reg['nombre']}</td>
                <td>{reg['dni']}</td>
                <td><img src="{reg.get('firma', '')}" alt="Firma"></td>
                <td>{reg['ip']}</td>
                <td><small>{reg['hash'][:20]}...</small></td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
