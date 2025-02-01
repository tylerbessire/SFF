import tkinter as tk
from gui import ModernGUI
from scraper import BusinessScraper
from pdf_filler import PDFFiller

def main():
    root = tk.Tk()
    scraper = BusinessScraper()
    pdf_filler = PDFFiller()
    gui = ModernGUI(root, scraper, pdf_filler)
    root.mainloop()

if __name__ == "__main__":
    main()
