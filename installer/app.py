# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 SonosDial contributors
"""Offline Windows provisioning assistant. No flashing without a button click."""
from __future__ import annotations
from i18n import tr,language,set_language
import argparse,hashlib,json,os,pathlib,queue,re,subprocess,sys,tempfile,threading,time,traceback,webbrowser
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.scrolledtext import ScrolledText
import serial
from serial.tools import list_ports

ROOT=pathlib.Path(getattr(sys,'_MEIPASS',pathlib.Path(__file__).resolve().parent))
DATA=ROOT/'data' if getattr(sys,'frozen',False) else ROOT.parent/'binaries'
ASSETS=ROOT/'assets' if getattr(sys,'frozen',False) else ROOT.parent/'assets'
VERSION='1.2.0'

def validate_firmware(data=DATA):
    image=data/'sonosdial-factory.bin'
    hashes=json.loads((data/'SHA256.json').read_text(encoding='utf-8'))
    for name in ('sonosdial-factory.bin','bootloader.bin','partitions.bin','boot_app0.bin','firmware.bin'):
        if hashlib.sha256((data/name).read_bytes()).hexdigest()!=hashes.get(name):
            raise RuntimeError(tr('Die Firmware-Prüfsumme stimmt nicht. Installer erneut herunterladen.'))
    return image

def check_device(text):
    # flash_id is read-only. --chip esp32s3 also rejects other chips in esptool.
    if not re.search(r'\bESP32-S3\b',text,re.I):
        raise RuntimeError(tr('Kein ESP32-S3 erkannt. Bitte den richtigen USB-Anschluss auswählen.'))
    if not re.search(r'Detected flash size:\s*8MB\b',text,re.I):
        raise RuntimeError(tr('8 MB Flash wurden nicht bestätigt. Es wurde nichts geschrieben. Bitte diymore-S3-Mini-Board und Anschluss prüfen.'))

def worker_main(action,port,logfile):
    # Windowed executables have no stdout. A private temporary file transports
    # esptool output to the GUI; no shell, external Python or downloaded tools.
    with open(logfile,'w',encoding='utf-8',buffering=1) as log:
        sys.stdout=sys.stderr=log
        try:
            import esptool
            image=validate_firmware()
            prefix=['--chip','esp32s3','--port',port,'--baud','115200','--before','default_reset']
            if action=='probe':
                esptool.main(prefix+['--after','no_reset','flash_id'])
            elif action=='flash':
                esptool.main(prefix+['--after','hard_reset','write_flash','--flash_size','8MB',
                    '0x0',str(DATA/'bootloader.bin'),'0x8000',str(DATA/'partitions.bin'),
                    '0xe000',str(DATA/'boot_app0.bin'),'0x10000',str(DATA/'firmware.bin')])
            elif action=='version':
                esptool.main(['version'])
            else:
                raise ValueError(tr('Unbekannter Vorgang'))
            return 0
        except SystemExit as exc:
            return exc.code if isinstance(exc.code,int) else 1
        except Exception:
            traceback.print_exc()
            return 1

