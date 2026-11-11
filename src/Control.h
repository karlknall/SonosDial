#pragma once
// Main-loop-owned provisioning. WiFi callbacks only publish atomic event flags.
const char* VERSION="1.2.0";
std::atomic<int> wpsEvent{0};
bool wpsRunning=false,wifiPending=false,scanRunning=false;
uint32_t provisionStarted=0;String pendingSsid,pendingPass,provisionError;
DynamicJsonDocument networks(8192);
LineBuffer<1536> serialLine;

void configJson(JsonObject o,const Config& c,bool secret=false){
 o["ssid"]=c.ssid;if(secret)o["pass"]=c.pass;
 o["room"]=c.room;o["seed"]=c.seed;o["smart"]=c.smart;o["group"]=c.group;
 o["reverse"]=c.reverse;o["step"]=c.step;o["edges"]=c.edges;
}
bool saveConfig(const Config& c){
 DynamicJsonDocument doc(2048);configJson(doc.to<JsonObject>(),c,true);String json;serializeJson(doc,json);
 if(prefs.putString("settings1",json)!=json.length()){provisionError="Einstellungen konnten nicht dauerhaft gespeichert werden.";return false;}
 xSemaphoreTake(lock,portMAX_DELAY);cfg=c;xSemaphoreGive(lock);encoderEdges=c.edges;return true;
}
void loadConfig(){
 DynamicJsonDocument d(2048);String saved=prefs.getString("settings1");
 if(saved.length() && !deserializeJson(d,saved)){
  cfg.ssid=d["ssid"].as<String>();cfg.pass=d["pass"].as<String>();cfg.room=d["room"].as<String>();cfg.seed=d["seed"].as<String>();
  cfg.smart=d["smart"]|false;cfg.group=d["group"]|true;cfg.reverse=d["reverse"]|true;cfg.step=d["step"]|2;cfg.edges=d["edges"]|4;
 }else{
  // Non-destructive migration of the known-working 0.1 settings.
  cfg.ssid=prefs.getString("ssid");cfg.pass=prefs.getString("pass");cfg.room=prefs.getString("room");cfg.seed=prefs.getString("seed");
  cfg.smart=prefs.getBool("smart",false);cfg.group=prefs.getBool("group",true);cfg.reverse=prefs.getBool("reverse",true);cfg.step=prefs.getInt("step",2);cfg.edges=prefs.getInt("edges",4);
 }
 cfg.step=constrain(cfg.step,1,5);if(cfg.edges!=2 && cfg.edges!=4)cfg.edges=4;
}
bool provisioningActive(){return wpsRunning||wifiPending;}
void wifiEvent(WiFiEvent_t event,arduino_event_info_t){
 if(event==ARDUINO_EVENT_WPS_ER_SUCCESS)wpsEvent=1;
 if(event==ARDUINO_EVENT_WPS_ER_FAILED)wpsEvent=2;
 if(event==ARDUINO_EVENT_WPS_ER_TIMEOUT)wpsEvent=3;
}
void stopWps(){if(wpsRunning)esp_wifi_wps_disable();wpsRunning=false;wpsEvent=0;}
void restoreKnownWifi(){
 Config c=config();WiFi.setAutoReconnect(true);
 if(c.ssid.length())WiFi.begin(c.ssid.c_str(),c.pass.c_str());else startAP();
}
void cancelProvisioning(){
 bool active=provisioningActive();stopWps();wifiPending=false;pendingSsid="";pendingPass="";controlPaused=false;
 if(active){WiFi.disconnect(false,false);restoreKnownWifi();}
}
void tickProvisioning(){
 if(scanRunning){int n=WiFi.scanComplete();if(n>=0){
   networks.clear();auto list=networks.to<JsonArray>();
   for(int i=0;i<n && list.size()<24;i++){
    String ssid=WiFi.SSID(i);if(ssid.isEmpty())continue;bool duplicate=false;
    for(auto item:list)if(item["ssid"].as<String>()==ssid)duplicate=true;
    if(duplicate)continue;auto item=list.createNestedObject();item["ssid"]=ssid;item["rssi"]=WiFi.RSSI(i);item["open"]=WiFi.encryptionType(i)==WIFI_AUTH_OPEN;
   }WiFi.scanDelete();scanRunning=false;
  }else if(n==WIFI_SCAN_FAILED){scanRunning=false;provisionError="WLAN-Suche fehlgeschlagen. Bitte erneut suchen.";}
 }
 if(wpsRunning){int event=wpsEvent.exchange(0);
  if(event==1){
   wifi_config_t obtained{};bool valid=esp_wifi_get_config(WIFI_IF_STA,&obtained)==ESP_OK;
   String ssid=String((char*)obtained.sta.ssid,strnlen((char*)obtained.sta.ssid,sizeof(obtained.sta.ssid))),pass=String((char*)obtained.sta.password,strnlen((char*)obtained.sta.password,sizeof(obtained.sta.password)));
   stopWps();if(valid && ssid.length()){
    pendingSsid=ssid;pendingPass=pass;wifiPending=true;provisionStarted=millis();WiFi.begin(ssid.c_str(),pass.c_str());
   }else{provisionError="WPS lieferte keine Zugangsdaten. Bitte WLAN mit Passwort verwenden.";controlPaused=false;restoreKnownWifi();}
  }else if(event==2 || event==3 || uint32_t(millis()-provisionStarted)>120000){
   stopWps();controlPaused=false;provisionError="WPS hat nicht geklappt. Bitte erneut versuchen oder WLAN mit Passwort wählen.";restoreKnownWifi();
  }
 }
 if(wifiPending){
  if(WiFi.status()==WL_CONNECTED && WiFi.SSID()==pendingSsid){
   Config c=config();if(c.ssid!=pendingSsid){c.room="";c.seed="";clearTopology=true;}c.ssid=pendingSsid;c.pass=pendingPass;
   bool stored=saveConfig(c);wifiPending=false;pendingSsid="";pendingPass="";controlPaused=false;WiFi.setAutoReconnect(true);
   if(stored){provisionError="";rescan=true;report("WLAN verbunden und gespeichert");}
  }else if(uint32_t(millis()-provisionStarted)>30000){
   cancelProvisioning();provisionError="WLAN-Verbindung fehlgeschlagen. Passwort und 2,4-GHz-Netz prüfen. Bisherige Einstellungen bleiben erhalten.";
  }
 }
}
void statusJson(JsonObject out){
 out["version"]=VERSION;out["protocol"]=1;out["product"]="SonosDial";out["hardware"]=HARDWARE_VARIANT;out["flash_bytes"]=ESP.getFlashChipSize();out["psram_bytes"]=ESP.getPsramSize();
 out["connected"]=WiFi.status()==WL_CONNECTED && !provisioningActive();
 out["ssid"]=WiFi.SSID();out["ip"]=WiFi.localIP().toString();out["pending"]=wifiPending;out["wps"]=wpsRunning;
 out["scanning"]=scanRunning;out["discovering"]=discoveryBusy.load()||rescan.load();out["error"]=provisionError;
 out["networks"].set(networks.as<JsonArray>());configJson(out.createNestedObject("config"),config());
 xSemaphoreTake(lock,portMAX_DELAY);String snapshot=roomSnapshot,s=status;uint32_t revision=roomRevision;xSemaphoreGive(lock);
 DynamicJsonDocument roomDoc(16384);deserializeJson(roomDoc,snapshot);out["rooms"].set(roomDoc.as<JsonArray>());
 out["room_revision"]=revision;out["status"]=s;
}
void handleCommand(JsonObject request,JsonDocument& reply){
 reply["id"]=request["id"]|0;reply["ok"]=false;
 String cmd=request["cmd"]|"";
 auto fail=[&](const char* message){reply["error"]=message;};
 if(cmd=="hello"||cmd=="status"||cmd=="config_get"){
  statusJson(reply.to<JsonObject>()); // to() clears members: restore request ID below.
  reply["id"]=request["id"]|0;reply["ok"]=true;return;
 }
 if(cmd=="wifi_scan"){
  if(provisioningActive()){fail("Bitte den laufenden Verbindungsversuch abwarten oder abbrechen.");return;}
  if(!scanRunning){WiFi.scanDelete();networks.clear();networks.to<JsonArray>();provisionError="";
   int result=WiFi.scanNetworks(true,true);scanRunning=result==WIFI_SCAN_RUNNING;
   if(result==WIFI_SCAN_FAILED){fail("WLAN-Suche konnte nicht gestartet werden.");return;}
  }
 }else if(cmd=="wifi_connect"){
  if(provisioningActive()||scanRunning){fail("Bitte den laufenden Vorgang abwarten.");return;}
  if(!request["ssid"].is<const char*>()||!request["password"].is<const char*>()){fail("WLAN-Name und Passwort fehlen.");return;}
  String ssid=request["ssid"].as<String>(),pass=request["password"].as<String>();
  if(!validWifi(ssid.length(),pass.length())){fail("WLAN-Name oder Passwortlänge ungültig.");return;}
  provisionError="";controlPaused=true;pendingSsid=ssid;pendingPass=pass;wifiPending=true;provisionStarted=millis();
  WiFi.setAutoReconnect(false);WiFi.disconnect(false,false);WiFi.begin(ssid.c_str(),pass.c_str());
 }else if(cmd=="wps_start"){
  if(provisioningActive()||scanRunning){fail("Bitte den laufenden Vorgang abwarten.");return;}
  provisionError="";wpsEvent=0;controlPaused=true;
  if(ap){dns.stop();WiFi.softAPdisconnect(true);ap=false;}
  WiFi.setAutoReconnect(false);WiFi.disconnect(false,false);WiFi.mode(WIFI_STA);
  esp_wps_config_t wps{};wps.wps_type=WPS_TYPE_PBC;
  strcpy(wps.factory_info.manufacturer,"SonosDial");strcpy(wps.factory_info.model_name,"SonosDial");strcpy(wps.factory_info.model_number,"1.2.0");strcpy(wps.factory_info.device_name,"SonosDial");
  esp_err_t enabled=esp_wifi_wps_enable(&wps);esp_err_t started=enabled==ESP_OK?esp_wifi_wps_start(0):enabled;
  if(started!=ESP_OK){esp_wifi_wps_disable();controlPaused=false;restoreKnownWifi();fail("WPS konnte nicht gestartet werden. Bitte WLAN mit Passwort wählen.");return;}
  wpsRunning=true;provisionStarted=millis();
 }else if(cmd=="wifi_cancel"){
  cancelProvisioning();provisionError="";
 }else if(cmd=="rooms_scan"){
  if(WiFi.status()!=WL_CONNECTED||provisioningActive()){fail("Bitte zuerst WLAN verbinden.");return;}provisionError="";rescan=true;
 }else if(cmd=="config_set"){
  Config c=config();
  if(request.containsKey("room")){
   if(!request["room"].is<const char*>()){fail("Bitte einen Raum wählen.");return;}
   String uuid=request["room"].as<String>();bool found=false;
   xSemaphoreTake(lock,portMAX_DELAY);String snapshot=roomSnapshot;xSemaphoreGive(lock);
   DynamicJsonDocument d(16384);deserializeJson(d,snapshot);for(auto r:d.as<JsonArray>())if(r["id"].as<String>()==uuid)found=true;
   if(!found){fail("Raum nicht mehr verfügbar. Bitte erneut suchen.");return;}c.room=uuid;
  }
  const char* boolKeys[]={"smart","group","reverse"};for(auto key:boolKeys)if(request.containsKey(key)&&!request[key].is<bool>()){fail("Ungültige Einstellung.");return;}
  if(request.containsKey("smart"))c.smart=request["smart"].as<bool>();if(request.containsKey("group"))c.group=request["group"].as<bool>();if(request.containsKey("reverse"))c.reverse=request["reverse"].as<bool>();
  if(request.containsKey("step")){if(!request["step"].is<int>()){fail("Schrittweite ungültig.");return;}c.step=request["step"].as<int>();}
  if(request.containsKey("edges")){if(!request["edges"].is<int>()){fail("Encoder-Einstellung ungültig.");return;}c.edges=request["edges"].as<int>();}
  if(!validEncoderSettings(c.step,c.edges)){fail("Einstellung außerhalb des erlaubten Bereichs.");return;}
  if(request.containsKey("seed")){IPAddress ip;c.seed=request["seed"].as<String>();if(c.seed.length()&&!ip.fromString(c.seed)){fail("Sonos-IP ungültig.");return;}rescan=true;}
  if(!saveConfig(c)){fail("Einstellungen konnten nicht gespeichert werden.");return;}
 }else{fail("Unbekannter Befehl. Assistent und Firmware müssen zusammenpassen.");return;}
 reply["ok"]=true;
}
void processSerial(){
 // Prefix and request ID let the PC ignore ROM boot output and old replies.
 for(int budget=0;budget<256&&Serial.available();budget++){
  int done=serialLine.put(char(Serial.read()));if(done<=0)continue;
  if(strncmp(serialLine.data,"@SD1 ",5)!=0)continue;
  DynamicJsonDocument request(2048),reply(28672);
  auto error=deserializeJson(request,serialLine.data+5);
  if(error || !request.is<JsonObject>()){reply["id"]=0;reply["ok"]=false;reply["error"]="Ungültige USB-Anfrage.";}
  else if(request["cmd"].as<String>()=="ap_info"){
   reply["id"]=request["id"]|0;reply["ok"]=true;reply["ssid"]="SonosDial-Setup";reply["password"]=apPassword;
  }else handleCommand(request.as<JsonObject>(),reply);
  Serial.print("@SD1 ");serializeJson(reply,Serial);Serial.println();
 }
}
