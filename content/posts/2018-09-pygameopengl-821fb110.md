---
title: "Pygame_openGL(第一人稱視角)"
date: "2018-09-07T02:09:00.001+08:00"
updated: "2019-09-13T08:53:13.629+08:00"
permalink: "/2018/09/pygameopengl.html"
original_url: "https://x8795278.blogspot.com/2018/09/pygameopengl.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5685245306657703089"
tags: ["Python", "Tutorial", "Projects"]
layout: post
---

## Pygame_openGL(第一人稱視角)

## ---

  

[![](https://i.imgur.com/IinMm86.gif)](https://i.imgur.com/IinMm86.gif)
  

修正後順便來鋪個地板，在移動方面可能還需要再更動
  

目前只有擺頭而已，移動的話可能還需要再研究，
找第一人稱視角真久，原理竟然是到線性代數最後幾章
[opengl-tutorial](http://www.opengl-tutorial.org/cn/beginners-tutorials/tutorial-6-keyboard-and-mouse/)參考公式
我們先來上扣以後再來理解原理
會覺得閃爍是版本問題沒有雙衝緩衝，pyopengl第一人稱資源少的可憐，恐怖fps?!
還是我沒找到?
#  if( buff==False):
#     buff= True
#     mypos_buff=direction
這邊我以為我腦袋有問題，看能不能避開閃爍，結果還是不行，y軸上下會增加卡頓，
  

  

```python
import pygame
from pygame.locals import *
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import sys
import random

tmp=0.5

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

vertices2 = (
    (-1.0,-1.0,1.0),
    (1.0,-1.0,1.0),
    (1.0,1.0,1.0),
    (-1.0,1.0,1.0),
    (-1.0,-1.0,-1.0),
    (-1.0,1.0,-1.0),
    (1.0,1.0,-1.0),
    (1.0,-1.0,-1.0),
    (-1.0,1.0,-1.0),
    (-1.0,1.0,1.0),
    (1.0,1.0,1.0),
    (1.0,1.0,-1.0),
    (-1.0,-1.0,-1.0),
    (1.0,-1.0,-1.0),
    (1.0,-1.0,1.0),
    (-1.0,-1.0,1.0),
    (1.0,-1.0,-1.0),
    (1.0,1.0,-1.0),
    (1.0,1.0,1.0),
    (1.0,-1.0,1.0),
    (-1.0,-1.0,-1.0),
    (-1.0,-1.0,1.0),
    (-1.0,1.0,1.0),
    (-1.0,1.0,-1.0),
    )
edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )


colors = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (1,1,1),
    (0,1,1),
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,0,0),
    (1,1,1),
    (0,1,1),
    )


txcolors = (

    (1.0,0.0),
      (0.0,1.0),
    (1.0,1.0),
     (1.0,0.0),
         (0.0,0.0),
    )
ground_surfaces = (0,1,2,3)

ground_vertices = (
    (-10,-1,50),
    (10,-1,50),
    (-10,-1,-300),
    (10,-1,-300),

    )


def set_vertices(max_distance, min_distance = -20):
    
    
    # x_value_change = random.randrange(-10,10)
    # y_value_change = random.randrange(-10,10)
    # z_value_change = random.randrange(-1*max_distance,min_distance)
    
    x_value_change =random.randrange(-10,10)
    y_value_change = 0
    z_value_change =random.randrange(-1*max_distance,min_distance)

    new_vertices = []

    for vert in vertices:
        new_vert = []

        new_x = vert[0] + x_value_change
        new_y = vert[1] + y_value_change
        new_z = vert[2] + z_value_change

        new_vert.append(new_x)
        new_vert.append(new_y)
        new_vert.append(new_z)

        new_vertices.append(new_vert)
    
    return new_vertices
        
def loadTexture():
    textureSurface = pygame.image.load('brick.png')
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()
    glEnable(GL_DEPTH_TEST);
    #glEnable(GL_CULL_FACE);
    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    return texid

def DrawText( string):
        
        # 循环处理字符串
        for c in string:
            # 输出文字
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))
def Ground():
    
    glBegin(GL_QUADS)

    x = 0
    for vertex in ground_vertices:
        x+=1
        glColor3fv((0,1,1))
        glVertex3fv(vertex)
        
    glEnd()
                
def Cube(vertices):
    
    # glBegin(GL_QUADS)

    
    # for surface in surfaces:
    #     x = 0

    #     for vertex in surface:
    #         x+=1
    #         glColor3fv(colors[x])
    #         glVertex3fv(vertices[vertex])
    
        
    # glEnd()

    glBegin(GL_QUADS)
    
    
    for surface in surfaces:
        x = 0

        for vertex in surface:
            x+=1

                # glTexCoord2fv(0.0,0.0)
    # glVertex3fv(-1.0,-1.0,1.0)

            glTexCoord2fv(txcolors[x])
            #glColor3fv(colors[x])
            glVertex3fv(vertices[vertex])
            
    
        
    glEnd()
 

    glBegin(GL_LINES)
    for edge in edges:
        glColor3fv((1, 1, 1))
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


pygame.init()
glutInit(sys.argv)
glutInit(sys.argv)
display = (800, 600)
screen = pygame.display.set_mode(
    display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.OPENGLBLIT)

loadTexture()
max_distance = 100

gluPerspective(45, display[0] / display[1],0.1,max_distance)
#glTranslatef(0.0, 0.0, -20)
#glClearColor(0.0, 0.0, 0.0, 0.0);

horizontalAngle = 3.14
   
verticalAngle = 0.0

initialFoV = 45.0

speed = 3.0
mouseSpeed = 0.000001
clock = pygame.time.Clock()
myposition=(0,0,0)
cube_dict = {}
#幾個方塊
for x in range(20):
    cube_dict[x] =set_vertices(max_distance)
test=0
mypos=np.zeros((3,), dtype=float)
mypos_buff=np.zeros((3,), dtype=float)
up=(0,0,0)
right=(0,0,0)
direction=(0,0,0)
    #glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB);
    #glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
buff=False
pygame.mouse.set_visible(False)
x_move = 0
y_move = 0
z_move = 0
glScalef(1.0,1.0,1.0)
while True:
    dt = clock.tick(60) 
    x = glGetDoublev(GL_MODELVIEW_MATRIX)
    #glMatrixMode(GL_MODELVIEW);
    camera_x = x[3][0]
    camera_y = x[3][1]
    camera_z = x[3][2]
    
    mypos_ex=(x[2])
    
    #print (    camera_x)  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
               # glTranslatef(-0.5,0,0)

                #gluPerspective(0, display[0] / display[1],view,0)
                # for x in range (1,500,1):
                   
                #     print (x)
                #     pygame.time.wait(10)
                # gluLoo
                # kAt (0,1,0,0,0,-20, 0, 1.0,0);
                x_move =0.5
                
                #glTranslatef(-0.5, 0,0)
                glTranslatef(x_move,0,z_move)
            if event.key == pygame.K_RIGHT:
                #glTranslatef(0.5,0,0)
                x_move =-0.5
               
                glTranslatef(x_move,0,z_move)
                #gluPerspective(0, display[0] / display[1], view, 0)
            if event.key == pygame.K_UP:
                #glTranslatef(0,0.5,0)
                #glTranslatef(0,0,0.5)
                
                z_move=0.5
                glTranslatef(x_move,0,z_move)
            if event.key == pygame.K_DOWN:
                #glTranslatef(0,0,0)
                z_move=-0.5
               
                #glTranslatef(0,-0.5,0)
                #glTranslatef(0,0,-0.5)
                glTranslatef(x_move,0,z_move)

                
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                tmp=tmp+0.5
                glTranslatef(0,0,0.5)

            if event.button == 5:
                tmp=tmp-0.5
                glTranslatef(0,0,-0.5)
        if event.type == pygame.MOUSEMOTION:
               
            # glfwSetMousePos(1024/2, 768/2);
                mouse_position = pygame.mouse.get_pos()
                
                pygame.mouse.set_pos(800/2,600/2)
                
                 
                
                horizontalAngle += mouseSpeed * dt * float((800/2) -mouse_position[0])
                verticalAngle   += mouseSpeed * dt * float( (600/2) -mouse_position[1] )

                
               # print (math.sin(horizontalAngle - 3.14/2.0))
                direction=(math.cos(verticalAngle) * math.sin(horizontalAngle),math.sin(verticalAngle),math.cos(verticalAngle) * math.cos(horizontalAngle))
                
                right=( math.sin(horizontalAngle - 3.14/4.0),0, math.cos(horizontalAngle - 3.14/4.0))
                #print (math.sin(horizontalAngle - 3.14/4.0))
            
                up=np.cross(right, direction)
                
                #tmp=np.matrix(mypos,direction)
                
                pd= np.array(mypos)+np.array(direction)
                
                #print (tmp)
                #print (mypos*direction*dt*0.5   )
                # glRotate(0,1,0,0)
                # glRotate(pd[0] * dt*10,0,1,0)
                # glRotate(0,0,0,1)
                # print (pd[0])
                print (mypos)
                gluLookAt (mypos[0],mypos[1],mypos[2], pd[0],pd[1],pd[2],up[0]  , up[1],up[2]);
                #glTranslatef(mypos[0],mypos[1],mypos[2])

                glClear(GL_COLOR_BUFFER_BIT|GL_COLOR_BUFFER_BIT)
                   
            
                #horizontalAngle=0
                #verticalAngle =0
        if event.type == pygame.KEYUP:
                
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    mypos[0]+=x_move*-1
                    x_move = 0


                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    mypos[2]+=  z_move*-1
                    z_move = 0
    
    print (mypos)
    print (z_move)
    print (x_move)
    # print ( mypos)
    # print (mypos_ex)
    # print (direction)
    # print (direction[0]*dt*x_move)
    # print (x[2])
    # print ('sssssssssssssssssssssssss')
    # x=np.array(mypos_ex)
    # y=np.array(direction)
    # print (x+y)
    
    #pygame.time.wait(60)
    # glRotate(0,1,0,0)
    # glRotate(1,0,1,0)
    # glRotate(0,0,0,1)

    
    # glTranslatef(x_move,0,z_move)
    #print (camera_x)
    #mypos[0]+=x_move*dt* 0.000001
    #print (x_move*dt)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    for each_cube in cube_dict:
        Cube(cube_dict[each_cube])
    Ground()

    pygame.display.flip()
```

  

  

  
## 緩衝區問題?

## ---

glutSwapBuffers()
其實這一行就可以解決了，我比較衰挑到3.6版，none沒有這個函數?
  

移動問題
