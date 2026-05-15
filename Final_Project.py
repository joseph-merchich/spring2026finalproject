import pygame,random,math,json
from pygame.locals import *
from pygame.math import Vector2
pygame.init()
pygame.mixer.init()
font = pygame.font.SysFont(None, 40)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

SKYBLUE = (75,191,255)
BLUE = (0,0,225)
DARKBLUE = (0,71,171)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
PEACH = (255,176,156)

gameLoop = True
gameMode = 0
playerSpeed = 5
grounded = False
fallSpeed = 9
playerSize = 150

momentumX = 0
momentumY = 0
momentum = pygame.math.Vector2(0,0)
data = {}

grass = pygame.image.load("grass.png")
dirt = pygame.image.load("dirt.png")
brimstone = pygame.image.load("brimstone.png")
lavarock = pygame.image.load("lavarock.png")
stone = pygame.image.load("Gray stone.png")
forest = pygame.image.load("Forest background.png")
running_sheet = pygame.image.load("Running Animation.png")
hero_facing_left = pygame.image.load("Amadis_facing_backwards.png")
hero_jumping = pygame.image.load("Amadis_Jumping_Forward.png")
troll = pygame.image.load("Troll with spear.png")
stab = pygame.image.load("stab.png")
up_slice = pygame.image.load("Up slice.png")
down_slice = pygame.image.load("Down slice.png")
demon = pygame.image.load("Demon.png")

##laceration = pygame.image.load("laceration.png")
##weakness= pygame.image.load("weakness.png")

boost = 10
boostVector = (0,0)
acceptingNewVector = True
inRange=False
pathTarget = Vector2(0, 0)
attackTimer = 0
levelExitPos = Vector2(0, 0)
levelExitRect = pygame.Rect(0, 0, 300, 300)

reticle = pygame.Rect(0,0,0,0)

FPS = 100
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 1000),pygame.RESIZABLE)
w, h = pygame.display.get_surface().get_size()
mousePos = pygame.mouse.get_pos()
offset = pygame.math.Vector2(0,0)
world = pygame.math.Vector2(w/2,h/2)
playerRect = pygame.Rect(w/2, h/2, 114, 128)
#playerRect = pygame.Rect(w/2,h/2,100,500)
playerFeet = playerRect
ground = pygame.Rect(world.x,world.y+100,1000,100)
jumping = False
walking = True
stabbing = False
slicing_up = False
slicing_down = False
levelLoaded = False
directionFacing = "right"
heroSheetW, heroSheetH = running_sheet.get_size()
heroSheetRows = 1
heroSheetColumns = 2
heroImageX = 0
heroImageY = 0
heroSheetCounter = 0
frameIndex = 0
troll = pygame.transform.scale(troll, playerRect.size)
demon = pygame.transform.scale(demon, playerRect.size)
enemies = []
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
        
    """def collide(self,player):
        global offset,grounded,mousePos,fallSpeed,momentumY,boost,reticle
            
        if self.rect.colliderect(player):
            grounded = True
            leftOverlap = player.right - self.rect.left
            rightOverlap = self.rect.right - player.left
            topOverlap = player.bottom - self.rect.top
            bottomOverlap = self.rect.bottom - player.top
            min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)#Which of these overlaps is smallest?
            
            if min_overlap == topOverlap:
                momentumY=0
                offset.y += topOverlap
                grounded = True
                momentumY = 0
                
            elif min_overlap == bottomOverlap:
                momentumY=0
                offset.y -= bottomOverlap
                boost=0
                grounded = True
                
            elif min_overlap == leftOverlap:
                offset.x += leftOverlap
                grounded = True
            elif min_overlap == rightOverlap:
                offset.x -= rightOverlap
                grounded = True"""
    
    def collide(self, player):
        global offset, grounded, mousePos, fallSpeed, momentumY, boost, reticle, frameCorrection

        if self.rect.colliderect(player):
            leftOverlap = player.right - self.rect.left
            rightOverlap = self.rect.right - player.left
            topOverlap = player.bottom - self.rect.top
            bottomOverlap = self.rect.bottom - player.top
            #min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)
            min_overlap = min(topOverlap, bottomOverlap, leftOverlap, rightOverlap)
            min(topOverlap, bottomOverlap, leftOverlap, rightOverlap)

            if min_overlap == topOverlap:
                if not frameCorrection:
                    momentumY = 0
                    offset.y += topOverlap
                    grounded = True        # <-- ONLY here
                    frameCorrection = True
            elif min_overlap == bottomOverlap:
                momentumY = 0
                offset.y -= bottomOverlap
                boost = 0
            elif min_overlap == leftOverlap:
                offset.x += leftOverlap
            elif min_overlap == rightOverlap:
                offset.x -= rightOverlap




