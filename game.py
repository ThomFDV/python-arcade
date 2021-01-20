import arcade

SPRITE_SIZE = 64

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "MarioTestNoPhysic"

# player settings
CHARACTER_SCALING = 0.5

# wall settings
WALL_SCALING = 0.5

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

LEFT, RIGHT, JUMP = 'L', 'R', 'J'
ACTIONS = [LEFT, RIGHT, JUMP]

PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 22
GRAVITY = 1


class Game(arcade.Window):

    def __init__(self, agent, map):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.agent = agent
        self.agent.environment.set_game(self)
        self.map = map
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.box_list = None
        self.goal = None
        self.player_sprite = None
        self.physique_engine = None
        self.action_number = 0
        self.best_action_number = None

        # init for scroll view
        self.view_bottom = 0
        self.view_left = 0

        self.best_score = None
        self.scores = []

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.states = {}
        self.walls = {}
        self.coins = {}
        self.boxes = {}
        lines = self.map.strip().split('\n')

        self.height_map = len(lines)
        self.width_map = len(lines[0])
        for row in range(self.height_map):
            for col in range(self.width_map):
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

    def setup(self):
        self.view_bottom = 0
        self.view_left = 0
        self.action_number = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png",
                                           CHARACTER_SCALING)
        self.player_sprite.center_x = self.starting_point[
                                          1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
        self.player_sprite.center_y = self.height - self.starting_point[
            0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
        self.player_list.append(self.player_sprite)

        for wall in self.walls:
            sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", WALL_SCALING)
            sprite.center_x = wall[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
            sprite.center_y = self.height - (wall[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING)
            self.wall_list.append(sprite)

        for state in self.states:
            if self.states[state] == '$':
                sprite = arcade.Sprite(":resources:images/items/gold_1.png", WALL_SCALING)
                sprite.center_x, sprite.center_y = self.convert_position(state, SPRITE_SIZE, WALL_SCALING)
                # sprite.center_x = state[1] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING
                # sprite.center_y = self.height - (state[0] * SPRITE_SIZE + SPRITE_SIZE * WALL_SCALING)
                self.coin_list.append(sprite)

        # for state in self.agent.environment.states:
        #     if self.agent.environment.states[state] == '#':

        self.goal_sprite = arcade.Sprite(":resources:images/items/flagGreen1.png", WALL_SCALING)
        self.goal_sprite.center_x, self.goal_sprite.center_y = self.convert_position(self.goal, self.goal_sprite.width,
                                                                                     WALL_SCALING)
        # self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * WALL_SCALING
        # self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * WALL_SCALING)

        self.physique_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_draw(self):
        arcade.start_render()

        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.goal_sprite.draw()

        score_text = f"Score: {self.agent.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.WHITE, 20)

        best_score_text = f"Best Score: {self.best_score}"
        arcade.draw_text(best_score_text, 10 + self.view_left, 30 + self.view_bottom, arcade.csscolor.WHITE, 20)

        player_position_text = f"x: {self.player_sprite.center_x}, y: {self.player_sprite.center_y}"
        arcade.draw_text(player_position_text, 10 + self.view_left, 50 + self.view_bottom, arcade.csscolor.WHITE, 20)

        best_action_number_text = f"Best Actions Number: {self.best_action_number}"
        arcade.draw_text(best_action_number_text, 10 + self.view_left, 70 + self.view_bottom, arcade.csscolor.WHITE, 20)

    def scroll_view(self):
        changed = False

        # find usage of this
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

        # change view
        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left, self.width + self.view_left, self.view_bottom,
                                self.height + self.view_bottom)

    def on_update(self, delta_time):

        if self.agent.done == False and self.agent.score > -1500:
            action = self.agent.best_action()
            print(f"Best Action: {action}")
            self.agent.do(action)
            self.agent.update_policy()
            self.action_number += 1
        else:
            self.best_score = max(self.best_score, self.agent.score) if self.best_score != None else self.agent.score
            self.scores.append(self.agent.score)
            self.best_action_number = min(self.best_action_number,
                                          self.action_number) if self.best_action_number != None else self.action_number
            self.agent.reset()
            self.setup()

        self.scroll_view()

    def check_collision_coin(self):
        return arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

    def check_collision_wall(self):
        return arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)

    def check_collision_goal(self):
        return arcade.check_for_collision(self.player_sprite, self.goal_sprite)

    def get_player_position(self):
        return self.player_sprite.center_x, self.player_sprite.center_y

    def remove_coin(self):
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()

    def update_player(self, action):
        self.player_sprite.change_x = 0
        if action == JUMP:
            if self.physique_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif action == LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif action == RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def convert_position(self, position, sprite_size, scalling):
        x = position[1] * sprite_size + sprite_size * scalling
        y = self.height - (position[0] * sprite_size + sprite_size * scalling)
        return x, y
