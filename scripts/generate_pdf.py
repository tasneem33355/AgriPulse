import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 750, 558, 750)
        self.drawString(54, 755, "AgriPulse — Predictive Maintenance Instrumentation Guide (v3.0)")
        
        # Footer line
        self.line(54, 45, 558, 45)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.drawString(54, 32, "CONFIDENTIAL — Graduation Project Engineering Reference")
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("AgriPulse: Target Machine & Sensor Instrumentation Guide", title_style))
    story.append(Paragraph("Engineering Reference for Two-Stage Centrifugal Pumping System & Benchtop Prototype (v3.0)", subtitle_style))

    # Metadata Box
    meta_data = [
        [Paragraph("<b>Target Asset:</b> Two-Stage Centrifugal Water Pump", table_body_style),
         Paragraph("<b>Telemetry Archive:</b> IBM/Kaggle (220,320 rows)", table_body_style)],
        [Paragraph("<b>Standard Ref:</b> ISO 10816-3, ANSI/HI 9.6, ISA-18.2", table_body_style),
         Paragraph("<b>Deployment Target:</b> Railway Cloud & ESP32 IoT Gateway", table_body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Target Asset Architecture & Mechanical Provenance", h1_style))
    story.append(Paragraph(
        "The AgriPulse predictive maintenance system is trained on high-resolution continuous telemetry from an industrial "
        "<b>Two-Stage Centrifugal Pumping System</b>. Telemetry encompasses 220,320 consecutive one-minute records (April–August 2018) "
        "containing 7 recorded failure events. The asset features a three-phase motor driving a two-stage pump casing via a flexible mechanical coupling.",
        body_style
    ))

    # Section 2: Sensor Configuration Table
    story.append(Paragraph("2. Core-7 Sensor Instrumentation & Physics Mapping", h1_style))
    story.append(Paragraph(
        "Through empirical feature ablation on historical failure events, a Core-7 sensor group was established, monitoring "
        "the primary mechanical, electrical, and hydraulic stress nodes:",
        body_style
    ))

    sensor_data = [
        [Paragraph("Sensor ID", table_header_style), Paragraph("Monitored Location", table_header_style), Paragraph("Physical Quantity & Failure Mode", table_header_style), Paragraph("Nominal Baseline", table_header_style)],
        [Paragraph("sensor_00", table_body_style), Paragraph("Motor DE Bearing", table_body_style), Paragraph("Radial vibration, race fatigue, rotor unbalance", table_body_style), Paragraph("~1.4 - 2.5", table_body_style)],
        [Paragraph("sensor_04", table_body_style), Paragraph("Motor Drive Shaft", table_body_style), Paragraph("Rotational speed proxy, motor slip (CPM)", table_body_style), Paragraph("~630 - 640", table_body_style)],
        [Paragraph("sensor_05", table_body_style), Paragraph("Motor Stator Feed (A)", table_body_style), Paragraph("Current draw, winding electrical load", table_body_style), Paragraph("~70 - 80", table_body_style)],
        [Paragraph("sensor_11", table_body_style), Paragraph("Motor Stator Feed (B)", table_body_style), Paragraph("Secondary current tap, phase balance", table_body_style), Paragraph("~45 - 55", table_body_style)],
        [Paragraph("sensor_13", table_body_style), Paragraph("Flexible Shaft Coupling", table_body_style), Paragraph("Axial vibration, angular/parallel misalignment", table_body_style), Paragraph("~1.5 - 3.2", table_body_style)],
        [Paragraph("sensor_28", table_body_style), Paragraph("Stage-2 Impeller", table_body_style), Paragraph("Stage 2 rotational speed / cavitation proxy", table_body_style), Paragraph("~1020 - 1080", table_body_style)],
        [Paragraph("sensor_40", table_body_style), Paragraph("Thrust Bearing Housing", table_body_style), Paragraph("Thrust bearing temperature, lubrication failure", table_body_style), Paragraph("~50 - 65 °C", table_body_style)],
    ]
    sensor_table = Table(sensor_data, colWidths=[65, 120, 230, 89])
    sensor_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sensor_table)
    story.append(Spacer(1, 10))

    # Section 3: Diagnostic Decision Matrix
    story.append(Paragraph("3. Directional Multi-Sensor Diagnostic Signatures", h1_style))
    story.append(Paragraph(
        "Root cause isolation uses directional multi-sensor pattern matching rather than isolated single-sensor thresholds:",
        body_style
    ))

    rules_data = [
        [Paragraph("Fault Category", table_header_style), Paragraph("Sensor Signature", table_header_style), Paragraph("Physical Mechanism & Action", table_header_style)],
        [Paragraph("Coupling Misalignment", table_body_style), Paragraph("sensor_13 (↑) + sensor_00 (↑)", table_body_style), Paragraph("Simultaneous axial & DE radial vibration surge indicates coupling misalignment or degraded elastomeric insert.", table_body_style)],
        [Paragraph("Hydraulic Binding", table_body_style), Paragraph("sensor_05 (↑) + sensor_28 (↓)", table_body_style), Paragraph("Current draw surges while impeller speed decelerates, confirming internal impeller obstruction or closed valve.", table_body_style)],
        [Paragraph("Lubrication Starvation", table_body_style), Paragraph("sensor_40 (↑) with normal vib", table_body_style), Paragraph("Isolated thermal rise without mechanical vibration indicates grease dry-out or degradation.", table_body_style)],
        [Paragraph("Bearing Raceway Fatigue", table_body_style), Paragraph("sensor_00 (↑) isolated", table_body_style), Paragraph("DE radial vibration elevation with stable coupling indicates localized bearing spalling/flaking.", table_body_style)],
        [Paragraph("Decoupling / Flatline", table_body_style), Paragraph("std_60 < 1e-3 (variance collapse)", table_body_style), Paragraph("Addresses Event 5 blindspot: flags sensor disconnection or zero-variance failure immediately.", table_body_style)],
    ]
    rules_table = Table(rules_data, colWidths=[120, 140, 244])
    rules_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D9488")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(rules_table)
    story.append(Spacer(1, 10))

    # Page Break for Hardware Rig Section
    story.append(PageBreak())

    # Section 4: Operational Cutoffs & Alarm Debouncing
    story.append(Paragraph("4. Industrial Alarm Debouncing (ANSI/ISA-18.2)", h1_style))
    story.append(Paragraph(
        "To suppress transient electrical spikes and reduce false alarms, the real-time engine enforces stateful time persistence:",
        body_style
    ))

    thresh_data = [
        [Paragraph("Alarm Tier", table_header_style), Paragraph("Calibrated Cutoff", table_header_style), Paragraph("Debounce Requirement", table_header_style), Paragraph("Verified Operational Lead Time", table_header_style)],
        [Paragraph("WARNING", table_body_style), Paragraph("0.3017 (June 95.0%)", table_body_style), Paragraph("5 Consecutive Minutes", table_body_style), Paragraph("Up to 120 minutes prior to failure", table_body_style)],
        [Paragraph("CRITICAL", table_body_style), Paragraph("0.3691 (June 98.5%)", table_body_style), Paragraph("8 Consecutive Minutes", table_body_style), Paragraph("46 min (Event 6), 70 min (Event 7)", table_body_style)],
    ]
    thresh_table = Table(thresh_data, colWidths=[90, 110, 130, 174])
    thresh_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(thresh_table)
    story.append(Spacer(1, 12))

    # Section 5: Benchtop Prototype Mapping
    story.append(Paragraph("5. Benchtop Scale Prototype (12V DC Pump Rig)", h1_style))
    story.append(Paragraph(
        "A physical test bench demonstrates the real-time IoT-to-cloud acquisition chain using an ESP32 microcontroller "
        "and a 12V DC circulating pump loop. Telemetry is adapted dynamically using relative Z-score normalization:",
        body_style
    ))

    bom_data = [
        [Paragraph("Channel / Role", table_header_style), Paragraph("Component", table_header_style), Paragraph("Interface / Address", table_header_style), Paragraph("Bench Operating Range", table_header_style)],
        [Paragraph("Motor Vibration", table_body_style), Paragraph("ADXL345 Accelerometer", table_body_style), Paragraph("I2C (0x53)", table_body_style), Paragraph("0.1 to 0.8 g RMS", table_body_style)],
        [Paragraph("Coupling Vibration", table_body_style), Paragraph("ADXL345 Accelerometer", table_body_style), Paragraph("I2C (0x1D, SDO to 3.3V)", table_body_style), Paragraph("0.05 to 0.5 g RMS", table_body_style)],
        [Paragraph("Motor Current", table_body_style), Paragraph("ACS712 30A DC Module", table_body_style), Paragraph("ADS1115 A0 (Analog)", table_body_style), Paragraph("1.8 to 3.5 A DC", table_body_style)],
        [Paragraph("Surface Temp", table_body_style), Paragraph("DS18B20 Waterproof Probe", table_body_style), Paragraph("1-Wire (GPIO 4)", table_body_style), Paragraph("25 to 45 °C", table_body_style)],
        [Paragraph("Discharge Pressure", table_body_style), Paragraph("G1/4\" Transducer (1.2 MPa)", table_body_style), Paragraph("ADS1115 A1 (Analog)", table_body_style), Paragraph("0.4 to 0.9 bar", table_body_style)],
        [Paragraph("Water Flow Rate", table_body_style), Paragraph("YF-S201 Turbine Meter", table_body_style), Paragraph("Pulse Interrupt (GPIO 34)", table_body_style), Paragraph("3.0 to 7.5 L/min", table_body_style)],
    ]
    bom_table = Table(bom_data, colWidths=[100, 140, 130, 134])
    bom_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#B45309")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(bom_table)
    story.append(Spacer(1, 10))

    # Concluding Callout
    callout_data = [[
        Paragraph(
            "<b>Engineering Notice:</b> The prototype demonstrates <i>methodology transfer</i> (streaming feature calculation, "
            "temporal debouncing, and multi-sensor fault isolation) rather than direct weight transfer. When running in "
            "prototype mode (<code>mode: 'prototype'</code>), the engine automatically employs self-calibrating relative deviations.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == "__main__":
    out_path = r"c:\My Download\تخرج\AgriPulse\docs\Target_Machine_and_Sensor_Instrumentation_Guide.pdf"
    build_pdf(out_path)
