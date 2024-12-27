import pywifi
from pywifi import const
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt
import datetime
import os
import time
import csv
import argparse

class WLANScanner:
    def __init__(self, output_dir=None, company_logo=None, scan_address=None):
        self.wifi = pywifi.PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.output_dir = output_dir if output_dir else os.getcwd()
        self.company_logo = company_logo
        self.scan_address = scan_address
        
    def scan_networks(self):
        """Scan for available wireless networks"""
        try:
            self.interface.scan()
            # Wait for scan to complete
            time.sleep(5)  # Increased wait time for better scan results
            networks = self.interface.scan_results()
            # Filter out networks with empty SSIDs
            networks = [n for n in networks if n.ssid.strip()]
            return networks
        except Exception as e:
            print(f"Error scanning networks: {e}")
            return []

    def create_signal_strength_graph(self, networks, filename='signal_strength.png'):
        """Create a bar graph of signal strengths"""
        try:
            ssids = [network.ssid for network in networks]
            # pywifi already returns signal strength in dBm
            signal_strengths = [network.signal for network in networks]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(ssids, signal_strengths)
            
            # Customize the graph
            plt.title('WLAN Signal Strengths')
            plt.xlabel('Network SSID')
            plt.ylabel('Signal Strength (dBm)')
            plt.xticks(rotation=45, ha='right')
            
            # Add colors based on signal strength
            for bar, strength in zip(bars, signal_strengths):
                if strength >= -50:
                    bar.set_color('green')
                elif strength >= -70:
                    bar.set_color('yellow')
                else:
                    bar.set_color('red')
                    
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            return filename
        except Exception as e:
            print(f"Error creating graph: {e}")
            return None

    def get_encryption_type(self, network):
        """Convert pywifi auth algorithm to readable string"""
        auth = network.akm[0] if network.akm else const.AKM_TYPE_NONE
        if auth == const.AKM_TYPE_NONE:
            return "None"
        elif auth == const.AKM_TYPE_WPA:
            return "WPA"
        elif auth == const.AKM_TYPE_WPA2:
            return "WPA2"
        elif auth == const.AKM_TYPE_WPA2PSK:
            return "WPA2-PSK"
        elif auth == const.AKM_TYPE_WPAPSK:
            return "WPA-PSK"
        return "Unknown"

    def get_frequency_channel(self, network):
        """Get channel number from frequency"""
        try:
            freq = network.freq
            if freq >= 2412 and freq <= 2484:
                return int((freq - 2412) / 5 + 1)
            elif freq >= 5170 and freq <= 5825:
                return int((freq - 5170) / 5 + 34)
            return "Unknown"
        except:
            return "Unknown"

    def get_explanation_text(self):
        """Get the explanation text for signal strength"""
        return """
        Förklaring
        
        Signalstyrka (WiFi) mätt i dBm (decibels relativt 1 milliwatt)
        
        Typiska omfång för signalstyrka:
        -30 dBm: Maximalt uppnålig signalstyrka, kan normalt uppnås vid skanning enstaka meter från routern.
        -50 dBm: Utmärkt signalstyrka och normalt sett den högsta möjliga.
        -67 dBm: Det lägsta värde som fortfarande kan leverera OK resultat för de flesta onlinetjänster (surf/streaming etc).
        -80 dBm: Indikerar svag och ej användbar signal.
        """

    def generate_pdf_report(self, networks):
        """Generate PDF report with network information and signal strength graph"""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f"wlan_report_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create the content for the PDF
        styles = getSampleStyleSheet()
        elements = []
        
        # Create header table for logo and title
        header_data = [[]]
        
        # Add logo if provided
        if self.company_logo and os.path.exists(self.company_logo):
            img = Image(self.company_logo)
            img.drawHeight = 100
            img.drawWidth = 100
            header_data[0].append(img)
        else:
            header_data[0].append('')
            
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        title = Paragraph("WLAN Scanningsrapport", title_style)
        header_data[0].append(title)
        
        # Create and style header table
        header_table = Table(header_data, colWidths=[110, 400])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(header_table)
        elements.append(Paragraph(f"Scanning utförd: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Create table data
        data = [['SSID', 'Signal Strength (dBm)', 'Frequency', 'Encryption', 'MAC Address']]
        for network in networks:
            data.append([
                network.ssid,
                f"{network.signal}",
                f"{network.freq} MHz",
                self.get_encryption_type(network),
                network.bssid
            ])
        
        # Create and style the table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Add signal strength graph
        elements.append(PageBreak())
        graph_filename = self.create_signal_strength_graph(networks)
        elements.append(Paragraph("Signalstyrka", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Image(graph_filename, width=400, height=300))
        
        
        # Add scan location if provided
        if self.scan_address:
            elements.append(Paragraph(f"Plats för scanning: {self.scan_address}", styles['Normal']))
            elements.append(Spacer(1, 20))
        
        # Add explanation text
        elements.append(Paragraph("Förklaring", styles['Heading2']))
        elements.append(Spacer(1, 10))
        explanation_style = ParagraphStyle(
            'Explanation',
            parent=styles['Normal'],
            leftIndent=20,
            spaceBefore=10,
            spaceAfter=10
        )
        for line in self.get_explanation_text().split('\n'):
            if line.strip():
                elements.append(Paragraph(line, explanation_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Clean up the temporary graph file
        os.remove(graph_filename)
        
        print(f"PDF report generated successfully: {output_file}")

    def generate_output_filename(self, extension):
        """Generate filename with timestamp"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.output_dir, f"wlan_report_{timestamp}.{extension}")

    def generate_csv_report(self, networks):
        """Generate CSV report with network information"""
        output_file = self.generate_output_filename('csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['SSID', 'Signal Strength (dBm)', 'Frequency', 'Encryption', 'MAC Address'])
            # Write data
            for network in networks:
                writer.writerow([
                    network.ssid,
                    network.signal,
                    f"{network.freq} MHz",
                    self.get_encryption_type(network),
                    network.bssid
                ])
        
        print(f"CSV report generated successfully: {output_file}")

    def generate_html_report(self, networks):
        """Generate HTML report with network information and signal strength graph"""
        output_file = self.generate_output_filename('html')
        graph_output = self.generate_output_filename('png')  # Generate png filename first
        
        # Create graph and save directly to output directory
        if self.create_signal_strength_graph(networks, graph_output):
            graph_section = f"""
            <div class="graph">
                <h2>Signalstyrka</h2>
                <img src="{os.path.basename(graph_output)}" style="max-width: 100%;">
            </div>
            """
        else:
            print("Warning: Could not create signal strength graph")
            graph_section = ""
        
        # Create table rows HTML
        table_rows = ""
        for network in networks:
            table_rows += f"""
                <tr>
                    <td>{network.ssid}</td>
                    <td>{network.signal}</td>
                    <td>{network.freq} MHz</td>
                    <td>{self.get_encryption_type(network)}</td>
                    <td>{network.bssid}</td>
                </tr>"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WLAN Scanningsrapport</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ display: flex; align-items: center; justify-content: space-between; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .graph {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                {f'<img src="{self.company_logo}" style="height: 100px;">' if self.company_logo and os.path.exists(self.company_logo) else ''}
                <h1>WLAN Scanningsrapport</h1>
            </div>
            <p>Scanning utförd: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <table>
                <tr>
                    <th>SSID</th>
                    <th>Signal Strength (dBm)</th>
                    <th>Frequency</th>
                    <th>Encryption</th>
                    <th>MAC Address</th>
                </tr>
                {table_rows}
            </table>
            
            {graph_section}
            
            {f'<p><strong>Plats för scanning:</strong> {self.scan_address}</p>' if self.scan_address else ''}
            
            <div class="explanation">
                <h2>Förklaring</h2>
                <pre style="font-family: Arial, sans-serif; white-space: pre-wrap;">
{self.get_explanation_text()}
                </pre>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated successfully: {output_file}")

    def generate_report(self, networks, format='pdf'):
        """Generate report in specified format"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        if format.lower() == 'pdf':
            self.generate_pdf_report(networks)
        elif format.lower() == 'csv':
            self.generate_csv_report(networks)
        elif format.lower() == 'html':
            self.generate_html_report(networks)
        else:
            raise ValueError(f"Unsupported format: {format}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='WLAN Scanner and Reporter')
    parser.add_argument('--format', '-f', 
                      choices=['pdf', 'csv', 'html'], 
                      default='pdf',
                      help='Output format (pdf, csv, or html)')
    parser.add_argument('--output', '-o',
                      default='reports',
                      help='Output directory for reports')
    parser.add_argument('--logo', '-l',
                      help='Path to company logo')
    parser.add_argument('--address', '-a',
                      help='Address where the scanning is performed')
    
    args = parser.parse_args()
    
    scanner = WLANScanner(
        output_dir=args.output,
        company_logo=args.logo,
        scan_address=args.address
    )
    networks = scanner.scan_networks()
    
    if networks:
        scanner.generate_report(networks, format=args.format)
    else:
        print("No wireless networks found or error occurred during scanning.")

if __name__ == "__main__":
    main()
