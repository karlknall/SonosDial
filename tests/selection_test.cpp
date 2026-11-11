#include "../include/Selection.h"
#include <string>
#include <cassert>
#include <cstdio>
struct R{std::string uuid;};
int main(){std::vector<R> rooms{{"R1"},{"R2"},{"R3"}};
 assert(chooseRoom(rooms,std::string("R2"),false,{0})==1);
 assert(chooseRoom(rooms,std::string("R2"),true,{0})==0);
 assert(chooseRoom(rooms,std::string("R2"),true,{0,2})==1);
 assert(chooseRoom(rooms,std::string("R2"),true,{})==1);
 assert(chooseRoom(rooms,std::string("missing"),true,{0,2})==-1);
 assert(chooseRoom(rooms,std::string("missing"),false,{0})==-1);
 assert(chooseRoom(std::vector<R>{},std::string("R1"),true,{})==-1);
 puts("PASS: fixed selection, unique playing group, ambiguous/idle fallback, absent room, empty household");
}
