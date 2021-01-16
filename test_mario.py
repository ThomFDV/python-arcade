import arcade
from environment import Environment
from agent import Agent

MARIO = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
X          $               X
X    #   #?#?#             X
X                 $        X
X.                        *X
X##########################X
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

SPRITE_SIZE = 64

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MarioTestNoPhysic"

#player settings
CHARACTER_SCALING = 0.5

#wall settings
WALL_SCALING = 0.5

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

class MarioTestWindow(arcade.Window):
    def __init__(self, agent):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.agent = agent

        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.box_list = None

        self.goal = None

        self.player_sprite = None

        #init for scroll view
        self.view_bottom = 0
        self.view_left = 0

        #init score
        self.score = 0
        self.best_score = None

        self.action_number = 0
        self.best_action_number = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.action_number = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png", CHARACTER_SCALING)
        self.player_sprite.center_x = self.agent.environment.starting_point[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
        self.player_sprite.center_y = self.height - self.agent.environment.starting_point[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
        self.player_list.append(self.player_sprite)

        for wall in self.agent.environment.walls:
            sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", WALL_SCALING)
            sprite.center_x = wall[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
            sprite.center_y = self.height - (wall[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING)
            self.wall_list.append(sprite)

        for state in self.agent.environment.states:
            if self.agent.environment.states[state] == '$':
                sprite = arcade.Sprite(":resources:images/items/gold_1.png", WALL_SCALING)
                sprite.center_x, sprite.center_y = self.convert_position(state, SPRITE_SIZE, WALL_SCALING)
                #sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
                #sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING)
                self.coin_list.append(sprite)

        # for state in self.agent.environment.states:
        #     if self.agent.environment.states[state] == '#':
                
        
        self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", WALL_SCALING)
        self.goal.center_x, self.goal.center_y = self.convert_position(self.agent.environment.goal, self.goal.width, WALL_SCALING)
        #self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * WALL_SCALING
        #self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * WALL_SCALING)

    def update_player(self):
        #self.player_sprite.center_x = self.agent.state[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
        #self.player_sprite.center_y = self.height - (self.agent.state[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING)
        self.player_sprite.center_x, self.player_sprite.center_y = self.convert_position(self.agent.state, SPRITE_SIZE, WALL_SCALING)

    
    def convert_position(self, position, sprite_size, scalling):
        x = position[1] * sprite_size + sprite_size * scalling
        y = self.height - (position[0] * sprite_size + sprite_size * scalling)
        return x, y

    def convert_position_to_state(self, x, y, sprite_size, scalling):
        p1 = int(x / sprite_size - scalling)
        p0 = int((self.height - y) / sprite_size - scalling)
        return p1, p0
        

    def on_draw(self):
        arcade.start_render()

        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.goal.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.WHITE, 20)

        best_score_text = f"Best Score: {self.best_score}"
        arcade.draw_text(best_score_text, 10 + self.view_left, 30 + self.view_bottom, arcade.csscolor.WHITE, 20)
    
        player_position_text = f"x: {self.player_sprite.center_x}, y: {self.player_sprite.center_y}"
        arcade.draw_text(player_position_text, 10 + self.view_left, 50 + self.view_bottom, arcade.csscolor.WHITE, 20)

        best_action_number_text = f"Best Actions Number: {self.best_action_number}"
        arcade.draw_text(best_action_number_text, 10 + self.view_left, 70 + self.view_bottom, arcade.csscolor.WHITE, 20)

    def scroll_view(self):
        changed = False

        #find usage of this
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = 0
            self.player_sprite.center_y = 0

            self.view_left = 0
            self.view_bottom = 0
            changed = True

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
        
        #change view 
        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left, self.width + self.view_left, self.view_bottom, self.height + self.view_bottom)
        
    def on_update(self, delta_time):

        #test state from player
        # test_state = self.agent.state
        # print(f"s1: {test_state[1]}, s2: {test_state[0]}")
        # x, y = self.convert_position(test_state, SPRITE_SIZE, WALL_SCALING)
        # print(f"x: {x}, y: {y}")
        # p1, p0 = self.convert_position_to_state(x, y, SPRITE_SIZE, WALL_SCALING)
        # print(f"p1: {p1}, p0: {p0}")


        # for getting x, y to state
        p1, p0 = self.convert_position_to_state(self.player_sprite.center_x, self.player_sprite.center_y, SPRITE_SIZE, CHARACTER_SCALING)
        self.agent.state = (p0, p1)

        if self.agent.state != self.agent.environment.goal:
            action = self.agent.best_action()
            print(f"Best Action: {action}")
            self.agent.do(action, True)
            self.agent.update_policy()
            self.update_player()
            self.action_number += 1
        else:
            self.best_score = max(self.best_score, self.agent.score) if self.best_score != None else self.agent.score
            self.best_action_number = min(self.best_action_number, self.action_number) if self.best_action_number != None else self.action_number
            self.agent.reset()
            self.agent.environment.reset()
            self.setup()


        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
        
        self.score = self.agent.score
        
        self.scroll_view()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.agent.reset()


def main():
    environment = Environment(MARIO)
    agent = Agent(environment)

    window = MarioTestWindow(agent)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()