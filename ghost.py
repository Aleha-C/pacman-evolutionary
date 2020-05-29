import random
from controller import Controller


class Ghost:
    def __init__(self, position, parseTree):
        self.currPos = position
        self.parseTree = parseTree
        self.functionSet = ["+", "-", "*", "/", "RAND"]
        self.terminalSet = ["M", "G"]
        self.combinedSet = self.functionSet + self.terminalSet

    def move(self, validMoves, world):
        moveScores = []
        for move in validMoves:
            terminalValues = {
                "M": self._getDistanceToPacMan(world, move),
                "G": self._getDistanceToPacMan(world, move)
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

    def _getDistanceToNearestGhost(self, world, coords):
        nearestDistance = float("inf")
        checkCoords = [coords[0], coords[1]]
        for ghost in world.ghostCoords:
            if ghost != checkCoords:
                distance = abs(coords[0] - ghost[0]) + abs(coords[1] - ghost[1])
                if distance < nearestDistance:
                    nearestDistance = distance
        return nearestDistance

    def _getDistanceToPacMan(self, world, coords):
        distance = abs(coords[0] - world.pacManCoords[0]) + abs(coords[1] - world.pacManCoords[1])
        return distance
