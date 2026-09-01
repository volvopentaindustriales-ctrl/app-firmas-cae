import io
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
    
    titulo_style = ParagraphStyle(
        'TituloEmpresa',
        parent=styles['Heading1'],
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#1A365D'),
        alignment=1,
        spaceAfter=10
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloLegal',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2D3748'),
        alignment=4,
        spaceAfter=15
    )

    story.append(Paragraph("<b>SELECON, S.L. — CERTIFICADO DE OBLIGACIONES SALARIALES Y CAE</b>", titulo_style))
    
    texto_declaracion = f"""
    Por la presente, <b>SELECON, S.L.</b> acredita y certifica que los trabajadores relacionados a continuación 
    han percibido íntegramente las retribuciones correspondientes a los <b>salarios del mes de {mes_firmado}</b> 
    y liquidación de obligaciones laborales. Asimismo, se adjunta la trazabilidad electrónica (fecha UTC, IP y Hash SHA-256) 
    capturada individualmente según la normativa vigente de Coordinación de Actividades Empresariales (CAE).
    """
    story.append(Paragraph(texto_declaracion, subtitulo_style))
    story.append(Spacer(1, 10))

    data_tabla = [
        ["Nº", "Trabajador", "DNI", "Fecha / Auditoría IP", "Firma Digital"]
    ]
    
    celda_style = ParagraphStyle('CeldaTabla', fontSize=8, leading=10)
    celda_hash_style = ParagraphStyle('CeldaHash', fontSize=6, leading=8, textColor=colors.HexColor('#4A5568'))

    for idx, reg in enumerate(lista_firmas_registradas, start=1):
        nombre = reg.get('nombre', 'Trabajador')
        dni = reg.get('dni', '')
        fecha = reg.get('fecha', '-')
        ip = reg.get('ip', '-')
        hash_val = reg.get('hash', '')[:16] + "..." if reg.get('hash') else ""
        
        img_element = "Pendiente"
        if reg.get('firma') and reg['firma'].startswith('data:image'):
            try:
                base64_data = reg['firma'].split(',')[1]
                img_data = base64.b64decode(base64_data)
                img_stream = io.BytesIO(img_data)
                img_element = Image(img_stream, width=90, height=30)
            except Exception:
                img_element = "Error Firma"

        col_auditoria = Paragraph(f"<b>{fecha}</b><br>IP: {ip}<br><font color='#718096'>Hash: {hash_val}</font>", celda_hash_style)
        
        data_tabla.append([
            str(idx),
            Paragraph(f"<b>{nombre}</b>", celda_style),
            dni,
            col_auditoria,
            img_element
        ])

    tabla = Table(data_tabla, colWidths=[25, 150, 75, 175, 110])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))

    story.append(tabla)
    doc.build(story)
    
    buffer.seek(0)
    return buffer
