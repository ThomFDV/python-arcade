import arcade
from environment import Environment
from agent import Agent

#Q-table
# U L R

MARIO = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
X          $               X
X    #   #?#?#             X
X                      $   X
X.                        *X
X##########################X
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

SPRITE_SIZE = 64


# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Mariozi2D"

CHARACTER_SCALING = 0.66
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 22

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100


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
                self.wall_list.append(sprite)

        self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", TILE_SCALING)
        self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * TILE_SCALING
        self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * TILE_SCALING)

        self.physique_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)


    def update_player(self):
        self.player_sprite.center_x = self.agent.state[1] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING
        self.player_sprite_center_y = self.height - (self.agent.state[0] * SPRITE_SIZE + SPRITE_SIZE * TILE_SCALING)

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

        #region apply game learning with update_player
        print(f"{self.agent.environment.goal}:{self.agent.state}")
        print(self.player_sprite.center_y)

        if self.agent.state != self.agent.environment.goal:
            action = self.agent.best_action()
            self.agent.do(action)
            self.agent.update_policy()
            self.update_player()

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
            print("boom")

        changed = False

        if self.player_sprite.center_y < -100:
            self.player_prite.center_x = 0
            self.player_sprite_center_y = 0

            self.view_left = 0
            self.view_bottom = 0
            changed = True
        
        # set end of game
        if self.player_sprite.center_x >= self.goal.center_x:
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
