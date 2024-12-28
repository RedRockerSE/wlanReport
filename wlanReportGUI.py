import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from wlanReport import WLANScanner
import threading

class WLANScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WLAN Scanner")
        self.root.geometry("800x600")
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.output_dir = tk.StringVar(value="reports")
        self.logo_path = tk.StringVar()
        self.scan_address = tk.StringVar()
        self.output_format = tk.StringVar(value="pdf")
        self.scanning = False
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="WLAN Scanner", font=('Helvetica', 24))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Output Directory
        ttk.Label(main_frame, text="Rapportkatalog:").grid(row=1, column=0, sticky=tk.W)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Bläddra", command=self.browse_output).grid(row=1, column=2)
        
        # Company Logo
        ttk.Label(main_frame, text="Logga för rapport:").grid(row=2, column=0, sticky=tk.W, pady=10)
        logo_entry = ttk.Entry(main_frame, textvariable=self.logo_path, width=50)
        logo_entry.grid(row=2, column=1, padx=5, pady=10)
        ttk.Button(main_frame, text="Bläddra", command=self.browse_logo).grid(row=2, column=2, pady=10)
        
        # Scan Address
        ttk.Label(main_frame, text="Aktuell plats:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.scan_address, width=50).grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        # Output Format
        ttk.Label(main_frame, text="Rapportformat:").grid(row=4, column=0, sticky=tk.W, pady=10)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Radiobutton(format_frame, text="PDF", variable=self.output_format, value="pdf").grid(row=0, column=0, padx=20)
        ttk.Radiobutton(format_frame, text="HTML", variable=self.output_format, value="html").grid(row=0, column=1, padx=20)
        ttk.Radiobutton(format_frame, text="CSV", variable=self.output_format, value="csv").grid(row=0, column=2, padx=20)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        self.status_label = ttk.Label(status_frame, text="Klar för scanning", font=('Helvetica', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=300)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Scan Button
        self.scan_button = ttk.Button(main_frame, text="Starta scanning", command=self.start_scan, style='Accent.TButton')
        self.scan_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Configure style for accent button
        self.style.configure('Accent.TButton', 
                           font=('Helvetica', 12),
                           padding=10)
        
        # Make the window resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def browse_output(self):
        directory = filedialog.askdirectory(initialdir=".")
        if directory:
            self.output_dir.set(directory)
            
    def browse_logo(self):
        filetypes = (
            ('Image files', '*.png *.jpg *.jpeg'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.logo_path.set(filename)
            
    def update_status(self, message, is_error=False):
        self.status_label.config(text=message, 
                               foreground='red' if is_error else 'black')
        
    def start_scan(self):
        if self.scanning:
            return
            
        # Validate output directory
        if not self.output_dir.get():
            messagebox.showerror("Error", "Välj katalog för export av scanningsrapport")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # Update UI
        self.scanning = True
        self.scan_button.config(state='disabled')
        self.progress_bar.start(10)
        self.update_status("Scannar nätverk...")
        
        # Start scan in separate thread
        thread = threading.Thread(target=self.perform_scan)
        thread.daemon = True
        thread.start()
        
    def perform_scan(self):
        try:
            try:
                # Your wpa_supplicant access code here
                pass
            except PermissionError:
                messagebox.showerror(
                    "Permission Error",
                    "Cannot access WiFi information. On Linux systems, this program needs elevated privileges.\n\n"
                    "Please run with 'sudo' or add your user to the 'netdev' group.\n"
                    "See the included sudoers_note.txt file for details."
                )
                # Either exit here or continue with limited functionality
            
            scanner = WLANScanner(
                output_dir=self.output_dir.get(),
                company_logo=self.logo_path.get() if self.logo_path.get() else None,
                scan_address=self.scan_address.get() if self.scan_address.get() else None
            )
            
            networks = scanner.scan_networks()
            
            if networks:
                scanner.generate_report(networks, format=self.output_format.get())
                self.root.after(0, self.update_status, f"Rapporten skapades {self.output_dir.get()}")
            else:
                self.root.after(0, self.update_status, "Hittade inga synliga nätverk...", True)
                
        except Exception as e:
            self.root.after(0, self.update_status, f"Error: {str(e)}", True)
            
        finally:
            # Reset UI
            self.root.after(0, self.scan_complete)
            
    def scan_complete(self):
        self.scanning = False
        self.scan_button.config(state='normal')
        self.progress_bar.stop()

def main():
    root = tk.Tk()
    app = WLANScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
