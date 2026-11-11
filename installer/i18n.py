# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 SonosDial contributors
"""English/German UI catalog; never translates device names, SSIDs or passwords."""
import ctypes,json,locale,os,pathlib,tempfile

EN={
 'Die Sprache gilt jetzt, konnte aber nicht gespeichert werden.':'The language has changed, but your preference could not be saved.',
 'Anschließen':'Connect','Installieren':'Install','WLAN verbinden':'Connect Wi-Fi','Raum auswählen':'Choose a room',
 'Version 1.2.0\nUnabhängiges Projekt':'Version 1.2.0\nIndependent project',
 'SonosDial · Einrichtung 1.2.0':'SonosDial · Setup 1.2.0','SonosDial · Einstellungen':'SonosDial · Settings','SonosDial · Details':'SonosDial · Details',
 'Zurück':'Back','Weiter →':'Next →','Fertig':'Done','SCHRITT {step} VON 4':'STEP {step} OF 4','ALLES EINGERICHTET':'ALL SET',
 'Verbinde deinen Regler.':'Connect your controller.','Bereit für deine Musik.':'Ready for your music.',
 'Verbinde dein WLAN.':'Connect to Wi-Fi.','Wo spielt deine Musik?':'Where is your music playing?','Dein Regler ist bereit.':'Your controller is ready.',
 'Ein USB-Datenkabel. Dann geht’s los.':'One USB data cable. Then you are ready to go.',
 'Wir bringen den Regler auf Version 1.2.0.':'Let’s get your controller ready with version 1.2.0.',
 'Alles hier im Assistenten. Kein Browser nötig.':'Everything happens here. No browser needed.',
 'Wähle den Raum, den dein Regler steuern soll.':'Choose the room you want to control.',
 'USB am Computer abziehen und später ein USB-Netzteil verwenden.':'You can now unplug it from your computer and use a USB power adapter.',
 'So einfach geht’s':'It’s this simple',
 '1. Board mit dem Computer verbinden.':'1. Connect the board to your computer.',
 '2. Die USB-C-Buchse am Mini-Board verwenden.':'2. Use the USB-C port on the mini board.',
 '3. Auf Weiter klicken.':'3. Click Next.',
 'diymore ESP32-S3 Mini: USB-C-Datenkabel verwenden und die mitgelieferte WLAN-Antenne anschließen.':'diymore ESP32-S3 Mini: use a USB-C data cable and attach the supplied Wi-Fi antenna.',
 '● USB-Anschluss gefunden':'● USB port found','Noch kein eindeutiger USB-Anschluss gefunden.':'No unambiguous USB port found yet.',
 'Neu suchen':'Refresh','Drehencoder anschließen ▾':'Connect the rotary encoder ▾','Drehencoder anschließen':'Connect the rotary encoder',
 'Vor dem Verdrahten USB abziehen.\n\nKY-040 → ESP32-S3\nCLK → D3 / GPIO4\nDT → D4 / GPIO5\nSW → D5 / GPIO6\n+ → 3V3 (niemals 5V)\nGND → GND\n\nNach den Pinbeschriftungen verbinden. Der Drucktaster ist bereits im KY-040 eingebaut.':'Unplug USB before wiring.\n\nKY-040 → ESP32-S3\nCLK → D3 / GPIO4\nDT → D4 / GPIO5\nSW → D5 / GPIO6\n+ → 3V3 (never 5V)\nGND → GND\n\nFollow the pin labels. The push button is already built into the KY-040.',
 '✓ Version 1.2.0 ist bereits installiert.':'✓ Version 1.2.0 is already installed.',
 'Die passende Firmware ist im Assistenten enthalten.':'The correct firmware is included in this assistant.',
 'WLAN- und Raumdaten bleiben beim Update erhalten, soweit sie aus SonosDial stammen. Bitte das USB-Kabel während der Installation angeschlossen lassen.':'Existing SonosDial Wi-Fi and room settings are preserved during updates. Keep USB connected throughout installation.',
 'Vor dem Schreiben werden Chip, 8-MB-Flash und alle Firmware-Prüfsummen geprüft. Es werden nur die Firmwarebereiche beschrieben.':'We check the chip, 8 MB flash and all firmware checksums first. Only firmware areas are written.',
 'Version 1.2.0 auf den ausgewählten Regler installieren.':'Install version 1.2.0 on the selected controller.',
 'Firmware installieren':'Install firmware','Firmware bei Bedarf erneut installieren':'Reinstall firmware if needed',
 'Hilfe: BOOT / RESET':'Help: BOOT / RESET','Wenn das Board nicht antwortet':'If the board does not respond',
 'BOOT halten → RESET kurz drücken → BOOT loslassen.\n\nDanach zurückgehen, „Neu suchen“ wählen und erneut versuchen. Nach dem Flashen gegebenenfalls RESET drücken. Der USB-Anschluss kann sich beim Neustart ändern.':'Hold BOOT → briefly press RESET → release BOOT.\n\nGo back, click Refresh and try again. Press RESET after flashing if needed. The USB port may change after a restart.',
 'Details':'Details','Noch keine Installationsmeldungen.':'No installation messages yet.',
 '✓ Verbunden mit ':'✓ Connected to ','deinem WLAN':'your Wi-Fi network',
 'Du kannst direkt zur Raumauswahl gehen oder die Verbindung hier ändern.':'Continue to room selection, or change the connection here.',
 'Dein WLAN':'Your Wi-Fi network','Verstecktes WLAN? Den Namen einfach eingeben.':'Hidden network? Just type its name.',
 'WLAN-Passwort':'Wi-Fi password','Verbinden':'Connect','WLANs suchen':'Find Wi-Fi networks',
 'Oder ohne Passworteingabe':'Or connect without typing a password',
 'WPS starten und anschließend die WPS-Taste am Router drücken. Der Router muss WPS für 2,4 GHz unterstützen.':'Start WPS, then press the WPS button on your router. Your router must support WPS for 2.4 GHz Wi-Fi.',
 'Mit WPS verbinden':'Connect with WPS','Verbindungsversuch abbrechen':'Cancel connection attempt',
 'Noch keine Sonos-Räume gefunden. Regler und Sonos müssen sich im selben erreichbaren Heimnetz befinden.':'No Sonos rooms found yet. The controller must be able to reach Sonos on your home network.',
 'Der Musik folgen':'Follow the music',
 'Steuert die einzige spielende Gruppe. Wenn mehrere oder keine spielen, gilt dein gewählter Raum.':'Controls the only group currently playing. If several groups or none are playing, your selected room is used.',
 'Lautstärke für die ganze Gruppe':'Control volume for the whole group',
 'Erneut suchen':'Search again','Weitere Einstellungen':'More settings','Raum speichern →':'Save room →',
 'Dein Regler steuert ':'Your controller controls ','deinen gewählten Raum':'your selected room','So bedienst du ihn':'How to use it',
 'Rechts drehen':'Turn right','Links drehen':'Turn left','Lauter':'Volume up','Leiser':'Volume down',
 '1× drücken':'Press once','2× drücken':'Press twice','3× drücken':'Press three times','2 Sekunden halten':'Hold for 2 seconds',
 'Nächster Titel':'Next track','Vorheriger Titel':'Previous track','Mute ein/aus':'Mute / unmute',
 'Du kannst den Assistenten später erneut öffnen und die Einstellungen über USB ändern.':'Reopen this assistant later to change settings over USB.',
 'Einstellungen öffnen':'Open settings','Drehrichtung umkehren':'Reverse rotation direction',
 'Lautstärkeschritt pro Rastung':'Volume step per detent','Flanken pro Rastung':'Encoder transitions per detent',
 'Optionale Sonos-IP':'Optional Sonos IP address','Speichern':'Save','Einstellungen gespeichert.':'Settings saved.',
 'Board anschließen':'Connect the board',
 'Bitte Board mit einem USB-Datenkabel anschließen und „Neu suchen“ wählen.':'Connect the board using a USB data cable, then click Refresh.',
 'USB-Verbindung wird geprüft …':'Checking the USB connection …','Bereit.':'Ready.',
 'Bitte die Installation auf dem ausgewählten Board bestätigen.':'Please confirm installation on the selected board.',
 'Board wird geprüft. USB bitte angeschlossen lassen …':'Checking the board. Keep USB connected …',
 'Firmware wird geschrieben und verifiziert …':'Writing and verifying firmware …',
 'Version 1.2.0 noch nicht gestartet.':'Version 1.2.0 has not started yet.',
 'Version 1.2.0 installiert. Jetzt WLAN verbinden.':'Version 1.2.0 installed. Now connect to Wi-Fi.',
 'Firmware wurde geschrieben. Bitte RESET drücken und über „Zurück“ den Anschluss neu suchen. ':'Firmware was written. Press RESET, go Back and refresh the USB port. ',
 'Der Regler sucht WLANs …':'Your controller is searching for Wi-Fi networks …',
 'WLAN auswählen oder den Namen eingeben.':'Choose a Wi-Fi network or type its name.',
 'WLAN prüfen':'Check Wi-Fi settings',
 'WLAN-Namen wählen und Passwort mit 8–63 Byte eingeben. Für ein offenes WLAN das Passwort leer lassen.':'Choose a Wi-Fi network and enter a password of 8–63 bytes. Leave it blank for an open network.',
 'WLAN-Verbindung wird aufgebaut …':'Connecting to Wi-Fi …',
 'WLAN verbunden und gespeichert. Weiter zur Raumauswahl.':'Wi-Fi connected and saved. Continue to room selection.',
 'Jetzt die WPS-Taste am Router drücken. Wir warten bis zu zwei Minuten …':'Press the WPS button on your router now. We will wait for up to two minutes …',
 'WPS erfolgreich. WLAN gespeichert.':'WPS successful. Wi-Fi settings saved.',
 'Verbindungsversuch wird abgebrochen …':'Cancelling the connection attempt …',
 'Sonos-Räume werden gesucht …':'Searching for Sonos rooms …','Raum auswählen.':'Choose a room.',
 'Keine neuen Sonos-Räume gefunden. Heimnetz prüfen oder unter „Weitere Einstellungen“ eine Sonos-IP eingeben.':'No new Sonos rooms found. Check your home network or enter a Sonos IP address under More settings.',
 'Bitte zuerst einen Sonos-Raum auswählen.':'Please select a Sonos room first.',
 'Alles gespeichert. Viel Spaß mit deinem Regler.':'Everything is saved. Enjoy your controller.',
 'Vorgang nicht abgeschlossen.':'Operation not completed.','Vorgang läuft':'Operation in progress',
 'Bitte den Vorgang abwarten. WLAN-/WPS-Verbindungen können über den Abbrechen-Knopf beendet werden.':'Please wait for the current operation to finish. Wi-Fi/WPS attempts can be stopped using Cancel connection attempt.',
 'Die Firmware-Prüfsumme stimmt nicht. Installer erneut herunterladen.':'The firmware checksum does not match. Download the installer again.',
 'Kein ESP32-S3 erkannt. Bitte den richtigen USB-Anschluss auswählen.':'No ESP32-S3 detected. Please select the correct USB port.',
 '8 MB Flash wurden nicht bestätigt. Es wurde nichts geschrieben. Bitte diymore-S3-Mini-Board und Anschluss prüfen.':'8 MB flash could not be confirmed. Nothing was written. Check your diymore-S3-Mini board and USB port.',
 'Unbekannter Vorgang':'Unknown operation',
 'Zeitüberschreitung. Verbindung prüfen und Firmware erneut vollständig schreiben.':'Operation timed out. Check the connection and write the complete firmware again.',
 'USB-Vorgang fehlgeschlagen. BOOT halten, RESET kurz drücken, BOOT loslassen; Anschluss neu suchen.\n\n':'USB operation failed. Hold BOOT, briefly press RESET, release BOOT, then refresh the USB port.\n\n',
 'Die Anfrage ist zu groß.':'The request is too large.','Der Regler konnte die Anfrage nicht ausführen.':'The controller could not complete the request.',
 'Der Regler antwortet nicht. USB / OTG und Datenkabel prüfen; nach einem Neustart „Neu suchen“ wählen.':'The controller is not responding. Check USB / OTG and your data cable; click Refresh after a restart.',
 'Dieser Regler verwendet eine andere Konfigurationsschnittstelle.':'This controller uses a different configuration protocol.',
 'Regler nicht erreichbar.':'Controller unavailable.','Verbindungsversuch abgebrochen.':'Connection attempt cancelled.',
 'Der Vorgang dauert zu lange. Bitte Verbindung prüfen und erneut versuchen.':'This is taking too long. Check the connection and try again.',
 # Known firmware messages are translated on the PC.
 'Einstellungen konnten nicht dauerhaft gespeichert werden.':'Settings could not be saved permanently.',
 'WLAN-Suche fehlgeschlagen. Bitte erneut suchen.':'Wi-Fi search failed. Please try again.',
 'WPS lieferte keine Zugangsdaten. Bitte WLAN mit Passwort verwenden.':'WPS did not provide credentials. Please connect using a Wi-Fi password.',
 'WPS hat nicht geklappt. Bitte erneut versuchen oder WLAN mit Passwort wählen.':'WPS failed. Try again or connect using a Wi-Fi password.',
 'WLAN-Verbindung fehlgeschlagen. Passwort und 2,4-GHz-Netz prüfen. Bisherige Einstellungen bleiben erhalten.':'Wi-Fi connection failed. Check the password and your 2.4 GHz network. Previous settings are preserved.',
 'Bitte den laufenden Verbindungsversuch abwarten oder abbrechen.':'Wait for the current connection attempt or cancel it.',
 'WLAN-Suche konnte nicht gestartet werden.':'The Wi-Fi search could not be started.',
 'Bitte den laufenden Vorgang abwarten.':'Please wait for the current operation to finish.',
 'WLAN-Name und Passwort fehlen.':'Wi-Fi network name and password are missing.',
 'WLAN-Name oder Passwortlänge ungültig.':'The Wi-Fi name or password length is invalid.',
 'WPS konnte nicht gestartet werden. Bitte WLAN mit Passwort wählen.':'WPS could not be started. Please connect using a Wi-Fi password.',
 'Bitte zuerst WLAN verbinden.':'Please connect to Wi-Fi first.','Bitte einen Raum wählen.':'Please choose a room.',
 'Raum nicht mehr verfügbar. Bitte erneut suchen.':'This room is no longer available. Please search again.',
 'Ungültige Einstellung.':'Invalid setting.','Schrittweite ungültig.':'Invalid volume step.',
 'Encoder-Einstellung ungültig.':'Invalid encoder setting.','Einstellung außerhalb des erlaubten Bereichs.':'Setting outside the allowed range.',
 'Sonos-IP ungültig.':'Invalid Sonos IP address.','Einstellungen konnten nicht gespeichert werden.':'Settings could not be saved.',
 'Unbekannter Befehl. Assistent und Firmware müssen zusammenpassen.':'Unknown command. The assistant and firmware must be compatible.',
 'Ungültige USB-Anfrage.':'Invalid USB request.',
 'WPS fehlgeschlagen':'WPS failed','Passwort prüfen':'Check the password',
}
_reverse={v:k for k,v in EN.items()}

