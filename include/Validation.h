#pragma once
#include <stddef.h>
#include <cstring>
inline bool validWifi(size_t ssidBytes,size_t passwordBytes){return ssidBytes>=1&&ssidBytes<=32&&(passwordBytes==0||(passwordBytes>=8&&passwordBytes<=63));}
inline bool validEncoderSettings(int step,int edges){return step>=1&&step<=5&&(edges==2||edges==4);}
inline const char* playbackAction(const char* state){
 if(!strcmp(state,"PLAYING"))return "Pause";
 if(!strcmp(state,"PAUSED_PLAYBACK")||!strcmp(state,"STOPPED"))return "Play";
 return nullptr;
}