class Enemy:
    def __init__(self, position, size, brain, health, offset, speed, grounded, momentumY,floatable):
        self.position = Vector2(position)
        self.size = size
        self.rect = pygame.Rect(position, size)
        self.brain = brain
        self.health = health
        self.offset = Vector2(position) - Vector2(world)
        self.speed = speed
        self.grounded = grounded
        self.momentumY = momentumY
        self.floatable = floatable
        self.hitTimer = 0
    def draw(self):
        global troll

        if self.brain == 1:
            screen.blit(troll,self.rect)
        if self.brain == 2:
            screen.blit(demon,self.rect)
        if self.brain == 3:
            screen.blit(troll,self.rect)
        if self.brain == 4:
            screen.blit(troll,self.rect)

    def EnemyGravity(self):
        global momentumY, offset
        if self.grounded == False:
            if self.momentumY<fallSpeed:
                self.momentumY += 1
            self.offset.y+=self.momentumY

        
        
    def huntGravity(self):
        global blocks,paths,screenRect,pathTarget, momentumY, offset
        self.grounded = False
        self.correctedThisFrame = False
        self.rect.center = (world.x + self.offset.x,world.y + self.offset.y)
        if self.brain < 3:
            if playerRect.centerx > self.rect.centerx:
                self.offset.x += self.speed * self.brain
            if playerRect.centerx < self.rect.centerx:
                self.offset.x -= self.speed * self.brain
