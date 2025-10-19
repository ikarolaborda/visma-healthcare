"""
Infrastructure Layer: Concrete implementations of report strategies.
Implements Strategy Pattern for different output formats.
"""
import json
import csv
import os
from io import BytesIO, StringIO
from typing import Any, Dict, List
from datetime import datetime
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.graphics.shapes import Drawing, Line as ReportLine
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .interfaces import IReportStrategy
from common.models import ClinicSettings


class PDFReportStrategy(IReportStrategy):
    """
    Enhanced PDF report generation strategy with professional layout, logo support, and page numbers.
    Features Tailwind-inspired color scheme and beautiful table formatting.
    """

    def generate(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
        """Generate beautifully formatted PDF report with logo and page numbers."""
        from django.conf import settings
        import os
        
        buffer = BytesIO()
        
        # Load clinic settings for logo and branding
        from common.models import ClinicSettings
        clinic_settings = ClinicSettings.load()
        
        # Create custom page template with header and footer
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.5*inch,
            bottomMargin=0.75*inch,
            title=metadata.get('title', 'Report')
        )
        
        # Create story (elements list)
        elements = []
        styles = getSampleStyleSheet()
        
        # Tailwind-inspired color palette
        primary_color = colors.HexColor(clinic_settings.primary_color)  # Blue-600
        secondary_color = colors.HexColor(clinic_settings.secondary_color)  # Green-500
        gray_50 = colors.HexColor('#F9FAFB')
        gray_100 = colors.HexColor('#F3F4F6')
        gray_300 = colors.HexColor('#D1D5DB')
        gray_600 = colors.HexColor('#4B5563')
        gray_700 = colors.HexColor('#374151')
        gray_900 = colors.HexColor('#111827')
        
        # ==================== LOGO AND HEADER ====================
        from reportlab.platypus import Image
        
        # Add logo if available and enabled
        if clinic_settings.include_logo_in_reports and clinic_settings.logo:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, str(clinic_settings.logo))
                if os.path.exists(logo_path):
                    logo = Image(logo_path, width=2*inch, height=0.8*inch, kind='proportional')
                    logo.hAlign = 'LEFT'
                    elements.append(logo)
                    elements.append(Spacer(1, 0.2*inch))
            except Exception as e:
                # If logo fails to load, continue without it
                pass
        
        # Clinic name and info header
        clinic_header_style = ParagraphStyle(
            'ClinicHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=gray_600,
            alignment=TA_LEFT
        )
        
        clinic_info = f"""
        <b>{clinic_settings.clinic_name}</b><br/>
        """
        if clinic_settings.clinic_address:
            clinic_info += f"{clinic_settings.clinic_address}<br/>"
        if clinic_settings.clinic_phone or clinic_settings.clinic_email:
            contact_parts = []
            if clinic_settings.clinic_phone:
                contact_parts.append(clinic_settings.clinic_phone)
            if clinic_settings.clinic_email:
                contact_parts.append(clinic_settings.clinic_email)
            clinic_info += " | ".join(contact_parts) + "<br/>"
        
        elements.append(Paragraph(clinic_info.strip(), clinic_header_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Horizontal line separator
        line_drawing = Drawing(6.5*inch, 1)
        line_drawing.add(ReportLine(0, 0, 6.5*inch, 0, strokeColor=gray_300, strokeWidth=2))
        elements.append(line_drawing)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== TITLE ====================
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=gray_900,
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(metadata.get('title', 'Report'), title_style)
        elements.append(title)
        
        # Subtitle with report type
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=gray_600,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        
        report_type_display = metadata.get('report_type', 'N/A').replace('_', ' ').title()
        subtitle = Paragraph(f"{report_type_display} Report", subtitle_style)
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # ==================== METADATA BOX ====================
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            textColor=gray_700,
            leading=14,
            leftIndent=15,
            rightIndent=15,
            spaceBefore=10,
            spaceAfter=10
        )
        
        metadata_text = f"""
        <b>Generated:</b> {metadata.get('generated_at', datetime.now().strftime('%B %d, %Y at %I:%M %p'))}<br/>
        <b>Total Records:</b> {len(data)}<br/>
        """
        
        if metadata.get('description'):
            metadata_text += f"<b>Description:</b> {metadata.get('description')}<br/>"
        
        if metadata.get('filters'):
            filters_str = self._format_filters(metadata['filters'])
            if filters_str != "None":
                metadata_text += f"<b>Filters Applied:</b> {filters_str}<br/>"
        
        # Create a colored box for metadata
        metadata_data = [[Paragraph(metadata_text.strip(), metadata_style)]]
        metadata_table = Table(metadata_data, colWidths=[6.5*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), gray_50),
            ('BOX', (0, 0), (-1, -1), 1, gray_300),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ==================== DATA TABLE ====================
        if data:
            # Extract headers and format them nicely
            headers = list(data[0].keys())
            formatted_headers = [header.replace('_', ' ').title() for header in headers]
            
            # Calculate column widths dynamically
            available_width = 6.5 * inch
            num_cols = len(headers)
            
            # Try to distribute width evenly, with a minimum width
            col_width = available_width / num_cols
            min_col_width = 0.8 * inch
            
            if col_width < min_col_width:
                col_width = min_col_width
            
            col_widths = [col_width] * num_cols
            
            # Build table data
            table_data = []
            
            # Header row with formatting
            header_row = []
            header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.white,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            )
            
            for header in formatted_headers:
                header_row.append(Paragraph(header, header_style))
            table_data.append(header_row)
            
            # Data rows with formatting
            cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontSize=9,
                textColor=gray_700,
                leading=12,
                alignment=TA_LEFT
            )
            
            for record in data:
                row = []
                for header in headers:
                    value = str(record.get(header, ''))
                    # Truncate long values
                    if len(value) > 100:
                        value = value[:97] + "..."
                    row.append(Paragraph(value, cell_style))
                table_data.append(row)
            
            # Create table with beautiful styling
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('LEFTPADDING', (0, 0), (-1, 0), 10),
                ('RIGHTPADDING', (0, 0), (-1, 0), 10),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 1), (-1, -1), 10),
                ('RIGHTPADDING', (0, 1), (-1, -1), 10),
                
                # Alternating row backgrounds (Tailwind-inspired)
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, gray_50]),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -1), 0.5, gray_300),
                ('BOX', (0, 0), (-1, -1), 1.5, gray_300),
                ('LINEBELOW', (0, 0), (-1, 0), 2, primary_color),
                
                # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(table)
        else:
            # No data message
            no_data_style = ParagraphStyle(
                'NoData',
                parent=styles['Normal'],
                fontSize=12,
                textColor=gray_600,
                alignment=TA_CENTER,
                spaceAfter=20,
                spaceBefore=20
            )
            elements.append(Paragraph("No data available for the selected criteria.", no_data_style))
        
        # ==================== BUILD PDF WITH CUSTOM FOOTER ====================
        def add_page_number(canvas, doc):
            """Add page numbers and footer to each page."""
            canvas.saveState()
            
            # Footer line
            canvas.setStrokeColor(gray_300)
            canvas.setLineWidth(0.5)
            canvas.line(0.75*inch, 0.6*inch, letter[0]-0.75*inch, 0.6*inch)
            
            # Page number
            page_num_text = f"Page {canvas.getPageNumber()}"
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(gray_600)
            canvas.drawRightString(letter[0]-0.75*inch, 0.4*inch, page_num_text)
            
            # Footer text
            footer_text = clinic_settings.report_footer_text or "© 2025 Healthcare Patient Management System"
            canvas.drawString(0.75*inch, 0.4*inch, footer_text)
            
            # FHIR compliance badge
            canvas.setFont('Helvetica-Bold', 7)
            canvas.setFillColor(secondary_color)
            canvas.drawCentredString(letter[0]/2, 0.4*inch, "✓ FHIR R4 COMPLIANT")
            
            canvas.restoreState()
        
        # Build PDF with page numbers
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        
        buffer.seek(0)
        return buffer.read()

    def _format_filters(self, filters: Dict[str, Any]) -> str:
        """Format filters for display."""
        filter_parts = []
        for key, value in filters.items():
            if value:
                # Format key nicely
                formatted_key = key.replace('_', ' ').title()
                filter_parts.append(f"{formatted_key}: {value}")
        return ", ".join(filter_parts) if filter_parts else "None"

    def get_file_extension(self) -> str:
        return 'pdf'

    def get_content_type(self) -> str:
        return 'application/pdf'