def run_tool(action,port,emit):
    if getattr(sys,'frozen',False):
        command=[sys.executable,'--worker',action,port]
    else:
        command=[sys.executable,str(pathlib.Path(__file__).resolve()),'--worker',action,port]
    with tempfile.TemporaryDirectory(prefix='SonosDial-') as temp:
        log=pathlib.Path(temp)/'operation.log'
        process=subprocess.Popen(command+[str(log)],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        sent=0;start=time.monotonic()
        try:
            while process.poll() is None:
                text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
                if len(text)>sent:emit(text[sent:]);sent=len(text)
                if time.monotonic()-start>300:
                    process.kill();process.wait()
                    raise RuntimeError(tr('Zeitüberschreitung. Verbindung prüfen und Firmware erneut vollständig schreiben.'))
                time.sleep(.15)
            text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
            if len(text)>sent:emit(text[sent:])
            if process.returncode:
                raise RuntimeError(tr('USB-Vorgang fehlgeschlagen. BOOT halten, RESET kurz drücken, BOOT loslassen; Anschluss neu suchen.\n\n')+text[-1400:])
            return text
        finally:
            if process.poll() is None:process.kill();process.wait()

from device import DeviceClient,DeviceError

class App:
    STEPS=('Anschließen','Installieren','WLAN verbinden','Raum auswählen')
    def __init__(self,root):
        self.root=root;self.events=queue.Queue();self.busy=False;self.client=None;self.device_port=None;self.page=0
        self.state={};self.ports={};self.pending_wifi=False;self.closed=False;self.details=[];self.wifi_scanned=False;self.cancel_event=threading.Event()
        root.title(tr('SonosDial · Einrichtung 1.2.0'));root.geometry('1120x820');root.minsize(900,720)
        root.protocol('WM_DELETE_WINDOW',self.close)
        self.window_icon=tk.PhotoImage(file=str(ASSETS/'sonosdial-256.png'))
        root.iconphoto(True,self.window_icon)
        style=ttk.Style();style.theme_use('clam')
        style.configure('TFrame',background='#ffffff');style.configure('TLabel',background='#ffffff',foreground='#111111',font=('Segoe UI',11))
        style.configure('TButton',font=('Segoe UI',10),padding=(14,9),background='#eeeeec',borderwidth=0)
        style.configure('Primary.TButton',background='#111111',foreground='white',font=('Segoe UI',11,'bold'),padding=(24,12))
        style.map('Primary.TButton',background=[('disabled','#aaaaaa'),('active','#333333')],foreground=[('disabled','white')])
        style.configure('TCheckbutton',background='white',font=('Segoe UI',10));style.configure('TRadiobutton',background='white',font=('Segoe UI',11))
        style.configure('TCombobox',font=('Segoe UI',11),padding=6)
        root.columnconfigure(1,weight=1);root.rowconfigure(0,weight=1)
        self.sidebar=tk.Frame(root,bg='#111111',width=220);self.sidebar.grid(row=0,column=0,sticky='ns');self.sidebar.grid_propagate(False)
        self.brand_icon=tk.PhotoImage(file=str(ASSETS/'sonosdial-48.png'))
        tk.Label(self.sidebar,image=self.brand_icon,bg='#111111',borderwidth=0).pack(anchor='w',padx=25,pady=(28,8))
        tk.Label(self.sidebar,text='SonosDial',bg='#111111',fg='white',font=('Segoe UI',25,'bold')).pack(anchor='w',padx=25,pady=(0,24))
        self.step_labels=[]
        for i,text in enumerate(self.STEPS):
            label=tk.Label(self.sidebar,text=f'{i+1}   {tr(text)}',bg='#111111',fg='#8b8b8b',font=('Segoe UI',12),anchor='w')
            label.pack(fill='x',padx=25,pady=22);self.step_labels.append(label)
        self.brand_note=tk.Label(self.sidebar,text=tr('Version 1.2.0\nUnabhängiges Projekt'),bg='#111111',fg='#aaaaaa',font=('Segoe UI',9),justify='left')
        self.brand_note.pack(side='bottom',anchor='w',padx=25,pady=25)
        language_panel=tk.Frame(self.sidebar,bg='#111111');language_panel.pack(side='bottom',fill='x',padx=25,pady=8)
        tk.Label(language_panel,text='Language / Sprache',bg='#111111',fg='#aaaaaa',font=('Segoe UI',9)).pack(anchor='w',pady=5)
        self.language_choice=tk.StringVar(value='Deutsch' if language()=='de' else 'English')
        self.language_menu=ttk.Combobox(language_panel,textvariable=self.language_choice,values=('English','Deutsch'),state='readonly',width=16)
        self.language_menu.pack(fill='x');self.language_menu.bind('<<ComboboxSelected>>',self.change_language)
        main=ttk.Frame(root,padding=(34,28));main.grid(row=0,column=1,sticky='nsew')
        footer=ttk.Frame(main);footer.pack(side='bottom',fill='x',pady=(15,0))
        self.back=ttk.Button(footer,text=tr('Zurück'),command=self.previous);self.back.pack(side='left')
        self.primary=ttk.Button(footer,text=tr('Weiter →'),style='Primary.TButton',command=self.advance);self.primary.pack(side='right')
        self.status=tk.StringVar(value='');ttk.Label(main,textvariable=self.status,wraplength=790,foreground='#555555').pack(side='bottom',fill='x',pady=(8,0))
        self.progress=ttk.Progressbar(main,mode='indeterminate');self.progress.pack(side='bottom',fill='x',pady=(8,0))
        self.eyebrow=ttk.Label(main,text='',font=('Segoe UI',9,'bold'),foreground='#666666');self.eyebrow.pack(anchor='w')
        self.title=ttk.Label(main,text='',font=('Segoe UI',28,'bold'),wraplength=800);self.title.pack(anchor='w',pady=(15,5))
        self.subtitle=ttk.Label(main,text='',wraplength=790,foreground='#555555');self.subtitle.pack(anchor='w',pady=(0,22))
        # Scroll the content only; navigation and errors remain visible on small screens.
        viewport=ttk.Frame(main);viewport.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(viewport,bg='white',highlightthickness=0);self.canvas.pack(side='left',fill='both',expand=True)
        scrollbar=ttk.Scrollbar(viewport,orient='vertical',command=self.canvas.yview);scrollbar.pack(side='right',fill='y');self.canvas.configure(yscrollcommand=scrollbar.set)
        self.body=ttk.Frame(self.canvas);self.body_id=self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(self.body_id,width=e.width))
        self.scan_ports();self.render(0);self.poll_id=root.after(100,self.poll);self.auto_scan_id=None

    def change_language(self,event=None):
        if self.busy:
            self.language_choice.set('Deutsch' if language()=='de' else 'English');return
        keep={}
        names={0:('port',),1:('consent',),2:('network_choice','password'),3:('room_choice','smart','group')}.get(self.page,())
        for name in names:
            if hasattr(self,name):keep[name]=getattr(self,name).get()
        previous_status=self.status.get();selected=self.language_choice.get()
        try:set_language(selected,persist=True)
        except OSError:
            set_language(selected)
            messagebox.showinfo('SonosDial',tr('Die Sprache gilt jetzt, konnte aber nicht gespeichert werden.'))
        self.render(self.page)
        for name,value in keep.items():getattr(self,name).set(value)
        self.status.set(tr(previous_status))

    def label(self,parent,text,size=11,**kwargs):
        label=ttk.Label(parent,text=text,font=('Segoe UI',size),wraplength=730,**kwargs);label.pack(anchor='w',pady=5);return label

    def scan_ports(self):
        found=list(list_ports.comports());self.ports={f'{p.device} · {p.description}':p.device for p in found}
        preferred=[p for p in found if p.vid==0x303a]
        self.suggested=preferred[0].device if len(preferred)==1 else found[0].device if len(found)==1 else None

    def refresh_ports(self):
        if self.busy:return
        self.scan_ports();self.render(0)

    def render(self,page):
        self.page=page
        self.root.title(tr('SonosDial · Einrichtung 1.2.0'));self.brand_note.configure(text=tr('Version 1.2.0\nUnabhängiges Projekt'));self.back.configure(text=tr('Zurück'))
        for child in self.body.winfo_children():child.destroy()
        self.canvas.yview_moveto(0)
        for i,label in enumerate(self.step_labels):
            label.configure(fg='white' if i==min(page,3) else '#8b8b8b',text=f'{"✓" if i<page else i+1}   {tr(self.STEPS[i])}')
        self.eyebrow.configure(text=tr('SCHRITT {step} VON 4').format(step=min(page+1,4)) if page<4 else tr('ALLES EINGERICHTET'))
        self.back.configure(state='normal' if page>0 and not self.busy else 'disabled')
        self.primary.configure(text=tr('Fertig') if page==4 else tr('Weiter →'),state='normal')
        titles=[tr('Verbinde deinen Regler.'),tr('Bereit für deine Musik.'),tr('Verbinde dein WLAN.'),tr('Wo spielt deine Musik?'),tr('Dein Regler ist bereit.')]
        subtitles=[tr('Ein USB-Datenkabel. Dann geht’s los.'),tr('Wir bringen den Regler auf Version 1.2.0.'),tr('Alles hier im Assistenten. Kein Browser nötig.'),tr('Wähle den Raum, den dein Regler steuern soll.'),tr('USB am Computer abziehen und später ein USB-Netzteil verwenden.')]
        self.title.configure(text=titles[page]);self.subtitle.configure(text=subtitles[page])
        if page==0:self.attach_page()
        elif page==1:self.install_page()
        elif page==2:
            self.wifi_page()
            if not self.state.get('connected') and not self.wifi_scanned:
                self.wifi_scanned=True;self.auto_scan_id=self.root.after(200,lambda:self.scan_wifi() if self.page==2 and not self.busy else None)
        elif page==3:self.rooms_page()
        else:self.ready_page()

    def attach_page(self):
        row=ttk.Frame(self.body);row.pack(fill='x',pady=10)
        picture=tk.Canvas(row,width=260,height=225,bg='white',highlightthickness=0);picture.pack(side='left',padx=(0,20))
        picture.create_rectangle(62,5,190,175,fill='#252525',outline='#111111',width=2)
        picture.create_rectangle(82,24,170,90,fill='#c2c0b9',outline='#888888');picture.create_text(126,57,text='ESP32-S3',font=('Segoe UI',11,'bold'))
        for y in range(17,165,14):
            for x in (70,182):picture.create_oval(x-3,y-3,x+3,y+3,fill='#d3b76c',outline='')
        picture.create_rectangle(105,0,147,29,fill='#b6b6b6',outline='#888888');picture.create_rectangle(112,0,140,9,fill='#333333',outline='')
        picture.create_text(126,128,text='USB-C · MINI',fill='white',font=('Segoe UI',10,'bold'))
        instructions=ttk.Frame(row);instructions.pack(side='left',fill='both',expand=True,pady=10)
        self.label(instructions,tr('So einfach geht’s'),17)
        for text in (tr('1. Board mit dem Computer verbinden.'),tr('2. Die USB-C-Buchse am Mini-Board verwenden.'),tr('3. Auf Weiter klicken.')):self.label(instructions,text)
        self.label(self.body,tr('diymore ESP32-S3 Mini: USB-C-Datenkabel verwenden und die mitgelieferte WLAN-Antenne anschließen.'),10,foreground='#666666')
        detected=bool(self.suggested)
        self.label(self.body,tr('● USB-Anschluss gefunden') if detected else tr('Noch kein eindeutiger USB-Anschluss gefunden.'),13,foreground='#247347' if detected else '#555555')
        choices=ttk.Frame(self.body);choices.pack(fill='x',pady=8)
        self.port=tk.StringVar(value=next((k for k,v in self.ports.items() if v==(self.device_port or self.suggested)),''))
        self.combo=ttk.Combobox(choices,textvariable=self.port,state='readonly',values=list(self.ports));self.combo.pack(side='left',fill='x',expand=True)
        ttk.Button(choices,text=tr('Neu suchen'),command=self.refresh_ports).pack(side='left',padx=8)
        ttk.Button(self.body,text=tr('Drehencoder anschließen ▾'),command=self.wiring).pack(anchor='w',pady=12)

    def wiring(self):
        messagebox.showinfo(tr('Drehencoder anschließen'),tr('Vor dem Verdrahten USB abziehen.\n\nKY-040 → ESP32-S3\nCLK → D3 / GPIO4\nDT → D4 / GPIO5\nSW → D5 / GPIO6\n+ → 3V3 (niemals 5V)\nGND → GND\n\nNach den Pinbeschriftungen verbinden. Der Drucktaster ist bereits im KY-040 eingebaut.'))

    def install_page(self):
        installed=self.state.get('version')=='1.2.0'
        self.label(self.body,tr('✓ Version 1.2.0 ist bereits installiert.') if installed else tr('Die passende Firmware ist im Assistenten enthalten.'),17)
        self.label(self.body,tr('WLAN- und Raumdaten bleiben beim Update erhalten, soweit sie aus SonosDial stammen. Bitte das USB-Kabel während der Installation angeschlossen lassen.'))
        self.label(self.body,tr('Vor dem Schreiben werden Chip, 8-MB-Flash und alle Firmware-Prüfsummen geprüft. Es werden nur die Firmwarebereiche beschrieben.'),10,foreground='#666666')
        self.consent=tk.BooleanVar(value=False)
        ttk.Checkbutton(self.body,text=tr('Version 1.2.0 auf den ausgewählten Regler installieren.'),variable=self.consent).pack(anchor='w',pady=18)
        self.primary.configure(text=tr('Weiter →') if installed else tr('Firmware installieren'))
        if installed:ttk.Button(self.body,text=tr('Firmware bei Bedarf erneut installieren'),command=lambda:self.flash(force=True)).pack(anchor='w',pady=8)
        ttk.Button(self.body,text=tr('Hilfe: BOOT / RESET'),command=lambda:messagebox.showinfo(tr('Wenn das Board nicht antwortet'),tr('BOOT halten → RESET kurz drücken → BOOT loslassen.\n\nDanach zurückgehen, „Neu suchen“ wählen und erneut versuchen. Nach dem Flashen gegebenenfalls RESET drücken. Der USB-Anschluss kann sich beim Neustart ändern.'))).pack(anchor='w',pady=15)
        ttk.Button(self.body,text=tr('Details'),command=self.show_details).pack(anchor='w',pady=5)

    def show_details(self):
        window=tk.Toplevel(self.root);window.title(tr('SonosDial · Details'));window.geometry('760x420')
        text=ScrolledText(window,font=('Consolas',9));text.pack(fill='both',expand=True,padx=15,pady=15)
        text.insert('end',''.join(self.details) or tr('Noch keine Installationsmeldungen.'));text.configure(state='disabled')

    def wifi_page(self):
        if self.state.get('connected'):
            self.label(self.body,tr('✓ Verbunden mit ')+self.state.get('ssid',tr('deinem WLAN')),17,foreground='#247347')
            self.label(self.body,tr('Du kannst direkt zur Raumauswahl gehen oder die Verbindung hier ändern.'))
        self.network_choice=tk.StringVar(value=self.state.get('ssid',''))
        self.label(self.body,tr('Dein WLAN'))
        networks=self.state.get('networks') or []
        self.network_box=ttk.Combobox(self.body,textvariable=self.network_choice,values=[n['ssid'] for n in networks]);self.network_box.pack(fill='x',pady=5)
        self.label(self.body,tr('Verstecktes WLAN? Den Namen einfach eingeben.'),10,foreground='#666666')
        self.password=tk.StringVar();self.label(self.body,tr('WLAN-Passwort'))
        self.password_entry=ttk.Entry(self.body,textvariable=self.password,show='●',font=('Segoe UI',12));self.password_entry.pack(fill='x',pady=5,ipady=6)
        buttons=ttk.Frame(self.body);buttons.pack(fill='x',pady=12)
        ttk.Button(buttons,text=tr('Verbinden'),style='Primary.TButton',command=self.connect_wifi).pack(side='left')
        ttk.Button(buttons,text=tr('WLANs suchen'),command=self.scan_wifi).pack(side='left',padx=8)
        self.label(self.body,tr('Oder ohne Passworteingabe'),14)
        self.label(self.body,tr('WPS starten und anschließend die WPS-Taste am Router drücken. Der Router muss WPS für 2,4 GHz unterstützen.'),10,foreground='#666666')
        ttk.Button(self.body,text=tr('Mit WPS verbinden'),command=self.wps).pack(anchor='w',pady=8)
        self.cancel_button=ttk.Button(self.body,text=tr('Verbindungsversuch abbrechen'),command=self.cancel_wifi);self.cancel_button.pack(anchor='w',pady=6)
        if not self.state.get('connected'):self.primary.configure(state='disabled')

    def rooms_page(self):
        self.room_choice=tk.StringVar(value=self.state.get('config',{}).get('room',''))
        for room in self.state.get('rooms') or []:
            ttk.Radiobutton(self.body,text=room['name'],variable=self.room_choice,value=room['id']).pack(fill='x',pady=10,ipady=7)
        if not self.state.get('rooms'):self.label(self.body,tr('Noch keine Sonos-Räume gefunden. Regler und Sonos müssen sich im selben erreichbaren Heimnetz befinden.'))
        self.smart=tk.BooleanVar(value=self.state.get('config',{}).get('smart',False))
        self.group=tk.BooleanVar(value=self.state.get('config',{}).get('group',True))
        ttk.Checkbutton(self.body,text=tr('Der Musik folgen'),variable=self.smart).pack(anchor='w',pady=(18,4))
        self.label(self.body,tr('Steuert die einzige spielende Gruppe. Wenn mehrere oder keine spielen, gilt dein gewählter Raum.'),10,foreground='#666666')
        ttk.Checkbutton(self.body,text=tr('Lautstärke für die ganze Gruppe'),variable=self.group).pack(anchor='w',pady=8)
        row=ttk.Frame(self.body);row.pack(fill='x',pady=14)
        ttk.Button(row,text=tr('Erneut suchen'),command=self.scan_rooms).pack(side='left')
        ttk.Button(row,text=tr('Weitere Einstellungen'),command=self.advanced).pack(side='left',padx=8)
        self.primary.configure(text=tr('Raum speichern →'))

    def ready_page(self):
        cfg=self.state.get('config',{});name=next((r['name'] for r in self.state.get('rooms',[]) if r['id']==cfg.get('room')),tr('deinen gewählten Raum'))
        self.label(self.body,tr('Dein Regler steuert ')+name+'.',19)
        self.label(self.body,tr('So bedienst du ihn'),16)
        for action,result in [(tr('Rechts drehen'),tr('Lauter')),(tr('Links drehen'),tr('Leiser')),(tr('1× drücken'),'Play/Pause'),(tr('2× drücken'),tr('Nächster Titel')),(tr('3× drücken'),tr('Vorheriger Titel'))]:
            row=ttk.Frame(self.body);row.pack(fill='x',pady=7);ttk.Label(row,text=action,width=25,font=('Segoe UI',12,'bold')).pack(side='left');ttk.Label(row,text=result).pack(side='left')
        self.label(self.body,tr('Du kannst den Assistenten später erneut öffnen und die Einstellungen über USB ändern.'),10,foreground='#666666')
        ttk.Button(self.body,text=tr('Einstellungen öffnen'),command=lambda:self.render(3)).pack(anchor='w',pady=15)

    def advanced(self):
        if self.busy:return
        window=tk.Toplevel(self.root);window.title(tr('SonosDial · Einstellungen'));window.geometry('520x440');window.transient(self.root);window.grab_set()
        frame=ttk.Frame(window,padding=25);frame.pack(fill='both',expand=True);cfg=self.state.get('config',{})
        reverse=tk.BooleanVar(value=cfg.get('reverse',True));step=tk.StringVar(value=str(cfg.get('step',2)));edges=tk.StringVar(value=str(cfg.get('edges',4)));seed=tk.StringVar(value=cfg.get('seed',''))
        ttk.Checkbutton(frame,text=tr('Drehrichtung umkehren'),variable=reverse).pack(anchor='w',pady=10)
        for label,variable,values in [(tr('Lautstärkeschritt pro Rastung'),step,['1','2','3','4','5']),(tr('Flanken pro Rastung'),edges,['4','2'])]:
            self.label(frame,label);ttk.Combobox(frame,textvariable=variable,values=values,state='readonly').pack(fill='x',pady=5)
        self.label(frame,tr('Optionale Sonos-IP'));ttk.Entry(frame,textvariable=seed).pack(fill='x',pady=5)
        def save():
            values=dict(reverse=reverse.get(),step=int(step.get()),edges=int(edges.get()),seed=seed.get().strip());window.destroy()
            self.start(lambda:self.save_settings(values))
        ttk.Button(frame,text=tr('Speichern'),style='Primary.TButton',command=save).pack(anchor='e',pady=20)

    def save_settings(self,values):
        self.client.request('config_set',**values);self.events.put(('state',self.client.request('status')));self.events.put(('status',tr('Einstellungen gespeichert.')))

    def previous(self):
        if not self.busy and self.page>0:self.render(self.page-1)

    def advance(self):
        if self.busy:return
        if self.page==0:self.connect_device()
        elif self.page==1:
            if self.state.get('version')=='1.2.0':self.render(2)
            else:self.flash()
        elif self.page==2:
            if self.state.get('connected'):self.scan_rooms()
        elif self.page==3:self.save_room()
        else:self.close()

    def set_busy(self,busy):
        self.busy=busy
        self.language_menu.configure(state='disabled' if busy else 'readonly')
        self.primary.configure(state='disabled' if busy else 'normal')
        self.back.configure(state='normal' if not busy and self.page>0 else 'disabled')
        if busy:self.progress.start(15)
        else:self.progress.stop()
        if not busy and self.page==2 and not self.state.get('connected'):self.primary.configure(state='disabled')

    def start(self,work):
        if self.busy:return
        self.set_busy(True)
        def task():
            try:work()
            except Exception as exc:self.events.put(('error',str(exc)))
            finally:self.events.put(('done',None))
        threading.Thread(target=task,daemon=True).start()

    def connect_device(self):
        port=self.ports.get(self.port.get())
        if not port:messagebox.showinfo(tr('Board anschließen'),tr('Bitte Board mit einem USB-Datenkabel anschließen und „Neu suchen“ wählen.'));return
        self.device_port=port;self.status.set(tr('USB-Verbindung wird geprüft …'))
        def task():
            if self.client:self.client.close();self.client=None
            client=DeviceClient(port)
            try:state=client.hello(timeout=3)
            except DeviceError:client.close();state={}
            else:self.client=client
            self.events.put(('state',state));self.events.put(('page',1));self.events.put(('status',tr('Bereit.')))
        self.start(task)

    def flash(self,force=False):
        if self.busy:return
        if not self.consent.get():messagebox.showinfo(tr('Firmware installieren'),tr('Bitte die Installation auf dem ausgewählten Board bestätigen.'));return
        port=self.device_port
        if not port:return
        self.status.set(tr('Board wird geprüft. USB bitte angeschlossen lassen …'))
        def task():
            if self.client:self.client.close();self.client=None
            emit=lambda text:self.events.put(('log',text))
            check_device(run_tool('probe',port,emit));self.events.put(('status',tr('Firmware wird geschrieben und verifiziert …')))
            run_tool('flash',port,emit)
            deadline=time.monotonic()+25;last=None
            while time.monotonic()<deadline:
                # USB CDC can disappear and re-enumerate after reset.
                available=list(list_ports.comports());native=[p.device for p in available if p.vid==0x303a]
                candidates=[port] if any(p.device==port for p in available) else native if len(native)==1 else []
                for candidate in candidates:
                    client=None
                    try:
                        client=DeviceClient(candidate);state=client.hello(timeout=2)
                        if state.get('version')!='1.2.0':raise DeviceError(tr('Version 1.2.0 noch nicht gestartet.'))
                    except Exception as exc:
                        last=exc
                        if client:client.close()
                    else:
                        self.client=client;self.device_port=candidate;self.events.put(('state',state));self.events.put(('page',2));self.events.put(('status',tr('Version 1.2.0 installiert. Jetzt WLAN verbinden.')));return
                time.sleep(.6)
            raise DeviceError(tr('Firmware wurde geschrieben. Bitte RESET drücken und über „Zurück“ den Anschluss neu suchen. ')+str(last or ''))
        self.start(task)

    def scan_wifi(self):
        if self.busy:return
        self.status.set(tr('Der Regler sucht WLANs …'))
        def task():
            self.client.request('wifi_scan');state=self.client.wait(lambda s:not s.get('scanning'),timeout=25)
            self.events.put(('state',state));self.events.put(('page',2));self.events.put(('status',tr('WLAN auswählen oder den Namen eingeben.')))
        self.start(task)

    def connect_wifi(self):
        if self.busy:return
        ssid=self.network_choice.get();password=self.password.get();self.password.set('')
        if not ssid or len(ssid.encode())>32 or (password and not 8<=len(password.encode())<=63):messagebox.showinfo(tr('WLAN prüfen'),tr('WLAN-Namen wählen und Passwort mit 8–63 Byte eingeben. Für ein offenes WLAN das Passwort leer lassen.'));return
        self.pending_wifi=True;self.cancel_event.clear();self.status.set(tr('WLAN-Verbindung wird aufgebaut …'))
        def task():
            try:
                self.client.request('wifi_connect',ssid=ssid,password=password)
                state=self.client.wait(lambda s:s.get('connected') and not s.get('pending'),timeout=40,cancel=self.cancel_event)
                self.events.put(('state',state));self.events.put(('page',2));self.events.put(('status',tr('WLAN verbunden und gespeichert. Weiter zur Raumauswahl.')))
            finally:
                if self.cancel_event.is_set():self.client.request('wifi_cancel')
                self.pending_wifi=False
        self.start(task)

    def wps(self):
        if self.busy:return
        self.pending_wifi=True;self.cancel_event.clear();self.status.set(tr('Jetzt die WPS-Taste am Router drücken. Wir warten bis zu zwei Minuten …'))
        def task():
            try:
                self.client.request('wps_start');state=self.client.wait(lambda s:s.get('connected') and not s.get('wps'),timeout=160,cancel=self.cancel_event)
                self.events.put(('state',state));self.events.put(('page',2));self.events.put(('status',tr('WPS erfolgreich. WLAN gespeichert.')))
            finally:
                if self.cancel_event.is_set():self.client.request('wifi_cancel')
                self.pending_wifi=False
        self.start(task)

    def cancel_wifi(self):
        if not self.pending_wifi:return
        self.cancel_event.set();self.status.set(tr('Verbindungsversuch wird abgebrochen …'))

    def scan_rooms(self):
        if self.busy:return
        self.status.set(tr('Sonos-Räume werden gesucht …'))
        def task():
            before=self.client.request('status').get('room_revision',0);self.client.request('rooms_scan')
            state=self.client.wait(lambda s:not s.get('discovering'),timeout=30)
            self.events.put(('state',state));self.events.put(('page',3))
            self.events.put(('status',tr('Raum auswählen.') if state.get('rooms') and state.get('room_revision',0)>before else tr('Keine neuen Sonos-Räume gefunden. Heimnetz prüfen oder unter „Weitere Einstellungen“ eine Sonos-IP eingeben.')))
        self.start(task)

    def save_room(self):
        if self.busy:return
        room=self.room_choice.get()
        if not room:messagebox.showinfo(tr('Raum auswählen'),tr('Bitte zuerst einen Sonos-Raum auswählen.'));return
        values=dict(room=room,smart=self.smart.get(),group=self.group.get())
        def task():
            self.client.request('config_set',**values);self.events.put(('state',self.client.request('status')));self.events.put(('page',4));self.events.put(('status',tr('Alles gespeichert. Viel Spaß mit deinem Regler.')))
        self.start(task)

    def poll(self):
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=='state':self.state=value
                elif kind=='page':self.render(value)
                elif kind=='status':self.status.set(value)
                elif kind=='log':self.details.append(value)
                elif kind=='error':self.status.set(tr('Vorgang nicht abgeschlossen.'));messagebox.showerror('SonosDial',value)
                elif kind=='done':self.set_busy(False)
        except queue.Empty:pass
        if not self.closed:self.poll_id=self.root.after(100,self.poll)

    def close(self):
        if self.busy:messagebox.showinfo(tr('Vorgang läuft'),tr('Bitte den Vorgang abwarten. WLAN-/WPS-Verbindungen können über den Abbrechen-Knopf beendet werden.'));return
        if self.client:self.client.close()
        self.closed=True
        for name in ('poll_id','auto_scan_id'):
            timer=getattr(self,name,None)
            if timer:
                try:self.root.after_cancel(timer)
                except tk.TclError:pass
        self.root.destroy()

