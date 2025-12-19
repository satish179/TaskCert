from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Certificate
from reportlab.pdfgen import canvas
import io

def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

    # Create a PDF buffer
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # Draw certificate content
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, "Certificate of Achievement")

    p.setFont("Helvetica", 14)
    p.drawString(100, 700, f"This is to certify that {certificate.user.get_full_name()}")
    p.drawString(100, 680, f"has successfully passed the {certificate.exam} exam.")
    p.drawString(100, 660, f"Institution: {certificate.institution_name}")
    p.drawString(100, 640, f"Certificate ID: {certificate.certificate_id}")

    # Finalize PDF
    p.showPage()
    p.save()

    # Return PDF as response
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')