import pygame
from math import *
from random import *
from constants import *

pygame.init()

class BodyPart:
    def __init__(self,parent,length,rotation,color):
        self.parent = parent
        self.length = length
        self.rotation = rotation
        self.color=color
    def get_rot(self):
        return self.rotation + self.parent.get_rot()

    def get_pos(self):
        px,py = self.parent.get_pos()
        x = px + cos(radians(self.get_rot()))*self.length
        y = py + sin(radians(self.get_rot()))*self.length
        return x,y
        
    def draw(self,surface):
        pygame.draw.line(surface,self.color,self.parent.get_pos(),self.get_pos(),1)

    def as_shrapnel(self):
        return BodyPartShrapnel(list(self.parent.get_pos()),self.length,self.rotation,self.color)

class BodyPartShrapnel:
    def __init__(self,pos,length,rotation,color):
        self.pos = pos
        self.length = length
        self.rotation = rotation
        self.vx = (random()-0.5)*2*MAX_SHRAPNEL_VX
        self.vy = random()*MAX_SHRAPNEL_VY
        self.color = color
        self.speed = (random()-0.5)*2*MAX_SHRAPNEL_SPEED
        
    def draw(self,surface):
        nx = self.pos[0] + cos(radians(self.rotation))*self.length
        ny = self.pos[1] + sin(radians(self.rotation))*self.length
        pygame.draw.line(surface,self.color,self.pos,(nx,ny),1)
    
    def update_shrapnel(self):
        self.pos[1] += self.vy
        self.pos[0] += self.vx
        self.vy += GRAVITY
        self.rotation += self.speed
        return self.pos[1]>ground
        
class Circle(BodyPart):
    def get_pos(self):
        px,py = self.parent.get_pos()
        return px,py+self.length
        
    def draw(self,surface):
        pygame.draw.circle(surface,self.color,map(int,self.parent.get_pos()),
        self.length)

    def as_shrapnel(self):
        return CircleShrapnel(list(self.parent.get_pos()),self.length,self.rotation,self.color)
        
class CircleShrapnel(BodyPartShrapnel):
    def draw(self,surface):
        pygame.draw.circle(surface,self.color,map(int,self.pos),
        self.length)
    
        
class Figure(BodyPart):
    def __init__(self,x,y,speed,color=(0,0,0)):
        self.pos = [x,y]
        self.rotation = 0
        self.vy = 0
        self.vx = speed
        self.torso = BodyPart(self,20,90,color)
        self.left_leg = BodyPart(self.torso,10,-45,color)
        self.right_leg = BodyPart(self.torso,10,45,color)
        self.left_arm = BodyPart(self,10,45,color)
        self.right_arm = BodyPart(self,10,135,color)
        self.neck = BodyPart(self,5,-90,color)
        self.head = Circle(self.neck,4,0,color)
        self.body_parts = [self.torso,self.left_leg,self.right_leg,
                           self.left_arm,self.right_arm,self.neck,self.head]

        self.walk = 0
        self.dead = False
        
    def update_gravity(self):
        self.pos[1] += self.vy
        self.vy += GRAVITY

        lowest = self.ground_y()
        if lowest >= ground:
            delta = lowest - ground
            self.pos[1] -= delta
            if self.vy > 0: self.vy = 0

    def do_walk(self,direction):
        self.pos[0] += direction*self.vx
        self.walk += direction*self.vx

    def update_legs(self):
        self.left_leg.rotation = sin(self.walk)*45
        self.right_leg.rotation = -sin(self.walk)*45

    def ground_y(self):
        return max([part.get_pos()[1] for part in self.body_parts]+[self.pos[1]])
       
    def get_pos(self):
        return self.pos

    def get_rot(self):
        return self.rotation

    def draw(self,surface):
        for part in self.body_parts:
            part.draw(surface)
            
    def update(self):
        self.vy += GRAVITY
        self.pos[1] += self.vy


    def update_shrapnel(self):
        self.update()
        self.pos[0] += self.vx
        for body_part in self.body_parts:
            body_part.rotation += body_part.speed
        return self.pos[1] > ground

class Bang:
    def __init__(self,x,y,color,max_size,expansion_speed=2):
        self.max_size = max_size
        self.x = int(x)
        self.y = int(y)
        self.color = color
        self.width = expansion_speed
        self.expansion_speed = expansion_speed
        
    def update_shrapnel(self):
        self.width += self.expansion_speed
        if self.width > self.max_size:
            return True
        else: return False
    
    def draw(self,surface):
        pygame.draw.circle(surface,self.color,(self.x,self.y),self.width,self.expansion_speed)

        
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Psychokinetic Ninja!')

power = 1
new_enemy_countdown = enemy_timer
health = 1

player = Figure(320,240,PLAYER_VX,(0,0,192))
enemies = [Figure(randint(0,640),randint(-100,60),random()*MAX_ENEMY_VX) for _ in xrange(1)]
clock = pygame.time.Clock()