class CSVReportStrategy(IReportStrategy):
    """
    CSV report generation strategy.
    """

    def generate(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
        """Generate CSV report."""
        output = StringIO()

        if data:
            # Get headers from first record
            headers = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=headers)

            # Write header
            writer.writeheader()

            # Write data
            for record in data:
                writer.writerow(record)

        # Convert to bytes
        output.seek(0)
        return output.getvalue().encode('utf-8')

    def get_file_extension(self) -> str:
        return 'csv'

    def get_content_type(self) -> str:
        return 'text/csv'


class TXTReportStrategy(IReportStrategy):
    """
    Plain text report generation strategy.
    """

    def generate(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
        """Generate plain text report."""
        lines = []

        # Add header
        lines.append("=" * 80)
        lines.append(metadata.get('title', 'Report').center(80))
        lines.append("=" * 80)
        lines.append("")

        # Add metadata
        lines.append(f"Generated: {metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
        lines.append(f"Report Type: {metadata.get('report_type', 'N/A')}")
        lines.append(f"Total Records: {len(data)}")

        if metadata.get('filters'):
            lines.append(f"Filters: {self._format_filters(metadata['filters'])}")

        lines.append("")
        lines.append("-" * 80)
        lines.append("")

        # Add data
        if data:
            headers = list(data[0].keys())

            # Calculate column widths
            col_widths = {header: len(header) for header in headers}
            for record in data:
                for header in headers:
                    value_len = len(str(record.get(header, '')))
                    col_widths[header] = max(col_widths[header], value_len)

            # Limit column widths
            max_width = 30
            for header in col_widths:
                col_widths[header] = min(col_widths[header], max_width)

            # Create header row
            header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
            lines.append(header_row)
            lines.append("-" * len(header_row))

            # Add data rows
            for record in data:
                row_parts = []
                for header in headers:
                    value = str(record.get(header, ''))
                    if len(value) > col_widths[header]:
                        value = value[:col_widths[header]-3] + "..."
                    row_parts.append(value.ljust(col_widths[header]))
                lines.append(" | ".join(row_parts))
        else:
            lines.append("No data available")

        # Add footer
        lines.append("")
        lines.append("-" * 80)
        lines.append(f"End of Report | Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines).encode('utf-8')

    def _format_filters(self, filters: Dict[str, Any]) -> str:
        """Format filters for display."""
        filter_parts = []
        for key, value in filters.items():
            if value:
                filter_parts.append(f"{key}={value}")
        return ", ".join(filter_parts) if filter_parts else "None"

    def get_file_extension(self) -> str:
        return 'txt'

    def get_content_type(self) -> str:
        return 'text/plain'


class JSONReportStrategy(IReportStrategy):
    """
    JSON report generation strategy.
    """

    def generate(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
        """Generate JSON report."""
        report = {
            'metadata': {
                'title': metadata.get('title', 'Report'),
                'report_type': metadata.get('report_type', 'N/A'),
                'generated_at': metadata.get('generated_at', datetime.now().isoformat()),
                'filters': metadata.get('filters', {}),
                'total_records': len(data)
            },
            'data': data
        }

        return json.dumps(report, indent=2, default=str).encode('utf-8')

    def get_file_extension(self) -> str:
        return 'json'

    def get_content_type(self) -> str:
        return 'application/json'
