#pragma once
#include <stdint.h>
// Gray-code decoder: reversals cancel; illegal two-bit jumps reset accumulation.
struct Encoder {
 uint8_t previous=3; int sum=0; int edges=4;
 int update(uint8_t value) {
  static const int8_t lut[16]={0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0};
  if ((previous^value)==3) sum=0;
  else sum+=lut[(previous<<2)|value];
  previous=value;
  if(sum>=edges){sum=0;return 1;} if(sum<=-edges){sum=0;return -1;} return 0;
 }
};
struct Button {
 bool raw=false, stable=false, held=false; uint8_t clicks=0;
 uint32_t changed=0, down=0, released=0;
 // USB standard: 1 play/pause, 2 next, 3 previous. Hold is consumed silently.
 // 350 ms between clicks; 25 ms debounce. No command while held or on release.
 int update(bool pressed,uint32_t now){
  if(pressed!=raw){raw=pressed;changed=now;}
  if(raw!=stable && uint32_t(now-changed)>=25){
   stable=raw;
   if(stable){down=now;held=false;}
   else if(!held){clicks++;released=now;if(clicks==3){clicks=0;return 3;}}
  }
  if(stable && !held && uint32_t(now-down)>=2000){held=true;clicks=0;return 0;}
  if(clicks && !stable && uint32_t(now-released)>350){int result=clicks;clicks=0;return result;} return 0;
 }
};
