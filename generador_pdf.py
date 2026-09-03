# 1. Márgenes reducidos del documento
doc = SimpleDocTemplate(
    buffer,
    pagesize=A4,
    rightMargin=20,
    leftMargin=20,
    topMargin=15,
    bottomMargin=15
)

# ... (código previo) ...

# 2. Tamaño de imagen de firma ajustado
img_element = Image(img_stream, width=70, height=18)  # Alto reducido a 18px

# 3. Estilos de celda compactos
celda_trabajador = ParagraphStyle('CeldaTrabajador', fontSize=7.5, leading=9, textColor=GRIS_TEXTO)
celda_hash_style = ParagraphStyle('CeldaHash', fontSize=6, leading=7.5, textColor=colors.HexColor('#546E7A'))

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
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),  # Padding reducido al mínimo
    ('TOPPADDING', (0,0), (-1,-1), 2),     # Padding reducido al mínimo
]))
