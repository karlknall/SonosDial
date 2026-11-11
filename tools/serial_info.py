"""Developer helper: read 1.0 status, never display saved WLAN passwords."""
import sys,json,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'installer'))
from device import DeviceClient
client=DeviceClient(sys.argv[1])
try:print(json.dumps(client.hello(),ensure_ascii=False,indent=2))
finally:client.close()
