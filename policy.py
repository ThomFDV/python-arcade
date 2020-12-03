DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.5

class Policy: #Q-table
    def __init__(self, states, actions,
                 learning_rate = DEFAULT_LEARNING_RATE,
                 discount_factor = DEFAULT_DISCOUNT_FACTOR):
        self.table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        for s in states:
            self.table[s] = {}
            for a in actions:
                self.table[s][a] = 0

    def __repr__(self):
        res = ''
        for state in self.table:
            res += f'{state}\t{self.table[state]}\n'
        return res

    def best_action(self, state):
        action = None
        for a in self.table[state]:
            if action is None or self.table[state][a] > self.table[state][action]:
                action = a
        return action

    def update(self, previous_state, state, last_action, reward):
        #Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        maxQ = max(self.table[state].values())
        self.table[previous_state][last_action] += self.learning_rate * \
            (reward + self.discount_factor * maxQ - self.table[previous_state][last_action])