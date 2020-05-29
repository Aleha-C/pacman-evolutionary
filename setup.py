import sys
import configparser
import random
import time

class Setup:
    def __init__(self):
        self.configDict = {}
        try:
            self.configDict["configPath"] = str(sys.argv[1])
        except IndexError:
            print("Please use the format ’./run.sh <configurationfilepath>’")
            sys.exit()

        try:
            verbose = str(sys.argv[2])
            if verbose == "output":
                self.configDict["verbose"] = True
            else:
                self.configDict["verbose"] = False
        except:
            self.configDict["verbose"] = False

        self._readConfigData()
        self._seedRNG()

    def _readConfigData(self):
        cfg = configparser.RawConfigParser()
        cfg.read(self.configDict["configPath"])

        self.configDict["algoType"] = cfg.get("Experiment", "algorithm type")
        self.configDict["numberOfRuns"] = cfg.getint("Experiment", "number of runs")
        self.configDict["numberOfEvals"] = cfg.getint("Experiment", "number of fitness evaluations")
        self.configDict["samplingRate"] = cfg.getint("Experiment", "sampling rate")

        self.configDict["rngType"] = cfg.get("RNG", "type")
        self.configDict["rngSeed"] = cfg.get("RNG", "seed")

        self.configDict["pillDensity"] = cfg.getfloat("World", "pill density")
        self.configDict["fruitSpawnProb"] = cfg.getfloat("World", "fruit spawn probability")
        self.configDict["fruitScore"] = cfg.getfloat("World", "fruit score")
        self.configDict["timeMultiplier"] = cfg.getfloat("World", "time multiplier")

        self.configDict["dMax"] = cfg.getint("General EA Settings", "d max")
        self.configDict["absDMax"] = cfg.getint("General EA Settings", "absolute d max")
        self.configDict["terminationStrat"] = cfg.get("General EA Settings", "termination")
        self.configDict["gensTilTermination"] = cfg.getint("General EA Settings", "generations until convergence")

        self.configDict["pacmanPopulationSize"] = cfg.getint("Pac-Man EA Settings", "population size")
        self.configDict["pacmanOffspringAmount"] = cfg.getint("Pac-Man EA Settings", "offspring pool size")
        self.configDict["pacmanParentSelectionStrat"] = cfg.get("Pac-Man EA Settings", "parent selection")
        self.configDict["pacmanOverSelectionPercent"] = cfg.getfloat("Pac-Man EA Settings", "over-selection top percent")
        self.configDict["pacmanMutationProbability"] = cfg.getfloat("Pac-Man EA Settings", "mutation probability")
        self.configDict["pacmanSurvivalSelectionStrat"] = cfg.get("Pac-Man EA Settings", "survival selection")
        self.configDict["pacmanSurvivalTournamentSize"] = cfg.getint("Pac-Man EA Settings", "tournament size")
        self.configDict["pacmanParsimonyPenaltyCoeff"] = cfg.getfloat("Pac-Man EA Settings", "parsimony pressure penalty coefficient")

        self.configDict["ghostPopulationSize"] = cfg.getint("Ghost EA Settings", "population size")
        self.configDict["ghostOffspringAmount"] = cfg.getint("Ghost EA Settings", "offspring pool size")
        self.configDict["ghostParentSelectionStrat"] = cfg.get("Ghost EA Settings", "parent selection")
        self.configDict["ghostOverSelectionPercent"] = cfg.getfloat("Ghost EA Settings", "over-selection top percent")
        self.configDict["ghostMutationProbability"] = cfg.getfloat("Ghost EA Settings", "mutation probability")
        self.configDict["ghostSurvivalSelectionStrat"] = cfg.get("Ghost EA Settings", "survival selection")
        self.configDict["ghostSurvivalTournamentSize"] = cfg.getint("Ghost EA Settings", "tournament size")
        self.configDict["ghostParsimonyPenaltyCoeff"] = cfg.getfloat("Ghost EA Settings", "parsimony pressure penalty coefficient")

        self.configDict["logPath"] = cfg.get("Files", "log file path")
        self.configDict["pacmanSolutionPath"] = cfg.get("Files", "pac-man solution file path")
        self.configDict["ghostSolutionPath"] = cfg.get("Files", "ghost solution file path")
        self.configDict["highScorePath"] = cfg.get("Files", "high score file path")

    def _seedRNG(self):
        # Seeds the RNG based on user's settings.
        if self.configDict["rngType"] == "seed":
            random.seed(self.configDict["rngSeed"])
        elif self.configDict["rngType"] == "time":
            rngSeed = int(round(time.time() * 1000))
            self.configDict["rngSeed"] = rngSeed
            random.seed(rngSeed)
        else:
            print("Invalid RNG type.")
            sys.exit()