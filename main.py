#   SMART BOXES
#   by Burak Unutmaz, 25.09.2019
#
#   A python, pygame program in which I try the genetic algorithm.
#   Boxes for each generation try to reach the end goal.

import pygame as pg
import sys
import math
import random

pg.init()

SW, SH = 1280, 720                          # Setting up
SC = pg.display.set_mode((SW,SH))           # the
pg.display.set_caption("Smart Boxes")       # screen
clock = pg.time.Clock()     # Clock object to control
FPS = 60                    # the Fps
defaultFont = pg.font.SysFont(None, 40)     # Default font of the program
random.seed(random.randrange(50000000))     # Setting the random seed to a random value
moveLimit = 300         # Frame limit for free movement of smart boxes
boxCount = 200          # Amount of smart boxes for each generation
generationCount = 0
frameCount = 0          # To count the frames until the moveLimit
levelCount = 1
successCount = 0        # Counting the successful smart boxes
avgFitness = 0          # Average fitness ( score from 0 to 1 ) of-
avgFitnessD = 0         # -the last generation, and the difference-
lowestTime = 0          # -between the last and current generation-
lowestTimeD = 0         # -same with lowest time. Record holder (fastest smart box) form the last gen
aliveBoxCount = boxCount    # Currently alive boxes
successCountD = 0           # Difference of this gen's successful boxes and the last one.
levelColor = [random.randrange(150) + 100, random.randrange(150) + 100, random.randrange(150) + 100]    # Randomly
finished = False       # Boolean for deciding when the generation is finished                           # Generated
walls = []             # List for obstacles                                                             # Level color

genePool = []          # Necessary for genetic algorithm, best boxes have more place in this gene pool. (mating pool)


def ShowText(string, x, y, size = 40, color=(255, 255, 255)):   # Quicker way to show text on the screen
    funcFont = pg.font.SysFont(None, size)
    SC.blit(funcFont.render(string, True, color), (x, y))


def Remap(low1, high1, low2, high2, value):                     # A mapping function needed for later
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)


def Distance(x1, x2, y1, y2):                                   # A function to calculate the distance between two-
    return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))     # -points.


class Obstacle(object):                                                             # Obstacle object
    def __init__(self, x, y, width, height):                                        # Getting position and size
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.subsurface = pg.Surface((self.width, self.height))                     # Creating a pygame surface for
                                                                                    # Collision detection
    def Draw(self):
        pg.draw.rect(SC, (150,150,150), (self.x, self.y, self.width, self.height))  # Drawing a rectangle at the
                                                                                    # object's position.

class DNA(object):                                                  # DNA object for genetic algorithm
    def __init__(self, genes=None):                                 # If initialized with a gene already, don't
        self.array = []                                             # generate random movements. Else, do.
        self.chain = pg.math.Vector2()              # DNA chain that is just a 2d vector. ( for random acceleration )
        if genes:
            self.array = genes
        else:
            for i in range(moveLimit):              # Till the limit frame, generate random movements.
                self.chain.xy = random.random()*2-1, random.random()*2-1
                self.array.append(self.chain.xy)

    def CrossOver(self, partner):                               # Select a partner from the gene pool,
        newGenes = []                                           # Choose a random point in the DNA chain,
        middle = math.floor(random.randrange(len(self.array)))  # Mix two genes and create a new array of motion.
        for i in range(len(self.array)):                        # Create a new DNA, with the gene created.
            if i < middle:
                newGenes.append(partner.array[i])
            else:
                newGenes.append(self.array[i])

        return DNA(newGenes)