def normalize_language(value):
    value=str(value or '').lower().replace('_','-')
    return 'de' if value in ('german','deutsch') or value.startswith('de') else 'en'

def windows_language(language_id=None):
    if language_id is not None:return 'de' if (language_id&0x3ff)==7 else 'en'
    if os.name=='nt':
        try:return windows_language(ctypes.windll.kernel32.GetUserDefaultUILanguage())
        except (AttributeError,OSError):pass
    try:return normalize_language(locale.getlocale()[0])
    except (ValueError,TypeError):return 'en'

def preferences_path():
    return pathlib.Path(os.environ.get('LOCALAPPDATA',str(pathlib.Path.home()/'.local/share')))/'SonosDial'/'ui.json'

def read_language(path=None):
    try:
        value=json.loads((path or preferences_path()).read_text(encoding='utf-8')).get('language')
        if value in ('en','de'):return value
    except (OSError,ValueError,AttributeError):pass
    return windows_language()

_language=read_language()

def language():return _language

def set_language(value,persist=False,path=None):
    global _language
    _language=normalize_language(value)
    if persist:
        dest=path or preferences_path();dest.parent.mkdir(parents=True,exist_ok=True)
        # Store only UI preference, never device configuration or Wi-Fi data.
        fd,name=tempfile.mkstemp(prefix='ui-',suffix='.json',dir=dest.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump({'language':_language},f)
            os.replace(name,dest)
        finally:
            if os.path.exists(name):os.unlink(name)
    return _language

def tr(text):
    return EN.get(text,text) if _language=='en' else _reverse.get(text,text) if text not in EN else text
