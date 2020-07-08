import pygame
import numpy as np
import gym
from pygame.math import Vector2
from gym import error, spaces, utils
from gym.utils import seeding
import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

WIDTH = 700
HEIGHT = 400


def _collide_rect(rect1, rect2):
    return (rect1.x <= rect2.x <= rect1.right and rect1.y <= rect2.y <= rect1.bottom) or \
           (rect1.x <= rect2.x <= rect1.right and rect1.y <= rect2.bottom <= rect1.bottom) or \
           (rect1.x <= rect2.right <= rect1.right and rect1.y <= rect2.y <= rect1.bottom) or \
           (rect1.x <= rect2.right <= rect1.right and rect1.y <= rect2.bottom <= rect1.bottom)


def collide_rect(rect1, rect2):
    return _collide_rect(rect1, rect2) or _collide_rect(rect2, rect1)


def collide_rects(rect, rects):
    for i in rects:
        if collide_rect(i, rect):
            return True, i
    return False, None


horizontal_borders = [pygame.Rect(12, 0, 676, 12), pygame.Rect(12, HEIGHT - 12, 676, 12)]
vertical_borders = [pygame.Rect(0, 0, 12, 50), pygame.Rect(0, 350, 12, 50), pygame.Rect(WIDTH - 12, 0, 12, 50),
                    pygame.Rect(WIDTH - 12, 350, 12, 50)]
goal_borders = [pygame.Rect(-24, 50, 24, 300), pygame.Rect(WIDTH, 50, 24, 300)]


def draw_borders(surf):
    for i in vertical_borders:
        pygame.draw.rect(surf, RED, i)

    for i in horizontal_borders:
        pygame.draw.rect(surf, RED, i)

    for i in goal_borders:
        pygame.draw.rect(surf, (0, 255, 0), i)


class Ball:
    def __init__(self):
        self.length = 15
        self.surf = pygame.Surface((self.length, self.length))
        self.rect = self.surf.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.color = WHITE
        self.theta = 0
        self.vel = Vector2(12, 0)
        self.max_theta = 60

    def update(self, paddle_1, paddle_2):
        self.theta %= 360
        if self.theta > 180:
            self.theta -= 360
        self.pos += self.vel.rotate(self.theta)
        self.rect.x, self.rect.y = self.pos.x, self.pos.y

        signal = -1
        # print(self.theta)
        if paddle_1.collide_ball(self):
            dist = self.rect.center[1] - paddle_1.rect.center[1]
            theta_prime = 0
            if dist != 0:
                theta_prime = np.sign(dist) * (90 - 2 * abs(dist) / paddle_1.height * self.max_theta) % 360
                if theta_prime > 180: theta_prime -= 360
                if theta_prime > self.max_theta:
                    theta_prime = self.max_theta
                elif theta_prime < -self.max_theta:
                    theta_prime = -self.max_theta

            self.theta = theta_prime
            self.rect.x = paddle_1.rect.right + 1
        elif paddle_2.collide_ball(self):
            dist = self.rect.center[1] - paddle_2.rect.center[1]
            theta_prime = 180
            if dist != 0:
                theta_prime = np.sign(-dist) * 180 + np.sign(-dist) * (
                            90 - 2 * abs(dist) / paddle_1.height * self.max_theta) % 360
                if theta_prime > 180: theta_prime -= 360
                if theta_prime < self.max_theta + 90:
                    theta_prime = self.max_theta + 90
                elif theta_prime > -self.max_theta - 90:
                    theta_prime = -self.max_theta - 90
            self.theta = theta_prime
            self.rect.right = paddle_2.rect.x - 1
            signal = 0
        elif collide_rect(horizontal_borders[0], self.rect):
            # print("top border")
            self.theta *= -1
            if self.theta < 0:
                # self.theta -= 2
                pass
            else:
                # self.theta += 2
                pass
            self.rect.y = horizontal_borders[0].bottom
        elif collide_rect(horizontal_borders[1], self.rect):
            # print("bottom border")
            self.theta *= -1
            if self.theta < 0:
                # self.theta -= 2
                pass
            else:
                # self.theta += 2
                pass
            self.rect.bottom = horizontal_borders[1].y
        elif collide_rect(vertical_borders[0], self.rect) or collide_rect(vertical_borders[1], self.rect):
            # print("left borders")
            self.theta *= -1
            self.theta += 180
            self.rect.x = vertical_borders[0].right
        elif collide_rect(vertical_borders[2], self.rect) or collide_rect(vertical_borders[3], self.rect):
            # print("right borders")
            self.theta *= -1
            self.theta += 180
            self.rect.right = vertical_borders[2].x
        elif collide_rect(goal_borders[0], self.rect):
            # print("player 2 scores")
            signal = 2
        elif collide_rect(goal_borders[1], self.rect):
            # print("player 1 scores")
            signal = 1
        else:
            signal = -1

        self.pos.x, self.pos.y = self.rect.x, self.rect.y

        return signal

    def render(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)


