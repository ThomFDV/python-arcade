import numpy as np
from sklearn.neural_network import MLPRegressor

DEFAULT_LEARNING_RATE = 1e-4
DEFAULT_DISCOUNT_FACTOR = 0.95

LEFT, RIGHT, JUMP = 'L', 'R', 'J'
ACTIONS = [LEFT, RIGHT, JUMP]

NOISE_INIT = 2
NOISE_DECAY = 0.99


class Policy:  # ANN
    def __init__(self, actions, width, height,
                 learning_rate=DEFAULT_LEARNING_RATE,
                 discount_factor=DEFAULT_DISCOUNT_FACTOR):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.actions = actions
        self.maxX = width
        self.maxY = height

        self.mlp = MLPRegressor(hidden_layer_sizes=(100,),
                                activation='tanh',
                                solver='adam',
                                learning_rate_init=self.learning_rate,
                                max_iter=1,
                                warm_start=True)
        self.mlp.fit([[0, 0]], [[0, 0, 0]])
        self.q_vector = None
        self.noise = NOISE_INIT

    def __repr__(self):
        return self.q_vector

    def state_to_dataset(self, state):
        return np.array([[state[0] / self.maxX, state[1] / self.maxY]])

    def best_action(self, state):
        self.q_vector = self.mlp.predict(self.state_to_dataset(state))[0]  # Le RN fournit un vecteur de probabilité
        print(self.q_vector)
        self.noise *= NOISE_DECAY
        self.q_vector += np.random.rand(len(self.q_vector)) * self.noise
        print(self.q_vector)
        action = self.actions[np.argmax(self.q_vector)]  # On choisit l'action la plus probable
        return action

    def update(self, previous_state, state, last_action, reward):
        # Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        # Mettre le réseau de neurone à jour, au lieu de la table
        maxQ = np.amax(self.q_vector)
        last_action = ACTIONS.index(last_action)
        self.q_vector[last_action] = reward + self.discount_factor * maxQ
        inputs = [state]
        outputs = [self.q_vector]
        # print(inputs, outputs)
        self.mlp.fit(inputs, outputs)
