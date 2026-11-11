#include "../include/Input.h"
#include <assert.h>
#include <stdio.h>
#include <initializer_list>
#include <vector>
struct Trace{Button button;std::vector<int> events;uint32_t time=0;void sample(bool down,uint32_t duration){for(uint32_t i=0;i<duration;i++,time++){int e=button.update(down,time);if(e)events.push_back(e);}}void click(){sample(true,70);sample(false,80);}};
int main(){
 Encoder e;int total=0;for(int n=0;n<100;n++)for(int s:{2,0,1,3})total+=e.update(s);assert(total==-100);
 for(int n=0;n<100;n++)for(int s:{1,0,2,3})total+=e.update(s);assert(total==0);
 // Contact bounce and reversal must not add detents.
 e=Encoder();total=0;for(int s:{2,3,2,0,2,0,1,0,1,3})total+=e.update(s);assert(total==-1);
 e=Encoder();assert(e.update(0)==0);assert(e.sum==0);
 for(int clicks=1;clicks<=3;clicks++){Trace t;for(int i=0;i<clicks;i++)t.click();t.sample(false,500);assert(t.events==std::vector<int>{clicks});}
 Trace held;held.sample(true,2500);held.sample(false,500);assert(held.events==std::vector<int>{});
 Trace bounce;bounce.sample(true,8);bounce.sample(false,9);bounce.sample(true,7);bounce.sample(false,600);assert(bounce.events.empty());
 Trace singles;singles.click();singles.sample(false,500);singles.click();singles.sample(false,500);assert((singles.events==std::vector<int>{1,1}));
 Trace clickHold;clickHold.click();clickHold.sample(true,2500);clickHold.sample(false,500);assert(clickHold.events==std::vector<int>{});
 Trace rollover;rollover.time=0xfffffff0u;rollover.sample(true,2500);rollover.sample(false,500);assert(rollover.events==std::vector<int>{});
 Trace four;for(int i=0;i<4;i++)four.click();four.sample(false,500);assert((four.events==std::vector<int>{3,1}));
 puts("PASS Mini USB: encoder/bounce, 1/2/3 clicks, hold, release suppression, click+hold, separated clicks, rollover, fourth click");
}
