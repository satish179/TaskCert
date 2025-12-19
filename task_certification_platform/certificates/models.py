import uuid
import os
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from exams.models import ExamAttempt

User = get_user_model()

def certificate_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/certificates/user_<id>/<filename>
    return f'certificates/user_{instance.user.id}/{filename}'

class Certificate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    exam_attempt = models.OneToOneField(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='certificate',
        null=True,
        blank=True
    )
    certificate_number = models.CharField(max_length=50, unique=True, editable=False)
    issue_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pdf_file = models.FileField(
        upload_to=certificate_upload_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    verification_url = models.URLField(blank=True, null=True)
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Certificate design fields
    title = models.CharField(max_length=200, default='Certificate of Completion')
    description = models.TextField(blank=True, null=True)
    organization_name = models.CharField(max_length=255, default='Your Organization')
    organization_logo = models.ImageField(
        upload_to='certificates/logos/',
        null=True,
        blank=True,
        help_text='Organization logo to be displayed on the certificate.'
    )
    signature = models.ImageField(
        upload_to='certificates/signatures/',
        null=True,
        blank=True,
        help_text='Signature image to be displayed on the certificate.'
    )
    signatory_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Name of the person signing the certificate.'
    )
    signatory_title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Title of the person signing the certificate.'
    )

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        permissions = [
            ('can_verify_certificate', 'Can verify certificate authenticity'),
        ]

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        
        if not self.verification_url:
            self.verification_url = self.get_verification_url()
            
        super().save(*args, **kwargs)
        
        # Generate PDF certificate if it doesn't exist
        if not self.pdf_file:
            self.generate_pdf_certificate()

    def generate_certificate_number(self):
        """Generate a unique certificate number."""
        prefix = 'CERT'
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4().hex[:8].upper())
        return f"{prefix}-{timestamp}-{unique_id}"

    def get_verification_url(self):
        """Generate a verification URL for this certificate."""
        if not self.verification_code:
            self.verification_code = uuid.uuid4()
        return f"{settings.SITE_URL}/verify-certificate/{self.verification_code}/"

    def is_valid(self):
        """Check if the certificate is valid (not expired and active)."""
        if not self.is_active:
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True

    def generate_pdf_certificate(self):
        """Generate a PDF certificate for this record."""
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer
        from reportlab.lib.units import inch
        from django.core.files import File
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file."
        width, height = letter  # 8.5 x 11 inches
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        
        # Set up styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=1  # Center alignment
        )
        
        recipient_style = ParagraphStyle(
            'Recipient',
            parent=styles['Heading2'],
            fontSize=20,
            spaceAfter=30,
            alignment=1
        )
        
        description_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=40,
            alignment=1
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=50,
            alignment=1
        )
        
        # Draw a border
        p.setStrokeColor(colors.HexColor('#CCCCCC'))
        p.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch, stroke=1, fill=0)
        
        # Add organization logo if available
        if self.organization_logo and os.path.exists(self.organization_logo.path):
            try:
                logo = Image(self.organization_logo.path, width=2*inch, height=1*inch)
                logo.drawOn(p, (width - logo.drawWidth) / 2, height - 2*inch)
                y_position = height - 2.5*inch
            except:
                y_position = height - 2*inch
        else:
            y_position = height - 2*inch
        
        # Add title
        title = Paragraph(self.title, title_style)
        title.wrapOn(p, width-2*inch, 50)
        title.drawOn(p, inch, y_position)
        y_position -= title.height + 20
        
        # Add "awarded to" text
        p.setFont("Helvetica", 14)
        p.drawCentredString(width/2, y_position, "This certificate is proudly presented to")
        y_position -= 30
        
        # Add recipient name
        recipient = Paragraph(f"<b>{self.user.get_full_name()}</b>", recipient_style)
        recipient.wrapOn(p, width-2*inch, 50)
        recipient.drawOn(p, inch, y_position - recipient.height)
        y_position -= recipient.height + 30
        
        # Add description
        if self.description:
            description = Paragraph(self.description, description_style)
            description.wrapOn(p, width-4*inch, 100)
            description.drawOn(p, 2*inch, y_position - description.height)
            y_position -= description.height + 40
        
        # Add completion details
        p.setFont("Helvetica", 12)
        if self.exam_attempt and self.exam_attempt.exam:
            p.drawCentredString(width/2, y_position, f"For successful completion of {self.exam_attempt.exam.title}")
            y_position -= 20
            p.drawCentredString(width/2, y_position, f"with a score of {self.exam_attempt.score:.1f}%")
            y_position -= 30
        
        # Add issue date
        p.drawCentredString(width/2, y_position, f"Issued on: {self.issue_date.strftime('%B %d, %Y')}")
        y_position -= 50
        
        # Add signature line
        p.line(width/2 - 100, y_position, width/2 + 100, y_position)
        y_position -= 20
        
        # Add signatory name and title
        if self.signature and os.path.exists(self.signature.path):
            try:
                signature = Image(self.signature.path, width=1.5*inch, height=0.5*inch)
                signature.drawOn(p, (width - signature.drawWidth) / 2, y_position - 0.7*inch)
                y_position -= 0.8*inch
            except:
                pass
        
        if self.signatory_name:
            p.drawCentredString(width/2, y_position, self.signatory_name)
            y_position -= 15
            if self.signatory_title:
                p.setFont("Helvetica-Oblique", 10)
                p.drawCentredString(width/2, y_position, self.signatory_title)
                p.setFont("Helvetica", 12)
        
        # Add footer with verification info
        footer_text = f"Certificate ID: {self.certificate_number} | "
        footer_text += f"Verify at: {settings.SITE_URL}/verify/{self.verification_code}/"
        
        p.setFont("Helvetica", 8)
        p.drawCentredString(width/2, 0.75*inch, footer_text)
        
        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()
        
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        
        # Save the PDF to the model
        filename = f"certificate_{self.certificate_number}.pdf"
        self.pdf_file.save(filename, File(buffer), save=False)
        
        # Save the model again to update the pdf_file field
        super().save(update_fields=['pdf_file'])
        
        return self.pdf_file

    def send_certificate_email(self, request=None):
        """Send the certificate via email to the recipient."""
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        if not self.pdf_file:
            self.generate_pdf_certificate()
        
        subject = f"Your Certificate: {self.title}"
        
        # Render HTML email template
        context = {
            'certificate': self,
            'user': self.user,
            'verification_url': self.get_verification_url(),
        }
        
        html_message = render_to_string('certificates/email/certificate_issued.html', context)
        plain_message = strip_tags(html_message)
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        
        # Attach the PDF
        email.attach_file(self.pdf_file.path)
        
        # Send email
        email.send(fail_silently=False)

    def revoke(self, reason=None):
        """Revoke this certificate."""
        self.is_active = False
        self.save(update_fields=['is_active'])
        
        # Log the revocation
        CertificateRevocation.objects.create(
            certificate=self,
            reason=reason or "Revoked by administrator",
            revoked_by=self.user
        )
        
        # Optionally notify the user
        self.send_revocation_notification(reason)

    def send_revocation_notification(self, reason=None):
        """Send notification that this certificate has been revoked."""
        from django.core.mail import send_mail
        
        subject = f"Certificate Revoked: {self.title}"
        message = f"""
        Dear {self.user.get_full_name()},
        
        We regret to inform you that your certificate has been revoked.
        
        Certificate: {self.title}
        Certificate ID: {self.certificate_number}
        Issue Date: {self.issue_date.strftime('%B %d, %Y')}
        
        Reason: {reason or 'Not specified'}
        
        If you believe this is an error, please contact our support team.
        """
        
        send_mail(
            subject=subject.strip(),
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            fail_silently=False,
        )


class CertificateTemplate(models.Model):
    """Template for generating certificates."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_file = models.FileField(
        upload_to='certificate_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html', 'htm'])]
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one default template exists
        if self.is_default:
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class CertificateRevocation(models.Model):
    """Track certificate revocations."""
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='revocations'
    )
    revoked_at = models.DateTimeField(auto_now_add=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='revoked_certificates'
    )
    reason = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-revoked_at']
        verbose_name = 'Certificate Revocation'
        verbose_name_plural = 'Certificate Revocations'
    
    def __str__(self):
        return f"Revocation of {self.certificate} on {self.revoked_at}"
