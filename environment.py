REWARD_GOAL = 200
REWARD_COIN = 100
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60

LEFT, RIGHT, JUMP = 'L', 'R', 'J'
ACTIONS = [LEFT, RIGHT, JUMP]


class Environment:
    def __init__(self, map):
        self.map = map
        self.reset()

    def reset(self):
        lines = self.map.strip().split('\n')
        self.height = len(lines)
        self.width = len(lines[0])

        for row in range(self.height):
            for col in range(self.width):
                if lines[row][col] == ".":
                    self.starting_point = (row, col)

    def apply(self, action):
        self.game.update_player(action)
        self.game.physique_engine.update()
        state = self.game.get_player_position()
        reward = self.get_reward(action)
        done = self.game.check_collision_goal()
        return state, reward, done

    def get_reward(self, action):

        if action == LEFT:
            score = REWARD_DEFAULT * 2
        else:
            score = REWARD_DEFAULT

        coin_hit_list = self.game.check_collision_coin()
        for coin in coin_hit_list:
            score += REWARD_COIN
            coin.remove_from_sprite_lists()

        wall_hit_list = self.game.check_collision_wall()
        for wall in wall_hit_list:
            score += REWARD_STUCK

        goal = self.game.check_collision_goal()
        if goal:
            score += REWARD_GOAL

        position_x, position_y = self.game.get_player_position()

        print(position_x, position_y)
        if position_x <= 0:
            score += REWARD_IMPOSSIBLE

        return score

    def set_game(self, game):
        self.game = game
