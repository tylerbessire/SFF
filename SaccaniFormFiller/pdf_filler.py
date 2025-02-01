from pdfrw import PdfReader, PdfWriter, PdfName, PdfDict
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader as PyPdfReader, PdfWriter as PyPdfWriter
from io import BytesIO

class PDFFiller:
    def __init__(self):
        self.field_mapping = {
            'New Account': (1.75, 1.75, 'Checkbox'),
            'Close Account': (1.75, 2.35, 'Checkbox'),
            'Change or Add Info': (5.5, 1.75, 'Checkbox'),
            'Old Account #': (8.4, 2.35, 'TextBox'),
            'Old DBA Name': (8.4, 2.7, 'TextBox'),
            'Account Number for Changes only': (7.61, 3.38, 'TextBox'),
            'LICENSE_NUMBER': (8.53, 7.17, 'TextBox'),
            'PRIMARY_OWNER': (5.18, 4.02, 'TextBox'),
            'BUSINESS_NAME': (2.54, 4.66, 'TextBox'),
            'STREET': (2.82, 5.29, 'TextBox'),
            'CITY': (2.48, 5.93, 'TextBox'),
            'STATE': (7.24, 5.91, 'TextBox'),
            'ZIP_CODE': (9.67, 5.89, 'TextBox'),
            'Buyer': (2.83, 7.17, 'TextBox'),
            'Delivery Location Front': (5.54, 7.8, 'Checkbox'),
            'Delivery Location Back': (6.72, 7.8, 'Checkbox'),
            'Delivery Location Side': (7.6, 7.8, 'Checkbox'),
            'Receiving Times': (4.15, 8.4, 'TextBox'),
            'Special Instructions': (4.92, 9, 'TextBox'),
            'Monday': (4.55, 9.65, 'Checkbox'),
            'Tuesday': (5.88, 9.65, 'Checkbox'),
            'Wednesday': (7.60, 9.65, 'Checkbox'),
            'Thursday': (9.25, 9.6, 'Checkbox'),
            'Friday': (10.62, 9.57, 'Checkbox'),
            'Credit Application Yes': (5.13, 10.17, 'Checkbox'),
            'Credit Application No': (5.8, 10.18, 'Checkbox'),
            'Phone Number': [(3.03, 6.54), (4.06, 6.54), (5.39, 6.54)],
            'COUNTY': (8.63, 10.75, 'TextBox'),
            'On Sale': (2.72, 11.35, 'Checkbox'),
            'Off-Sale': (4.22, 11.35, 'Checkbox'),
            'Draft Status Ours': (7.22, 11.35, 'Checkbox'),
            'Draft Status Theirs': (8.22, 11.35, 'Checkbox'),
            'Draft Status Ours & Theirs': (9.22, 11.35, 'Checkbox'),
            'Draft Status Other': (10.1, 11.35, 'Checkbox'),
            'Market Type Bar': (4.19, 11.79, 'Checkbox'),
            'Market Type Restaurant': (5.39, 11.79, 'Checkbox'),
            'Market Type Grocery': (6.7, 11.79, 'Checkbox'),
            'Market Type Deli': (7.63, 11.79, 'Checkbox'),
            'Market Type Convenience': (8.86, 11.79, 'Checkbox'),
            'Market Type Other': (10.07, 11.79, 'Checkbox'),
            'Buying Yes': (7.06, 12.35, 'Checkbox'),
            'Buying No': (7.71, 12.34, 'Checkbox'),
            'Route #': (3.29, 12.73, 'TextBox'),
            'Salesperson': (7.25, 12.74, 'TextBox'),
            'ACCOUNT_NUMBER': (10.07, 13.39, 'TextBox'),
        }

    def fill_pdf(self, account_data, template_pdf_path, output_folder):
        output_folder = output_folder if output_folder.endswith('/') else output_folder + '/'
        os.makedirs(output_folder, exist_ok=True)
        output_pdf_path = f'{output_folder}{account_data.get("BUSINESS_NAME", "Unknown").replace(" ", "_")}_{account_data.get("LICENSE_NUMBER", "Unknown")}.pdf'

        # Create a new PDF with ReportLab
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        for field, (x, y, field_type) in self.field_mapping.items():
            if field in account_data:
                value = account_data[field]
                if field_type == 'TextBox':
                    can.drawString(x * 72, (11 - y) * 72, str(value))  # Convert inches to points
                elif field_type == 'Checkbox':
                    if value.lower() in ('true', 'yes', 'on', '1'):
                        can.rect(x * 72, (11 - y) * 72, 12, 12, fill=1)  # Draw filled rectangle for checked box
            elif field == 'Phone Number' and 'Phone Number' in account_data:
                phone_parts = account_data['Phone Number'].split('-')
                for i, (x, y) in enumerate(value):
                    if i < len(phone_parts):
                        can.drawString(x * 72, (11 - y) * 72, phone_parts[i])

        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PyPdfReader(packet)

        # Read your existing PDF
        existing_pdf = PyPdfReader(open(template_pdf_path, "rb"))
        output = PyPdfWriter()

        # Add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        # Finally, write "output" to a real file
        output_stream = open(output_pdf_path, "wb")
        output.write(output_stream)
        output_stream.close()

        print(f"PDF saved for {account_data.get('BUSINESS_NAME', 'Unknown')} at {output_pdf_path}")
        return output_pdf_path

    def extract_address_components(self, address):
        parts = [part.strip() for part in address.split(',')]
        street = parts[0] if len(parts) > 0 else ""
        city = parts[1] if len(parts) > 1 else ""
        state = ""
        zip_code = ""
        if len(parts) > 2:
            state_zip = parts[2].strip()
            state_zip_parts = state_zip.split()
            if len(state_zip_parts) > 0:
                state = state_zip_parts[0]
            if len(state_zip_parts) > 1:
                zip_code = state_zip_parts[1]
        return street, city, state, zip_code
