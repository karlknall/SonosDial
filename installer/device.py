# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 SonosDial contributors
"""Versioned, bounded USB JSON protocol. Never logs requests or WLAN passwords."""
import json,threading,time
from i18n import tr
import serial
PREFIX=b'@SD1 '
class DeviceError(RuntimeError):pass
class DeviceClient:
    def __init__(self,port,transport=None):
        self.port=port;self.counter=0;self.lock=threading.Lock()
        if transport is None:
            self.serial=serial.Serial(port=None,baudrate=115200,timeout=.15,write_timeout=2)
            self.serial.port=port;self.serial.dtr=True;self.serial.rts=False;self.serial.open()
        else:self.serial=transport
    def close(self):self.serial.close()
    def request(self,cmd,timeout=5,**args):
        with self.lock:
            self.counter+=1;identifier=self.counter
            frame=PREFIX+json.dumps(dict(id=identifier,cmd=cmd,**args),ensure_ascii=False,separators=(',',':')).encode()+b'\n'
            if len(frame)>1537:raise DeviceError(tr('Die Anfrage ist zu groß.'))
            self.serial.write(frame);deadline=time.monotonic()+timeout;pending=b'';dropping=False
            while time.monotonic()<deadline:
                line=self.serial.readline(32769)
                if not line:continue
                if dropping:
                    if line.endswith(b'\n'):dropping=False
                    continue
                pending+=line
                if len(pending)>32768:
                    dropping=not pending.endswith(b'\n');pending=b'';continue
                if not pending.endswith(b'\n'):continue
                line=pending;pending=b''
                if not line.startswith(PREFIX):continue
                try:reply=json.loads(line[len(PREFIX):])
                except (ValueError,UnicodeError):continue
                if not isinstance(reply,dict) or reply.get('id')!=identifier:continue
                if reply.get('ok') is not True:raise DeviceError(tr(str(reply.get('error','Der Regler konnte die Anfrage nicht ausführen.'))))
                return reply
            raise DeviceError(tr('Der Regler antwortet nicht. USB / OTG und Datenkabel prüfen; nach einem Neustart „Neu suchen“ wählen.'))
    def hello(self,timeout=8):
        deadline=time.monotonic()+timeout;last=None
        while time.monotonic()<deadline:
            try:
                reply=self.request('hello',timeout=min(1.2,max(.1,deadline-time.monotonic())))
                if reply.get('product')!='SonosDial' or reply.get('protocol')!=1:raise DeviceError(tr('Dieser Regler verwendet eine andere Konfigurationsschnittstelle.'))
                return reply
            except DeviceError as exc:last=exc
        raise last or DeviceError(tr('Regler nicht erreichbar.'))
    def wait(self,predicate,timeout=35,notify=None,cancel=None):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if cancel and cancel.is_set():raise DeviceError(tr('Verbindungsversuch abgebrochen.'))
            state=self.request('status')
            if state.get('error'):raise DeviceError(tr(state['error']))
            if notify:notify(state)
            if predicate(state):return state
            time.sleep(.4)
        raise DeviceError(tr('Der Vorgang dauert zu lange. Bitte Verbindung prüfen und erneut versuchen.'))
