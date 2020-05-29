import copy
import math
from engine import GameEngine
from controller import Controller
from controller import ParseTreeNode
from log import Logger
import random


class Individual:
    def __init__(self, solutionArray, parseTree, treeDepth, type):
        self.type = type
        self.solutionArray = solutionArray
        self.parseTree = parseTree
        self.treeDepth = treeDepth
        self.worldSteps = []
        self.fitness = 0
        self.fitnessRecords = []

    def updateFitness(self, newFitness):
        self.fitnessRecords.append(newFitness)
        self.fitness = sum(self.fitnessRecords) / len(self.fitnessRecords)


class EvolutionEngine:
    def __init__(self, configDict, log):
        self.configDict = configDict
        self.log = log
        self.bestPacMan = None
        self.bestGhost = None
        self.pacmanPopulation = []
        self.ghostPopulation = []
        self.controllerCreator = Controller(configDict["dMax"], configDict["absDMax"])
        self.totalEvals = self.configDict["numberOfEvals"]
        self.evalsCompleted = 0

    def evolve(self):
        self._initializePopulation()
        self._updateLogs()
        endOfRun = self._runWillTerminate()
        while not endOfRun:
            pacManOffspring = self._nextGenerationOffspring("pac-men")
            ghostOffspring = self._nextGenerationOffspring("ghosts")
            pacManOffspring, ghostOffspring = self._fitnessEvaluations(pacManOffspring, ghostOffspring)
            self._survival("pac-men", pacManOffspring)
            self._survival("ghosts", ghostOffspring)
            self._updateLogs()
            endOfRun = self._runWillTerminate()

    def _nextGenerationOffspring(self, populationType):
        parents = self._selectParents(populationType)
        offspring = self._createOffspring(parents)
        return offspring

    def _fitnessEvaluations(self, pacmen, ghosts):
        totalGames = max(len(pacmen), len(ghosts))
        pacManNumber = 0
        ghostNumber = 0
        for evaluation in range(totalGames):
            pacMan = None
            ghost = None
            if pacManNumber > len(pacmen) -1 :
                pacManNumber = 0
            if ghostNumber > len(ghosts) - 1:
                ghostNumber = 0
            pacMan = pacmen[pacManNumber]
            ghost = ghosts[ghostNumber]

            engine = GameEngine(self.configDict, pacMan.parseTree, ghost.parseTree)
            engine.runGame()
            pacMan, ghost = self._evaluateFitness(engine, pacMan, ghost)
            pacmen[pacManNumber] = pacMan
            ghosts[ghostNumber] = ghost

            pacManNumber += 1
            ghostNumber += 1

        return pacmen, ghosts


    def _survival(self, populationType, population):
        survivors = self._selectSurvivors(population, populationType)
        if populationType == "pac-men":
            self.pacmanPopulation = survivors
        else:
            self.ghostPopulation = survivors


    def _updateLogs(self):
        totalFitness = 0
        best = float("-inf")
        for individual in self.pacmanPopulation:
            totalFitness += individual.fitness
            if individual.fitness > best:
                best = individual.fitness
        averageFitness = totalFitness / len(self.pacmanPopulation)

        self.log.logGeneration(self.evalsCompleted, averageFitness, best)

    def _initializePopulation(self):
        newPacMen = []
        numberOfPacMen = self.configDict["pacmanPopulationSize"]
        if self.totalEvals < numberOfPacMen:
            numberOfPacMen = self.totalEvals
        newGhosts = []
        numberOfGhosts = self.configDict["ghostPopulationSize"]
        if self.totalEvals < numberOfGhosts:
            numberOfGhosts = self.totalEvals

        totalGames = max(numberOfPacMen, numberOfGhosts)
        for evaluation in range(totalGames):
            pacMan = None
            ghost = None
            # Random number passed to _generateSolution implements ramped half and half.
            if numberOfPacMen > 0:
                pacMan = self._generateSolution("pac-man", random.randint(0, 1))
                numberOfPacMen -= 1
            if numberOfGhosts > 0:
                ghost = self._generateSolution("ghost", random.randint(0, 1))
                numberOfGhosts -= 1

            reusedPacManInd = -1
            reusedGhostInd = -1
            if not pacMan:
                reusedPacManInd = random.randint(0, len(newPacMen)-1)
                pacMan = newPacMen[reusedPacManInd]
            elif not ghost:
                reusedGhostInd = random.randint(0, len(newGhosts)-1)
                ghost = newGhosts[reusedGhostInd]

            engine = GameEngine(self.configDict, pacMan.parseTree, ghost.parseTree)
            engine.runGame()
            pacMan, ghost = self._evaluateFitness(engine, pacMan, ghost)\

            if reusedPacManInd != -1:
                newPacMen[reusedPacManInd] = pacMan
            else:
                newPacMen.append(pacMan)

            if reusedGhostInd != -1:
                newGhosts[reusedGhostInd] = ghost
            else:
                newGhosts.append(ghost)

        self.pacmanPopulation = newPacMen
        self.ghostPopulation = newGhosts

    def _selectParents(self, populationType):
        selectionStratDict = {
            "pac-men": self.configDict["pacmanParentSelectionStrat"],
            "ghosts": self.configDict["ghostParentSelectionStrat"]
        }
        parents = []
        if selectionStratDict[populationType] == "fitness proportional":
            fitnessProportions = self._calculateFitnessProportions(populationType)
            parents = self._fitnessProportionalParentSelection(populationType, fitnessProportions)
        else:
            rankings = self._calculateRankings(populationType)
            parents = self._parentOverSelection(populationType, rankings)

        return parents

    def _fitnessProportionalParentSelection(self, populationType, proportions):
        populationDict = {
            "pac-men": self.pacmanPopulation,
            "ghosts": self.ghostPopulation
        }
        offspringAmountDict = {
            "pac-men": self.configDict["pacmanOffspringAmount"],
            "ghosts": self.configDict["ghostOffspringAmount"]
        }
        mutationProbabilityDict = {
            "pac-men": self.configDict["pacmanMutationProbability"],
            "ghosts": self.configDict["ghostMutationProbability"]
        }
        population = populationDict[populationType]
        offspringAmount = offspringAmountDict[populationType]
        if offspringAmount > self.totalEvals - self.evalsCompleted:
            offspringAmount = self.totalEvals - self.evalsCompleted
        mutationProbability = mutationProbabilityDict[populationType]

        allParents = []
        for child in range(offspringAmount):
            mutationProb = random.uniform(0, 1)
            parentProbs = [random.uniform(0, proportions[-1])]
            # If not mutating, add second parent for recombination.
            if mutationProb > mutationProbability:
                parentProbs.append(random.uniform(0, proportions[-1]))
            parents = []
            foundParent1 = False
            foundParent2 = False
            if len(parentProbs) == 1:
                foundParent2 = True
            for individual in range(len(proportions)):
                if not foundParent1 and parentProbs[0] <= proportions[individual]:
                    parents.append(population[individual])
                    foundParent1 = True
                if not foundParent2 and parentProbs[1] <= proportions[individual]:
                    parents.append(population[individual])
                    foundParent2 = True
                if foundParent1 and foundParent2:
                    break
            allParents.append(parents)

        return allParents

    def _calculateFitnessProportions(self, populationType):
        population = self.pacmanPopulation
        if populationType == "ghosts":
            population = self.ghostPopulation

        proportions = []
        totalFitness = 0
        for individual in population:
            totalFitness += individual.fitness

        currPercent = 0
        for individual in population:
            percent = individual.fitness / totalFitness
            currPercent += percent
            proportions.append(currPercent)

        return proportions

    def _parentOverSelection(self, populationType, rankings):
        populationDict = {
            "pac-men": self.pacmanPopulation,
            "ghosts": self.ghostPopulation
        }
        offspringAmountDict = {
            "pac-men": self.configDict["pacmanOffspringAmount"],
            "ghosts": self.configDict["ghostOffspringAmount"]
        }
        mutationProbabilityDict = {
            "pac-men": self.configDict["pacmanMutationProbability"],
            "ghosts": self.configDict["ghostMutationProbability"]
        }
        population = populationDict[populationType]
        offspringAmount = offspringAmountDict[populationType]
        if offspringAmount > self.totalEvals - self.evalsCompleted:
            offspringAmount = self.totalEvals - self.evalsCompleted
        mutationProbability = mutationProbabilityDict[populationType]

        parents = []
        topIndices = [rank[0] for rank in list(filter(lambda rank: rank[1], rankings))]
        bottomIndices = [rank[0] for rank in list(filter(lambda rank: not rank[1], rankings))]
        for child in range(offspringAmount):
            mutationProb = random.uniform(0, 1)
            parentProbs = [random.randint(1, 100)]
            if mutationProb > mutationProbability:
                parentProbs.append(random.randint(1, 100))
            selection = []
            for parent in parentProbs:
                choice = -1
                if parent <= 20:
                    choice = bottomIndices[random.randint(0, len(bottomIndices) - 1)]
                else:
                    choice = topIndices[random.randint(0, len(topIndices) - 1)]
                selection.append(population[choice])
            parents.append(selection)

        return parents

    def _calculateRankings(self, populationType):
        overSelectionDict = {
            "pac-men": self.configDict["pacmanOverSelectionPercent"],
            "ghosts": self.configDict["ghostOverSelectionPercent"]
        }
        overSelectionPercent = overSelectionDict[populationType]
        population = self.pacmanPopulation
        if populationType == "ghosts":
            population = self.ghostPopulation

        rankings = [False] * len(population)
        topPercent = overSelectionPercent
        numberInTop = math.ceil(len(population) * topPercent)
        indivIndexList = [[index, individual.fitness] for index, individual in enumerate(population)]
        fitnessSorted = sorted(indivIndexList, key=lambda x: x[1], reverse=True)
        for top in range(numberInTop):
            index = fitnessSorted[top][0]
            rankings[index] = True
        return [[index, inTop] for index, inTop in enumerate(rankings)]

    def _createOffspring(self, parents):
        offspring = []
        for parent in parents:
            child = None
            childArray = []
            if len(parent) == 2:
                child, childArray = self._recombine(copy.deepcopy(parent))
            else:
                child, childArray = self._mutateIndividual(copy.deepcopy(parent[0].solutionArray), parent[0].type)

            depths = [entry[0] for entry in childArray]
            newChild = Individual(childArray, child, max(depths), parent[0].type)
            offspring.append(newChild)
            if self._runWillTerminate():
                break
        return offspring

    def _recombine(self, parents):
        childTree, childTreeArray = self._subTreeCrossover(parents[0].solutionArray, parents[1].solutionArray)
        return childTree, childTreeArray

    def _subTreeCrossover(self, tree1, tree2):
        trees = [tree1, tree2]
        baseChoice = random.randint(0, 1)
        replaceChoice = 1 - baseChoice
        baseTree = trees[baseChoice]
        replaceTree = trees[replaceChoice]
        replaceTreeStart = random.randint(0, len(replaceTree) - 1)
        replaceTreeStartDepth = replaceTree[replaceTreeStart][0]

        root = replaceTree[replaceTreeStart].copy()
        root[1] = root[1][root[0]:]
        root[0] = root[0] - replaceTreeStartDepth
        addTree = [root]
        for node in range(replaceTreeStart+1, len(replaceTree)):
            check = replaceTree[node].copy()
            if check[0] <= replaceTreeStartDepth:
                break
            else:
                check[1] = check[1][check[0]:]
                check[0] = check[0] - replaceTreeStartDepth
                addTree.append(check)

        baseTreeStart = random.randint(0, len(baseTree) - 1)
        baseTreeStartDepth = baseTree[baseTreeStart][0]
        baseTreeEnd = len(baseTree)
        for node in range(baseTreeStart+1, len(baseTree)):
            check = baseTree[node]
            if check[0] <= baseTreeStartDepth:
                baseTreeEnd = node
                break
        for node in range(len(addTree)):
            branches = "|" * (baseTreeStartDepth + addTree[node][0])
            addTree[node][0] = baseTreeStartDepth + addTree[node][0]
            addTree[node][1] = branches + addTree[node][1]

        newSolution = baseTree[:baseTreeStart] + addTree + baseTree[baseTreeEnd:]
        newSolutionTrimmed = self._trimTree(newSolution)
        #print("---Base Tree---")
        #print(trees[baseChoice])
        #print("Insert point: ", baseTreeStart)
        #print("End Point: ", baseTreeEnd)
        #print("---Top---")
        #print("\n".join([x[1] for x in baseTree[:baseTreeStart]]))
        #print("---Crossover Tree---")
        #print("\n".join([x[1] for x in addTree]))
        #print("---Bottom---")
        #print("\n".join([x[1] for x in baseTree[baseTreeEnd+1:]]))
        #print("---Final Tree---")
        #print("\n".join([x[1] for x in newSolution]))
        newTree = self._arrayToTree(copy.deepcopy(newSolutionTrimmed))
        return newTree, newSolutionTrimmed

    def _trimTree(self, treeArray):
        functionSet = ["+", "-", "*", "/", "RAND"]
        maxDepth = self.configDict["absDMax"]
        treeIsValid = True
        outOfBoundsNodes = list(filter(lambda x: x > maxDepth, [node[0] for node in treeArray]))
        if len(outOfBoundsNodes) != 0:
            treeIsValid = False
        while not treeIsValid:
            invalidRoot = -1
            for n in range(len(treeArray)):
                node = treeArray[n]
                if node[0] == maxDepth and node[1][node[0]:] in functionSet:
                    invalidRoot = n
                    break

            termNodeIndex = len(treeArray) - 1
            for n in range(invalidRoot+1, len(treeArray)):
                if treeArray[n][0] <= maxDepth:
                    termNodeIndex = n - 1
                    break
            termNode = treeArray[termNodeIndex].copy()
            termNode[1] = ("|" * maxDepth) + termNode[1][termNode[0]:]
            termNode[0] = maxDepth
            treeArray[invalidRoot] = termNode
            treeArray = treeArray[:invalidRoot+1] + treeArray[termNodeIndex+1:]
            outOfBoundsNodes = list(filter(lambda x: x > maxDepth, [node[0] for node in treeArray]))
            if len(outOfBoundsNodes) == 0:
                treeIsValid = True
        return treeArray

    def _arrayToTree(self, treeArray):
        for node in range(len(treeArray)):
            treeArray[node][1] = treeArray[node][1][treeArray[node][0]:]
        root = self._initTree(treeArray)
        return root

    def _initTree(self, treeArray):
        rootVal = treeArray[0][1]
        if "." in rootVal:
            rootVal = float(rootVal)
        node = ParseTreeNode(rootVal)
        childDepth = treeArray[0][0] + 1
        del treeArray[0]
        if treeArray:
            leftChildStart = 0
            rightChildStart = -1
            for child in range(1, len(treeArray)):
                if treeArray[child][0] == childDepth:
                    rightChildStart = child
                    break
            leftChild = treeArray[:rightChildStart]
            rightChild = treeArray[rightChildStart:]
            node.leftChild = self._initTree(leftChild)
            node.rightChild = self._initTree(rightChild)

        return node

    def _mutateIndividual(self, parent, solutionType):
        baseTree = parent.copy()
        mutationPoint = random.randint(0, len(baseTree) - 1)
        mutationPointDepth = baseTree[mutationPoint][0]

        mutationEndPoint = len(baseTree)
        for node in range(mutationPoint + 1, len(baseTree)):
            if baseTree[node][0] <= mutationPointDepth:
                mutationEndPoint = node
                break

        rootNode, depth, mutationTree = self.controllerCreator.createController(solutionType, False)
        for node in range(len(mutationTree)):
            value = mutationTree[node][1][mutationTree[node][0]:]
            mutationTree[node][0] = mutationTree[node][0] + mutationPointDepth
            mutationTree[node][1] = ("|" * mutationTree[node][0]) + value

        #print(baseTree[:mutationPoint])
        #print("---")
        #print(baseTree[mutationEndPoint:])
        mutatedSolution = baseTree[:mutationPoint] + mutationTree + baseTree[mutationEndPoint:]
        #print("---Base Tree---")
        #print("\n".join([x[1] for x in baseTree]))
        #print("Mutation Point: ", mutationPoint)
        #print("Mutation End Point: ", mutationEndPoint)
        #print("Mutation Point Value: ", baseTree[mutationPoint])
        #print("---Mutation Tree---")
        #print("\n".join([x[1] for x in mutationTree]))
        #print("---Result Tree---")
        #print("\n".join([x[1] for x in mutatedSolution]))
        mutatedSolutionTrimmed = self._trimTree(mutatedSolution)
        mutatedTree = self._arrayToTree(copy.deepcopy(mutatedSolutionTrimmed))
        return mutatedTree, mutatedSolutionTrimmed

    def _generateSolution(self, solutionType, fullMethod):
        rootNode, treeDepth, treeArray = self.controllerCreator.createController(solutionType, fullMethod)
        individual = Individual(treeArray, rootNode, treeDepth, solutionType)
        return individual

    def _evaluateFitness(self, engine, pacMan, ghost):
        self.evalsCompleted += 1
        score = engine.score
        timePercentRemaining = (engine.world.time / engine.world.timeStart) * 100
        pillsPercentRemaining = ((engine.world.totalPills - engine.world.pillsEaten) / engine.world.totalPills) * 100

        pacManFitness = score - (self.configDict["pacmanParsimonyPenaltyCoeff"] * pacMan.treeDepth)
        pacMan.updateFitness(pacManFitness)
        ghostFitness = timePercentRemaining + pillsPercentRemaining - (self.configDict["ghostParsimonyPenaltyCoeff"] * ghost.treeDepth)
        ghost.updateFitness(ghostFitness)
        if self.configDict["verbose"]:
            print("Eval #" + str(self.evalsCompleted))
            print("|\tPac-Man Fitness: " + str(pacManFitness))
            print("|\tGhost Fitness: " + str(ghostFitness))
        return pacMan, ghost

    def _selectSurvivors(self, offspring, populationType):
        survivors = []

        populationDict = {
            "pac-men": self.pacmanPopulation,
            "ghosts": self.ghostPopulation
        }
        selectionPool = populationDict[populationType] + offspring
        selectionStratDict = {
            "pac-men": self.configDict["pacmanSurvivalSelectionStrat"],
            "ghosts": self.configDict["ghostSurvivalSelectionStrat"]
        }
        if selectionStratDict[populationType] == "truncation":
            survivors = self._truncationSurvivalSelection(selectionPool, populationType)
        else:
            survivors = self._kTournamentSurvivalSelection(selectionPool, populationType)
        random.shuffle(survivors)
        return survivors

    def _truncationSurvivalSelection(self, population, populationType):
        populationSizeDict = {
            "pac-men": self.configDict["pacmanPopulationSize"],
            "ghosts": self.configDict["ghostPopulationSize"]
        }
        fitnessEnum = [[index, individual.fitness] for index, individual in enumerate(population)]
        fitnessSorted = sorted(fitnessEnum, key=lambda x: x[1], reverse=True)
        survivorIndices = [individual[0] for individual in fitnessSorted[:populationSizeDict[populationType]]]
        survivors = [population[survivor] for survivor in survivorIndices]
        return survivors

    def _kTournamentSurvivalSelection(self, population, populationType):
        populationSizeDict = {
            "pac-men": self.configDict["pacmanPopulationSize"],
            "ghosts": self.configDict["ghostPopulationSize"]
        }
        tournamentSizeDict = {
            "pac-men": self.configDict["pacmanSurvivalTournamentSize"],
            "ghosts": self.configDict["ghostSurvivalTournamentSize"]
        }
        survivors = []
        selectionPopulation = population.copy()
        for survivor in range(populationSizeDict[populationType]):
            survivorIndex = self._kTournament(tournamentSizeDict[populationType], selectionPopulation)
            survivors.append(selectionPopulation[survivorIndex])
            del selectionPopulation[survivorIndex]

        return survivors

    def _kTournament(self, k, population):
        survivorIndex = -1
        if k > len(population):
            k = len(population)

        competitorIndices = []
        for competitors in range(k):
            choice = random.randint(0, len(population)-1)
            while choice in competitorIndices:
                choice = random.randint(0, len(population) - 1)
            competitorIndices.append(choice)

        competitorFitnesses = [[index, population[index].fitness] for index in competitorIndices]
        winner = sorted(competitorFitnesses, key=lambda x: x[1])[-1]
        survivorIndex = winner[0]

        return survivorIndex

    def _runWillTerminate(self):
        if self.evalsCompleted == self.totalEvals:
            return True
        else:
            return False
