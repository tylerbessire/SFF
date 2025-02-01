from pdfrw import PdfReader, PdfWriter, PdfName, PdfDict
import os

class PDFFiller:
    def __init__(self):
        self.checkbox_fields = {
            "NEW ACCOUNT CHECKBOX": "New Account",
            "dhFormfield-4142143975": "Close Account",
            "dhFormfield-4142144245": "Change or Add Info",
            "dhFormfield-4142144376": "Delivery Location Front",
            "dhFormfield-4142144379": "Delivery Location Back",
            "dhFormfield-4142144381": "Delivery Location Side",
            "dhFormfield-4142144430": "True",
            "dhFormfield-4142144579": 'on',
            "dhFormfield-4142144586": "on",
            "dhFormfield-4142144590": "Thursday",
            "dhFormfield-4142144593": "Friday",
            "dhFormfield-4142144596": "Credit Application Yes",
            "dhFormfield-4142144622": "Credit Application No",
            "dhFormfield-4142144642": "On Sale",
            "dhFormfield-4142144644": "Off-Sale",
            "dhFormfield-4142144650": "Draft Status Ours",
            "dhFormfield-4142144727": "Draft Status Theirs",
            "dhFormfield-4142144729": "Draft Status Ours & Theirs",
            "dhFormfield-4142144743": "Market Type Bar",
            "dhFormfield-4142144745": "Market Type Restaurant",
            "dhFormfield-4142144747": "Market Type Grocery",
            "dhFormfield-4142144749": "Market Type Deli",
            "dhFormfield-4142144831": "Market Type Convenience",
            "dhFormfield-4142144870": "Market Type Other",
            "dhFormfield-4142144871": "Buying Yes",
            "dhFormfield-4142144873": "Buying No"
        }
        
        self.field_mapping = {
            'LICENSE_NUMBER': 'dhFormfield-4142141861',
            'PRIMARY_OWNER': 'dhFormfield-4142140595',
            'BUSINESS_NAME': 'dhFormfield-4142140675',
            'STREET': 'dhFormfield-4142140681',
            'CITY': 'dhFormfield-4142140699',
            'STATE': 'dhFormfield-4142140862',
            'ZIP_CODE': 'dhFormfield-4142141170',
            'COUNTY': 'dhFormfield-4142142275',
            'ACCOUNT_NUMBER': 'dhFormfield-4142143057',
            'Old Account #': 'dhFormfield-4142140357',
            'Old DBA Name': 'dhFormfield-4142140423',
            'Account Number for Changes only': 'dhFormfield-4142140428',
            'Buyer': 'dhFormfield-4142141854',
            'Receiving Times': 'dhFormfield-4142141978',
            'Special Instructions': 'dhFormfield-4142142170',
            'Phone Number': ['dhFormfield-4142141562', 'dhFormfield-4142141756', 'dhFormfield-4142141762'],
            'Route #': 'dhFormfield-4142142398',
            'Salesperson': 'dhFormfield-4142143042',
        }

    def clear_fields(self, template_pdf):
        for page in template_pdf.pages:
            annotations = page['/Annots']
            if annotations:
                for annotation in annotations:
                    if annotation['/Subtype'] == '/Widget' and '/T' in annotation:
                        field_name = annotation['/T'][1:-1]  # Remove surrounding parentheses
                        if field_name in self.checkbox_fields:
                            # Clear checkbox
                            annotation.update(PdfDict(AS=PdfName('Off'), V=''))
                        else:
                            # Clear text field
                            annotation.update(PdfDict(V=''))
        return template_pdf

    def fill_pdf(self, account_data, template_pdf_path, output_folder):
        output_folder = output_folder if output_folder.endswith('/') else output_folder + '/'
        os.makedirs(output_folder, exist_ok=True)
        output_pdf_path = f'{output_folder}{account_data.get("BUSINESS_NAME", "Unknown").replace(" ", "_")}_{account_data.get("LICENSE_NUMBER", "Unknown")}.pdf'

        template_pdf = PdfReader(template_pdf_path)
        
        # Clear all fields before filling
        template_pdf = self.clear_fields(template_pdf)

        print("DEBUG: Data to fill:")
        for key, value in account_data.items():
            print(f"{key}: {value}")

        for page in template_pdf.pages:
            annotations = page['/Annots']
            if annotations:
                for annotation in annotations:
                    if annotation['/Subtype'] == '/Widget' and '/T' in annotation:
                        field_name = annotation['/T'][1:-1]  # Remove surrounding parentheses
                        print(f"DEBUG: Processing field: {field_name}")
                        
                        # Handle checkboxes
                        if field_name in self.checkbox_fields:
                            checkbox_value = account_data.get(field_name, '')
                            checkbox_state, _ = checkbox_value.split(' ; ', 1) if ' ; ' in checkbox_value else (checkbox_value, '')
                            if checkbox_state == 'Yes':
                                print(f"DEBUG: Setting checkbox {field_name} to True")
                                annotation.update(PdfDict(AS=PdfName('on'), V='/Yes'))
                            else:
                                print(f"DEBUG: Setting checkbox {field_name} to False")
                                annotation.update(PdfDict(AS=PdfName('Off'), V=''))
                        else:
                            # Handle text fields
                            for key, value in self.field_mapping.items():
                                if isinstance(value, list) and field_name in value:
                                    # Handle phone number fields
                                    if key == 'Phone Number' and account_data.get(key):
                                        phone_parts = account_data[key].split('-')
                                        if len(phone_parts) == 3 and value.index(field_name) < len(phone_parts):
                                            annotation.update(PdfDict(V='{}'.format(phone_parts[value.index(field_name)])))
                                            print(f"DEBUG: Setting phone field {field_name} to {phone_parts[value.index(field_name)]}")
                                elif field_name == value:
                                    if key in account_data:
                                        print(f"DEBUG: Setting text field {field_name} to {account_data[key]}")
                                        annotation.update(PdfDict(V='{}'.format(account_data[key])))
                                    break

        PdfWriter().write(output_pdf_path, template_pdf)
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
