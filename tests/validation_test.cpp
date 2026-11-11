#include "../include/Validation.h"
#include <cassert>
#include <cstdio>
int main(){
 assert(validWifi(1,0)&&validWifi(32,63)&&validWifi(4,8));
 assert(!validWifi(0,8)&&!validWifi(33,8)&&!validWifi(4,7)&&!validWifi(4,64));
 assert(validEncoderSettings(1,2)&&validEncoderSettings(5,4));
 assert(!validEncoderSettings(0,4)&&!validEncoderSettings(6,4)&&!validEncoderSettings(2,3));
 assert(!strcmp(playbackAction("PLAYING"),"Pause"));assert(!strcmp(playbackAction("PAUSED_PLAYBACK"),"Play"));assert(!strcmp(playbackAction("STOPPED"),"Play"));
 assert(!playbackAction("TRANSITIONING")&&!playbackAction("")&&!playbackAction("NO_MEDIA_PRESENT"));
 puts("PASS: WiFi byte bounds, setting bounds, Play/Pause state decisions and unsupported/unknown states");
}