class SmartBox(object):                         # Our smart box object
    def __init__(self, dna=None):               # If initialized with a DNA, use that dna, else, create new.
        self.alive = True           # Bool to see if it's alive
        self.crashed = False        # Bool to see if it's crashed
        self.won = False            # Bool to see if it's won
        self.wonTime = 0            # To save the time that the box has won ( faster boxes get more places-
                                    # -in the gene pool.
        if dna:
            self.gene = DNA(dna)
        else:
            self.gene = DNA()

        self.x, self.y = 10, SH//2          # Some initializations of variables,
        self.size = 10                      # position, size, acceleration, velocity, velocity limit,
        self.acc = pg.math.Vector2()        # thrust colour, thrust size, fitness
        self.acc.xy = 0, 0
        self.vel = pg.math.Vector2()
        self.vel.xy = 0, 0
        self.velLimit = 6
        self.burstColor = pg.Color("red")
        self.burstSize = 10
        self.fitness = 0
        self.subsurface = pg.Surface((self.size, self.size))    # Creating a surface to check for collisions.
        self.subsurface.fill((50, 215, 240))
        self.subsurface.set_alpha(128)

    def CheckCollision(self, arr):              # Checking if this object collides with the obstacles OR window frame.
        global aliveBoxCount
        if self.x + self.size > SW or self.x < 0 or self.y < 0 or self.y + self.size > SH:
            self.crashed = True
        for item in arr:
            if self.subsurface.get_rect(topleft=(self.x, self.y)).colliderect(item.subsurface.get_rect(topleft=(item.x, item.y))):
                self.crashed = True
        if self.crashed:
            self.alive = False
            aliveBoxCount -= 1      # If it's crashed, make it not alive.

    def CalculateFitness(self):     # The closer it is, the better it's fitness is.
        dist = Distance(self.x, finish.x, self.y, finish.y)
        self.fitness = Remap(0, SW, 1, 0, dist)     # Remapping the distance to 0-1, If it's further, fitness is
                                                    # closer to 0, if it wins, fitness is 1.

    def Update(self):   # Update the object every frame.
        if self.crashed:
            self.subsurface.fill((128, 0, 0))   # If crashed, turn it's color to red.
        if self.alive:
            self.acc = self.gene.array[frameCount]
            if self.subsurface.get_rect(topleft=(self.x, self.y)).colliderect(winRect) and not self.won:
                self.won = True
                self.wonTime = frameCount
            if self.won:
                self.x, self.y = finish.x, finish.y
                self.vel.xy = 0, 0
                self.acc.xy = 0, 0
                self.alive = False

        self.vel += self.acc                                # Adding accel. to velocity, and changing the position
        if self.vel.x > self.velLimit and self.acc.x > 0:   # according to the velocity.
            self.vel.x = self.velLimit
        if self.vel.x < -self.velLimit and self.acc.x < 0:
            self.vel.x = -self.velLimit
        if self.vel.y > self.velLimit and self.acc.y > 0:
            self.vel.y = self.velLimit
        if self.vel.y < -self.velLimit and self.acc.y < 0:
            self.vel.y = -self.velLimit
        self.x += self.vel.x
        self.y += self.vel.y

    def Draw(self):                                     # If it's alive, every 5 frames change the burst size and
        if self.alive:                                  # color.
            if frameCount % 5 == 0:
                self.burstColor = pg.Color("red")
                self.burstSize = 5
            else:
                self.burstColor = pg.Color("orange")
                self.burstSize = 10

            if math.fabs(self.vel.x) > math.fabs(self.vel.y):       # Deciding where to draw the thrust.
                if self.vel.x > 0:
                    pg.draw.rect(SC, self.burstColor, (self.x - 5, self.y + 3, self.burstSize, 3))
                else:
                    pg.draw.rect(SC, self.burstColor, (self.x + 10, self.y + 3, self.burstSize, 3))
            else:
                if self.vel.y > 0:
                    pg.draw.rect(SC, self.burstColor, (self.x + 3, self.y - 5, 3, self.burstSize))
                else:
                    pg.draw.rect(SC, self.burstColor, (self.x + 3, self.y + 10, 3, self.burstSize))
        SC.blit(self.subsurface, (self.x, self.y))


