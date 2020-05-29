from os import walk
import random


class WorldTracker:
    def __init__(self, configDict):
        self.configDict = configDict
        self.pillDensity = self.configDict["pillDensity"]
        self.fruitSpawnProb = self.configDict["fruitSpawnProb"]
        self.fruitScore = self.configDict["fruitScore"]
        self.timeMultiplier = self.configDict["timeMultiplier"]
        self.mapFiles = self._loadMapFiles()

    def _loadMapFiles(self):
        (_, _, filenames) = next(walk("maps"))
        return filenames

    def loadWorlds(self, amount):
        worlds = []

        selectedMaps = self._selectRandomMaps(amount)
        for map_ in selectedMaps:
            path = "maps/" + map_
            mapData = []
            with open(path, 'r') as file:
                for line in file:
                    line = line.rstrip("\n")
                    mapData.append(list(line))

            mapSpecs = "".join(mapData[0]).split()
            del mapData[0]
            filledMap, pillCoords, wallCoords = self._fillPills(mapData.copy())
            world = World(int(mapSpecs[0]), int(mapSpecs[1]), filledMap)
            world.pillCoords = pillCoords
            world.totalPills = len(pillCoords)
            world.wallCoords = wallCoords
            world.time = self._calculateTime(world)
            world.timeStart = world.time
            world = self._initWorld(world)
            world.validMoves = self.getValidMoves(world)
            worlds.append(world)

        return worlds

    def _selectRandomMaps(self, amount):
        if amount > len(self.mapFiles):
            amount = len(self.mapFiles)

        selectedMapInds = []
        for map in range(amount):
            while True:
                mapIndex = random.randint(0, len(self.mapFiles) - 1)
                if mapIndex not in selectedMapInds:
                    selectedMapInds.append(mapIndex)
                    break

        selectedMaps = []
        for index in selectedMapInds:
            selectedMaps.append(self.mapFiles[index])

        return selectedMaps

    def _calculateTime(self, world):
        squares = world.width * world.height
        time = self.timeMultiplier * squares

        return time

    def _fillPills(self, map_):
        filledSquares = 0
        pillCoords = []
        wallCoords = []

        for row in range(len(map_)):
            for column in range(len(map_[row])):
                if row == 0 and column == 0:
                    continue
                if map_[row][column] == "#":
                    wallCoords.append([row, column])
                    continue

                probability = random.uniform(0, 1)
                if probability <= self.pillDensity:
                    pillCoords.append([row, column])
                    map_[row][column] = "p"
                    filledSquares += 1

        return map_, pillCoords, wallCoords

    def _initWorld(self, world):
        for ghost in range(3):
            world.ghostCoords.append([world.height - 1, world.width - 1])
        world.pacManCoords = [0, 0]

        world.steps.append(str(world.width))
        world.steps.append(str(world.height))
        world.steps.append(self._pacManStep(world.pacManCoords, world.height))
        for ghost in range(3):
            world.steps.append(self._ghostStep(ghost+1, world.ghostCoords[ghost], world.height))
        for wall in world.wallCoords:
            world.steps.append(self._wallStep(wall, world.height))
        for pill in world.pillCoords:
            world.steps.append(self._pillStep(pill, world.height))
        world.steps.append(self._timeStep(world.time, 0))

        return world

    def _pacManStep(self, coords, worldHeight):
        translatedCoords = [coords[1], (worldHeight - 1) - coords[0]]
        return "m " + str(translatedCoords[0]) + " " + str(translatedCoords[1])

    def _ghostStep(self, ghostNum, coords, worldHeight):
        translatedCoords = [coords[1], (worldHeight - 1) - coords[0]]
        return str(ghostNum) + " " + str(translatedCoords[0]) + " " + str(translatedCoords[1])

    def _wallStep(self, coords, worldHeight):
        translatedCoords = [coords[1], (worldHeight - 1) - coords[0]]
        return "w " + str(translatedCoords[0]) + " " + str(translatedCoords[1])

    def _pillStep(self, coords, worldHeight):
        translatedCoords = [coords[1], (worldHeight - 1) - coords[0]]
        return "p " + str(translatedCoords[0]) + " " + str(translatedCoords[1])

    def _fruitStep(self, coords, worldHeight):
        translatedCoords = [coords[1], (worldHeight - 1) - coords[0]]
        return "f " + str(translatedCoords[0]) + " " + str(translatedCoords[1])

    def _timeStep(self, timeRemaining, score):
        return "t " + str(int(timeRemaining)) + " " + str(int(score))

    def getValidMoves(self, world):
        moveArr = []

        pacManMoves = self._findValidMoves(world.pacManCoords, world, True)
        moveArr.append(pacManMoves)
        for ghost in range(3):
            ghostMoves = self._findValidMoves(world.ghostCoords[ghost], world, False)
            moveArr.append(ghostMoves)

        return moveArr

    def _findValidMoves(self, coords, world, isPacMan):
        up = [coords[0] - 1, coords[1], 0]
        right = [coords[0], coords[1] + 1, 1]
        down = [coords[0] + 1, coords[1], 2]
        left = [coords[0], coords[1] - 1, 3]

        moves = [up, right, down, left]
        validMoves = []
        for move in moves:
            if move[0] < 0 or move[0] > world.height - 1:
                continue
            if move[1] < 0 or move[1] > world.width - 1:
                continue
            if world.map[move[0]][move[1]] == "#":
                continue
            validMoves.append(move)

        # Holding is always valid
        if isPacMan:
            validMoves.append([coords[0], coords[1], 4])

        return validMoves

    def addSnapshot(self, world):
        world.steps.append(self._pacManStep(world.pacManCoords, world.height))
        for ghost in range(3):
            world.steps.append(self._ghostStep(ghost + 1, world.ghostCoords[ghost], world.height))
        if world.outputFruit:
            world.steps.append(self._fruitStep(world.fruitCoords, world.height))
            world.outputFruit = False
        world.steps.append(self._timeStep(world.time, world.score))


class World:
    def __init__(self, width, height, map_):
        self.width = width
        self.height = height
        self.map = map_
        self.wallCoords = []
        self.pillCoords = []
        self.totalPills = 0
        self.pillsEaten = 0
        self.ghostCoords = []
        self.pacManCoords = []
        self.fruitCoords = []
        self.fruitScore = 0
        self.steps = []
        self.time = 0
        self.timeStart = 0
        self.score = 0
        self.validMoves = []
        self.outputFruit = False
