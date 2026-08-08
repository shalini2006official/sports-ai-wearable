from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


def generate_report(sensor_data, ai_analysis):

    pdf = SimpleDocTemplate("Sports_AI_Report.pdf")

    story = []

    story.append(Paragraph("<b>Sports AI Performance Report</b>", styles["Heading1"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Heart Rate:</b> {} BPM".format(sensor_data["heart_rate"]), styles["Normal"]))

    story.append(Paragraph("<b>SpO2:</b> {} %".format(sensor_data["spo2"]), styles["Normal"]))

    story.append(Paragraph("<b>Fatigue:</b> {} %".format(sensor_data["fatigue"]), styles["Normal"]))

    story.append(Paragraph("<b>Performance:</b> {}".format(sensor_data["performance"]), styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>AI Analysis</b>", styles["Heading2"]))

    story.append(Paragraph(ai_analysis.replace("\n", "<br/>"), styles["Normal"]))

    pdf.build(story)

    return "Sports_AI_Report.pdf"