finish = pg.math.Vector2()                                                  # Setting
finish.xy = SW-50, SH//2                                                    # up
                                                                            # the
winSurface = pg.Surface((80, 80))                                           # end
winRect = winSurface.get_rect(topleft=(finish.x-40, finish.y-40))           # goal      # A rect to check for collision.

boxes = []                      # List to hold the smart boxes.
for i in range(boxCount):
    boxes.append(SmartBox())


def FinishGeneration():     # A function for resetting process.

    global finished, avgFitness, moveLimit, walls, successCount             # Getting all the global variables.
    global generationCount, frameCount, levelCount, lowestTime
    global levelColor, avgFitnessD, lowestTimeD, successCountD, aliveBoxCount

    tempLowestTime = lowestTime         # Setting up some values.
    tempAvgFitness = avgFitness
    tempSuccessCount = successCount
    genePool.clear()
    maxFit = 0
    lowestTime = moveLimit
    lowestIndex = 0
    successCount = 0
    avgFitnessSum = 0
    maxFitIndex = 0
    for box in boxes:
        box.CalculateFitness()
        avgFitnessSum += box.fitness
        if box.fitness >= 1.0:
            successCount += 1
        if box.fitness > maxFit:
            maxFit = box.fitness
            maxFitIndex = boxes.index(box)
    successCountD = successCount - tempSuccessCount
    avgFitness = avgFitnessSum / len(boxes)
    avgFitnessD = avgFitness - tempAvgFitness

    for i, box in enumerate(boxes):
        if box.won:
            if box.wonTime < lowestTime:
                lowestTime = box.wonTime
                lowestIndex = i
    lowestTimeD = lowestTime - tempLowestTime

    for i, box in enumerate(boxes):
        n = int((box.fitness ** 2) * 100)
        if i == maxFitIndex:
            print(box.fitness)
            if successCount < 2:
                n = int((box.fitness ** 2) * 150)       # Squared the fitness value to make sure
                                                        # The furthest ones get much more place in the gene pool.
        if i == lowestIndex and successCount > 1:
            n = int((box.fitness ** 2) * 500)           # If it's the first one to finish when there are more boxes
                                                        # finishing the level, get much much more places in the pool.
        for j in range(n):
            genePool.append(boxes[i])

    if successCount >= len(boxes)//2:
        levelCount += 1

        if levelCount == 1:                 # Set the level accordingly.
            moveLimit = 300
            walls = [

            ]
        elif levelCount == 2:
            moveLimit = 350
            walls = [
                Obstacle(500, 150, 20, 420)
            ]
        elif levelCount == 3:
            moveLimit = 400
            walls = [
                Obstacle(350, 200, 20, 320),
                Obstacle(750, 200, 20, 320),
                Obstacle(550, 0, 20, 200),
                Obstacle(550, 520, 20, 200)
            ]
        elif levelCount == 4:
            moveLimit = 400
            walls = [
                Obstacle(300, 0, 20, 400),
                Obstacle(500, 420, 20, 300),
                Obstacle(410, 250, 200, 20),
                Obstacle(650, 0, 20, 200),
                Obstacle(650, 670, 20, 50),
                Obstacle(670, 0, 20, 300),
                Obstacle(670, 570, 20, 150),
                Obstacle(690, 0, 20, 400),
                Obstacle(690, 470, 20, 250),
                Obstacle(710, 0, 20, 400),
                Obstacle(710, 470, 20, 250),
                Obstacle(730, 0, 20, 400),
                Obstacle(730, 470, 20, 250),
                Obstacle(800, 370, 300, 20),
                Obstacle(800, 470, 300, 20),
            ]
        elif levelCount == 5:
            moveLimit = 450
            walls = [
                Obstacle(200, 100, 20, 620),
                Obstacle(500, 0, 20, 380),
                Obstacle(500, 530, 20, 190),
                Obstacle(800, 300, 20, 420),
                Obstacle(800, 0, 20, 200),
                Obstacle(1100, 0, 20, 350),
                Obstacle(1100, 450, 20, 270),
            ]

        levelColor = [random.randrange(150)+100, random.randrange(150)+100, random.randrange(150)+100]

        boxes.clear()
        generationCount = 0
        for i in range(boxCount):
            boxes.append(SmartBox())
    else:
        for i, box in enumerate(boxes):                         # For every box, create a child box with crossover.
            randomIndex = random.randint(0, len(genePool) - 1)
            parentA = genePool[randomIndex].gene
            randomIndex = random.randint(0, len(genePool) - 1)
            parentB = genePool[randomIndex].gene
            child = parentA.CrossOver(parentB)
            boxes[i] = SmartBox(child.array)
        generationCount += 1
    frameCount = 0
    aliveBoxCount = boxCount
    finished = False


