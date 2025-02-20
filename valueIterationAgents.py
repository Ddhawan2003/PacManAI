# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            new_vals = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                else:
                    q_values = [self.computeQValueFromValues(state, action)
                                for action in self.mdp.getPossibleActions(state)]
                    new_vals[state] = max(q_values)
            self.values = new_vals


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        q_value = 0
        transitions = self.mdp.getTransitionStatesAndProbs(state, action)
        for next_state, prob in transitions:
            reward = self.mdp.getReward(state, action, next_state)
            q_value += prob * (reward + self.discount * self.getValue(next_state))
        return q_value
        #util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        actions = self.mdp.getPossibleActions(state)
        q_values = [(action, self.computeQValueFromValues(state, action)) for action in actions]
        best_action, _ = max(q_values, key=lambda x: x[1])
        return best_action
        #util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()  # Get all states from MDP
        num_states = len(states)
        for i in range(self.iterations):  # Iterate for the specified number of iterations
            state_i = i % num_states  # Cycle through states using modulo operation
            state = states[state_i]
            if self.mdp.isTerminal(state):
                continue
            else:  # Check if the state is not terminal
                actions = self.mdp.getPossibleActions(state)
                if actions:  # Ensure there are available actions for the state
                    max_val = float('-inf')
                    for action in actions:
                        val = self.computeQValueFromValues(state, action)
                        if val > max_val:
                            max_val = val
                    self.values[state] = max_val

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        predecessors = {s: set() for s in self.mdp.getStates()}
        pq = util.PriorityQueue()

        # Compute predecessors and initialize priority queue
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            else:
                max_q_value = max([self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)])
                diff = abs(self.values[state] - max_q_value)
                pq.update(state, -diff)

                for action in self.mdp.getPossibleActions(state):
                    for next_state, _ in self.mdp.getTransitionStatesAndProbs(state, action):
                        predecessors[next_state].add(state)

        # Perform prioritized sweeping updates
        for i in range(self.iterations):
            if pq.isEmpty():
                break

            state = pq.pop()

            if not self.mdp.isTerminal(state):
                self.values[state] = max([self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)])

            for predecessor in predecessors[state]:
                max_q_value = max([self.computeQValueFromValues(predecessor, action) for action in self.mdp.getPossibleActions(predecessor)])
                diff = abs(self.values[predecessor] - max_q_value)
                if diff > self.theta:
                    pq.update(predecessor, -diff)
