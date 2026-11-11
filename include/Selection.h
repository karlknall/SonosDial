#pragma once
#include <vector>
#include <stddef.h>
template<class Rooms,class Id>
int chooseRoom(const Rooms& rooms,const Id& fixed,bool smart,const std::vector<size_t>& playing){
 if(smart && playing.size()==1 && playing[0]<rooms.size())return int(playing[0]);
 for(size_t i=0;i<rooms.size();i++)if(rooms[i].uuid==fixed)return int(i);
 return -1;
}
