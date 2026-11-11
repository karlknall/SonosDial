#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <ESPmDNS.h>
#include <tinyxml2.h>
#include <vector>
#include <atomic>
#include <ArduinoJson.h>
#include <esp_wps.h>
#include <esp_wifi.h>
#include "Framing.h"
#include "Input.h"
#include "Board.h"
#include "Xml.h"
#include "Selection.h"
#include "Validation.h"
using namespace tinyxml2;
struct Room {String uuid,name,ip,coordinator;};
struct Config {String ssid,pass,room,seed; bool smart=false,group=true,reverse=true; int step=2,edges=4;};
Config cfg; Preferences prefs; WebServer web(80); DNSServer dns;
SemaphoreHandle_t lock; QueueHandle_t actions; portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;
struct Action {int kind;uint32_t at;};
volatile int delta=0; volatile uint32_t deltaAt=0; std::atomic<bool> rescan{true}; String status="Start", roomList; bool ap=false;
std::atomic<int> encoderEdges{4};
std::atomic<bool> discoveryBusy{false};
std::atomic<bool> controlPaused{false},clearTopology{false};
String roomSnapshot="[]"; uint32_t roomRevision=0;
String token,apPassword; std::vector<Room> rooms; uint32_t topologyAt=0;
void report(String s){xSemaphoreTake(lock,portMAX_DELAY);status=s;xSemaphoreGive(lock);}
Config config(){xSemaphoreTake(lock,portMAX_DELAY);Config c=cfg;xSemaphoreGive(lock);return c;}
String escape(String s){s.replace("&","&amp;");s.replace("<","&lt;");s.replace(">","&gt;");s.replace("\"","&quot;");s.replace("'","&#39;");return s;}
String decode(String s){s.replace("&lt;","<");s.replace("&gt;",">");s.replace("&quot;","\"");s.replace("&apos;","'");s.replace("&amp;","&");return s;}
String value(const String&s,const char*t){XMLDocument doc;if(doc.Parse(s.c_str())!=XML_SUCCESS)return "";auto* e=findElement(&doc,t);return e&&e->GetText()?String(e->GetText()):String("");}
String soap(String ip,String service,String action,String args){
 WiFiClient client; HTTPClient h; String path=service=="ZoneGroupTopology"?"/ZoneGroupTopology/Control":"/MediaRenderer/"+service+"/Control";
 h.setConnectTimeout(700);h.setTimeout(900);
 if(!h.begin(client,"http://"+ip+":1400"+path))return "";
 String urn="urn:schemas-upnp-org:service:"+service+":1";
 h.addHeader("Content-Type","text/xml; charset=\"utf-8\"");h.addHeader("SOAPACTION","\""+urn+"#"+action+"\"");
 String body="<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:"+action+" xmlns:u=\""+urn+"\">"+args+"</u:"+action+"></s:Body></s:Envelope>";
 int code=h.POST(body);String result=h.getString();h.end();
 if(code!=200 || result.indexOf("<s:Fault")>=0){report(action+": HTTP "+String(code)+" UPnP "+value(result,"errorCode"));return "";}return result;
}
String attr(XMLElement* e,const char*n){const char*v=e->Attribute(n);return v?String(v):String("");}
String host(String url){int p=url.indexOf("://");if(p<0)return "";int end=url.indexOf(':',p+3);if(end<0)end=url.indexOf('/',p+3);String s=url.substring(p+3,end);IPAddress ip;return ip.fromString(s)?s:String("");}
bool topology(String ip){
 String xml=value(soap(ip,"ZoneGroupTopology","GetZoneGroupState",""),"ZoneGroupState");
 XMLDocument doc;if(doc.Parse(xml.c_str())!=XML_SUCCESS)return false;
 XMLElement* root=findElement(&doc,"ZoneGroups");if(!root)return false;
 std::vector<Room> fresh;
 for(auto*g=root->FirstChildElement("ZoneGroup");g;g=g->NextSiblingElement("ZoneGroup"))
 for(auto*m=g->FirstChildElement("ZoneGroupMember");m;m=m->NextSiblingElement("ZoneGroupMember")){
  if(attr(m,"Invisible")=="1")continue;
  Room r{attr(m,"UUID"),attr(m,"ZoneName"),host(attr(m,"Location")),attr(g,"Coordinator")};
  if(r.ip.length() && r.uuid.length() && fresh.size()<64)fresh.push_back(r);
 }
 if(fresh.empty())return false;rooms=fresh;topologyAt=millis();String list;
 for(auto&r:rooms)list+="<option value='"+escape(r.uuid)+"'>"+escape(r.name)+"</option>";
 DynamicJsonDocument snapshot(16384);auto array=snapshot.to<JsonArray>();
 for(auto&r:rooms){auto item=array.createNestedObject();item["id"]=r.uuid;item["name"]=r.name;item["coordinator"]=r.coordinator;}
 String json;serializeJson(snapshot,json);
 xSemaphoreTake(lock,portMAX_DELAY);roomList=list;roomSnapshot=json;roomRevision++;xSemaphoreGive(lock);report("Sonos-Raeume: "+String(rooms.size()));return true;
}
bool discover(){
 Config c=config();if(c.seed.length() && topology(c.seed))return true;
 if(!rooms.empty() && topology(rooms[0].ip))return true;
 WiFiUDP udp;udp.begin(0);udp.beginPacket(IPAddress(239,255,255,250),1900);
 udp.print("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: urn:schemas-upnp-org:device:ZonePlayer:1\r\n\r\n");udp.endPacket();
 uint32_t start=millis();std::vector<String> ips;
 while(uint32_t(millis()-start)<1600){if(udp.parsePacket()){String ip=udp.remoteIP().toString();bool seen=false;for(auto&s:ips)if(s==ip)seen=true;if(!seen && ips.size()<64)ips.push_back(ip);while(udp.available())udp.read();}vTaskDelay(5);}
 udp.stop();for(auto&ip:ips)if(topology(ip))return true;report("Keine Sonos gefunden; WLAN/Multicast oder Start-IP pruefen");return false;
}
bool selectRoom(Config c,Room &selected,Room &coordinator){
 std::vector<size_t> playing;
 if(c.smart){for(size_t i=0;i<rooms.size();i++)if(rooms[i].uuid==rooms[i].coordinator){
  String s=soap(rooms[i].ip,"AVTransport","GetTransportInfo","<InstanceID>0</InstanceID>");
  if(value(s,"CurrentTransportState")=="PLAYING")playing.push_back(i);}
 }
 int chosen=chooseRoom(rooms,c.room,c.smart,playing);
 if(chosen<0){report("Bitte festen Raum waehlen; intelligente Auswahl ist nicht eindeutig");return false;}
 selected=rooms[chosen];for(auto&r:rooms)if(r.uuid==selected.coordinator){coordinator=r;return true;}
 report("Gruppenkoordinator fehlt");return false;
}
void worker(void*){
 uint32_t lastDiscovery=0;bool connected=false;
 for(;;){
  if(clearTopology.exchange(false)){rooms.clear();topologyAt=0;xSemaphoreTake(lock,portMAX_DELAY);roomSnapshot="[]";roomRevision++;xSemaphoreGive(lock);}
  if(controlPaused){portENTER_CRITICAL(&mux);delta=0;portEXIT_CRITICAL(&mux);xQueueReset(actions);vTaskDelay(50);continue;}
  if(WiFi.status()!=WL_CONNECTED){connected=false;portENTER_CRITICAL(&mux);delta=0;portEXIT_CRITICAL(&mux);xQueueReset(actions);vTaskDelay(100);continue;}
  if(!connected){connected=true;rescan=true;}
  if(rescan.exchange(false) || uint32_t(millis()-lastDiscovery)>30000){lastDiscovery=millis();discoveryBusy=true;discover();discoveryBusy=false;}
  int d;uint32_t at;portENTER_CRITICAL(&mux);d=delta;at=deltaAt;delta=0;portEXIT_CRITICAL(&mux);
  if(uint32_t(millis()-at)>1500)d=0;
  Action event{0,0};xQueueReceive(actions,&event,0);int action=uint32_t(millis()-event.at)<=1500?event.kind:0;
  if(d || action){
   // Refresh coordinator membership before a new gesture after an idle period.
   if(uint32_t(millis()-topologyAt)>5000 && !rooms.empty() && !topology(rooms[0].ip)){report("Topologie nicht erreichbar; Eingabe verworfen");rescan=true;continue;}
   // Never execute old gestures after long discovery/outage.
   if(uint32_t(millis()-topologyAt)>45000){report("Topologie veraltet; Eingabe verworfen");rescan=true;continue;}
   Config c=config();Room r,g;if(!selectRoom(c,r,g))continue;
   if(uint32_t(millis()-at)>2000)d=0;
   if(uint32_t(millis()-event.at)>2000)action=0;
   String service=c.group?"GroupRenderingControl":"RenderingControl";String ip=c.group?g.ip:r.ip;
   String base="<InstanceID>0</InstanceID>";if(!c.group)base+="<Channel>Master</Channel>";
   if(d){
    // Relative commands avoid a read-modify-write race with the Sonos app.
    // Group snapshot preserves current member volume relationships.
    bool ready=!c.group || soap(ip,service,"SnapshotGroupVolume",base).length();
    if(ready)soap(ip,service,c.group?"SetRelativeGroupVolume":"SetRelativeVolume",base+"<Adjustment>"+String(constrain(d,-20,20)*c.step*(c.reverse?-1:1))+"</Adjustment>");
   }
   if(action==1){String transport=value(soap(g.ip,"AVTransport","GetTransportInfo","<InstanceID>0</InstanceID>"),"CurrentTransportState");
    const char* command=playbackAction(transport.c_str());
    if(command)soap(g.ip,"AVTransport",command,String("<InstanceID>0</InstanceID>")+(String(command)=="Play"?"<Speed>1</Speed>":""));
    else report("Wiedergabe derzeit nicht umschaltbar");
   }
   if(action==2 || action==3)soap(g.ip,"AVTransport",action==2?"Next":"Previous","<InstanceID>0</InstanceID>");
  }vTaskDelay(35);
 }
}
void inputTask(void*){Encoder e;Button b;while(!digitalRead(ENCODER_SW))vTaskDelay(10);e.previous=(digitalRead(ENCODER_CLK)<<1)|digitalRead(ENCODER_DT);e.edges=encoderEdges;for(;;){if(e.edges!=encoderEdges){e.edges=encoderEdges;e.sum=0;}int d=e.update((digitalRead(ENCODER_CLK)<<1)|digitalRead(ENCODER_DT));if(d){portENTER_CRITICAL(&mux);delta=constrain(delta+d,-20,20);deltaAt=millis();portEXIT_CRITICAL(&mux);}Action a{b.update(!digitalRead(ENCODER_SW),millis()),millis()};if(a.kind)xQueueSend(actions,&a,0);vTaskDelay(1);}}
void startAP(){if(ap)return;ap=true;WiFi.softAP("SonosDial-Setup",apPassword.c_str());dns.start(53,"*",WiFi.softAPIP());report("Setup-WLAN Passwort: "+apPassword);}
#include "Control.h"
#include "WebUI.h"
void setup(){
 Serial.begin(115200);pinMode(ENCODER_CLK,INPUT_PULLUP);pinMode(ENCODER_DT,INPUT_PULLUP);pinMode(ENCODER_SW,INPUT_PULLUP);
 lock=xSemaphoreCreateMutex();actions=xQueueCreate(8,sizeof(Action));prefs.begin("sonosdial",false);
 loadConfig();encoderEdges=cfg.edges;networks.to<JsonArray>();
 token=String(esp_random(),HEX)+String(esp_random(),HEX);apPassword=prefs.getString("apkey");if(apPassword.isEmpty()){apPassword="dial-"+String(esp_random(),HEX);prefs.putString("apkey",apPassword);}
 WiFi.persistent(false);WiFi.onEvent(wifiEvent);WiFi.mode(WIFI_AP_STA);WiFi.setSleep(false);WiFi.setAutoReconnect(true);
 if(cfg.ssid.length())WiFi.begin(cfg.ssid.c_str(),cfg.pass.c_str());
 if(cfg.ssid.isEmpty() || !digitalRead(ENCODER_SW))startAP();
 installWebRoutes();web.begin();
 xTaskCreatePinnedToCore(inputTask,"input",4096,nullptr,2,nullptr,1);
 xTaskCreatePinnedToCore(worker,"sonos",16384,nullptr,1,nullptr,0);
}
void loop(){
 processSerial();tickProvisioning();web.handleClient();if(ap)dns.processNextRequest();
 static uint32_t lost=millis();static bool mdns=false;
 if(WiFi.status()==WL_CONNECTED){lost=millis();if(!mdns)mdns=MDNS.begin("sonosdial");}
 else if(!provisioningActive() && uint32_t(millis()-lost)>25000)startAP();
 delay(2);
}
