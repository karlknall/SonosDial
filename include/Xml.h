#pragma once
#include <tinyxml2.h>
#include <cstring>
inline tinyxml2::XMLElement* findElement(tinyxml2::XMLNode* node,const char* name){
 if(!node)return nullptr;
 for(auto* e=node->FirstChildElement();e;e=e->NextSiblingElement()){
  const char* local=std::strrchr(e->Name(),':');local=local?local+1:e->Name();
  if(std::strcmp(local,name)==0)return e;
  if(auto* found=findElement(e,name))return found;
 }return nullptr;
}
