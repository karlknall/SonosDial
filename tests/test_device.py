import collections,json,pathlib,sys,threading,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
from device import DeviceClient,DeviceError,PREFIX
from i18n import set_language
class FakeSerial:
    def __init__(self,reply=None):self.lines=collections.deque();self.sent=[];self.reply=reply;self.closed=False
    def write(self,frame):
        request=json.loads(frame[len(PREFIX):]);self.sent.append(request)
        reply=self.reply(request) if self.reply else dict(id=request['id'],ok=True,product='SonosDial',protocol=1,version='1.2.0')
        if reply is not None:self.lines.append(PREFIX+json.dumps(reply,ensure_ascii=False).encode()+b'\n')
    def readline(self,n):return self.lines.popleft() if self.lines else b''
    def close(self):self.closed=True
class DeviceTests(unittest.TestCase):
    def setUp(self):set_language('de')
    def test_hello(self):
        fake=FakeSerial();c=DeviceClient('FAKE',fake);self.assertEqual(c.hello()['version'],'1.2.0');c.close();self.assertTrue(fake.closed)
    def test_boot_noise_and_wrong_id(self):
        fake=FakeSerial();fake.lines.extend([b'ESP-ROM boot\n',PREFIX+b'{bad}\n',PREFIX+b'{"id":99,"ok":true}\n']);self.assertTrue(DeviceClient('FAKE',fake).request('status')['ok'])
    def test_fragmented_response(self):
        fake=FakeSerial(lambda r:None);fake.lines.extend([PREFIX+b'{"id":',b'1,"ok":true,',b'"name":"K\xc3',b'\xbcche"}\n']);self.assertEqual(DeviceClient('FAKE',fake).request('status')['name'],'Küche')
    def test_oversized_response_recovery(self):
        fake=FakeSerial();fake.lines.extend([PREFIX+b'x'*32768,b'end\n']);self.assertTrue(DeviceClient('FAKE',fake).request('status')['ok'])
    def test_error(self):
        c=DeviceClient('FAKE',FakeSerial(lambda r:dict(id=r['id'],ok=False,error='Passwort prüfen')))
        with self.assertRaisesRegex(DeviceError,'Passwort prüfen'):c.request('wifi_connect',ssid='Test',password='secret-123')
    def test_timeout(self):
        with self.assertRaises(DeviceError):DeviceClient('FAKE',FakeSerial(lambda r:None)).request('status',timeout=.005)
    def test_request_bound(self):
        fake=FakeSerial()
        with self.assertRaises(DeviceError):DeviceClient('FAKE',fake).request('wifi_connect',password='x'*2000)
        self.assertEqual(fake.sent,[])
    def test_cancel(self):
        event=threading.Event();event.set();fake=FakeSerial()
        with self.assertRaisesRegex(DeviceError,'abgebrochen'):DeviceClient('FAKE',fake).wait(lambda s:False,cancel=event)
        self.assertEqual(fake.sent,[])
    def test_saved_settings_no_password_in_status(self):
        saved={};connected=False
        def emulator(r):
            nonlocal connected
            if r['cmd']=='wifi_connect':saved.update(ssid=r['ssid'],password=r['password']);connected=True
            if r['cmd']=='config_set':saved['room']=r['room']
            return dict(id=r['id'],ok=True,connected=connected,pending=False,config={'room':saved.get('room','')},ssid=saved.get('ssid',''),error='')
        c=DeviceClient('FAKE',FakeSerial(emulator));c.request('wifi_connect',ssid='Küche WLAN',password='secret-123');self.assertTrue(c.wait(lambda s:s['connected'])['connected']);c.request('config_set',room='R1');state=c.request('status');self.assertEqual(state['config']['room'],'R1');self.assertNotIn('secret-123',json.dumps(state))
    def test_wps_success_and_failure(self):
        for success in (True,False):
            def emulator(r):return dict(id=r['id'],ok=True,connected=success,wps=False,error='' if success else 'WPS hat nicht geklappt')
            c=DeviceClient('FAKE',FakeSerial(emulator));c.request('wps_start')
            if success:self.assertTrue(c.wait(lambda s:s['connected'])['connected'])
            else:
                with self.assertRaisesRegex(DeviceError,'WPS'):c.wait(lambda s:s['connected'])
if __name__=='__main__':unittest.main()
