#include "../include/Framing.h"
#include <cassert>
#include <cstring>
#include <cstdio>
#include <initializer_list>
int main(){LineBuffer<8> b;for(char c: {'a','b','c'})assert(b.put(c)==0);assert(b.put('\n')==1);assert(!strcmp(b.data,"abc"));
 for(int i=0;i<9;i++)assert(!b.put('x'));assert(b.put('\n')==-1);
 assert(!b.put('o'));assert(!b.put('\r'));assert(!b.put('k'));assert(b.put('\n')==1);assert(!strcmp(b.data,"ok"));
 for(int i=0;i<8;i++)b.put('a');assert(b.put('\n')==1);assert(strlen(b.data)==8);
 puts("PASS framing: bounded lines, overflow drop/recovery, CRLF, exact capacity");}
