import os

class Logger:
    def __init__(self, configDict):
        self.configDict = configDict
        self.logPath = configDict["logPath"]
        self.pacmanSolutionPath = configDict["pacmanSolutionPath"]
        self.ghostSolutionPath = configDict["ghostSolutionPath"]
        self.highScorePath = configDict["highScorePath"]

        self._createLog()

    def _createLog(self):
        if os.path.exists(self.logPath):
            os.remove(self.logPath)
        with open(self.logPath, 'w+') as file:
            file.write("-----Configuration-----")
            file.write("\nExperiment")
            file.write("\n|\tAlgorithm Type: " + str(self.configDict["algoType"]))
            file.write("\n|\tNumber of Runs: " + str(self.configDict["numberOfRuns"]))
            file.write("\n|\tNumber of Evaluations: " + str(self.configDict["numberOfEvals"]))
            file.write("\n|\tSampling Rate: " + str(self.configDict["samplingRate"]))
            file.write("\nWorld")
            file.write("\n|\tPill density: " + str(self.configDict["pillDensity"]))
            file.write("\n|\tFruit spawn probability: " + str(self.configDict["fruitSpawnProb"]))
            file.write("\n|\tFruit score: " + str(self.configDict["fruitScore"]))
            file.write("\n|\tTime multiplier: " + str(self.configDict["timeMultiplier"]))
            file.write("\nRNG")
            file.write("\n|\tType: " + self.configDict["rngType"])
            file.write("\n|\tSeed: " + str(self.configDict["rngSeed"]))
            file.write("\nGeneral EA Settings")
            file.write("\n|\tD Max: " + str(self.configDict["dMax"]))
            file.write("\n|\tTermination: " + str(self.configDict["terminationStrat"]))
            file.write("\n|\tGenerations until Convergence: " + str(self.configDict["gensTilTermination"]))
            file.write("\nPac-Man EA Settings")
            file.write("\n|\tPopulation Size: " + str(self.configDict["pacmanPopulationSize"]))
            file.write("\n|\tOffspring Pool Size: " + str(self.configDict["pacmanOffspringAmount"]))
            file.write("\n|\tParent Selection: " + str(self.configDict["pacmanParentSelectionStrat"]))
            file.write("\n|\tSurvival Selection: " + str(self.configDict["pacmanSurvivalSelectionStrat"]))
            file.write("\n|\tTournament Size: " + str(self.configDict["pacmanSurvivalTournamentSize"]))
            file.write("\n|\tParsimony Pressure Penalty Coefficient: " + str(self.configDict["pacmanParsimonyPenaltyCoeff"]))
            file.write("\nGhost EA Settings")
            file.write("\n|\tPopulation Size: " + str(self.configDict["ghostPopulationSize"]))
            file.write("\n|\tOffspring Pool Size: " + str(self.configDict["ghostOffspringAmount"]))
            file.write("\n|\tParent Selection: " + str(self.configDict["ghostParentSelectionStrat"]))
            file.write("\n|\tSurvival Selection: " + str(self.configDict["ghostSurvivalSelectionStrat"]))
            file.write("\n|\tTournament Size: " + str(self.configDict["ghostSurvivalTournamentSize"]))
            file.write("\n|\tParsimony Pressure Penalty Coefficient: " + str(self.configDict["ghostParsimonyPenaltyCoeff"]))
            file.write("\nFile Paths")
            file.write("\n|\tConfiguration file: " + self.configDict["configPath"])
            file.write("\n|\tLog file: " + self.configDict["logPath"])
            file.write("\n|\tPac-Man Solution file: " + self.configDict["pacmanSolutionPath"])
            file.write("\n|\tGhost Solution file: " + self.configDict["ghostSolutionPath"])
            file.write("\n|\tHigh score file: " + self.configDict["highScorePath"])
            file.write("\n--------------------------------")
            file.write("\n\nResult Log")

    def addRunHeader(self, runNumber):
        if self.configDict["verbose"]:
            print("\nRun " + str(runNumber))
        with open(self.logPath, 'a+') as file:
            file.write("\n\nRun " + str(runNumber))

    def logEvalHighScore(self, evals, score):
        if self.configDict["verbose"]:
            print(str(evals) + "\t" + str(score))
        with open(self.logPath, 'a+') as file:
            file.write("\n" + str(evals) + "\t" + str(score))

    def logGeneration(self, evals, averageFitness, bestFitness):
        if self.configDict["verbose"]:
            print(str(evals) + "\t" + str(round(averageFitness, 2)) + "\t" + str(bestFitness))
        with open(self.logPath, 'a+') as file:
            file.write("\n" + str(evals) + "\t" + str(averageFitness) + "\t" + str(bestFitness))

    def logBestPacManSolution(self, parseTreeString):
        if os.path.exists(self.pacmanSolutionPath):
            os.remove(self.pacmanSolutionPath)
        with open(self.pacmanSolutionPath, 'w+') as file:
            file.write(parseTreeString)

    def logBestGhostSolution(self, parseTreeString):
        if os.path.exists(self.ghostSolutionPath):
            os.remove(self.ghostSolutionPath)
        with open(self.ghostSolutionPath, 'w+') as file:
            file.write(parseTreeString)

    def logBestWorld(self, stepString):
        if os.path.exists(self.highScorePath):
            os.remove(self.highScorePath)
        with open(self.highScorePath, 'w+') as file:
            file.write(stepString)
