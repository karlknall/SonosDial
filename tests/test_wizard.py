import pathlib,sys,time,unittest,gc
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
from app import App,tk
from device import DeviceClient
from test_device import FakeSerial
from i18n import set_language
class WizardTests(unittest.TestCase):
    def setUp(self):
        set_language('de')
        self.root=tk.Tk();self.root.withdraw();self.app=App(self.root);self.errors=[]
        self.error_patch=patch('app.messagebox.showerror',side_effect=lambda title,message:self.errors.append(message));self.error_patch.start()
        self.saved={'ssid':'','room':''};self.connected=False;self.revision=0;self.wps_fail=False;self.hold_wps=False;self.commands=[]
        self.fake=FakeSerial(self.emulator);self.app.client=DeviceClient('FAKE',self.fake);self.app.wifi_scanned=True
        self.app.state=self.emulator({'cmd':'status','id':0});self.app.render(2)
    def tearDown(self):
        self.error_patch.stop();self.app.close();self.app=None;self.root=None;gc.collect()
    def emulator(self,r):
        cmd=r['cmd'];self.commands.append(cmd)
        if cmd=='wifi_connect':self.saved['ssid']=r['ssid'];self.connected=True
        if cmd=='rooms_scan':self.revision+=1
        if cmd=='config_set':self.saved.update({k:r[k] for k in ('room','smart','group') if k in r})
        if cmd=='wifi_cancel':self.hold_wps=False
        return dict(id=r['id'],ok=True,product='SonosDial',protocol=1,version='1.2.0',connected=self.connected,pending=False,wps=self.hold_wps,ssid=self.saved['ssid'],config=dict(self.saved),networks=[{'ssid':'Testnetz'}],scanning=False,discovering=False,room_revision=self.revision,rooms=[{'id':'R1','name':'Wohnzimmer'}] if self.connected else [],error='WPS fehlgeschlagen' if self.wps_fail and cmd=='status' else '')
    def drain(self,timeout=4):
        deadline=time.monotonic()+timeout
        while self.app.busy and time.monotonic()<deadline:self.root.update();time.sleep(.01)
        self.root.update();self.assertFalse(self.app.busy)
    def test_full_usb_setup(self):
        for lang in ('en','de'):
            set_language(lang);self.app.render(2)
            self.app.network_choice.set('Testnetz');self.app.password.set('secret-123');self.app.connect_wifi();self.drain()
            self.assertTrue(self.app.state['connected']);self.assertEqual(self.app.password.get(),'')
            self.app.scan_rooms();self.drain();self.assertEqual(self.app.page,3)
            self.app.room_choice.set('R1');self.app.save_room();self.drain();self.assertEqual(self.app.page,4)
            self.assertEqual(self.saved['room'],'R1');self.assertFalse(self.errors)
            self.assertNotIn('secret-123',str(self.app.details)+str(self.app.state))
    def test_wps_failure(self):
        self.wps_fail=True;self.app.wps();self.drain();self.assertTrue(any('WPS' in e for e in self.errors));self.assertEqual(self.app.page,2)
    def test_wps_cancel(self):
        self.hold_wps=True;self.app.wps();self.root.update();self.app.cancel_wifi();self.drain()
        self.assertIn('wifi_cancel',self.commands);self.assertFalse(self.app.pending_wifi);self.assertTrue(any('abgebrochen' in e for e in self.errors))
    def test_scanning_and_invalid_password(self):
        self.app.scan_wifi();self.drain();self.assertIn('Testnetz',self.app.network_box['values'])
        with patch('app.messagebox.showinfo') as info:
            self.app.network_choice.set('Testnetz');self.app.password.set('short');self.app.connect_wifi();info.assert_called_once()
        self.assertNotIn('wifi_connect',self.commands)
if __name__=='__main__':unittest.main()
