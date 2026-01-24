"""
PDF Generation Service
Tạo PDF bằng cấp từ template và nhúng QR Code
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from datetime import datetime
from typing import Dict, Any


class DiplomaPDFGenerator:
    """
    Service để generate PDF bằng cấp
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
    
    def generate_diploma_pdf(
        self,
        student_info: Dict[str, Any],
        school_info: Dict[str, Any],
        file_hash: str,
        signature: str,
        verify_base_url: str = "https://verify.edu.vn"
    ) -> BytesIO:
        """
        Tạo PDF bằng cấp
        
        Args:
            student_info: Thông tin sinh viên
            school_info: Thông tin trường
            file_hash: Hash của PDF (để tạo QR)
            signature: Chữ ký số
            verify_base_url: Base URL cho verification
            
        Returns:
            BytesIO chứa PDF content
        """
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # 1. Vẽ border
        self._draw_border(pdf)
        
        # 2. Vẽ header
        self._draw_header(pdf, school_info)
        
        # 3. Vẽ nội dung bằng
        self._draw_diploma_content(pdf, student_info)
        
        # 4. Vẽ chữ ký
        self._draw_signature_section(pdf, school_info)
        
        # 5. Nhúng QR Code
        verify_url = f"{verify_base_url}/diploma/{file_hash}"
        self._embed_qr_code(pdf, verify_url)
        
        # 6. Thêm metadata
        pdf.setTitle(f"Diploma - {student_info['studentName']}")
        pdf.setAuthor(school_info['name'])
        pdf.setSubject("University Diploma")
        
        # Custom metadata (signature)
        pdf.setKeywords(f"signature:{signature}")
        
        pdf.save()
        buffer.seek(0)
        return buffer
    
    def _draw_border(self, pdf: canvas.Canvas):
        """Vẽ viền trang trí"""
        margin = 20 * mm
        pdf.setLineWidth(2)
        pdf.setStrokeColorRGB(0.2, 0.2, 0.6)
        pdf.rect(margin, margin, self.page_width - 2*margin, self.page_height - 2*margin)
        
        # Inner border
        pdf.setLineWidth(0.5)
        inner_margin = 25 * mm
        pdf.rect(inner_margin, inner_margin, 
                self.page_width - 2*inner_margin, 
                self.page_height - 2*inner_margin)
    
    def _draw_header(self, pdf: canvas.Canvas, school_info: Dict[str, Any]):
        """Vẽ header với tên trường"""
        y = self.page_height - 40 * mm
        
        # Tên nước
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(self.page_width / 2, y, "SOCIALIST REPUBLIC OF VIETNAM")
        
        y -= 15
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(self.page_width / 2, y, "Independence - Freedom - Happiness")
        
        y -= 25
        # Tên trường
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(self.page_width / 2, y, school_info['name'].upper())
        
        y -= 30
        # Tiêu đề DIPLOMA
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColorRGB(0.2, 0.2, 0.6)
        pdf.drawCentredString(self.page_width / 2, y, "DIPLOMA")
    
    def _draw_diploma_content(self, pdf: canvas.Canvas, student_info: Dict[str, Any]):
        """Vẽ nội dung bằng cấp"""
        y = self.page_height / 2 + 20 * mm
        x_center = self.page_width / 2
        
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica", 12)
        
        # This is to certify that
        pdf.drawCentredString(x_center, y, "This is to certify that")
        
        y -= 20
        # Tên sinh viên
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(x_center, y, student_info['studentName'].upper())
        
        y -= 25
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(x_center, y, f"Student ID: {student_info['studentId']}")
        
        y -= 25
        pdf.drawCentredString(x_center, y, "has successfully completed the requirements for the degree of")
        
        y -= 20
        # Ngành học
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(x_center, y, f"Bachelor of {student_info['major']}")
        
        y -= 25
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(x_center, y, f"with {student_info['grade']} honors")
        
        y -= 25
        # Ngày cấp
        issue_date = datetime.strptime(student_info['issueDate'], "%Y-%m-%d")
        pdf.drawCentredString(x_center, y, 
                            f"Issued on {issue_date.strftime('%B %d, %Y')}")
    
    def _draw_signature_section(self, pdf: canvas.Canvas, school_info: Dict[str, Any]):
        """Vẽ phần chữ ký"""
        y = 80 * mm
        x_right = self.page_width - 60 * mm
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(x_right, y, "PRESIDENT")
        
        y -= 30
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawCentredString(x_right, y, "(Digitally Signed)")
        
        y -= 15
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(x_right, y, "________________________")
    
    def _embed_qr_code(self, pdf: canvas.Canvas, verify_url: str):
        """Nhúng QR Code vào PDF"""
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to ImageReader
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)
        
        # Draw QR Code
        qr_size = 40 * mm
        x = 30 * mm
        y = 30 * mm
        pdf.drawImage(qr_image, x, y, width=qr_size, height=qr_size)
        
        # Add text below QR
        pdf.setFont("Helvetica", 7)
        pdf.drawCentredString(x + qr_size/2, y - 10, "Scan to verify")


# Singleton instance
_pdf_generator = None

def get_pdf_generator() -> DiplomaPDFGenerator:
    """Get singleton PDF generator"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = DiplomaPDFGenerator()
    return _pdf_generator