def self_test(destination):
    results={};validate_firmware();results['firmware_sha256']='pass'
    check_device('Chip is ESP32-S3\nDetected flash size: 8MB')
    for bad in ('Chip is ESP32\nDetected flash size: 8MB','Chip is ESP32-S3\nDetected flash size: 16MB',''):
        try:check_device(bad)
        except RuntimeError:pass
        else:raise AssertionError('Unsafe chip accepted')
    results['device_guards']='pass';assert '4.8.1' in run_tool('version','unused',lambda text:None);results['bundled_esptool']='pass'
    root=tk.Tk();root.withdraw();app=App(root)
    app.state={'connected':True,'ssid':'Testnetz','config':{'room':'R1','step':2,'edges':4},'rooms':[{'id':'R1','name':'Wohnzimmer'}],'networks':[{'ssid':'Testnetz'}]}
    original_language=language()
    for selected_language in ('en','de'):
        set_language(selected_language)
        for page in range(5):app.render(page);root.update()
        assert app.primary['text']==tr('Fertig')
    app.close();set_language(original_language);results['five_wizard_screens']='pass';results['english_german_screens']='pass';results['startup_language']=original_language
    pathlib.Path(destination).write_text(json.dumps(results,indent=2),encoding='utf-8')

def parse_args(argv=None):
    parser=argparse.ArgumentParser(description='SonosDial USB setup assistant')
    parser.add_argument('--lang',choices=('en','de','english','german','English','Deutsch'))
    parser.add_argument('--self-test',metavar='RESULT_JSON')
    parser.add_argument('--worker',nargs=3,metavar=('ACTION','PORT','LOG'))
    return parser.parse_args(argv)

if __name__=='__main__':
    args=parse_args()
    if args.lang:set_language(args.lang)
    if args.worker:raise SystemExit(worker_main(*args.worker))
    if args.self_test:
        try:self_test(args.self_test)
        except Exception:pathlib.Path(args.self_test).write_text(traceback.format_exc(),encoding='utf-8');raise
    else:
        root=tk.Tk();App(root);root.mainloop()
