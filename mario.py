import arcade

#Q-table
# U L R

MARIO = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
X          $               X
X    #   #?#?#             X
X                          X
X                      $   X
X.                        *X
X##########################X
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

SPRITE_SIZE = 64

REWARD_GOAL = 60
REWARD_COIN = 30
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60

DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.5

UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [UP, DOWN, LEFT, RIGHT]


# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Mariozi2D"

CHARACTER_SCALING = 0.66
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 23

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100


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
                    
    
    def apply(self, state, action):
        if action == UP:
            new_state = (state[0] - 1, state[1])
        elif action == DOWN:
            new_state = (state[0] + 1, state[1])
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

class MarioWindow(arcade.Window):
    def __init__(self, agent):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.agent = agent

        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.box_list = None
        
        self.player_sprite = None

        self.physique_engine = None

        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.end_of_map = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
    
    def setup(self): 
        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()


        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", CHARACTER_SCALING)
        self.player_sprite.center_x = self.agent.environment.starting_point[1] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
        self.player_sprite.center_y = self.height - self.agent.environment.starting_point[0] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
        self.player_list.append(self.player_sprite)


        for state in self.agent.environment.states:
            if self.agent.environment.states[state] == '#':
                sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", TILE_SCALING)
                sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
                sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING)
                self.wall_list.append(sprite)
            # elif self.agent.environment.states[state] == '£':
            #     sprite = arcade.Sprite(":resources:images/tiles/snowCenter.png", 0.5)
            #     sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * 0.5
            #     sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * 0.5)
            #     self.walls.append(sprite)
            elif self.agent.environment.states[state] == '$':
                sprite = arcade.Sprite(":resources:images/items/gold_1.png", TILE_SCALING)
                sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
                sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING)
                self.coin_list.append(sprite)
            elif self.agent.environment.states[state] == '?':
                sprite = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
                sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
                sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING)
                self.box_list.append(sprite)
                # self.wall_list.append(sprite)

        self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", TILE_SCALING)
        self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * TILE_SCALING
        self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * TILE_SCALING)

        self.physique_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_draw(self):
        arcade.start_render()

        self.wall_list.draw()
        self.coin_list.draw()
        self.box_list.draw()
        self.player_list.draw()
        self.goal.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.WHITE, 20)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physique_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        self.physique_engine.update()

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        box_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.box_list)

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            # self.score += REWARD_COIN
        for box in box_hit_list:
            # TODO
            # if (self.player_sprite.center_y < box.center_y):
            box.remove_from_sprite_lists()
            # self.score += REWARD_COIN

        changed = False

        if self.player_sprite.center_y < -100:
            self.player_prite.center_x = 0
            self.player_sprite_center_y = 0

            self.view_left = 0
            self.view_bottom = 0
            changed = True
        
        # set end of game
        if self.player_sprite.center_x >= self.end_of_map:
            #add code for end of game
            pass

        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
        
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)


def main():
    environment = Environment(MARIO)
    agent = Agent(environment)

    window = MarioWindow(agent)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()


# class MarioWindow(arcade.Window):
#     def __init__(self, agent):
#         super().__init__(agent.environment.width * SPRITE_SIZE,
#                         agent.environment.height * SPRITE_SIZE,
#                         "Mario Test ESGI")
#         self.agent = agent
#         arcade.set_background_color(arcade.csscolor.MEDIUM_PURPLE)
    
#     def setup(self):
#         self.walls = arcade.SpriteList()
#         for state in self.agent.environment.states:
#             if self.agent.environment.states[state] == '#':
#                 sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", 0.5)
#                 sprite.center_x = state[1] * sprite.width + sprite.width * 0.5
#                 sprite.center_y = self.height - (state[0] * sprite.width + sprite.width * 0.5)
#                 self.walls.append(sprite)
#             elif self.agent.environment.states[state] == '£': 
#                 sprite = arcade.Sprite(":resources:images/tiles/snowCenter.png", 0.5)
#                 sprite.center_x = state[1] * sprite.width + sprite.width * 0.5
#                 sprite.center_y = self.height - (state[0] * sprite.width + sprite.width * 0.5)
#                 self.walls.append(sprite)
#             elif self.agent.environment.states[state] == 'C': 
#                 sprite = arcade.Sprite(":resources:images/items/gold_1.png", 0.5)
#                 sprite.center_x = state[1] * sprite.width + sprite.width * 0.5
#                 sprite.center_y = self.height - (state[0] * sprite.width + sprite.width * 0.5)
#                 self.walls.append(sprite)
#             elif self.agent.environment.states[state] == '?': 
#                 sprite = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", 0.5)
#                 sprite.center_x = state[1] * sprite.width + sprite.width * 0.5
#                 sprite.center_y = self.height - (state[0] * sprite.width + sprite.width * 0.5)
#                 self.walls.append(sprite)
        
#         self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", 0.5)
#         self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * 0.5
#         self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * 0.5)

#         self.player = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", 0.5)
#         self.update_player()
    
#     def update_player(self):
#         self.player.center_x = self.agent.state[1] * self.player.width + self.player.width * 0.5
#         self.player.center_y = self.height - (self.agent.state[0] * self.player.width + self.player.width * 0.5)

#     def on_update(self, delta_time):
#         if agent.state != agent.environment.goal:
#             action = self.agent.best_action()
#             self.agent.do(action)
#             self.agent.update_policy()
#             self.update_player()
    
#     def on_draw(self):
#         arcade.start_render()
#         self.walls.draw()
#         self.goal.draw()
#         self.player.draw()

#         arcade.draw_text(f"Score: {self.agent.score}", 10, 10, arcade.csscolor.WHITE, 20)

#     def on_key_press(self, key, modifiers):
#         if key == arcade.key.R:
#             self.agent.reset()

# if __name__ == "__main__":
#     environment = Environment(MARIO)
#     agent = Agent(environment)

#     window = MarioWindow(agent)
#     window.setup()
#     arcade.run()