class Paddle:
    def __init__(self, center_x, center_y, id):
        self.width = 10
        self.height = 50
        self.surf = pygame.Surface((self.width, self.height))
        self.rect = self.surf.get_rect()
        self.color = WHITE
        self.rect.center = (center_x, center_y)
        self.vel = 5  # px per second
        self.id = id

    def collide_ball(self, ball):
        return collide_rect(self.rect, ball.rect)

    def update(self, action):
        if action == 0:
            self.rect.y -= self.vel
        elif action == 1:
            self.rect.y += self.vel
        else:
            self.rect.y += 0

        if self.rect.y < 12:
            self.rect.y = 12
        elif self.rect.bottom > HEIGHT - 12:
            self.rect.bottom = HEIGHT - 12

    def render(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)


class Game:
    def __init__(self, render_game=False, enable_human_input=False, enable_paddle_1_ai=True):
        self.render_game = render_game
        self.enable_human_input = enable_human_input
        self.enable_paddle_1_ai = enable_paddle_1_ai
        if self.render_game:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.paddle_1 = Paddle(50, 200, 0)
        self.paddle_2 = Paddle(WIDTH - 50, 200, 1)
        self.ball = Ball()
        self.good_score = 0
        self.bad_score = 0
        self.prev_time = 0

    def naive_paddle_1_ai(self):
        delta = self.paddle_1.rect.center[1] - self.ball.rect.center[1]
        if delta > 0:
            return 0
        elif delta < 0:
            return 1
        else:
            return 2

    def update(self, action_2):
        if self.render_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -2
            dt = self.clock.tick(60)
        curr_time = time.time()
        # print(curr_time-self.prev_time)
        self.prev_time = curr_time
        action_1 = 2
        # action_2 = action_2
        if self.render_game and self.enable_human_input:
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_w]:
                action_1 = 0
            elif pressed[pygame.K_s]:
                action_1 = 1
            if pressed[pygame.K_UP]:
                action_2 = 0
            elif pressed[pygame.K_DOWN]:
                action_2 = 1

        if self.enable_paddle_1_ai:
            action_1 = self.naive_paddle_1_ai()

        score_id = self.ball.update(self.paddle_1, self.paddle_2)
        self.paddle_1.update(action_1)
        self.paddle_2.update(action_2)
        return score_id

    def render(self):
        self.screen.fill(BLACK)
        draw_borders(self.screen)
        self.ball.render(self.screen)
        self.paddle_1.render(self.screen)
        self.paddle_2.render(self.screen)
        pygame.display.update()

    def reset(self):
        self.paddle_1 = Paddle(50, 200, 0)
        self.paddle_2 = Paddle(WIDTH - 50, 200, 1)
        self.ball = Ball()

    def gameloop(self):
        while True:
            score_id = self.update(2)
            if score_id != -1 and score_id != 0:
                if self.render_game: pygame.quit()
                return score_id
            if self.render_game: self.render()


# game = Game(render_game=True, enable_human_input=True)

# result = game.gameloop()
# print(result)



class PongEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(PongEnv, self).__init__()
        self.game = None
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=np.array([-1, -1, -1, -1]), high=np.array([1, 1, 1, 1]),
                                            dtype=np.float64)  # ball/paddle_2 x delta and y delta and ball/paddle_1 x delta and y delta
        self.frames = 0

    def _get_state(self):
        return self.game.ball.rect.center[0], self.game.ball.rect.center[1], self.game.paddle_1.rect.center[1], \
               self.game.paddle_2.rect.center[1]

    def _get_rewards(self, score_id):
        if score_id == 2:
            self.game.reset()
            #print("Player two scores!")
            self.game.good_score += 1
            return 1
        elif score_id == 1:
            self.game.reset()
            #print("Player one scored :(")
            self.game.bad_score += 1
            return -1
        elif score_id == 0:
            #print("Hit!")
            return 0
        else:
            return 0

    def step(self, action):
        # print(self.frames)
        score_id = self.game.update(action)
        done = False
        if self.frames > 3530: done = True
        reward = self._get_rewards(score_id)

        state = self._get_state()
        self.frames += 1
        return state, reward, done, {}

    def render(self, mode='human'):
        if self.game.render_game: self.game.render()

    def close(self):
        pass


class PongEnvUnrendered(PongEnv):

    def __init__(self):
        super(PongEnvUnrendered, self).__init__()

    def reset(self):
        if self.game != None: print("P1: {} P2: {}".format(self.game.bad_score, self.game.good_score))
        else: print("P1: 0 P2: 0")
        #print("New Game")
        self.game = Game(render_game=False)
        self.frames = 0
        return self._get_state()

class PongEnvRendered(PongEnv):

    def __init__(self):
        super(PongEnvRendered, self).__init__()

    def reset(self, render_game):
        if self.game != None:
            print("P1: {} P2: {}".format(self.game.bad_score, self.game.good_score))
        else:
            print("P1: 0 P2: 0")
        self.game = Game(render_game=render_game)
        self.frames = 0

        return self._get_state()


#game = Game(render_game=True, enable_human_input=True)
#game.gameloop()
