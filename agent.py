
from policy import Policy
from environment import ACTIONS

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.reset()
        self.policy = Policy(environment.states.keys(), ACTIONS)
    
    def reset(self):
        self.state = self.environment.starting_point
        self.previous_state = self.state
        self.score = 0
    
    def best_action(self):
        return self.policy.best_action(self.state)

    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward = self.environment.apply(self.state, action)
        self.score += self.reward
        self.last_action = action
    
    def update_policy(self):
        self.policy.update(self.previous_state, self.state, self.last_action, self.reward)