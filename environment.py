REWARD_GOAL = 60
REWARD_COIN = 15
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60


UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [UP, LEFT, RIGHT]

class Environment:
    def __init__(self, text):
        self.states = {}
        self.walls = {}
        self.coins = {}
        self.boxes = {}
        lines = text.strip().split('\n')

        self.height = len(lines)
        self.width = len(lines[0])
        print(lines)
        print(self.height)
        print(self.width)

        for row in range(self.height):
            for col in range(self.width):
                self.states[(row, col)] = lines[row][col]
                if lines[row][col] == ".":
                    self.starting_point = (row, col)
                elif lines[row][col] == "*":
                    self.goal = (row, col)
                elif lines[row][col] == "#":
                    self.walls[(row, col)] = lines[row][col]
                elif lines[row][col] == "$":
                    self.coins[(row, col)] = lines[row][col]
                elif lines[row][col] == "?":
                    self.boxes[(row, col)] = lines[row][col]


        print(self.states)
                    
    
    def apply(self, state, action):
        if action == UP:
            new_state = (state[0] - 1, state[1])
        #elif action == DOWN:
        #    new_state = (state[0] + 1, state[1])
        elif action == LEFT:
            new_state = (state[0], state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0], state[1] + 1)
            
        if new_state in self.walls:
            return state, 0
        
        if new_state in self.states:
            #calculer la récompense
            if self.states[new_state] in ['.']:
                reward = REWARD_STUCK
            elif self.states[new_state] in ['*']: #Sortie du labyrinthe : grosse récompense
                reward = REWARD_GOAL
            elif self.states[new_state] in ['$']:
                reward = REWARD_COIN
            # if self.states[new_state] in ['#']:
            #     reward = REWARD_IMPOSSIBLE
            else:
                reward = REWARD_DEFAULT
        else:
           #Etat impossible: grosse pénalité
           new_state = state
           reward = REWARD_IMPOSSIBLE

        return new_state, reward 