import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Definición de colores
AZUL_SELECON = colors.HexColor('#1A365D')
GRIS_TEXTO = colors.HexColor('#2D3748')

def generar_pdf_cae_bytes(mes_firmado, lista_firmas_registradas):
    buffer = io.BytesIO()
    
    # 1. Márgenes reducidos del documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=15,
        bottomMargin=15
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloEmpresa',
        parent=styles['Heading1'],
        fontSize=12,
        leading=14,
        textColor=AZUL_SELECON,
        alignment=1,
        spaceAfter=8
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloLegal',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=GRIS_TEXTO,
        alignment=4,
        spaceAfter=10
    )

    story.append(Paragraph("<b>SELECON, S.L. — CERTIFICADO DE OBLIGACIONES SALARIALES Y CAE</b>", titulo_style))
    
    texto_declaracion = f"""
    Por la presente, <b>SELECON, S.L.</b> acredita y certifica que los trabajadores relacionados a continuación 
    han percibido íntegramente las retribuciones correspondientes a los <b>salarios del mes de {mes_firmado}</b> 
    y liquidación de obligaciones laborales. Asimismo, se adjunta la trazabilidad electrónica (fecha UTC, IP y Hash SHA-256) 
    capturada individualmente según la normativa vigente de Coordinación de Actividades Empresariales (CAE).
    """
    story.append(Paragraph(texto_declaracion, subtitulo_style))
    story.append(Spacer(1, 5))

    data_tabla = [
        ["Nº", "Trabajador / DNI", "Fecha / Auditoría IP / Hash", "Firma Digital"]
    ]
    
    # 3. Estilos de celda compactos
    celda_trabajador = ParagraphStyle('CeldaTrabajador', fontSize=7.5, leading=9, textColor=GRIS_TEXTO)
    celda_hash_style = ParagraphStyle('CeldaHash', fontSize=6, leading=7.5, textColor=colors.HexColor('#546E7A'))

    for idx, reg in enumerate(lista_firmas_registradas, start=1):
        nombre = reg.get('nombre', 'Trabajador')
        dni = reg.get('dni', '')
        fecha = reg.get('fecha', '-')
        ip = reg.get('ip', '-')
        hash_completo = reg.get('hash', '-')
        
        img_element = "Pendiente"
        if reg.get('firma') and reg['firma'].startswith('data:image'):
            try:
                base64_data = reg['firma'].split(',')[1]
                img_data = base64.b64decode(base64_data)
                img_stream = io.BytesIO(img_data)
                # 2. Tamaño de imagen de firma ajustado
                img_element = Image(img_stream, width=70, height=18)
            except Exception:
                img_element = "Error Firma"

        col_trabajador = Paragraph(f"<b>{nombre}</b><br/>DNI: {dni}", celda_trabajador)
        
        col_auditoria = Paragraph(
            f"<b>{fecha}</b><br/>"
            f"IP: {ip}<br/>"
            f"<font color='#546E7A'><b>HASH:</b> {hash_completo}</font>", 
            celda_hash_style
        )
        
        data_tabla.append([
            str(idx),
            col_trabajador,
            col_auditoria,
            img_element
        ])

    # 4. Tabla compacta con padding mínimo
    tabla_firmas = Table(data_tabla, colWidths=[18, 195, 220, 110])
    tabla_firmas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_SELECON),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CFD8DC')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F7FA')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))

    story.append(tabla_firmas)
    doc.build(story)
    
    buffer.seek(0)
    return buffer
