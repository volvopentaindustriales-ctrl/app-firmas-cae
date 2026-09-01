import os
import base64
import hashlib
import datetime
from flask import Flask, render_template, request, send_file
from generador_pdf import generar_pdf_cae_bytes

app = Flask(__name__)

TRABAJADORES = {
    "77860653H": {"nombre": "Álvaro Arteaga Miranda", "dni": "77860653H"},
    "80103380S": {"nombre": "Antonio Bartolomé Salazar Giles", "dni": "80103380S"},
    "30229595M": {"nombre": "Carlos Alejandro Guerrero Cotrina", "dni": "30229595M"},
    "28930685C": {"nombre": "David Gil Lora", "dni": "28930685C"},
    "28639586D": {"nombre": "Fernando Jaime Macías", "dni": "28639586D"},
    "77802398E": {"nombre": "Francisco Manuel Rodríguez Estévez", "dni": "77802398E"},
    "28792032B": {"nombre": "Israel Benítez Fernández", "dni": "28792032B"},
    "28464839Q": {"nombre": "José Joaquín Hidalgo Romero", "dni": "28464839Q"},
    "28753694Z": {"nombre": "Juan M. Pernía León", "dni": "28753694Z"},
    "29516739B": {"nombre": "Juan Miguel Ojeda Bobo", "dni": "29516739B"},
    "28806388S": {"nombre": "Luis Otero Carrasco", "dni": "28806388S"},
    "28763151H": {"nombre": "Rafael Fernández Cruz", "dni": "28763151H"},
    "77537479V": {"nombre": "Francisco Martín Morón Medina", "dni": "77537479V"},
    "53353316D": {"nombre": "Fernando González Mosqueda", "dni": "53353316D"},
    "48192022F": {"nombre": "Francisco Javier Santos Álvarez", "dni": "48192022F"},
    "75070372M": {"nombre": "Jesús Nieto Fernández", "dni": "75070372M"},
    "20079831A": {"nombre": "José Alexis Rodríguez Chica", "dni": "20079831A"},
    "77446244T": {"nombre": "Javier Morente Rodríguez", "dni": "77446244T"},
    "33373171X": {"nombre": "José Luis Campos Ruiz", "dni": "33373171X"},
    "77492245R": {"nombre": "Jesús Porras Rueda", "dni": "77492245R"},
    "26267627V": {"nombre": "Sergio Zotano Plaza", "dni": "26267627V"}
}

REGISTRO_AUDITORIA = []

def obtener_mes_actual_texto():
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    ahora = datetime.datetime.now()
    mes_num = ahora.month - 1 if ahora.month > 1 else 12
    anio = ahora.year if ahora.month > 1 else ahora.year - 1
    return f"{meses[mes_num - 1]} {anio}"

@app.route('/')
def inicio():
    return "Servidor de Firmas CAE Activo."

@app.route('/firmar/<dni>')
def firmar_individual(dni):
    mes_param = request.args.get('mes', obtener_mes_actual_texto())
    trabajador = TRABAJADORES.get(dni, {"nombre": "Trabajador", "dni": dni})
    return render_template('firmar.html', nombre=trabajador['nombre'], dni=trabajador['dni'], mes=mes_param)

@app.route('/guardar_firma', methods=['POST'])
def guardar_firma():
    dni = request.form.get('dni')
    mes = request.form.get('mes', obtener_mes_actual_texto())
    firma_base64 = request.form.get('imagen_firma')
    
    trabajador = TRABAJADORES.get(dni, {"nombre": "Trabajador"})
    nombre = trabajador.get('nombre')
    
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    fecha_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    cadena_bruta = f"{dni}-{mes}-{fecha_utc}-{ip_cliente}"
    hash_auditoria = hashlib.sha256(cadena_bruta.encode()).hexdigest()
    
    REGISTRO_AUDITORIA.append({
        "dni": dni,
        "nombre": nombre,
        "mes": mes,
        "fecha": fecha_utc,
        "ip": ip_cliente,
        "user_agent": user_agent,
        "hash": hash_auditoria,
        "firma": firma_base64
    })
    
    return f"<h2 style='text-align:center; color:green; font-family:sans-serif; margin-top:50px;'>¡Firma del mes de {mes} registrada con éxito!</h2>"

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
            table { width: 100%; border-collapse: collapse; background: #fff; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }
            th { background-color: #0D47A1; color: white; }
            img { max-height: 40px; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #E65100; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h2>Registro de Auditoría de Firmas CAE</h2>
        <a href="/descargar_pdf" class="btn">📄 Descargar PDF Consolidado</a>
        <table>
            <tr>
                <th>Fecha (UTC)</th>
                <th>Mes</th>
                <th>Nombre</th>
                <th>DNI</th>
                <th>Firma</th>
                <th>IP</th>
                <th>Hash</th>
            </tr>
    """
    for reg in REGISTRO_AUDITORIA:
        html += f"""
        <tr>
            <td>{reg['fecha']}</td>
            <td><b>{reg.get('mes', '-')}</b></td>
            <td>{reg['nombre']}</td>
            <td>{reg['dni']}</td>
            <td><img src="{reg.get('firma', '')}" alt="Firma"></td>
            <td>{reg['ip']}</td>
            <td><small>{reg['hash'][:15]}...</small></td>
        </tr>
        """
    html += "</table></body></html>"
    return html

@app.route('/descargar_pdf')
def descargar_pdf():
    # Detecta el mes de las firmas o usa el mes actual por defecto sin crash
    if len(REGISTRO_AUDITORIA) > 0:
        mes = REGISTRO_AUDITORIA[0].get('mes', obtener_mes_actual_texto())
    else:
        mes = obtener_mes_actual_texto()
    
    try:
        pdf_buffer = generar_pdf_cae_bytes(mes, REGISTRO_AUDITORIA)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"Certificado_CAE_Salarios_{mes.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"<h3 style='color:red; text-align:center;'>Error al generar el PDF: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