##           if playerRect.centery > self.rect.centery:
##                self.offset.y += self.speed * self.brain
##            if playerRect.centery < self.rect.centery:
##                self.offset.y -= self.speed * self.brain
        if self.brain >= 1:
            for block in blocks:
                if block.rect.colliderect(self.rect):
                    
                    
                    leftOverlap = block.rect.right - self.rect.left
                    rightOverlap = self.rect.right - block.rect.left
                    topOverlap = block.rect.bottom - self.rect.top
                    bottomOverlap = self.rect.bottom - block.rect.top
                    min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)
                    
                    if min_overlap == topOverlap:
                        self.offset.y += topOverlap
                        
                    elif min_overlap == bottomOverlap:
                            if not self.correctedThisFrame:
                                self.offset.y -= bottomOverlap
                                self.grounded = True
                                self.momentumY = 0
                                self.correctedThisFrame = True
                    elif min_overlap == leftOverlap:
                        self.offset.x += leftOverlap
                    elif min_overlap == rightOverlap:
                        self.offset.x -= rightOverlap
               
        if self.brain >= 2:
            for block in blocks:
                if block.rect.colliderect(self.rect):
                    
                    
                    leftOverlap = block.rect.right - self.rect.left
                    rightOverlap = self.rect.right - block.rect.left
                    topOverlap = block.rect.bottom - self.rect.top
                    bottomOverlap = self.rect.bottom - block.rect.top
                    min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)
                    
                    if min_overlap == topOverlap:
                        self.offset.y += topOverlap
                        
                    elif min_overlap == bottomOverlap:
                            if not self.correctedThisFrame:
                                self.offset.y -= bottomOverlap
                                self.grounded = True
                                self.momentumY = 0
                                self.correctedThisFrame = True
                    elif min_overlap == leftOverlap:
                        self.offset.x += leftOverlap
                    elif min_overlap == rightOverlap:
                        self.offset.x -= rightOverlap
                    
        if self.brain >= 3:
            if pathTarget.x > self.rect.centerx:
                self.offset.x += self.speed * self.brain
            if pathTarget.x < self.rect.centerx:
                self.offset.x -= self.speed * self.brain
            if pathTarget.y > self.rect.centery:
                self.offset.y += self.speed * self.brain
            if pathTarget.y < self.rect.centery:
                self.offset.y -= self.speed * self.brain
        if self.brain == 4:
            pass



    def hunt(self):
        global blocks,paths,screenRect,pathTarget, momentumY
        self.grounded = False
        self.correctedThisFrame = False
        self.rect.center = (world.x + self.offset.x,world.y + self.offset.y)
        if self.brain < 3:
            if playerRect.centerx > self.rect.centerx:
                self.offset.x += self.speed * self.brain
            if playerRect.centerx < self.rect.centerx:
                self.offset.x -= self.speed * self.brain
            if playerRect.centery > self.rect.centery:
                self.offset.y += self.speed * self.brain
            if playerRect.centery < self.rect.centery:
                self.offset.y -= self.speed * self.brain
        if self.brain == 1:
                pass
        if self.brain >= 2:
            for block in blocks:
                if block.rect.colliderect(self.rect):
                    
                    
                    leftOverlap = block.rect.right - self.rect.left
                    rightOverlap = self.rect.right - block.rect.left
                    topOverlap = block.rect.bottom - self.rect.top
                    bottomOverlap = self.rect.bottom - block.rect.top
                    min_overlap = min(leftOverlap, rightOverlap, topOverlap, bottomOverlap)
                    
                    if min_overlap == topOverlap:
                        self.offset.y += topOverlap
                        
                    elif min_overlap == bottomOverlap:
                        if not self.floatable:
                            if not self.correctedThisFrame:
                                self.offset.y -= bottomOverlap
                                self.grounded = True
                                self.momentumY = 0
                                self.correctedThisFrame = True
                    elif min_overlap == leftOverlap:
                        self.offset.x += leftOverlap
                    elif min_overlap == rightOverlap:
                        self.offset.x -= rightOverlap
                    
        if self.brain >= 3:
            if pathTarget.x > self.rect.centerx:
                self.offset.x += self.speed * self.brain
            if pathTarget.x < self.rect.centerx:
                self.offset.x -= self.speed * self.brain
            if pathTarget.y > self.rect.centery:
                self.offset.y += self.speed * self.brain
            if pathTarget.y < self.rect.centery:
                self.offset.y -= self.speed * self.brain
        if self.brain == 4:
            pass


#enemy1 = Enemy((100,100), (troll.size), 1,1,(0,0,),1)
def handleInputs():
    global gameLoop,boost,world,acceptingNewVector,inRange, jumping, directionFacing, walking, stabbing, slicing_up, slicing_down, attackTimer, offset
    walking = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        #offset.y += playerSpeed
        pass
    if keys[pygame.K_s]:
        #offset.y -= playerSpeed
        pass
    if keys[pygame.K_a]:
        directionFacing = "left"
        offset.x += playerSpeed
        walking = True
    if keys[pygame.K_d]:
        directionFacing = "right"
        offset.x -= playerSpeed
        walking = True
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            #print(f"Mouse button {event.button} clicked at {event.pos}")
            if inRange==True:
                inRange = False
                boost = 40
                acceptingNewVector = True
                jumping = True
##                while event.type == MOUSEBUTTONDOWN:
##                    jumping = True
        if event.type == pygame.QUIT:
            gameLoop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                stabbing = True
                attackTimer = pygame.time.get_ticks()
            if event.key == pygame.K_UP:
                slicing_up = True
                attackTimer = pygame.time.get_ticks()
            if event.key == pygame.K_DOWN:
                slicing_down = True
                attackTimer = pygame.time.get_ticks()
            if event.key == pygame.K_ESCAPE:
                gameLoop = False
                
