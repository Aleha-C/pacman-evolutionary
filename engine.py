from world import WorldTracker
from pacman import PacMan
from ghost import Ghost
import random


class GameEngine:
    def __init__(self, configDict, pacman, ghost):
        self.configDict = configDict
        self.worldTracker = WorldTracker(configDict)
        self.world = self._getWorld()
        self.score = 0
        self.bestWorldSteps = []
        self.pacManSolution = pacman
        self.ghostSolution = ghost

    def runGame(self):
        players = [
            PacMan(self.world.pacManCoords, self.pacManSolution),
            Ghost(self.world.ghostCoords[0], self.ghostSolution),
            Ghost(self.world.ghostCoords[1], self.ghostSolution),
            Ghost(self.world.ghostCoords[2], self.ghostSolution)
        ]

        gameRunning = True
        won = False
        while gameRunning:
            oldPlayerCoords = [self.world.pacManCoords] + self.world.ghostCoords
            decisions = []
            for player in range(len(players)):
                currPlayer = players[player]
                validMoves = self.world.validMoves[player]
                choice = currPlayer.move(validMoves, self.world)
                decisions.append(choice)

            self._movePlayers(players, decisions)
            self.world.time -= 1
            newPlayerCoords = [self.world.pacManCoords] + self.world.ghostCoords
            if self._pacManGhostCollision(oldPlayerCoords, newPlayerCoords):
                gameRunning = False
                break

            self._removePills()
            self._removeFruit()

            if len(self.world.pillCoords) == 0:
                won = True
                gameRunning = False
                break

            if self.world.time == 0:
                gameRunning = False
                break

            self._addFruit(self.world)
            self.worldTracker.addSnapshot(self.world)

            self.world.validMoves = self.worldTracker.getValidMoves(self.world)

        if won and self.world.time != 0:
            percentTime = int((self.world.time / self.world.timeStart) * 100)
            score = self.world.score + percentTime
            self.world.score = score


        self.worldTracker.addSnapshot(self.world)

        self.score = self.world.score

    def _movePlayers(self, players, decisions):
        currPlayerCoords = [self.world.pacManCoords] + self.world.ghostCoords
        newPlayerCoords = []
        moveDict = {
            0: [-1, 0],
            1: [0, 1],
            2: [1, 0],
            3: [0, -1],
            4: [0, 0]
        }

        for player in range(len(players)):
            currCoords = currPlayerCoords[player]
            moveVect = moveDict[decisions[player][2]]
            newCoords = [moveVect[0] + currCoords[0], moveVect[1] + currCoords[1]]
            newPlayerCoords.append(newCoords)

        self.world.pacManCoords = newPlayerCoords[0]
        for ghost in range(1, 4):
            self.world.ghostCoords[ghost - 1] = newPlayerCoords[ghost]

    def _getWorld(self):
        world = self.worldTracker.loadWorlds(1)[0]
        return world

    def _removePills(self):
        pacManNewCoords = self.world.pacManCoords
        if pacManNewCoords in self.world.pillCoords:
            pillIndex = self.world.pillCoords.index(pacManNewCoords)
            del self.world.pillCoords[pillIndex]
            self.world.pillsEaten += 1
            self.world.score = int((self.world.pillsEaten / self.world.totalPills) * 100) + self.world.fruitScore

    def _removeFruit(self):
        pacManNewCoords = self.world.pacManCoords
        if pacManNewCoords == self.world.fruitCoords:
            self.world.fruitCoords = []
            self.world.fruitScore += self.configDict["fruitScore"]

    def _pacManGhostCollision(self, oldPlayerCoords, newPlayerCoords):
        collision = False
        for ghost in range(1, 4):
            if newPlayerCoords[0] == newPlayerCoords[ghost]:
                collision = True
                break
            if newPlayerCoords[0] == oldPlayerCoords[ghost] and newPlayerCoords[ghost] == oldPlayerCoords[0]:
                collision = True
                break

        return collision

    def _addFruit(self, world):
        if not world.fruitCoords:
            probability = random.uniform(0, 1)
            if probability <= self.configDict["fruitSpawnProb"]:
                validSquare = False
                while not validSquare:
                    row = random.randint(0, world.height - 1)
                    column = random.randint(0, world.width - 1)
                    coords = [row, column]
                    if coords in world.wallCoords or coords in world.pillCoords or coords == world.pacManCoords:
                        break
                    validSquare = True
                    world.fruitCoords = coords
                    world.outputFruit = True
