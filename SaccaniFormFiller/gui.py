import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import pandas as pd
from ttkbootstrap import Style
import openpyxl
import docx
import csv
from scraper import BusinessScraper
from pdf_filler import PDFFiller

def read_input_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.csv':
        return pd.read_csv(file_path).to_dict('records')
    elif file_extension.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path).to_dict('records')
    elif file_extension.lower() == '.docx':
        doc = docx.Document(file_path)
        lines = [para.text for para in doc.paragraphs if para.text.strip()]
        headers = lines[0].split(',')
        return [dict(zip(headers, line.split(','))) for line in lines[1:]]
    elif file_extension.lower() == '.txt':
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

class ModernGUI:
    def __init__(self, root, scraper, pdf_filler):
        self.root = root
        self.scraper = scraper
        self.pdf_filler = pdf_filler
        
        style = Style(theme='superhero')
        self.root.title("Saccani Business License Scraper")
        self.root.geometry("1200x800")

        self.orange = "#FFA500"
        self.blue = "#007BFF"
        self.yellow = "#FFFF00"
        
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.file_frame = ttk.Frame(self.notebook)
        self.manual_entry_frame = ttk.Frame(self.notebook)
        self.additional_info_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.file_frame, text="File Selection")
        self.notebook.add(self.manual_entry_frame, text="Manual Entry")
        self.notebook.add(self.additional_info_frame, text="Additional Info")
        self.notebook.add(self.log_frame, text="Log")

        self.create_file_widgets()
        self.create_manual_entry_widgets()
        self.create_additional_info_widgets()
        self.create_log_widgets()

    def create_file_widgets(self):
        file_frame_inner = ttk.Frame(self.file_frame, style='TFrame', padding="10 10 10 10")
        file_frame_inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(file_frame_inner, text="Input File:", font=("Arial", 12, "bold")).grid(column=0, row=0, sticky=tk.W, pady=10)
        self.input_entry = ttk.Entry(file_frame_inner, width=70, font=("Arial", 12))
        self.input_entry.grid(column=1, row=0, sticky="we", pady=10)
        ttk.Button(file_frame_inner, text="Browse", command=self.browse_input, style='warning.TButton').grid(column=2, row=0, padx=10, pady=10)

        ttk.Label(file_frame_inner, text="PDF Template:", font=("Arial", 12, "bold")).grid(column=0, row=1, sticky=tk.W, pady=10)
        self.template_entry = ttk.Entry(file_frame_inner, width=70, font=("Arial", 12))
        self.template_entry.grid(column=1, row=1, sticky="we", pady=10)
        ttk.Button(file_frame_inner, text="Browse", command=self.browse_template, style='warning.TButton').grid(column=2, row=1, padx=10, pady=10)

        ttk.Label(file_frame_inner, text="Output Folder:", font=("Arial", 12, "bold")).grid(column=0, row=2, sticky=tk.W, pady=10)
        self.output_entry = ttk.Entry(file_frame_inner, width=70, font=("Arial", 12))
        self.output_entry.grid(column=1, row=2, sticky="we", pady=10)
        ttk.Button(file_frame_inner, text="Browse", command=self.browse_output, style='warning.TButton').grid(column=2, row=2, padx=10, pady=10)

        self.start_button = ttk.Button(file_frame_inner, text="Start Scraping", command=self.start_scraping, style='success.TButton')
        self.start_button.grid(column=1, row=3, pady=20)

        self.progress = ttk.Progressbar(file_frame_inner, orient=tk.HORIZONTAL, length=500, mode='determinate', style='warning.Horizontal.TProgressbar')
        self.progress.grid(column=0, row=4, columnspan=3, sticky="we", pady=10)

    def create_manual_entry_widgets(self):
        manual_frame = ttk.Frame(self.manual_entry_frame, style='TFrame', padding="10 10 10 10")
        manual_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(manual_frame, text="Account Number:", font=("Arial", 12, "bold")).grid(column=0, row=0, sticky=tk.W, pady=5)
        self.account_entry = ttk.Entry(manual_frame, width=30, font=("Arial", 12))
        self.account_entry.grid(column=1, row=0, sticky="we", pady=5)

        ttk.Label(manual_frame, text="Client:", font=("Arial", 12, "bold")).grid(column=0, row=1, sticky=tk.W, pady=5)
        self.client_entry = ttk.Entry(manual_frame, width=30, font=("Arial", 12))
        self.client_entry.grid(column=1, row=1, sticky="we", pady=5)

        ttk.Label(manual_frame, text="City:", font=("Arial", 12, "bold")).grid(column=0, row=2, sticky=tk.W, pady=5)
        self.city_entry = ttk.Entry(manual_frame, width=30, font=("Arial", 12))
        self.city_entry.grid(column=1, row=2, sticky="we", pady=5)

        self.add_account_button = ttk.Button(manual_frame, text="Add Account", command=self.add_manual_account, style='success.TButton')
        self.add_account_button.grid(column=1, row=3, pady=20)

        self.manual_accounts_list = tk.Listbox(manual_frame, width=50, height=10, font=("Arial", 12))
        self.manual_accounts_list.grid(column=0, row=4, columnspan=2, sticky="we", pady=10)

        self.remove_account_button = ttk.Button(manual_frame, text="Remove Selected Account", command=self.remove_manual_account, style='danger.TButton')
        self.remove_account_button.grid(column=1, row=5, pady=10)

    def create_additional_info_widgets(self):
        additional_frame = ttk.Frame(self.additional_info_frame, style='TFrame', padding="10 10 10 10")
        additional_frame.pack(fill=tk.BOTH, expand=True)

        self.additional_info = {}

        # Text fields
        text_fields = [
            "Old Account #", "Old DBA Name", "Account Number for Changes only", 
            "Buyer", "Receiving Times", "Special Instructions", "Phone Number",
            "Route #", "Salesperson", "Account Number"
        ]

        for i, field in enumerate(text_fields):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(additional_frame, text=field + ':', font=("Arial", 10, "bold")).grid(column=col, row=row, sticky=tk.W, pady=5, padx=5)
            var = tk.StringVar()
            entry = ttk.Entry(additional_frame, textvariable=var, width=30, font=("Arial", 10))
            entry.grid(column=col+1, row=row, sticky="we", pady=5, padx=5)
            self.additional_info[field] = var

        # Checkboxes
        checkbox_frame = ttk.Frame(additional_frame, style='TFrame', padding="10 10 10 10")
        checkbox_frame.grid(column=0, row=len(text_fields)//2 + 1, columnspan=4, sticky="we")

        self.checkbox_fields = {
            "New Account": "New Account",
            "Close Account": "Close Account",
            "Change or Add Info": "Change or Add Info",
            "Delivery Location Front": "Delivery Location Front",
            "Delivery Location Back": "Delivery Location Back",
            "Delivery Location Side": "Delivery Location Side",
            "Monday": "Monday",
            "Tuesday": "Tuesday",
            "Wednesday": "Wednesday",
            "Thursday": "Thursday",
            "Friday": "Friday",
            "Credit Application Yes": "Credit Application Yes",
            "Credit Application No": "Credit Application No",
            "On Sale": "On Sale",
            "Off-Sale": "Off-Sale",
            "Draft Status Ours": "Draft Status Ours",
            "Draft Status Theirs": "Draft Status Theirs",
            "Draft Status Ours & Theirs": "Draft Status Ours & Theirs",
            "Draft Status Other": "Draft Status Other",
            "Market Type Bar": "Market Type Bar",
            "Market Type Restaurant": "Market Type Restaurant",
            "Market Type Grocery": "Market Type Grocery",
            "Market Type Deli": "Market Type Deli",
            "Market Type Convenience": "Market Type Convenience",
            "Market Type Other": "Market Type Other",
            "Buying Yes": "Buying Yes",
            "Buying No": "Buying No"
        }

        for i, (field_name, checkbox_text) in enumerate(self.checkbox_fields.items()):
            var = tk.StringVar(value="Off")
            cb = ttk.Checkbutton(checkbox_frame, text=checkbox_text, variable=var, 
                                 onvalue="on", offvalue="Off", 
                                 style='success.TCheckbutton', 
                                 command=lambda f=field_name: self.on_checkbox_click(f))
            cb.grid(column=i%4, row=i//4, sticky=tk.W, pady=5, padx=5)
            self.additional_info[field_name] = {'var': var, 'label': checkbox_text, 'widget': cb}

        ttk.Button(additional_frame, text="Print Checkbox States", command=self.print_checkbox_states).grid(column=0, row=len(text_fields)//2 + 2, columnspan=4, pady=10)

    def create_log_widgets(self):
        log_frame_inner = ttk.Frame(self.log_frame, style='TFrame', padding="10 10 10 10")
        log_frame_inner.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame_inner, wrap=tk.WORD, width=100, height=20, bg=self.blue, fg=self.yellow, font=("Arial", 12))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame_inner, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("All supported files", "*.csv;*.xlsx;*.xls;*.docx;*.txt"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx;*.xls"),
            ("Word files", "*.docx"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ])
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def browse_template(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.template_entry.delete(0, tk.END)
            self.template_entry.insert(0, filename)

    def browse_output(self):
        foldername = filedialog.askdirectory()
        if foldername:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, foldername)

    def add_manual_account(self):
        account = self.account_entry.get()
        client = self.client_entry.get()
        city = self.city_entry.get()
        if account and client and city:
            self.manual_accounts_list.insert(tk.END, f"{account} - {client} - {city}")
            self.account_entry.delete(0, tk.END)
            self.client_entry.delete(0, tk.END)
            self.city_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def remove_manual_account(self):
        selection = self.manual_accounts_list.curselection()
        if selection:
            self.manual_accounts_list.delete(selection)

    def start_scraping(self):
        input_file = self.input_entry.get()
        template_file = self.template_entry.get()
        output_folder = self.output_entry.get()

        if not all([template_file, output_folder]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.scrape_businesses, args=(input_file, template_file, output_folder), daemon=True).start()

    def scrape_businesses(self, input_file, template_file, output_folder):
        try:
            businesses = []
            if input_file:
                businesses = read_input_file(input_file)
            
            # Add manually entered accounts
            for item in self.manual_accounts_list.get(0, tk.END):
                account, client, city = item.split(" - ")
                businesses.append({"Account #": account, "Client": client, "City": city})

            self.scraper.setup_driver()
            self.progress['maximum'] = len(businesses)

            for i, business in enumerate(businesses):
                try:
                    client = business.get('Client', 'Unknown')
                    city = business.get('City', 'Unknown')
                    account_number = business.get('Account #', '')
                    self.log(f"Processing {client} in {city}")
                    
                    account_data = self.scraper.scrape_business(client, city)
                    self.log(f"Scraped data: {account_data}")
                    
                    if account_data:
                        account_data['ACCOUNT_NUMBER'] = account_number
                        
                        # Add additional info to account_data
                        for field, info in self.additional_info.items():
                            if isinstance(info, dict):  # It's a checkbox
                                account_data[field] = info['var'].get()
                            else:  # It's a text field
                                account_data[field] = info.get()
                        
                        # Extract address components
                        self.log("Extracting address components")
                        street, city, state, zip_code = self.pdf_filler.extract_address_components(account_data.get('BUSINESS_ADDRESS', ''))
                        account_data['STREET'] = street
                        account_data['CITY'] = city
                        account_data['STATE'] = state
                        account_data['ZIP_CODE'] = zip_code
                        
                        # Debug print
                        self.log("Account data before PDF filling:")
                        for key, value in account_data.items():
                            self.log(f"{key}: {value}")
                        
                        self.log("Calling fill_pdf method")
                        pdf_path = self.pdf_filler.fill_pdf(account_data, template_file, output_folder)
                        self.log(f"PDF saved: {pdf_path}")
                    else:
                        self.log(f"No data found for {client}")
                    self.progress['value'] = i + 1
                    self.root.update_idletasks()
                except Exception as e:
                    self.log(f"Error processing business {client}: {str(e)}")
                    import traceback
                    self.log(traceback.format_exc())
                    continue

            self.scraper.close_driver()
            self.log("Scraping completed")
        except Exception as e:
            self.log(f"Error during scraping: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.start_button.config(state=tk.NORMAL)

    def log(self, message):
        print(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def on_checkbox_click(self, field_name):
        checkbox_info = self.additional_info[field_name]
        state = checkbox_info['var'].get()
        if state == "on":
            checkbox_info['widget'].state(['selected'])
        else:
            checkbox_info['widget'].state(['!selected'])
        self.print_checkbox_states()

    def print_checkbox_states(self):
        self.log("Current Checkbox States:")
        for field, info in self.additional_info.items():
            if isinstance(info, dict):  # It's a checkbox
                state = info['var'].get()
                self.log(f"{field}: {state}")

if __name__ == "__main__":
    root = tk.Tk()
    scraper = BusinessScraper()  # Assuming your scraper class is named BusinessScraper
    pdf_filler = PDFFiller()  # Assuming your PDF filler class is named PDFFiller
    app = ModernGUI(root, scraper, pdf_filler)
    root.mainloop()