#hero = pygame.transform.scale(hero,playerRect.size)
def drawPlayerRect():
    global grounded, playerRect
    pygame.draw.rect(screen, ('orange'), (playerRect),0,5)
    
    """screen.blit(hero_facing_forward,(playerRect.centerx,playerRect.centery))"""
    
    """screen.blit(hero_facing_forward,(playerRect.centerx-playerSize/2,playerRect.centery-playerSize/2))"""
    
    """,(soulImageX,0,soulImageStep,soulImageH))"""
    

def drawPlayerWalk():
    global grounded, playerRect
    screen.blit(hero_facing_forward,(playerRect.x-playerSize,playerRect.y-playerSize))


def fightEnemy():
    global playerRect, enemies, offset
    for enemy in enemies:
        if playerRect.colliderect(enemy.rect) and (stabbing or slicing_up or slicing_down) == True:
            if pygame.time.get_ticks() - enemy.hitTimer > 500:
                enemy.health -= 1
                enemy.hitTimer = pygame.time.get_ticks()
                if directionFacing == "left":
                    enemy.offset.x -= 100
                else:
                    enemy.offset.x += 100
    

    
def loadGame():
    global data,gameMode, offset
    try:
        # the file already exists
        with open('save.txt') as load_file:
            data = json.load(load_file)
            offset.x = data["x"] - playerRect.x
            offset.y = data["y"] - playerRect.y
            momentum.x = data["momentumX"]
            momentum.y = data["momentumY"]
            #world = pygame.Rect(Vector2(data["x"],data["y"]),50,50)
    except:
        # create the file and store initial values
        with open('save.txt', 'w') as store_file:
            json.dump(data, store_file)
    gameMode=1


def newGame():
    global data,gameMode
    with open('save.txt', 'w') as store_file:
        json.dump(data, store_file)
    gameMode=1

buttons = []
messages = []

button0 = buttons.append(pygame.Rect(100,100,300,50))
message0 = messages.append("New Game")

button1 = buttons.append(pygame.Rect(100,300,300,50))
message1 = messages.append("Resume Game")

def drawButtons():
    global buttons,messages,data
    buttons[0] = pygame.Rect(w/2-buttons[0].w/2,h/2-buttons[0].h/2,500,50)
    buttons[1] = pygame.Rect(w/2-buttons[1].w/2,h/2+100,500,50)

    for button in buttons:
        pygame.draw.rect(screen, ('lightgray'), button,0,5)
        if button.contains(mousePos,(1,1)):
            pygame.draw.rect(screen, ('lightblue'), button,0,5)
            if button==buttons[0]:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        newGame()
            if button==buttons[1]:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        loadGame()
                    
            
        message = f"{messages[buttons.index(button)]}"
        textBox = font.render(message, True,'darkblue')
        screen.blit(textBox, (button.centerx - textBox.get_rect().w/2,button.centery - textBox.get_rect().h/2))  



def angleCalc():
    global playerRect,boost,offset,acceptingNewVector,boostVector,mousePos,reticle
    direction_vector = Vector2(mousePos) - playerRect.center
    if direction_vector.length() > 0:
        direction_vector = direction_vector.normalize()
    target_offset = direction_vector * 150
    square_pos = playerRect.center + target_offset
    reticle = pygame.Rect(square_pos.x-25,square_pos.y-25,50,50)
##    pygame.draw.rect(screen, ('yellow'), reticle,0,5)
    
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

##def endLevel(end):
##    here = font.render("Hit here!", True, RED)
##    screen.blit(here,(end,end))
##    if playerRect.collidepoint(endPoint):
##        message = font.render("You have completed the level!", True, RED)
##        screen.blit(message, (100,100))
##        level += 1
        
