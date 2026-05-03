from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from generators.base_generator import BaseGenerator
from models.schemas import DataType
from utils.logger import setup_logger

logger = setup_logger(__name__)

class PDFGenerator(BaseGenerator):
    def __init__(self, structured_output, output_filename=None):
        super().__init__(structured_output, output_filename)
        self.story = []
        self.styles = self._create_styles()
    
    def generate(self) -> Path:
        try:
            logger.info(f"Generating PDF: {self.filepath}")
            
            doc = SimpleDocTemplate(
                str(self.filepath),
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            self._add_title()
            
            if self.output.description:
                self._add_description()
            
            for section in sorted(self.output.sections, key=lambda x: x.order):
                self._add_section(section)
            
            doc.build(self.story)
            logger.info(f"PDF generated: {self.filepath}")
            return self.filepath
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    def get_file_extension(self) -> str:
        return "pdf"
    
    def _create_styles(self):
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor(self.colors['primary']),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.colors['secondary']),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor(self.colors['dark'])
        ))
        
        return styles
    
    def _add_title(self):
        title = Paragraph(self.output.title, self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_description(self):
        desc = Paragraph(self.output.description, self.styles['CustomBody'])
        self.story.append(desc)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_section(self, section):
        if section.type == DataType.HEADING:
            self._add_heading(section)
        elif section.type == DataType.TEXT:
            self._add_text(section)
        elif section.type == DataType.TABLE:
            self._add_table(section)
        elif section.type == DataType.CHART:
            self._add_chart(section)
    
    def _add_heading(self, section):
        text = section.content.get('text', '')
        heading = Paragraph(text, self.styles['CustomHeading'])
        self.story.append(heading)
        self.story.append(Spacer(1, 0.15*inch))
    
    def _add_text(self, section):
        text = section.content.get('text', '')
        para = Paragraph(text, self.styles['CustomBody'])
        self.story.append(para)
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_table(self, section):
        content = section.content
        title = content.get('title', '')
        headers = content.get('headers', [])
        rows = content.get('rows', [])
        
        if title:
            heading = Paragraph(title, self.styles['CustomHeading'])
            self.story.append(heading)
            self.story.append(Spacer(1, 0.1*inch))
        
        data = [headers] + rows
        table = Table(data, colWidths=[2.5*inch/len(headers)] * len(headers))
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['secondary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(self.colors['light'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.colors['secondary'])),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_chart(self, section):
        content = section.content
        title = content.get('title', '')
        chart_type = content.get('type', 'bar')
        labels = content.get('labels', [])
        datasets = content.get('datasets', [])
        
        if title:
            heading = Paragraph(title, self.styles['CustomHeading'])
            self.story.append(heading)
            self.story.append(Spacer(1, 0.1*inch))
        
        chart_path = self._generate_chart(chart_type, labels, datasets)
        
        if chart_path:
            img = RLImage(str(chart_path), width=5*inch, height=3*inch)
            self.story.append(img)
            self.story.append(Spacer(1, 0.2*inch))
    
    def _generate_chart(self, chart_type, labels, datasets) -> Path:
        try:
            plt.figure(figsize=(8, 5))
            
            if chart_type == 'bar':
                for dataset in datasets:
                    plt.bar(labels, dataset['values'], label=dataset.get('name', ''), alpha=0.8)
            elif chart_type == 'line':
                for dataset in datasets:
                    plt.plot(labels, dataset['values'], marker='o', label=dataset.get('name', ''))
            elif chart_type == 'pie':
                if datasets and 'values' in datasets[0]:
                    plt.pie(datasets[0]['values'], labels=labels, autopct='%1.1f%%')
            
            plt.tight_layout()
            
            chart_path = Path(f"/tmp/chart_{id(self)}.png")
            plt.savefig(str(chart_path), dpi=100, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}")
            return None