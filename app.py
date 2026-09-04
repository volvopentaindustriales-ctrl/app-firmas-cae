import os
import base64
import hashlib
import datetime
import csv
import zoneinfo

from flask import Flask, render_template, request, send_file
from supabase import create_client, Client
from generador_pdf import generar_pdf_cae_bytes

app = Flask(__name__)

# --- CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ovfhnwejascrdivqdjvd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_01Wb6l61WUwztzqjON2HuA_-S8_07jp")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CARGAR TRABAJADORES DESDE SUPABASE (O FALLBACK A CSV SI NO HAY BD) ---
def obtener_trabajadores():
    """
    Obtiene la lista de trabajadores desde la tabla 'trabajadores' en Supabase.
    Si ocurre un error o la tabla no existe, intenta leer desde 'trabajadores.csv'.
    """
    trabajadores = {}
    try:
        respuesta = supabase.table("trabajadores").select("*").execute()
        if respuesta.data:
            for t in respuesta.data:
                dni = t.get('dni', '').strip()
                nombre = t.get('nombre', '').strip()
                if dni:
                    trabajadores[dni] = {"nombre": nombre, "dni": dni}
            return trabajadores
    except Exception as e:
        print(f"Aviso Supabase: No se pudo cargar trabajadores desde BD ({e}). Probando CSV local...")

    # Fallback: Cargar desde trabajadores.csv si existiera en la carpeta local
    if os.path.exists("trabajadores.csv"):
        try:
            with open("trabajadores.csv", mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dni = row.get('dni', '').strip()
                    nombre = row.get('nombre', '').strip()
                    if dni:
                        trabajadores[dni] = {"nombre": nombre, "dni": dni}
        except Exception as e:
            print(f"Error al leer trabajadores.csv: {e}")

    return trabajadores


def obtener_mes_actual_texto():
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    ahora = datetime.datetime.now()
    if ahora.month == 1:
        mes_idx = 11
        anio = ahora.year - 1
    else:
        mes_idx = ahora.month - 2
        anio = ahora.year
    return f"{meses[mes_idx]} {anio}"


@app.route('/')
def inicio():
    return "Servidor de Firmas CAE Activo con Base de Datos Persistente."


@app.route('/firmar/<dni>')
def firmar_individual(dni):
    mes_param = request.args.get('mes', obtener_mes_actual_texto())
    trabajadores = obtener_trabajadores()
    trabajador = trabajadores.get(dni, {"nombre": "Trabajador", "dni": dni})
    return render_template('firmar.html', nombre=trabajador['nombre'], dni=trabajador['dni'], mes=mes_param)


@app.route('/guardar_firma', methods=['POST'])
@app.route('/guardar_firma', methods=['POST'])
def guardar_firma():
    dni = request.form.get('dni')
    mes = request.form.get('mes', obtener_mes_actual_texto())
    firma_base64 = request.form.get('imagen_firma')
    
    trabajadores = obtener_trabajadores()
    trabajador = trabajadores.get(dni, {"nombre": "Trabajador"})
    nombre = trabajador.get('nombre')
    
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    # --- FECHA EN HORA OFICIAL DE ESPAÑA ---
    zona_madrid = zoneinfo.ZoneInfo("Europe/Madrid")
    fecha_utc = datetime.datetime.now(zona_madrid).strftime("%Y-%m-%d %H:%M:%S CEST")
    
    cadena_bruta = f"{dni}-{mes}-{fecha_utc}-{ip_cliente}"
    hash_auditoria = hashlib.sha256(cadena_bruta.encode()).hexdigest()
    
    datos_registro = {
        "dni": dni,
        "nombre": nombre,
        "mes": mes,
        "fecha_utc": fecha_utc, # Mantiene el nombre de la columna en Supabase
        "ip": ip_cliente,
        "user_agent": user_agent,
        "hash_sha256": hash_auditoria,
        "firma_base64": firma_base64
    }
    
    try:
        supabase.table("registro_firmas").insert(datos_registro).execute()
    except Exception as e:
        print(f"Error guardando en Supabase: {e}")

    return f"<h2 style='text-align:center; color:green; font-family:sans-serif; margin-top:50px;'>¡Firma del mes de {mes} registrada con éxito!</h2>"
        supabase.table("registro_firmas").insert(datos_registro).execute()
    

@app.route('/ver_firmas')
def ver_firmas():
    try:
        respuesta = supabase.table("registro_firmas").select("*").order("id", desc=True).execute()
        registros = respuesta.data
    except Exception as e:
        registros = []

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
            .celda-hash { word-break: break-all; font-family: monospace; font-size: 11px; max-width: 250px; }
        </style>
    </head>
    <body>
        <h2>Registro de Auditoría de Firmas CAE (Persistente)</h2>
        <a href="/descargar_pdf" class="btn">📄 Descargar PDF Consolidado</a>
        <table>
            <tr>
                <th>Fecha (UTC)</th>
                <th>Mes</th>
                <th>Nombre</th>
                <th>DNI</th>
                <th>Firma</th>
                <th>IP</th>
                <th>Hash SHA-256 (Completo)</th>
            </tr>
    """
    for reg in registros:
        html += f"""
        <tr>
            <td>{reg.get('fecha_utc', '')}</td>
            <td><b>{reg.get('mes', '-')}</b></td>
            <td>{reg.get('nombre', '')}</td>
            <td>{reg.get('dni', '')}</td>
            <td><img src="{reg.get('firma_base64', '')}" alt="Firma"></td>
            <td>{reg.get('ip', '')}</td>
            <td class="celda-hash">{reg.get('hash_sha256', '')}</td>
        </tr>
        """
    html += "</table></body></html>"
    return html


@app.route('/descargar_pdf')
def descargar_pdf():
    try:
        respuesta = supabase.table("registro_firmas").select("*").order("id", desc=False).execute()
        registros_bd = respuesta.data
    except Exception:
        registros_bd = []

    lista_para_pdf = []
    for r in registros_bd:
        lista_para_pdf.append({
            "nombre": r.get('nombre'),
            "dni": r.get('dni'),
            "fecha": r.get('fecha_utc'),
            "ip": r.get('ip'),
            "hash": r.get('hash_sha256'),
            "firma": r.get('firma_base64')
        })

    mes = registros_bd[0].get('mes', obtener_mes_actual_texto()) if registros_bd else obtener_mes_actual_texto()
    
    try:
        pdf_buffer = generar_pdf_cae_bytes(mes, lista_para_pdf)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"Certificado_CAE_Salarios_{mes.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"<h3 style='color:red; text-align:center;'>Error al generar el PDF: {str(e)}</h3>"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