shrapnel = []

fireballs = []
meta_timer = META_TIMER

survival_timer = 1

class Fireball:
    def __init__(self,x,y,v):
        self.x = int(x)
        self.y = int(y)
        self.v = v
    
    def update(self):
        self.x += self.v*FIREBALL_SPEED
        return (self.x<-10) or (self.x>650)

    def draw(self,surface):
        pygame.draw.circle(surface,(255,0,0),(self.x,self.y),5)

while True:
    clock.tick(60)
    #player.update()

    health += HEAL_RATE
    health = min(health,1)
    power += POWERUP_RATE
    power = min(power,1)

    survival_timer -= 0.0001
    
    attack_count = 0
    for enemy in enemies:
        if (abs(enemy.pos[0]-player.pos[0]) < ENEMY_X_EFFECT) and (abs(enemy.pos[1]-player.pos[1]) < ENEMY_Y_EFFECT):
            health -= DAMAGE_RATE
            health = max(health,0)
            attack_count += 1
            if attack_count == MAX_ATTACKS_PER_TURN:
                break
    #recharge_power_strike -= 1
    new_enemy_countdown -= 1
    
    if new_enemy_countdown <= 0:
        new_enemy_countdown = enemy_timer
        enemies.append(Figure(randint(0,640),randint(-200,0),random()*MAX_ENEMY_VX))
    
    meta_timer -= 1
    if not meta_timer:
        meta_timer = META_TIMER
        if enemy_timer: enemy_timer -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.vy = JUMP_VELOCITY
            if event.key == pygame.K_BACKQUOTE:
                paused=True
                while paused:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_BACKQUOTE:
                                paused=False
            if event.key == pygame.K_j:
                if power >= POWER_FIREBALL:
                    power -= POWER_FIREBALL
                    fireballs.append(Fireball(player.pos[0],player.pos[1],-1))
                    fireballs.append(Fireball(player.pos[0],player.pos[1],1))
            if event.key == pygame.K_k:
                if power >= POWER_SHOCKWAVE:
                    power -= POWER_SHOCKWAVE
                    for enemy in enemies[:]:
                        if sqrt(abs(enemy.pos[0]-player.pos[0])**2+abs(enemy.pos[1]-player.pos[1])**2) < SHOCKWAVE_EFFECT:
                            enemies.remove(enemy)
                            shrapnel.append(enemy)
                            enemy.dead=True
                            for part in enemy.body_parts:
                                part.speed = (random()-0.5)*MAX_HURTLE_FLAIL_SPEED*2
                            enemy.vy = random()*MAX_HURTLE_VY
                            enemy.vx = (random())*MAX_HURTLE_VX*(-1 if enemy.pos[0]<player.pos[0] else 1)
                    shrapnel.append(Bang(player.pos[0],player.pos[1],(255,255,0),100,10))
    p = pygame.key.get_pressed()
    if p[pygame.K_a]:
        player.do_walk(-1)
    elif p[pygame.K_d]:
        player.do_walk(1)
        
    for enemy in enemies:
        enemy.update_gravity()

        if not enemy.dead:
            if player.pos[0] > enemy.pos[0]:
                enemy.do_walk(1)
            else:
                enemy.do_walk(-1)
            if (enemy.ground_y() >= ground) and not randint(0,256):
                enemy.vy = JUMP_VELOCITY
            enemy.update_legs()
            enemy.left_arm.rotation -= FLAIL_SPEED
            enemy.right_arm.rotation += FLAIL_SPEED
        else:
            pass
    player.update_gravity()    
    player.update_legs()         

    screen.fill((0,255,255))
    pygame.draw.rect(screen,(0,128,0),(0,ground,640,480-ground))
    for enemy in enemies: enemy.draw(screen)
    player.draw(screen)
    for item in shrapnel[:]:
        if item.update_shrapnel():
            shrapnel.remove(item)
            if isinstance(item,Figure):
                for part in item.body_parts:
                    shrapnel.append(part.as_shrapnel())
        item.draw(screen)
    #print fireballs
    for item2 in fireballs[:]:
        if item2.update(): fireballs.remove(item2)
        item2.draw(screen)
        for enemy in enemies[:]:
            #print fireballs,item2
            if (abs(enemy.pos[0]-item2.x)<FIREBALL_X_EFFECT) and (abs(enemy.pos[1]-item2.y)<FIREBALL_Y_EFFECT):
                enemies.remove(enemy)
                for item3 in enemy.body_parts:
                    shrapnel.append(item3.as_shrapnel())
    pygame.draw.rect(screen,(0,255,0),(0,450,survival_timer*640,10))
    pygame.draw.rect(screen,(192,0,0),(0,470,health*640,10))
    pygame.draw.rect(screen,(0,0,255),(0,460,power*640,10))
    pygame.display.update()
        
