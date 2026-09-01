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
        "hash": hash_auditoria
    })
    
    return "<h2 style='text-align:center; color:green;'>¡Firma registrada con éxito! Puede cerrar esta pestaña.</h2>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
