REWARD_GOAL = 60
REWARD_COIN = 15
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60


UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [LEFT, RIGHT, UP, DOWN]

class Environment:
    def __init__(self, text):
        self.raw_text = text
        self.reset()
        

    def reset(self):
        self.states = {}
        self.walls = {}
        self.coins = {}
        self.boxes = {}
        lines = self.raw_text.strip().split('\n')

        self.height = len(lines)
        self.width = len(lines[0])
        #print(lines)
        #print(self.height)
        #print(self.width)

        for row in range(self.height):
            for col in range(self.width):
                if lines[row][col] == ".":
                    self.starting_point = (row, col)
                elif lines[row][col] == "*":
                    self.goal = (row, col)
                elif lines[row][col] == "#":
                    self.walls[(row, col)] = lines[row][col]
                    continue
                elif lines[row][col] == "X":
                    continue
                elif lines[row][col] == "$":
                    self.coins[(row, col)] = lines[row][col]
                elif lines[row][col] == "?":
                    self.boxes[(row, col)] = lines[row][col]

                self.states[(row, col)] = lines[row][col]

        print(self.states)
                    
    
    def apply(self, state, action, can_jump):
        #remove down when physique engine enable
        
        if action == UP:
            new_state = (state[0] - 3, state[1])
        elif action == DOWN:
            new_state = (state[0] + 1, state[1])
        if action == LEFT:
            new_state = (state[0], state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0], state[1] + 1)
            
        #if new_state in self.walls:
         #   return state, REWARD_STUCK
        
        if new_state in self.states:
            #calculer la récompense

            #todo verify if working 
            # if action == UP and not can_jump:
            #     reward = REWARD_IMPOSSIBLE
            #     new_state = state


            if self.states[new_state] in ['.']: #debut de carte : pénalité moyenne pour que le joueur bouge
                reward = REWARD_STUCK
            elif self.states[new_state] in ['*']: #fin de carte : grosse récompense
                reward = REWARD_GOAL
            elif self.states[new_state] in ['$']:
                reward = REWARD_COIN
                self.states[new_state] = ' '
            else:
                #can't go back
                if action == LEFT:
                    reward = REWARD_DEFAULT * 2
                else:
                    #normal move
                    reward = REWARD_DEFAULT
        else:
           #Etat impossible: grosse pénalité
           new_state = state
           reward = REWARD_IMPOSSIBLE
        return new_state, reward 