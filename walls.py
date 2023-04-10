import pygame
import sys
import math

img_enemy = pygame.image.load('img\enemy.png')
img_bg = pygame.image.load('img\Background.png')
img_title = pygame.image.load('img\Title.png')


L = 960
H = 540

idx = 0
info = 0
time = 0

class Character:#建立角色物件
    xpos, ypos = (1,1)
    rot_p = math.radians(45)#視線朝向
    precision = 0.02#光線投射時每次累加的距離
    speed = 0.05

    def move(self,direct):
        self.xpos, self.ypos = (self.xpos + direct*self.speed*math.cos(self.rot_p), 
                                self.ypos + direct*self.speed*math.sin(self.rot_p))
    def move_but_touch(self,direct):
        self.xpos, self.ypos = (self.xpos + -0.06*math.cos(direct), 
                                self.ypos + -0.06*math.sin(direct))
    def move_but_LR(self,direct):
        self.xpos, self.ypos = (self.xpos + direct*self.speed*math.cos(self.rot_p + 90), 
                                self.ypos + direct*self.speed*math.sin(self.rot_p + 90))

    def rotate(self,direct):
        self.rot_p += direct*math.pi/96
        self.rot_p = self.rot_p % (2*math.pi)
        
class Enemy:
    global idx,time
    rot_p = 0
    speed = 0.02
    
    def __init__(self,xpos,ypos):
        self.xpos, self.ypos = xpos, ypos
    def find_c(self,c_xpos,c_ypos,c_rot):
        deltaX = c_xpos - self.xpos
        deltaY = c_ypos - self.ypos
        d = math.sqrt((deltaX)**2 + (deltaY)**2)
        theta = math.atan2(deltaY,deltaX)
        deltaRot = theta - c_rot + math.radians(180)
        if idx == 1 and d > 0.2:
            self.xpos += self.speed*deltaX
            self.ypos += self.speed*deltaY
        if -30 <= math.degrees(deltaRot) <= 30:
            pack = [abs(d*math.cos(deltaRot)),d*math.sin(theta - c_rot)/d*math.cos(deltaRot)*math.tan(math.radians(45)),d]
            return(pack)
        else:
            return [0,0,d]         
   
map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,2,0,0,0,0,0,0,0,0,1],
    [1,2,2,1,1,0,0,0,0,0,0,0,1,1],
    [1,0,0,1,1,0,0,0,1,1,0,0,1,1],
    [1,1,0,1,1,1,1,0,1,1,0,0,0,1],
    [1,0,0,1,1,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,2,0,0,1,0,0,1],
    [1,0,2,0,0,1,0,0,0,0,1,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]#1代表牆壁

casting_line = int(L/18)#投射線數aka在畫面繪製的長方形數