tilemapLevel1 = [
    'B_______B_____________D______D_________BBB_______________________T',
    'B__________________________________BBB_______________________BBBBBBBBB_____________________________________________________________________________________________________DDDDDDDDDD',
    'B______B________________________BBB______________________',
    'B___________BB____T_________BBB_____________________________BBBBBBBBBBBB___T___D________________________D____________B_____B_T____B______B_____BBBBBBBBBBBBBBBBBB____',
    'B____T_B____BBBB_________BB_______________________________BBBBBBBBBBBB_______________________________________________B_____B______B______B___D_______D_________________________________LLLLLLLLLLLLLLLLLLLL__',
    'BBBBBBBBB__BBBBBBB__BBBB_____________________BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB_BBBBBBBBBBBBBB__BB__BB__BB__BB__BB__BB__BB_____B______B______B____BBBBBBBBBBBBBBBBBBB___________BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    '___________________________________________________________________________________________________________BBBBBBBBBBBBBBBBBBBBBBBB______BBBBBBBB__________________________BBBBBBBBBB'
    ]

endPoint = 500,500

tileMapLevel1_1 = [
    '---------------------------BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB------BBBBB',
    '------------------------------------------------------',
    '--------------------E---------BBBBBBBBBB---------------------------',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
    ]
    
   
def parallax():
    global level
    background = pygame.Rect(world.x*50,world.y,1000,1000)
    pygame.draw.rect(screen, ('black'), (background))
    if playerRect.colliderect(background):
        message = font.render("You have completed the level!", True, RED)
        screen.blit(message, (100,100))
        level += 1
        
level = 1
blocks = []
tileSize = 100
def buildWorld(tilemap):
    global level, levelExitPos, offset
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == 'B':
                #blocks.append(Block(x*tileSize, y*tileSize), (tileSize, tileSize), BLUE)
                blocks.append(Block((offset.x + (x*tileSize), offset.y+(y*tileSize)), (tileSize, tileSize), BLUE))
                # Remember: Enemy = position, size, brain, health, offset, speed, grounded, momentumY,floatable
            elif tile == 'T':
                enemies.append(Enemy((offset.x + (x*tileSize), offset.y+(y*tileSize)), troll.get_size(), 1,1, (0,0), 1, False, 0,False))
            elif tile == 'D':
                enemies.append(Enemy((offset.x + (x*tileSize), offset.y+(y*tileSize)), demon.get_size(), 2,3, (0,0), 1, False, 0, True))
            elif tile == 'L':
                levelExitPos = Vector2(x * tileSize, y * tileSize)
            elif tile == 'E':
                enemies.append(Enemy((offset.x + (x*tileSize), offset.y+(y*tileSize)), demon.get_size(), 3,10, (0,0), 1, False, 0, False))
##            if tile == 'F':
##                parallax()

