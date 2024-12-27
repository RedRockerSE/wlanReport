# wlanReport

## Installation
`pip install reportlab matplotlib pandas customtkinter

## Användning
1. Skapa PDF rapport (default)
python wlanReport.py

2. Skapa CSV rapport
python wlanReport.py --format csv

3. Skapa HTML rapport
python wlanReport.py --format html

4. Ange mapp som rapport skrivs till. Utelämnas denna flagga används standardmappen 
python wlanReport.py --output "C:\Users\XXX\Desktop\Case1\"

5. Inkludera logga 
python wlanReport.py --logo "C:\forensic\logo\logo.png"

6. Combine options
python wlanReport.py --format html --output "C:\Users\XXX\Desktop\K111222-24\" --logo "C:\forensic\logo\Riksemblem.png"

Signalstyrka (WiFi) mätt i dBm (decibels relativt 1 milliwatt)

Typiska omfång för signalstyrka:
- 30 dBm: Maximalt uppnålig signalstyrka, kan normalt uppnås vid skanning enstaka meter från routern.
- 50 dBm: Utmärkt signalstyrka och normalt sett den högsta möjliga.
- 67 dBm: Det lägsta värde som fortfarande kan leverera OK resultat för de flesta onlinetjänster (surf/streaming etc).
- 80 dBm: Indikerar svag och ej användbar signal.