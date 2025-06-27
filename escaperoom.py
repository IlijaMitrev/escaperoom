import pygame,sys,random,math

pygame.init()
info=pygame.display.Info()
WIDTH,HEIGHT=info.current_w*9//10,info.current_h*9//10
FPS=60
WHITE=(255,255,255)
BLACK=(0,0,0)
BLUE=(0,120,255)
GOLD=(255,215,0)
RED=(200,50,50)
GREEN=(50,200,50)
PINK=(255,105,180)
ORANGE=(255,165,0)
GRAY=(30,30,30)

screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Escape Room Pro")
clock=pygame.time.Clock()
font=pygame.font.SysFont("Calibri",48)
big_font=pygame.font.SysFont("Calibri",100)

figur_img=pygame.image.load("figur.png").convert_alpha()
figur_img=pygame.transform.scale(figur_img,(180,360))
door_img=pygame.image.load("tuer.png").convert_alpha()
door_img=pygame.transform.scale(door_img,(260,520))


def draw_text(text,x,y,color=WHITE,center=False,big=False):
    f=big_font if big else font
    img=f.render(text,True,color)
    rect=img.get_rect(center=(x,y)) if center else (x,y)
    screen.blit(img,rect)


class Player:
    def __init__(self):
        self.pos=[100,HEIGHT//2]
        self.speed=7
    def move(self,keys):
        if keys[pygame.K_w]:self.pos[1]-=self.speed
        if keys[pygame.K_s]:self.pos[1]+=self.speed
        if keys[pygame.K_a]:self.pos[0]-=self.speed
        if keys[pygame.K_d]:self.pos[0]+=self.speed
        self.pos[0]=max(0,min(WIDTH-90,self.pos[0]))
        self.pos[1]=max(0,min(HEIGHT-360,self.pos[1]))
    def draw(self):
        screen.blit(figur_img,(self.pos[0],self.pos[1]))


class Item:
    def __init__(self,x,y,kind,hidden=False):
        self.rect=pygame.Rect(x,y,40,40)
        self.kind=kind
        self.hidden=hidden
        self.collected=False
    def draw(self):
        if self.collected:return
        if self.hidden:
            px,py=player_global.pos
            if math.hypot(self.rect.centerx-px,self.rect.centery-py)>150:return
        if self.kind=="key":
            pygame.draw.rect(screen,GOLD,self.rect,border_radius=5)
            pygame.draw.circle(screen,GOLD,(self.rect.x+40,self.rect.y+10),10)
        else:
            pts=[(self.rect.x,self.rect.y+20),(self.rect.x+20,self.rect.y),
                 (self.rect.x+40,self.rect.y+20),(self.rect.x+20,self.rect.y+40)]
            pygame.draw.polygon(screen,PINK,pts)
    def check_collect(self,pr):
        if not self.collected and self.rect.colliderect(pr):
            self.collected=True
            return self.kind
        return None


class PressurePlate:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,60,60)
        self.active=False
    def draw(self):
        col=ORANGE if self.active else GRAY
        pygame.draw.rect(screen,col,self.rect,border_radius=8)
    def update(self,pr):
        if pr.colliderect(self.rect):self.active=True


class Door:
    def __init__(self,x,y,locked=True):
        self.rect=pygame.Rect(x,y,130,260)
        self.locked=locked
    def draw(self):
        screen.blit(door_img,(self.rect.x-65,self.rect.y-130))