def animate():
    global heroImageX,heroImageY,heroSheetCounter,playerRect,heroSheetW, hero_jumping,stab,up_slice
    global heroSheetH,heroSheetColumns,scaledHero,subArea,directionFacing,walking,stabbing,slicing_up,slicing_down,frameIndex,attackTimer
    heroImageY = 0
    heroSheetCounter +=4
    """if jumping == True:
        if directionFacing = 'left':
            hero_jumping = pygame.transform.scale(hero_jumping, playerRect.size)
            hero_jumping = pygame.transform.flip
            screen.blit(hero_jumping, (playerRect.centerx - hero_jumping.get_width() // 2, playerRect.centery - hero_jumping.get_height() // 2))
        return"""
    if heroSheetCounter % (heroSheetW/heroSheetColumns) == 0:
         heroImageX = frameIndex * (heroSheetW / heroSheetColumns)
        #heroImageX=heroSheetCounter
    if heroSheetCounter>=heroSheetW-(heroSheetW/heroSheetColumns):
        heroSheetCounter=0
        frameIndex = 1 if frameIndex == 0 else 0
    if jumping == True:    
        subArea = hero_jumping
    elif stabbing == True:
        if pygame.time.get_ticks() - attackTimer > 100:
            stabbing = False
        else:
            subArea = stab
    elif slicing_up == True:
        if pygame.time.get_ticks() - attackTimer > 100:
            slicing_up = False
        else:
            subArea = up_slice
    elif slicing_down == True:
        if pygame.time.get_ticks() - attackTimer > 100:
            slicing_down = False
        else:
            subArea = down_slice
    else:
        subArea = running_sheet.subsurface((heroImageX,heroImageY,(heroSheetW/heroSheetColumns),(heroSheetH/heroSheetRows)))
    
    if not walking:
        heroImageX = 0
        heroSheetCounter = 0
        frameIndex = 0
        walking = False
        
    """if stabbing == True:
        scaledStab = pygame.transform.scale(stab, playerRect.size)
        screen.blit(scaledStab, playerRect)"""
    if directionFacing == "left":
        
        #heroImageY = (heroSheetH/heroSheetRows)*3
        flippedSub = pygame.transform.flip(subArea, True, False)
        #pygame.transform.flip(subArea, True, False)
        #pygame.transform.scale(subArea, playerRect.size)
        #screen.blit(flippedSub,playerRect)
        scaledSub = pygame.transform.scale(flippedSub, playerRect.size)
        screen.blit(scaledSub, playerRect)
    #if directionFacing == "right":
        heroImageY = 0
        #heroImageY = (heroSheetH/heroSheetRows)*2
        #scaledHero = pygame.transform.scale(subArea,playerRect.size)
    else:
        """"pygame.transform.scale(subArea, playerRect.size)
        screen.blit(subArea,playerRect)"""
        scaledSub = pygame.transform.scale(subArea, playerRect.size)
        screen.blit(scaledSub, playerRect)

"""def animate():
    global playerRect, jumping
    if jumping == True and pygame.time.get_ticks() > 100:
        playerRect = pygame.Rect(w/2,h/2,playerSize-10,playerSize-10)
        screen.blit(hero_jumping, (playerRect.centerx - hero_jumping.get_width() // 2, playerRect.centery - hero_jumping.get_height() // 2))
        #screen.blit(hero_jumping,(playerRect.x-playerSize,playerRect.y-playerSize+50))
    elif jumping == False:
        screen.blit(hero_facing_forward,(playerRect.centerx - hero_facing_forward.get_width() // 2, playerRect.centery - hero_facing_forward.get_height() // 2))
        #screen.blit(hero_facing_forward,(playerRect.x-50,playerRect.y-playerSize))
    elif directionFacing == "left":
        screen.blit(hero_facing_left,(playerRect.centerx - hero_facing_left.get_width() // 2, playerRect.centery - hero_facing_left.get_height() // 2))
        #screen.blit(hero_facing_left,(playerRect.x-playerSize,playerRect.y-playerSize+50))
    elif directionFacing == 'right':
        screen.blit(hero_facing_forward,(playerRect.centerx - hero_facing_forward.get_width() // 2, playerRect.centery - hero_facing_forward.get_height() // 2))
        #screen.blit(hero_facing_forward,(playerRect.x-playerSize,playerRect.y-playerSize+50))"""
"""def animate():
    global playerRect, jumping
    if jumping == True:
        screen.blit(hero_jumping, (playerRect.centerx - hero_jumping.get_width() // 2, playerRect.centery - hero_jumping.get_height() // 2))
    elif directionFacing == "left":
        screen.blit(hero_facing_left, (playerRect.centerx - hero_facing_left.get_width() // 2, playerRect.centery - hero_facing_left.get_height() // 2))
    else:
        screen.blit(hero_facing_forward, (playerRect.centerx - hero_facing_forward.get_width() // 2, playerRect.centery - hero_facing_forward.get_height() // 2))"""
##if level == 1:
offset.y = 500 - (1 * tileSize) - playerRect.height
buildWorld(tilemapLevel1)
##if level == 1_1:
##            buildWorld(tileMapLevel1_1)
    
world = pygame.Vector2(playerRect.x+offset.x,playerRect.y+offset.y)

