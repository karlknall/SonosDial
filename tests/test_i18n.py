import ast,json,pathlib,sys,tempfile,unittest,gc
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
import i18n
from app import App,tk
from device import DeviceClient,DeviceError
from test_device import FakeSerial
class LanguageTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language('de');gc.collect()
    def test_windows_default(self):
        self.assertEqual(i18n.windows_language(0x0407),'de');self.assertEqual(i18n.windows_language(0x0807),'de')
        self.assertEqual(i18n.windows_language(0x0409),'en');self.assertEqual(i18n.windows_language(0x0411),'en')
    def test_preference_roundtrip_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'ui.json';i18n.set_language('English',persist=True,path=p);self.assertEqual(i18n.read_language(p),'en')
            self.assertEqual(json.loads(p.read_text()),{'language':'en'})
            i18n.set_language('Deutsch',persist=True,path=p);self.assertEqual(i18n.read_language(p),'de')
            p.write_text('bad')
            with patch('i18n.windows_language',return_value='en'):self.assertEqual(i18n.read_language(p),'en')
    def test_known_device_errors_in_english(self):
        i18n.set_language('en');fake=FakeSerial(lambda r:dict(id=r['id'],ok=False,error='Bitte zuerst WLAN verbinden.'))
        with self.assertRaisesRegex(DeviceError,'connect to Wi-Fi first'):DeviceClient('FAKE',fake).request('rooms_scan')
    def test_all_screens_both_languages(self):
        root=tk.Tk();root.withdraw();app=App(root);app.wifi_scanned=True
        app.state={'connected':True,'ssid':'Küche WLAN','config':{'room':'R1'},'rooms':[{'id':'R1','name':'Wohnzimmer'}],'networks':[]}
        try:
            for lang in ('en','de'):
                i18n.set_language(lang)
                for page in range(5):app.render(page);root.update_idletasks()
                self.assertEqual(app.primary['text'],'Done' if lang=='en' else 'Fertig')
                self.assertEqual(app.title['text'],'Your controller is ready.' if lang=='en' else 'Dein Regler ist bereit.')
            self.assertEqual(app.state['ssid'],'Küche WLAN');self.assertEqual(app.state['rooms'][0]['name'],'Wohnzimmer')
        finally:app.close()
    def test_manual_switch_preserves_unsaved_inputs(self):
        i18n.set_language('de');root=tk.Tk();root.withdraw();app=App(root);app.wifi_scanned=True
        app.state={'connected':True,'ssid':'Testnetz','config':{},'rooms':[]};app.render(2)
        try:
            app.network_choice.set('Mein eigenes WLAN');app.password.set('secret-123')
            with tempfile.TemporaryDirectory() as d,patch('i18n.preferences_path',return_value=pathlib.Path(d)/'ui.json'):
                app.language_choice.set('English');app.change_language()
                self.assertEqual(app.network_choice.get(),'Mein eigenes WLAN');self.assertEqual(app.password.get(),'secret-123')
                self.assertEqual(app.title['text'],'Connect to Wi-Fi.')
                self.assertEqual(json.loads((pathlib.Path(d)/'ui.json').read_text()),{'language':'en'})
        finally:app.close()
    def test_firmware_messages_have_translations(self):
        source=pathlib.Path(__file__).resolve().parents[1]/'src/Control.h'
        import re
        messages=re.findall(r'(?:fail\(|provisionError=)"([^"]+)"',source.read_text(encoding='utf-8'))
        for message in messages:self.assertIn(message,i18n.EN)
if __name__=='__main__':unittest.main()
