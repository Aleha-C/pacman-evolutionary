import random


class ParseTreeNode:
    def __init__(self, value):
        self.value = value
        self.leftChild = None
        self.rightChild = None

        if value == "#.#":
            self.value = random.uniform(0, 25)


class Controller:
    def __init__(self, dMax, absoluteDMax):
        self.functionSet = ["+", "-", "*", "/", "RAND"]
        self.terminalSetDict = {
            "pac-man": ["G", "P", "W", "F", "#.#"],
            "ghost": ["M", "G"]
        }
        self.combinedSetDict = {
            "pac-man": self.functionSet + self.terminalSetDict["pac-man"],
            "ghost": self.functionSet + self.terminalSetDict["ghost"]
        }
        self.dMax = dMax
        self.absDMax = absoluteDMax

    def createController(self, controllerType, fullMethod):
        rootNode = None
        if fullMethod == 1:
            rootNode, depth, treeArray = self._initFullParseTree(0, controllerType)
        else:
            rootNode, depth, treeArray = self._initGrowParseTree(0, controllerType)

        treeArrayEnum = [[node.count("|"), node] for node in treeArray]
        return rootNode, depth, treeArrayEnum

    def _initFullParseTree(self, depth, controllerType):
        node = None
        if depth == self.dMax:
            value = random.randint(0, len(self.terminalSetDict[controllerType]) - 1)
            node = ParseTreeNode(self.terminalSetDict[controllerType][value])
            nodeString = ("|" * depth) + str(node.value)
            newControllerArray = [nodeString]
            return node, depth, newControllerArray
        else:
            value = random.randint(0, len(self.functionSet) - 1)
            node = ParseTreeNode(self.functionSet[value])
            rootNodeString = ("|" * depth) + node.value
            node.leftChild, leftDepth, leftNodeArray = self._initFullParseTree(depth + 1, controllerType)
            node.rightChild, rightDepth, rightNodeArray = self._initFullParseTree(depth + 1, controllerType)

            newControllerArray = [rootNodeString] + leftNodeArray + rightNodeArray
            return node, leftDepth, newControllerArray

    def _initGrowParseTree(self, depth, controllerType):
        node = None
        if depth == self.dMax:
            value = random.randint(0, len(self.terminalSetDict[controllerType]) - 1)
            node = ParseTreeNode(self.terminalSetDict[controllerType][value])
        else:
            value = random.randint(0, len(self.combinedSetDict[controllerType]) - 1)
            node = ParseTreeNode(self.combinedSetDict[controllerType][value])

        if node.value in self.terminalSetDict[controllerType] or type(node.value) == float:
            nodeString = ("|" * depth) + str(node.value)
            newControllerArray = [nodeString]
            return node, depth, newControllerArray
        else:
            rootNodeString = ("|" * depth) + node.value
            node.leftChild, leftDepth, leftNodeArray = self._initGrowParseTree(depth+1, controllerType)
            node.rightChild, rightDepth, rightNodeArray = self._initGrowParseTree(depth+1, controllerType)
            newControllerArray = [rootNodeString] + leftNodeArray + rightNodeArray
            return node, max(leftDepth, rightDepth), newControllerArray
