#include "../include/Xml.h"
#include <cassert>
#include <cstdio>
int main(){
 tinyxml2::XMLDocument doc;
 const char* soap="<s:Envelope xmlns:s='urn:test'><s:Body><u:GetZoneGroupStateResponse xmlns:u='urn:test'><ZoneGroupState>&lt;ZoneGroupState&gt;&lt;ZoneGroups&gt;&lt;ZoneGroup Coordinator=&quot;R1&quot;&gt;&lt;ZoneGroupMember UUID=&quot;R1&quot; ZoneName=&quot;Küche &amp;amp; Essen&quot; Location=&quot;http://192.168.1.2:1400/xml/device_description.xml&quot;/&gt;&lt;/ZoneGroup&gt;&lt;/ZoneGroups&gt;&lt;/ZoneGroupState&gt;</ZoneGroupState></u:GetZoneGroupStateResponse></s:Body></s:Envelope>";
 assert(doc.Parse(soap)==tinyxml2::XML_SUCCESS);
 auto* state=findElement(&doc,"ZoneGroupState");assert(state&&state->GetText());tinyxml2::XMLDocument inner;assert(inner.Parse(state->GetText())==tinyxml2::XML_SUCCESS);
 auto* groups=findElement(&inner,"ZoneGroups");assert(groups);auto* group=groups->FirstChildElement("ZoneGroup");assert(!strcmp(group->Attribute("Coordinator"),"R1"));assert(!strcmp(group->FirstChildElement()->Attribute("ZoneName"),"Küche & Essen"));
 doc.Parse("<ZoneGroups><ZoneGroup/></ZoneGroups>");assert(findElement(&doc,"ZoneGroups"));assert(!findElement(&doc,"Missing"));
 assert(doc.Parse("<broken>")!=tinyxml2::XML_SUCCESS);
 doc.Parse("<s:Envelope><s:Body><CurrentMute>0</CurrentMute></s:Body></s:Envelope>");assert(!strcmp(findElement(&doc,"CurrentMute")->GetText(),"0"));
 doc.Parse("<root><ZoneGroupState><![CDATA[<ZoneGroups/>]]></ZoneGroupState></root>");assert(!strcmp(findElement(&doc,"ZoneGroupState")->GetText(),"<ZoneGroups/>"));
 puts("PASS: SOAP namespaces, nested/flat topology, escaped room names, missing tags, malformed XML, CDATA, zero mute");
}
