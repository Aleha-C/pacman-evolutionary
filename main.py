from setup import Setup
from log import Logger
from engine import GameEngine
from evolution import EvolutionEngine
from evolution import Individual
import random


def main():
    setup = Setup()
    if setup.configDict["verbose"]:
        print("Running Experiment...")
    if setup.configDict["algoType"] == "random search":
        print("Random Search no longer supported.")
    elif setup.configDict["algoType"] == "ea":
        ea(setup.configDict)
    else:
        print("Invalid algorithm type. Please review the configuration file and README.")


def ea(configDict):
    # Load all configurations and store them for easy access.
    log = Logger(configDict)
    highScore = float("-inf")
    for run in range(configDict["numberOfRuns"]):
        log.addRunHeader(run + 1)
        evolutionEngine = EvolutionEngine(configDict, log)
        evolutionEngine.evolve()

        bestPacMan = None
        for pacman in evolutionEngine.pacmanPopulation:
            if not bestPacMan:
                bestPacMan = pacman
                continue
            if pacman.fitness > bestPacMan.fitness:
                bestPacMan = pacman

        bestGhost = None
        for ghost in evolutionEngine.ghostPopulation:
            if not bestGhost:
                bestGhost = ghost
                continue
            if ghost.fitness > bestGhost.fitness:
                bestGhost = ghost

        engine = GameEngine(configDict, bestPacMan.parseTree, bestGhost.parseTree)
        engine.runGame()
        if configDict["verbose"]:
            print("Exhibition Score:", engine.score)
        if engine.score > highScore:
            highScore = engine.score
            log.logBestWorld("\n".join(engine.world.steps))
            pacManArray = [arr[1] for arr in bestPacMan.solutionArray]
            log.logBestPacManSolution("\n".join(pacManArray))
            ghostArray = [arr[1] for arr in bestGhost.solutionArray]
            log.logBestGhostSolution("\n".join(ghostArray))


if __name__ == "__main__":
    main()