if levelCount == 1:         # If something went wrong, just make sure that the level is 1 and
    moveLimit = 300         # set the movement limit to 300, clear the walls list.
    walls = [

    ]

while True:                             # To keep the window open.
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:       # If X button is pressed, close the screen and exit the program.
            pg.quit()
            sys.exit()

    counterText = "Frame: " + str(frameCount)       # Set the frame count text.
    counterLimitText = " / " + str(moveLimit)

    SC.fill((51, 51, 51))                           # Fill the screen with the color (51, 51, 51)
    for wall in walls:      # Draw every wall.
        wall.Draw()

    for box in boxes:       # Draw, check collision, and update for every smart box.
        box.Draw()
        if box.alive:
            box.CheckCollision(walls)
            box.Update()

    ShowText(counterText, 10, 30)                                           # Drawing
    ShowText(counterLimitText, 160, 33, 30)                                 # The
    ShowText("Generation: " + str(generationCount), 10, 80)                 # Menu
    ShowText("Alive Boxes: " + str(aliveBoxCount), 10, 110, 30)             # .
                                                                            # .
    ShowText("Last Gen:", 10, 550, 45)                                      # .
    ShowText("Total Boxes:             " + str(len(boxes)), 30, 590, 25)    # .
    ShowText("Successful Boxes:   " + str(successCount), 30, 610, 25)       # .
    if successCountD > 0:                                                   # . Change color and sign accordingly
        ShowText("+" + str(successCountD), 250, 610, 25, pg.Color("green")) # .
    else:                                                                   # .
        ShowText("-" + str(-successCountD), 250, 610, 25, pg.Color("red"))  # .

    ShowText("Avg. Fitness:            " + str(round(avgFitness, 3)), 30, 630, 25)
    if avgFitnessD > 0:
        ShowText("+" + str(round(avgFitnessD, 3)), 250, 630, 25, pg.Color("green"))
    else:
        ShowText("-" + str(round(-avgFitnessD, 3)), 250, 630, 25, pg.Color("red"))

    ShowText("Record Time :           " + str(lowestTime), 30, 650, 25)
    if lowestTimeD > 0:
        ShowText("+" + str(lowestTimeD), 250, 650, 25, pg.Color("red"))
    else:
        ShowText("-" + str(-lowestTimeD), 250, 650, 25, pg.Color("green"))

    ShowText("Level " + str(levelCount), 550, 20, 80, levelColor)
    if levelCount == 5:
        ShowText("FINAL", 604, 80, 40, levelColor)

    pg.draw.circle(SC, pg.Color("green"), (int(finish.x), int(finish.y)), 20)       # Finally, draw the end goal.


    pg.display.update()     # Update the display of the screen every frame.

    if (frameCount >= moveLimit-1 and levelCount < 6) or aliveBoxCount <= 0:        # If frame count is larger than
        frameCount = moveLimit-1                                                    # the limit, or level is higher than
        finished = True                                                             # 5, or no boxes left, generation is
    else:                                                                           # finished.
        frameCount += 1     # Add to  the frame count every frame.

    if finished:
        FinishGeneration()  # Start the resetting process.