while gameLoop:
    clock.tick(FPS)
    mousePos = pygame.mouse.get_pos()
    events = pygame.event.get()
    handleInputs()
    if gameMode == 0:
        screen.fill("black")
        drawButtons()
    elif gameMode == 1:
    #perform all physics calculations first
        screen.fill(SKYBLUE)
        frameCorrection = False
        grounded = False
##    stabbing = False
##    slicing_up = False
##    slicing_down = False
        animate()
    

        w, h = pygame.display.get_surface().get_size()
    #playerRect = pygame.Rect(w/2,h/2,playerSize-10/2,playerSize)
    #playerRect = pygame.Rect(w/2-playerRect.w/2,h/2-playerRect.h/2,100,100)
    #playerRect = pygame.Rect(w/2,h/2,playerSize/2+10,playerSize+60)
    #playerRect = pygame.Rect(w/2,h/2,100,500)
    #world = pygame.Vector2(playerRect.x+offset.x,playerRect.y+offset.y)
    #world = pygame.Rect(playerRect.x+offset.x,playerRect.y+offset.y,playerRect.w,playerRect.h)
        world = pygame.Vector2(playerRect.x + offset.x, playerRect.y + offset.y)
    
##    parallax()
        inRange=False
    #jumping = False
    #if level == 1:
##        for block in blocks:
##            block.rect.topleft = (block.position.x + world.x,block.position.y + world.y)
##            block.collide(playerRect)
##            if block.rect.colliderect(reticle):
##                inRange = True
##            grounded = False
        gravity()
        for block in blocks:
            block.rect.topleft = ((block.position.x+world.x),(block.position.y+world.y))
            if block.rect.colliderect(playerRect):
                block.collide(playerRect)
            if block.rect.colliderect(reticle):
                inRange = True
        
    
    #ground = pygame.Rect(world.x-100,world.y+150,800,200)
    #block1 = Block((world.x-100,world.y+150),(200,200),BLUE)
    
    #collidePlayer(ground,playerRect)

    #offset.y+=momentumV
    #then do all your drawing
##    dirt = pygame.transform.scale(dirt,world.size)
##    grass = pygame.transform.scale(grass,world.size)
##    lavarock = pygame.transform.scale(lavarock,world.size)
##    brimstone = pygame.transform.scale(brimstone,world.size)
##    troll = pygame.transform.scale(troll,world.size)
##    hero_facing_forward = pygame.transform.scale(hero_facing_forward, world.size)
##    hero_jumping = pygame.transform.scale(hero_jumping, world.size)
    #playerRect = pygame.Rect(w/2,h/2,playerSize,playerSize)
        for block in blocks:
            if level == 1:
                block.draw(grass)
            elif level == 2:
                block.draw(stone)
        levelExitRect.topleft = (levelExitPos.x + world.x, levelExitPos.y + world.y)
        if playerRect.colliderect(levelExitRect):
            level = 1_1
            print("You have completed the level!")
        if level == 1_1 and not levelLoaded:
            blocks.clear()
            enemies.clear()
            offset.x = 0
            offset.y = -400
            momentumY = 0
            buildWorld(tileMapLevel1_1)
            levelLoaded = True
        pygame.display.set_caption(f"{inRange}")
        angleCalc()
        for enemy in enemies:
            if enemy.health > 0:   
                enemy.draw()
                if enemy.floatable == True:
                    enemy.hunt()
                elif enemy.floatable == False:
                    enemy.EnemyGravity()
                    enemy.huntGravity()
        #drawPlayerRect()
        fightEnemy()
        if grounded == False:
            jumping = True
        else:
            jumping = False
    
##    endLevel(endPoint)
    #screen.blit(currentImage,(playerRect.x-playerSize,playerRect.y-playerSize+50))
    #screen.blit(currentImage,(playerRect.x-50,playerRect.y-playerSize))
    
    pygame.display.flip()
    
    if gameMode>0:
        data = {"x": int(world.x), "y": int(world.y+22),"momentumX":momentum.x,"momentumY":momentum.y}
        with open('save.txt', 'w') as file:
            json.dump(data,file)

pygame.quit()
