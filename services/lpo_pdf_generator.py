"""
LPO PDF Generator Service
Converts LPO data to professional PDF using WeasyPrint and HTML template
"""
from weasyprint import HTML, CSS
from flask import render_template
import os
from datetime import datetime


class LPOPDFGenerator:
    """Service for generating LPO PDFs"""
    
    @staticmethod
    def generate_pdf(lpo, output_path=None):
        """
        Generate PDF from LPO object
        
        Args:
            lpo: LPO model instance
            output_path: Optional file path to save PDF. If None, returns PDF bytes
        
        Returns:
            PDF file path if output_path provided, else bytes
        """
        # Prepare data for template
        template_data = LPOPDFGenerator._prepare_template_data(lpo)
        
        # Render HTML from template
        html_content = render_template('lpo_template.html', **template_data)
        
        # Generate PDF
        pdf = HTML(string=html_content).write_pdf()
        
        if output_path:
            # Save to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(pdf)
            return output_path
        else:
            # Return bytes
            return pdf
    
    @staticmethod
    def _prepare_template_data(lpo):
        """
        Prepare LPO data for template rendering
        
        Args:
            lpo: LPO model instance
        
        Returns:
            Dict with template variables
        """
        # Format dates
        lpo_date_formatted = lpo.lpo_date.strftime('%d/%m/%Y') if lpo.lpo_date else ''
        quotation_date_formatted = lpo.quotation_date.strftime('%d/%m/%Y') if lpo.quotation_date else ''
        delivery_date_formatted = lpo.delivery_date.strftime('%d/%m/%Y') if lpo.delivery_date else ''
        
        # Process items for display
        display_items = []
        for item in lpo.items:
            display_item = {
                'number': item.get('number', ''),
                'quantity': item.get('quantity', item.get('qty', '')),
                'unit': item.get('unit', ''),
                'unit_price': item.get('unit_price', item.get('rate', item.get('price', 0))),
                'vat_amount': item.get('vat_amount', 0),
                'total_amount': item.get('total_amount', 0)
            }
            
            # Add dynamic columns based on column_structure
            for col in lpo.column_structure:
                col_key = col.lower().replace(' ', '_').replace('.', '')
                display_item[col_key] = item.get(col_key, item.get(col, '-'))
            
            display_items.append(display_item)
        
        # Calculate totals in words (for grand total)
        grand_total_words = LPOPDFGenerator._number_to_words(float(lpo.grand_total))
        
        return {
            # Header
            'lpo_number': lpo.lpo_number,
            'revision': lpo.revision,
            'lpo_date': lpo_date_formatted,
            
            # Project Info
            'project_name': lpo.project_name,
            'project_location': lpo.project_location or '',
            'consultant': lpo.consultant or '',
            
            # Supplier Info
            'supplier_name': lpo.supplier_name,
            'supplier_address': lpo.supplier_address or '',
            'supplier_trn': lpo.supplier_trn or '',
            'supplier_tel': lpo.supplier_tel or '',
            'supplier_fax': lpo.supplier_fax or '',
            'contact_person': lpo.contact_person or '',
            'contact_number': lpo.contact_number or '',
            
            # Reference
            'quotation_ref': lpo.quotation_ref or '',
            'quotation_date': quotation_date_formatted,
            'delivery_date': delivery_date_formatted,
            
            # Items
            'column_structure': lpo.column_structure,
            'items': display_items,
            
            # Totals
            'subtotal': float(lpo.subtotal),
            'vat_percentage': float(lpo.vat_percentage),
            'vat_amount': float(lpo.vat_amount),
            'grand_total': float(lpo.grand_total),
            'grand_total_words': grand_total_words,
            
            # Terms
            'payment_terms': lpo.payment_terms or 'As per agreement',
            'delivery_terms': lpo.delivery_terms or 'As per LPO requirement',
            'warranty_terms': lpo.warranty_terms or 'As per manufacturer warranty',
            'other_terms': lpo.other_terms or '',
            
            # Notes
            'notes': lpo.notes or '',
            
            # Footer
            'generated_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'is_draft': lpo.status == 'draft'
        }
    
    @staticmethod
    def _number_to_words(number):
        """
        Convert number to words for UAE Dirhams
        Example: 1250.50 -> "One Thousand Two Hundred Fifty Dirhams and Fifty Fils"
        """
        # Simple implementation - can be enhanced with inflect library
        try:
            number = float(number)
            dirhams = int(number)
            fils = int(round((number - dirhams) * 100))
            
            # Basic number to words (simplified)
            ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
            teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 
                    'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
            tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
            thousands = ['', 'Thousand', 'Million', 'Billion']
            
            if dirhams == 0:
                words = 'Zero'
            else:
                words = LPOPDFGenerator._convert_group(dirhams, ones, teens, tens, thousands)
            
            result = f"{words} Dirhams"
            
            if fils > 0:
                fils_words = LPOPDFGenerator._convert_group(fils, ones, teens, tens, [])
                result += f" and {fils_words} Fils"
            
            return result + " Only"
        
        except Exception:
            return f"AED {number:.2f}"
    
    @staticmethod
    def _convert_group(number, ones, teens, tens, thousands):
        """Helper to convert number groups to words"""
        if number == 0:
            return ''
        
        # Simple conversion for numbers up to 999,999
        if number < 10:
            return ones[number]
        elif number < 20:
            return teens[number - 10]
        elif number < 100:
            return tens[number // 10] + (' ' + ones[number % 10] if number % 10 != 0 else '')
        elif number < 1000:
            return ones[number // 100] + ' Hundred' + (' ' + LPOPDFGenerator._convert_group(number % 100, ones, teens, tens, thousands) if number % 100 != 0 else '')
        elif number < 1000000:
            return LPOPDFGenerator._convert_group(number // 1000, ones, teens, tens, thousands) + ' Thousand' + (' ' + LPOPDFGenerator._convert_group(number % 1000, ones, teens, tens, thousands) if number % 1000 != 0 else '')
        else:
            return str(number)
    
    @staticmethod
    def get_pdf_filename(lpo):
        """
        Generate standard PDF filename for LPO
        Format: LPO_PKP_2025_0001_rev00.pdf
        """
        # Replace slashes with underscores
        clean_number = lpo.lpo_number.replace('/', '_')
        filename = f"{clean_number}_rev{lpo.revision}.pdf"
        return filename
    
    @staticmethod
    def get_pdf_storage_path(lpo, base_dir='lpo_pdfs'):
        """
        Get full storage path for LPO PDF
        Organizes by year and month
        """
        year = lpo.lpo_date.year if lpo.lpo_date else datetime.now().year
        month = lpo.lpo_date.month if lpo.lpo_date else datetime.now().month
        
        # Create directory structure: lpo_pdfs/2025/01/
        directory = os.path.join(base_dir, str(year), f"{month:02d}")
        filename = LPOPDFGenerator.get_pdf_filename(lpo)
        
        return os.path.join(directory, filename)