class CodePanel:
    def __init__(self,x,y,code="1234"):
        self.rect=pygame.Rect(x,y,60,60)
        self.code=code
        self.unlocked=False
    def draw(self):
        col=GREEN if self.unlocked else BLUE
        pygame.draw.rect(screen,col,self.rect,border_radius=10)
    def interact(self,pr):
        if self.rect.colliderect(pr) and not self.unlocked:
            return self.enter_code()
        return None
    def enter_code(self):
        code_in=""
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:pygame.quit();sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_RETURN:
                        if code_in==self.code:
                            self.unlocked=True
                            return True
                        return False
                    if e.key==pygame.K_ESCAPE:
                        return None
                    if e.key==pygame.K_BACKSPACE:
                        code_in=code_in[:-1]
                    else:code_in+=e.unicode
            screen.fill(BLACK)
            pygame.draw.rect(screen,ORANGE,pygame.Rect(WIDTH//2-200,HEIGHT//2-100,400,160),border_radius=20)
            draw_text("CODE EINGEBEN",WIDTH//2,HEIGHT//2-30,WHITE,center=True)
            draw_text(code_in,WIDTH//2,HEIGHT//2+30,GOLD,center=True)
            pygame.display.flip()


class Level:
    def __init__(self,n):
        self.n=n
        self.items=[]
        self.plates=[]
        self.code_panel=None
        self.hint=""
        bg=pygame.image.load("geheim.png").convert()
        self.bg=pygame.transform.scale(bg,(WIDTH,HEIGHT))
        self.init_level()
        self.door=Door(WIDTH-200,HEIGHT//2-100)
    def init_level(self):
        p=(self.n-1)%10
        if p in [0,5]:
            self.items=[Item(random.randint(200,WIDTH-300),random.randint(200,HEIGHT-300),"key",True)]
            self.hint="Finde den versteckten Schlüssel"
        elif p in [1,6]:
            code="".join(random.choice("0123456789") for _ in range(4))
            x,y=random.randint(300,WIDTH-300),random.randint(200,HEIGHT-300)
            self.code_panel=CodePanel(x,y,code)
            self.hint="Löse das Panel, um weiterzukommen"
        elif p in [2,7]:
            cnt=3+self.n//2
            self.items=[Item(random.randint(200,WIDTH-200),random.randint(200,HEIGHT-200),"gem") for _ in range(cnt)]
            self.hint="Sammle alle Edelsteine"
        elif p in [3,8]:
            x1,y1=random.randint(200,WIDTH-300),random.randint(200,HEIGHT-300)
            x2,y2=random.randint(200,WIDTH-300),random.randint(200,HEIGHT-300)
            self.plates=[PressurePlate(x1,y1),PressurePlate(x2,y2)]
            self.hint="Stelle dich auf beide Platten"
        else:
            self.items=[Item(random.randint(100,WIDTH-100),random.randint(100,HEIGHT-100),"gem") for _ in range(5)]
            self.code_panel=CodePanel(random.randint(300,WIDTH-300),random.randint(200,HEIGHT-300),"4321")
            self.hint="Sammle Edelsteine und löse Code"
    def draw(self):
        screen.blit(self.bg,(0,0))
        for itm in self.items:itm.draw()
        for pl in self.plates:pl.draw()
        if self.code_panel:self.code_panel.draw()
        self.door.draw()
        draw_text(self.hint,50,50)
    def update(self,pr):
        for itm in self.items:itm.check_collect(pr)
        for pl in self.plates:pl.update(pr)
        if self.code_panel:
            result=self.code_panel.interact(pr)
            if result==True:self.door.locked=False
        elif self.plates:
            if all(pl.active for pl in self.plates):self.door.locked=False
        else:
            if all(itm.collected for itm in self.items):self.door.locked=False
    def complete(self,pr):
        return pr.colliderect(self.door.rect) and not self.door.locked


class Timer:
    def __init__(self,limit):
        self.limit=limit
        self.start=pygame.time.get_ticks()
    def update(self):
        rem=max(0,self.limit-((pygame.time.get_ticks()-self.start)//1000))
        draw_text(f"ZEIT {rem}s",WIDTH//2+300,50)
        if rem<=0:
            draw_text("ZEIT ABGELAUFEN",WIDTH//2,HEIGHT//2,RED,center=True,big=True)
            pygame.display.flip();pygame.time.wait(2000);pygame.quit();sys.exit()


class Score:
    def __init__(self):self.points=0
    def add(self,v):self.points+=v
    def draw(self):draw_text(f"PUNKTE {self.points}",WIDTH-300,50)


def main():
    global player_global
    player=Player();player_global=player
    level_num=1;level=Level(level_num)
    frame=0;score=Score();timer=Timer(450)
    code_timer=0;code_val="";collected=set()
    while True:
        clock.tick(FPS);frame+=1
        for e in pygame.event.get():
            if e.type==pygame.QUIT:pygame.quit();sys.exit()
        keys=pygame.key.get_pressed();player.move(keys)
        level.draw();player.draw()
        pr=pygame.Rect(player.pos[0],player.pos[1],90,180)
        for itm in level.items:
            if itm.kind=="key" and itm.collected and itm not in collected:
                collected.add(itm)
                if level.code_panel:
                    code_val=level.code_panel.code;code_timer=pygame.time.get_ticks()
        level.update(pr)
        if level.complete(pr):
            level_num+=1;level=Level(level_num)
            player.pos=[100,HEIGHT//2];score.add(100)
            collected.clear();code_timer=0;code_val=""
        if code_timer and pygame.time.get_ticks()-code_timer<5000:
            bx,by,bw,bh=50,HEIGHT-100,250,80
            pygame.draw.rect(screen,ORANGE,pygame.Rect(bx,by,bw,bh),border_radius=10)
            draw_text(f"CODE {code_val}",bx+bw//2,by+bh//2,GOLD,center=True)
        timer.update();score.draw();pygame.display.flip()


if __name__=="__main__":
    main()
