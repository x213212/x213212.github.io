---
title: "氣浮球 實作"
date: "2018-08-25T14:14:00.000+08:00"
updated: "2019-10-06T22:46:39.081+08:00"
permalink: "/2018/08/x-ylcd2d-main.html"
original_url: "https://x8795278.blogspot.com/2018/08/x-ylcd2d-main.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-1597631945059229784"
tags: ["Embedded", "GameMaker", "Tutorial", "Projects"]
layout: post
---

# 氣浮球 嵌入式構思

這次我們要結合的觸控螢幕x y軸和lcd繪圖的控制做出2D氣浮球對打  

![](https://i.imgur.com/yNVtR3A.png)

遊戲方法想辦法進入對手的得分區  

![](https://i.imgur.com/HClMJDz.png)

預期功能要實作的功能是
牆壁反射和得分區和腳色移動的球反射
[![](https://i.imgur.com/Nal1r33.jpg)](https://i.imgur.com/Nal1r33.jpg)
  

時間允許的會可能會增加得分還是記分板
[![](https://i.imgur.com/IdHmP8g.jpg)](https://i.imgur.com/IdHmP8g.jpg)
  

```c
Main.c
#include “irq.h”
#include “uart.h”
#include “lib.h”
#include “stdio.h”
/////////////////////////////////////
//宣告player struct
//x 腳色位置
//y 腳色位置
//point 得幾分
/////////////////////////////////////
typedef struct player {
unsigned int x;
unsigned int y;
unsigned int point;
} Player;
int tmp_ballx=10;
int tmp_bally=10;

static Player p1,p2,ball;
void ball_move(){
int touch=0,i=0,j=0;
if(ball.x+20>=800 ||p2.x>ball.x && p2.x<ball.x+20 && p2.y<=ball.y && ball.y<=p2.y+60 || ball.x+20 >p1.x && ball.x < p1.x && p1.y<=ball.y && ball.y<=p1.y+60 ){
tmp_ballx=-10;
touch=1;
}

if(ball.x-20<=0 || ball.x >p1.x && ball.x-20 < p1.x && p1.y<=ball.y && ball.y<=p1.y+60  ||p2.x>ball.x-20 &&  p2.x<ball.x && p2.y<=ball.y && ball.y<=p2.y+60  ){
  tmp_ballx=10;
  touch=1;
}
if(ball.y+20>=480 ||p2.x>ball.x && p2.x <ball.x+20 && p2.y<=ball.y && ball.y<=p2.y+60 ||  ball.x+20 >p1.x && ball.x < p1.x && p1.y<=ball.y && ball.y<=p1.y+60 ){
  tmp_bally=-10;
touch=1;
}
if(ball.y-20<=0 || ball.x >p1.x >p1.x &&  ball.x-20 < p1.x && p1.y<=ball.y && ball.y<=p1.y+60 ||p2.x>ball.x-20 &&  p2.x<ball.x && p2.y<=ball.y && ball.y<=p2.y+60  ){
  tmp_bally=10;
  touch=1;
}
  lcd_clr_rect(ball.y,ball.x,ball.y+20,ball.x+20,0x0);
  ball.y+=tmp_bally;
  ball.x+=tmp_ballx;
  lcd_clr_rect(ball.y,ball.x,ball.y+20,ball.x+20,0xffffff);
if(touch==1){
    char k[300]="Player1:";
    char kk[10];
    sprintf(kk,"%d",p1.point);
    char kk2[]="  Player2:";
    char kk3[10];
    sprintf(kk3,"%d",p2.point);
    char kk4[]="\n\r";
    strcat(k,kk);
    strcat(k,kk2);
    strcat(k,kk3);
    strcat(k,kk4);
 for(i=300;i<300+200;i++)
    for(j=400;j<400+16;j++)
      lcd_draw_pixel(j, i, 0x0);
      printf2(k,300,400);
      lcd_clr_rect(p1.y,p1.x,p1.y+60,p1.x+10,0xffffff);
      lcd_clr_rect(p2.y,p2.x,p2.y+60,p2.x+10,0xffffff);}
if(ball.x<25&& ball.y>=160&& ball.y<=320){
      lcd_clr_rect(160,0,160*2,50,0xffffff);
      lcd_clr_rect(160,0,160*2,50,0x0);
      p2.point+=1;
	}
if(ball.x>775&& ball.y>=160&& ball.y<=320){
      lcd_clr_rect(160,750,160*2,800,0xffffff);
      lcd_clr_rect(160,750,160*2,800,0x0);
      p1.point+=1;
    }
}

int main(void){
/////////////////////////////////////
//初始化參數
//tmpx[2] tmpy[2] 用來抓點
//ret…用來儲存暫存器的值
/////////////////////////////////////
unsigned int tmpx[2]={0};
unsigned int tmpy[2]={0};
unsigned int tmp = 0;
unsigned int ret = 0, ret1 = 0,ret3 = 0,ret5 = 0,ret4 = 0,ret2 = 0,i = 0x00001;
unsigned int count=0;
p1.point=0;
p2.point=0;
p1.x=20;
p1.y=0;
p2.x=760;
p2.y=0;
ball.x=400;
ball.y=240;

irq_init();
i2c_init();
lcd_init();
//清空畫面 
lcd_clear_screen(0x0);
unsigned int j=0,k=0,l=0,m=0,op;

while(1)
{
  //畫地圖 
  lcd_draw_vline(50, 160, 320, 0xffffff);//進球孔 
  lcd_draw_vline(750, 160, 320, 0xffffff);//進球孔
  lcd_draw_hline(160, 0,50, 0xffffff);//進球孔
  lcd_draw_hline(320, 0,50, 0xffffff);//進球孔
  lcd_draw_hline(160, 750,800, 0xffffff);//進球孔
  lcd_draw_hline(320, 750,800, 0xffffff);//進球孔
  Delay(10000);
  ball_move();
  
  
  tmp = at24cxx_read(0x02);
 	if(tmp > 0 && tmp < 6){
 		//補足在讀取時間 球沒有移動 
        for(i=0;i<4;i++)
            ball_move();

        ret2 = at24cxx_read(0x04);//xl
		ret3 = at24cxx_read(0x03);//xh
		ret4 = at24cxx_read(0x06);//yl
		ret5 = at24cxx_read(0x05);//yh
        tmpx[0]=((ret3&0xf)<<8)|ret2;
        tmpy[0]=((ret5&0xf)<<8)|ret4;

        ret2 = at24cxx_read(0x0A);//xl
		ret3 = at24cxx_read(0x09);//xh
		ret4 = at24cxx_read(0x0C);//yl
		ret5 = at24cxx_read(0x0B);//yh
        tmpx[1]=((ret3&0xf)<<8)|ret2;
        tmpy[1]=((ret5&0xf)<<8)|ret4;
        
        for(i =0 ;i<2;i++){
            if(tmpx[i]>=0 && tmpx[i]<=200){      
                 lcd_clr_rect(p1.y,p1.x,p1.y+60,p1.x+10,0x0);
                 lcd_clr_rect(tmpy[i],tmpx[i],tmpy[i]+60,tmpx[i]+10,0xffffff);
                 p1.y=tmpy[i];
                 p1.x=tmpx[i];
            }
            else if(tmpx[i]>=600&& tmpx[i]<=800){
                 lcd_clr_rect(p2.y,p2.x,p2.y+60,p2.x+10,0x0);
                 lcd_clr_rect(tmpy[i],tmpx[i],tmpy[i]+60,tmpx[i]+10,0xffffff);
                 p2.y=tmpy[i];
                 p2.x=tmpx[i];
            }
        }
 
	
}
}
return 0;
}
```
