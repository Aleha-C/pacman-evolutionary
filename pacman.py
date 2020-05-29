import random


class PacMan:
    def __init__(self, position, parseTree):
        self.currPos = position
        self.parseTree = parseTree
        self.functionSet = ["+", "-", "*", "/", "RAND"]
        self.terminalSet = ["G", "P", "W", "F", "#.#"]
        self.combinedSet = self.functionSet + self.terminalSet

    def move(self, validMoves, world):
        moveScores = []
        for move in validMoves:
            terminalValues = {
                "G": self._getGhostDistance(world, move),
                "P": self._getPillDistance(world, move),
                "W": self._numAdjacentWall(world, move),
                "F": self._getFruitDistance(world, move)
            }
            moveScores.append(self._calculateValue(self.parseTree, terminalValues))
        best = max(moveScores)
        return validMoves[moveScores.index(best)]

    def _calculateValue(self, node, terminalValues):
        if type(node.value) == float:
            return node.value
        if node.value in terminalValues.keys():
            return terminalValues[node.value]

        left = self._calculateValue(node.leftChild, terminalValues)
        right = self._calculateValue(node.rightChild, terminalValues)
        if node.value == "+":
            return left + right
        elif node.value == "-":
            return left - right
        elif node.value == "*":
            return left * right
        elif node.value == "/":
            if right == 0:
                right += 1
            return left / right
        elif node.value == "RAND":
            return random.randint(min(int(left), int(right)), max(int(left), int(right)))

    def _getPillDistance(self, world, coords):
        nearestDistance = float("inf")
        for pill in world.pillCoords:
            distance = abs(coords[0] - pill[0]) + abs(coords[1] - pill[1])
            if distance < nearestDistance:
                nearestDistance = distance

        return nearestDistance

    def _getGhostDistance(self, world, coords):
        nearestDistance = float("inf")
        for ghost in world.ghostCoords:
            distance = abs(coords[0] - ghost[0]) + abs(coords[1] - ghost[1])
            if distance < nearestDistance:
                nearestDistance = distance

        return nearestDistance

    def _getFruitDistance(self, world, coords):
        if not world.fruitCoords:
            return 0
        distance = abs(coords[0] - world.fruitCoords[0]) + abs(coords[1] - world.fruitCoords[1])
        return distance

    def _numAdjacentWall(self, world, move):
        numberOfWalls = 0
        coords = [move[0], move[1]]
        coordArr = [
            [coords[0] + 1, coords[1]],
            [coords[0] - 1, coords[1]],
            [coords[0], coords[1] + 1],
            [coords[0], coords[1] - 1]
        ]

        for coord in coordArr:
            if coord[0] < 0 or coord[0] > world.height - 1:
                numberOfWalls += 1
                continue
            if coord[1] < 0 or coord[1] > world.width - 1:
                numberOfWalls += 1
                continue
            if coord in world.wallCoords:
                numberOfWalls += 1
                continue

        return numberOfWalls
