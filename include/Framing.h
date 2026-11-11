#pragma once
#include <stddef.h>
// Bounded serial framing. On overflow discard the entire line through newline.
template<size_t Capacity> struct LineBuffer {
 char data[Capacity+1]{};size_t size=0;bool dropping=false;
 // 1 complete line, -1 discarded oversized line, 0 incomplete.
 int put(char c){
  if(c=='\r')return 0;
  if(c=='\n'){if(dropping){dropping=false;size=0;return -1;}data[size]=0;size=0;return 1;}
  if(dropping)return 0;
  if(size==Capacity){dropping=true;size=0;return 0;}
  data[size++]=c;return 0;
 }
};
