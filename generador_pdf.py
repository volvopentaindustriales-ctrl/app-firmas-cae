import io
import os
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generar_pdf_cae_bytes(mes_firmado, lista_firmas_registradas):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Colores corporativos Selecon
    AZUL_SELECON = colors.HexColor('#0D47A1')
    NARANJA_SELECON = colors.HexColor('#E65100')
    GRIS_TEXTO = colors.HexColor('#2C3E50')
    
    # Estilos tipográficos
    titulo_style = ParagraphStyle(
        'TituloEmpresa',
        parent=styles['Heading1'],
        fontSize=12,
        leading=15,
        textColor=AZUL_SELECON,
        alignment=0,
        spaceAfter=2
    )
    
    subtitulo_header = ParagraphStyle(
        'SubtituloHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=NARANJA_SELECON,
        alignment=0
    )

    legal_style = ParagraphStyle(
        'TextoLegal',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=GRIS_TEXTO,
        alignment=4,
        spaceAfter=10
    )

    # --- ENCABEZADO CON DETECCIÓN DE LOGO ---
    posibles_nombres = ["logo.png", "logo.PNG", "logo.jpg", "logo.jpeg", "static/logo.png"]
    ruta_logo = None
    
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            ruta_logo = nombre
            break

    if ruta_logo:
        try:
            img_logo = Image(ruta_logo, width=130, height=40)
        except Exception:
            img_logo = Paragraph("", styles['Normal'])
    else:
        img_logo = Paragraph("", styles['Normal'])

    header_text = [
        Paragraph("<b>SELECON, S.L.</b>", titulo_style),
        Paragraph("<b>EL DOMINIO DE LA ENERGÍA</b>", subtitulo_header),
        Paragraph("<font size=7 color='#7F8C8D'>CERTIFICADO DE OBLIGACIONES SALARIALES Y CUMPLIMIENTO CAE</font>", subtitulo_header)
    ]

    header_table = Table([[header_text, img_logo]], colWidths=[370, 165])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 10))

    # --- CUADRO LEGAL DE DECLARACIÓN ---
    texto_declaracion = f"""
    <b>DECLARACIÓN JURADA Y AUDITORÍA ELECTRÓNICA</b><br/>
    Por la presente, <b>SELECON, S.L.</b> certifica que el personal relacionado a continuación ha percibido 
    satisfactoriamente los importes correspondientes a la liquidación salarial del periodo <b>{mes_firmado}</b>. 
    Se adjunta la prueba técnica con validez legal (sellado UTC, dirección IP y huella digital criptográfica SHA-256) 
    para los requisitos de Coordinación de Actividades Empresariales (CAE).
    """
    
    tabla_declaracion = Table([[Paragraph(texto_declaracion, legal_style)]], colWidths=[535])
    tabla_declaracion.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3E0')),
        ('BOX', (0,0), (-1,-1), 1, NARANJA_SELECON),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(tabla_declaracion)
    story.append(Spacer(1, 12))

    # --- TABLA DE REGISTROS DE FIRMA ---
    data_tabla = [
        ["Nº", "Trabajador / DNI", "Registro de Auditoría IP & Criptografía", "Firma Digital"]
    ]
    
    celda_trabajador = ParagraphStyle('CeldaTrabajador', fontSize=8, leading=10, textColor=GRIS_TEXTO)
    celda_hash_style = ParagraphStyle('CeldaHash', fontSize=6.5, leading=8, textColor=colors.HexColor('#546E7A'))

    if not lista_firmas_registradas:
        data_tabla.append(["-", "Sin registros de firma aún", "-", "-"])
    else:
        for idx, reg in enumerate(lista_firmas_registradas, start=1):
            nombre = reg.get('nombre', 'Trabajador')
            dni = reg.get('dni', '')
            fecha = reg.get('fecha', '-')
            ip = reg.get('ip', '-')
            hash_val = reg.get('hash', '')[:16] + "..." if reg.get('hash') else "-"
            
            img_element = "Pendiente"
            if reg.get('firma') and isinstance(reg['firma'], str) and reg['firma'].startswith('data:image'):
                try:
                    base64_data = reg['firma'].split(',')[1]
                    img_data = base64.b64decode(base64_data)
                    img_stream = io.BytesIO(img_data)
                    img_element = Image(img_stream, width=85, height=25)
                except Exception:
                    img_element = "Error"

            col_trabajador = Paragraph(f"<b>{nombre}</b><br/><font color='#E65100'>DNI: {dni}</font>", celda_trabajador)
            col_auditoria = Paragraph(f"<b>Fecha UTC:</b> {fecha}<br/><b>IP:</b> {ip}<br/><font color='#78909C'>HASH: {hash_val}</font>", celda_hash_style)
            
            data_tabla.append([
                str(idx),
                col_trabajador,
                col_auditoria,
                img_element
            ])

    tabla_firmas = Table(data_tabla, colWidths=[20, 200, 205, 110])
    tabla_firmas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_SELECON),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CFD8DC')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F7FA')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))

    story.append(tabla_firmas)
    doc.build(story)
    
    buffer.seek(0)
    return buffer
