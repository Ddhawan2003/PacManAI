# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        ghost_dist = [manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates]
        closest_ghost_dist = min(ghost_dist) if ghost_dist else float('inf')

        foodList = newFood.asList()
        if foodList:
            food_distances = [manhattanDistance(newPos, food) for food in foodList]
            closeFoodDist = min(food_distances)
        else:
            closeFoodDist = 0
        scoreDiff = successorGameState.getScore() - scoreEvaluationFunction(currentGameState)
        
        for dist in ghost_dist[1:]:
          if dist < closest_ghost_dist:
            closest_ghost_dist = dist
        temp = closest_ghost_dist

        if min(newScaredTimes) != 0:
            temp = -temp*3

        if action == 'Stop':
            return (1/closeFoodDist)
        else:
            return (15 / (closeFoodDist + 1) + 80 / (successorGameState.getNumFood() + 1) + temp / 8 + scoreDiff)

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        num_ghosts = gameState.getNumAgents() - 1

        # Max level function for Pacman
        def max_level(state, depth):
            current_depth = depth + 1
            if state.isWin() or state.isLose() or current_depth == self.depth:
                return self.evaluationFunction(state)
            max_value = float('-inf')
            actions = state.getLegalActions(0)
            for action in actions:
                successor = state.generateSuccessor(0, action)
                max_value = max(max_value, min_level(successor, current_depth, 1))
            return max_value

        # Min level function for ghosts
        def min_level(state, depth, agent_index):
            min_value = float('inf')
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent_index)
            for action in actions:
                successor = state.generateSuccessor(agent_index, action)
                if agent_index == num_ghosts:
                    min_value = min(min_value, max_level(successor, depth))
                else:
                    min_value = min(min_value, min_level(successor, depth, agent_index + 1))
            return min_value

        # Root level action selection
        actions = gameState.getLegalActions(0)
        current_score = float('-inf')
        best_action = ''
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            score = min_level(next_state, 0, 1)
            if score > current_score:
                best_action = action
                current_score = score
        return best_action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        # Max level function for Pacman
        def max_level(state, depth, alpha, beta):
            current_depth = depth + 1
            if state.isWin() or state.isLose() or current_depth == self.depth:
                return self.evaluationFunction(state)
            max_value = float('-inf')
            actions = state.getLegalActions(0)
            for action in actions:
                successor = state.generateSuccessor(0, action)
                max_value = max(max_value, min_level(successor, current_depth, 1, alpha, beta))
                if max_value > beta:
                    return max_value
                alpha = max(alpha, max_value)
            return max_value

        # Min level function for ghosts
        def min_level(state, depth, agent_index, alpha, beta):
            min_value = float('inf')
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent_index)
            for action in actions:
                successor = state.generateSuccessor(agent_index, action)
                if agent_index == (state.getNumAgents() - 1):
                    min_value = min(min_value, max_level(successor, depth, alpha, beta))
                    if min_value < alpha:
                        return min_value
                    beta = min(beta, min_value)
                else:
                    min_value = min(min_value, min_level(successor, depth, agent_index + 1, alpha, beta))
                    if min_value < alpha:
                        return min_value
                    beta = min(beta, min_value)
            return min_value

        # Root level action selection with alpha-beta pruning
        actions = gameState.getLegalActions(0)
        current_score = float('-inf')
        best_action = ''
        alpha = float('-inf')
        beta = float('inf')
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            score = min_level(next_state, 0, 1, alpha, beta)
            if score > current_score:
                best_action = action
                current_score = score
            if score > beta:
                return best_action
            alpha = max(alpha, score)
        return best_action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        # Max level function for Pacman
        def max_level(state, depth):
            current_depth = depth + 1
            if state.isWin() or state.isLose() or current_depth == self.depth:
                return self.evaluationFunction(state)
            max_value = float('-inf')
            actions = state.getLegalActions(0)
            for action in actions:
                successor = state.generateSuccessor(0, action)
                max_value = max(max_value, expect_level(successor, current_depth, 1))
            return max_value

        # Expect level function for ghosts
        def expect_level(state, depth, agent_index):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent_index)
            total_expected_value = 0
            number_of_actions = len(actions)
            for action in actions:
                successor = state.generateSuccessor(agent_index, action)
                if agent_index == (state.getNumAgents() - 1):
                    expected_value = max_level(successor, depth)
                else:
                    expected_value = expect_level(successor, depth, agent_index + 1)
                total_expected_value += expected_value
            if number_of_actions == 0:
                return 0
            return total_expected_value / number_of_actions

        # Root level action selection
        actions = gameState.getLegalActions(0)
        current_score = float('-inf')
        best_action = ''
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            score = expect_level(next_state, 0, 1)
            if score > current_score:
                best_action = action
                current_score = score
        return best_action


def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: This function evaluates the current game state based on factors
    such as distance to food, distance to ghosts, number of power pellets, and
    current score. It aims to guide Pacman towards winning strategies by
    prioritizing actions that lead to eating food, avoiding ghosts, consuming
    power pellets, and maximizing the score.
    """
    "*** YOUR CODE HERE ***"
    # Extract necessary information from the game state
    new_pos = currentGameState.getPacmanPosition()
    new_food = currentGameState.getFood()
    new_ghost_states = currentGameState.getGhostStates()
    new_scared_times = [ghost_state.scaredTimer for ghost_state in new_ghost_states]

    # Calculate Manhattan distance to each food from the current state
    food_list = new_food.asList()
    from util import manhattanDistance
    food_distances = [manhattanDistance(new_pos, food_pos) for food_pos in food_list]

    # Calculate Manhattan distance to each ghost from the current state
    ghost_positions = [ghost_state.getPosition() for ghost_state in new_ghost_states]
    ghost_distances = [manhattanDistance(new_pos, ghost_pos) for ghost_pos in ghost_positions]

    number_of_power_pellets = len(currentGameState.getCapsules())
    current_score = currentGameState.getScore()
    number_of_no_foods = len(food_list)
    sum_scared_times = sum(new_scared_times)
    sum_ghost_distance = sum(ghost_distances)

    reciprocal_food_distance = 0
    if sum(food_distances) > 0:
        reciprocal_food_distance = 1.0 / sum(food_distances)

    score = current_score + reciprocal_food_distance + number_of_no_foods

    if sum_scared_times > 0:
        score += sum_scared_times - number_of_power_pellets - sum_ghost_distance
    else:
        score += sum_ghost_distance + number_of_power_pellets
    return score

# Abbreviation
better = betterEvaluationFunction
