import pygame,random,math
from pygame.locals import *
from pygame.math import Vector2
pygame.init()
pygame.mixer.init()
font = pygame.font.SysFont(None, 40)

SKYBLUE = (75,191,255)
BLUE = (0,0,225)
DARKBLUE = (0,71,171)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
PEACH = (255,176,156)

gameLoop = True
playerSpeed = 5
grounded = False
fallSpeed = 9

momentumX = 0
momentumY = 0

grass = pygame.image.load("grass.png")
dirt = pygame.image.load("dirt.png")
brimstone = pygame.image.load("brimstone.png")
lavarock = pygame.image.load("lavarock.png")
##laceration = pygame.image.load("laceration.png")
##weakness= pygame.image.load("weakness.png")

boost = 10
boostVector = (0,0)
acceptingNewVector = True
inRange=False

reticle = pygame.Rect(0,0,0,0)

FPS = 100
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 1000),pygame.RESIZABLE)
w, h = pygame.display.get_surface().get_size()
mousePos = pygame.mouse.get_pos()
offset = pygame.math.Vector2(0,0)
world = pygame.math.Vector2(w/2,h/2)
playerRect = pygame.Rect(w/2,h/2,100,100)
playerFeet = playerRect
ground = pygame.Rect(world.x,world.y+100,1000,100)

class Block:
    def __init__(self, position, size, color):
        self.position = Vector2(position)
        self.size = size
        self.rect = pygame.Rect(position, size)
        self.color = color
    def draw(self, surface):
        surface = pygame.transform.scale(surface,self.size)
        screen.blit(surface,block)
        #pygame.draw.rect(screen, (BLUE), self.rect, 0, 0)
        
    def collide(self,player):
        global offset,grounded,mousePos,fallSpeed,momentumY,boost,reticle
            
        if self.rect.colliderect(player):
            leftOverlap = player.right - self.rect.left
            rightOverlap = self.rect.right - player.left
            topOverlap = player.bottom - self.rect.top
            bottomOverlap = self.rect.bottom - player.top
            min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)#Which of these overlaps is smallest?
            
            if min_overlap == topOverlap:
                momentumY=0
                offset.y += topOverlap
                
            elif min_overlap == bottomOverlap:
                momentumY=0
                offset.y -= bottomOverlap
                boost=0
                
            elif min_overlap == leftOverlap:
                offset.x += leftOverlap
            elif min_overlap == rightOverlap:
                offset.x -= rightOverlap
def handleInputs():
    global gameLoop,boost,world,acceptingNewVector,inRange
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        #offset.y += playerSpeed
        pass
    if keys[pygame.K_s]:
        #offset.y -= playerSpeed
        pass
    if keys[pygame.K_a]:
        offset.x += playerSpeed
    if keys[pygame.K_d]:
        offset.x -= playerSpeed
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            #print(f"Mouse button {event.button} clicked at {event.pos}")
            if inRange==True:
                inRange = False
                boost = 40
                acceptingNewVector = True
                
        if event.type == pygame.QUIT:
            gameLoop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gameLoop = False

def drawPlayer():
    
    #screen.blit(soulImage,(playerRect.centerx-soulImageSize/2,playerRect.centery-soulImageSize/2),(soulImageX,0,soulImageStep,soulImageH))
    
    
    
    
    pygame.draw.rect(screen, ('orange'), (playerRect),0,5)
    


def angleCalc():
    global playerRect,boost,offset,acceptingNewVector,boostVector,mousePos,reticle
    direction_vector = Vector2(mousePos) - playerRect.center
    if direction_vector.length() > 0:
        direction_vector = direction_vector.normalize()
    target_offset = direction_vector * 100
    square_pos = playerRect.center + target_offset
    reticle = pygame.Rect(square_pos.x-25,square_pos.y-25,50,50)
    pygame.draw.rect(screen, ('yellow'), reticle,0,5)
    
    if (acceptingNewVector):
        boostVector = direction_vector
        acceptingNewVector = False
        
    velocity = boostVector * boost
    offset += velocity
    if boost > 0:
        boost -= 1
def gravity():
    global offset,grounded,fallSpeed,momentumY
    
    if grounded == False:
        if momentumY<fallSpeed:
            momentumY += 1
        offset.y-=momentumY

def endLevel(end):
    here = font.render("Hit here!", True, RED)
    screen.blit(here,(end,end))
    if playerRect.collidepoint(endPoint):
        message = font.render("You have completed the level!", True, RED)
        screen.blit(message, (100,100))
        level += 1
        
tilemapLevel1 = [
    'B_______B______________________________BBB______________',
    'B__________________________________BBB_______________________BBBBBBBBB',
    'B_______B______________________BBB______________________',
    'B___________BB______________BBB_____________________________BBBBBBBBBBBB_____________________________________________B_____B______B______B',
    'B______B____BBBB_________BB_______________________________BBBBBBBBBBBB_______________________________________________B_____B______B______B________E',
    'BBBBBBBBB__BBBBBBB__BBBB_____________________BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB_BBBBBBBBBBBBBB__BB__BB__BB__BB__BB__BB__BB_____B______B______B____BBBBB',
    '___________________________________________________________________________________________________________BBBBBBBBBBBBBBBBBBBBBBBB______BBBBBBBB'
    ]

endPoint = 500,500

tileMapLevel2 = [
    '--------------',
    '---------------',
    '-----------------',
    'BBBBBBBBBBBBBBBBBB'
    ]
    
   
    
level = 1
blocks = []
tileSize = 100
def buildWorld(tilemap):
    global level
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == 'B':
                blocks.append(Block((offset.x + (x*tileSize), offset.y+(y*tileSize)), (tileSize, tileSize), BLUE))
##            if tile == 'E':
##                endLevel(endPoint)
                
if level == 1:
    buildWorld(tilemapLevel1)
    
if level == 2:
    buildWorld(tileMapLevel2)
world = pygame.Vector2(playerRect.x+offset.x,playerRect.y+offset.y)
while gameLoop:
    #perform all physics calculations first
    screen.fill(SKYBLUE)
    clock.tick(FPS)
    mousePos = pygame.mouse.get_pos()
    #grounded = False
    
    handleInputs()

    w, h = pygame.display.get_surface().get_size()
    playerRect = pygame.Rect(w/2-playerRect.w/2,h/2-playerRect.h/2,100,100)
    world = pygame.Vector2(playerRect.x+offset.x,playerRect.y+offset.y)
    gravity()
    inRange=False
    for block in blocks:
        block.rect.topleft = (block.position.x + world.x,block.position.y + world.y)
        block.collide(playerRect)
        if block.rect.colliderect(reticle):
            inRange = True
    grounded = False
    #ground = pygame.Rect(world.x-100,world.y+150,800,200)
    #block1 = Block((world.x-100,world.y+150),(200,200),BLUE)
    
    #collidePlayer(ground,playerRect)

    #offset.y+=momentumV
    #then do all your drawing
    for block in blocks:
        block.draw(grass)
    pygame.display.set_caption(f"{inRange}")
    drawPlayer()
    angleCalc()
    endLevel(endPoint)
    pygame.display.flip()
    

pygame.quit()