def main():
    pygame.init()
    pygame.mixer.init()
    global idx,info,time
    screen = pygame.display.set_mode((L,H))#視窗大小是960*540
    clock = pygame.time.Clock()
    character = Character()
    tex_scale = 20
    font = pygame.font.Font(None,tex_scale)
    chinese_font = pygame.font.Font('Font\GENYOMIN-B.TTC',tex_scale)
    enemy_run = pygame.mixer.Sound('sound\Sneaker Stairs Run Concrete.mp3')
    
    enemy = Enemy(3,2)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        key = pygame.key.get_pressed()#依WASD鍵位移動
        [mouse_x, mouse_y] = pygame.mouse.get_rel()
        [mouse_x_p, mouse_y_p] = pygame.mouse.get_pos()
        if idx == 1:
            
            time += 1/60
            
            if key[pygame.K_w]:
                character.move(1)
            if key[pygame.K_s]:
                character.move(-1)
            if key[pygame.K_d]:
                character.move_but_LR(-0.5)
            if key[pygame.K_a]:
                character.move_but_LR(0.5)
            if H/5 < mouse_y_p < 4*H/5:
                character.rotate(-1*(mouse_x/4))
            if key[pygame.K_f]:
                info = 1
            if enemy.speed <= 0.05:
                enemy.speed += time/2000000
        img_bg_tr = pygame.transform.scale(img_bg,(L,H))
        screen.blit(img_bg_tr,(0,0))#背景      

        for i in range(0,casting_line +1):
            rot_r = character.rot_p + math.radians(30) - math.radians(i*60/casting_line)#從視線逆時針30度的位置開始由左至右測量與物體的距離
            x, y = (character.xpos, character.ypos)
            sin, cos = (character.precision*math.sin(rot_r), character.precision*math.cos(rot_r))#設定X、Y座標累加的值
            d = 0
            while True:
                x, y = (x + cos,y + sin)
                d += 1
                if map[int(x)][int(y)] == 1:#累加直至碰到牆壁
                    rot_d = character.rot_p - rot_r
                    height = 540*3*H/(d*math.cos(rot_d))/100#修正魚眼現象
                    break

            if d/2 >128:
                d = 256
            
            pygame.draw.line(screen,
                            (255-d/1.5,240-d/1.5,128-d/2),#離得越遠則越暗
                            (i*(L/casting_line),(H/2)+height),
                            (i*(L/casting_line),(H/2)-height),
                            width=int((L/casting_line)+1)
            )
        x, y = (character.xpos, character.ypos)
        sin, cos = (character.precision*math.sin(character.rot_p), character.precision*math.cos(character.rot_p))#設定X、Y座標累加的值
        d = 0
        d_pack = enemy.find_c(character.xpos,character.ypos,character.rot_p)
        d_e, d_side, d_e_for_game_status = d_pack
        if d_e_for_game_status*3 > 1:
            enemy_run.set_volume(1/(d_e_for_game_status*3))
        else:
            enemy_run.set_volume(1)
        enemy_is_behind_the_wall = False
        if d_e != 0:
            while d < d_e:
                x, y = (x + cos,y + sin)
                d += character.precision
                if map[int(x)][int(y)] == 1:#累加直至碰到牆壁
                    enemy_is_behind_the_wall = True
                    break
            if enemy_is_behind_the_wall == False:
                img_enemy_tr = pygame.transform.scale(img_enemy,(18*30/d_e,16*30/d_e))
                screen.blit(img_enemy_tr,(L/2-18*15/d_e + L*d_side,H/2 - 16*15/d_e))
        if d_e_for_game_status <= 0.25:
            idx = 3                 
        
        for i in range(0,360):
            rot_r = character.rot_p + math.radians(180) - math.radians(i)#從視線逆時針30度的位置開始由左至右測量與物體的距離
            x, y = (character.xpos, character.ypos)
            sin, cos = (character.precision*math.sin(rot_r), character.precision*math.cos(rot_r))#設定X、Y座標累加的值
            d = 0
            while True:
                x, y = (x + cos,y + sin)
                d += 1
                if map[int(x)][int(y)] == 1:#累加直至碰到牆壁
                    break
            if d < 6:
                character.move_but_touch(rot_r)    
        tex_scale = 20
        time_tex = 'TIME:{0}'.format(round(time))
        time_shown = chinese_font.render(time_tex,True,(0,0,0))
        screen.blit(time_shown,(50,25))
        
        if idx == 0:#主畫面
            tex_scale = 20
            start_tex = 'move the cursor to the center to start'
            start_shown = chinese_font.render(start_tex,True,(0,0,0),(255,255,255))
            screen.blit(start_shown,(L/2-200,H/2 + 50))
            screen.blit(img_title,((L/2)-200,(H/2)-45))
            if mouse_x_p <= L/2 + 50 and mouse_x_p >= L/2 -50 and mouse_y_p <= H/2 + 45 and mouse_y_p >= H/2 -45 and event.type == pygame.MOUSEBUTTONDOWN:
                idx = 1
                enemy_run.play(-1)
        if idx == 3:
            enemy_run.stop()
            tex_scale = 50
            setting_tex = 'game over'
            setting_shown = chinese_font.render(setting_tex,True,(0,0,0),(255,255,255))
            screen.blit(setting_shown,(L/2-200,H/2))

            back_to_0 = 'back to main screen'
            back_shown = chinese_font.render(back_to_0,True,(0,0,0),(255,255,255))
            screen.blit(back_shown,(L/2 + 200,H/2))

            if L/2 + 150 <= mouse_x_p <= L/2 +450 and H/2 -50 <= mouse_y_p <= H/2 +50 and event.type == pygame.MOUSEBUTTONDOWN:
                enemy.xpos, enemy.ypos = (3,2)
                character.xpos, character.ypos = (1,1)
                character.rot_p = math.radians(45)
                enemy.speed = 0.02
                time = 0
                idx = 0
            
            if key[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        if info == 1:
            pos_tex = 'x:{0:.2f},y:{1:.2f},mouseX:{2:.2f},mouseY:{3:.2f}'.format(character.xpos,character.ypos,mouse_x_p,mouse_y_p)
            pos_info = font.render(pos_tex,True,(0,0,0))
            screen.blit(pos_info,(int(L/100),int(L/100)))
        
        pygame.display.update()
        pygame.display.set_caption("Raycasting - FPS: " + str(round(clock.get_fps())))
        clock.tick(60)

if __name__ == '__main__':
    main() 