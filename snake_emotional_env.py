import gym
import numpy as np
import pygame
import random

class SnakeEmotionalEnv(gym.Env):
    """Snake environment with a simple 'emotional state' system."""

    def __init__(self, width=100, height=100, snake_block=10):
        super(SnakeEmotionalEnv, self).__init__()

        # Game parameters
        self.width = width
        self.height = height
        self.snake_block = snake_block

        # Define action and observation space
        # Actions: 0=LEFT, 1=RIGHT, 2=UP, 3=DOWN
        self.action_space = gym.spaces.Discrete(4)
        low = np.array([0, 0, 0, 0, -1, -1], dtype=np.float32)
        high = np.array([width, height, width, height, 1, 1], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low, high, dtype=np.float32)

        # Emotional states
        self.emotions = {
            "fear": 0.0,
            "joy": 0.0,
            "sadness": 0.0
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake Emotional')

        self.reset()

    def reset(self):
        """Reset the game and emotions."""
        # Game state
        self.game_close = False
        self.x1 = self.width / 2
        self.y1 = self.height / 2
        self.x1_change = 0
        self.y1_change = 0
        self.snake_List = []
        self.Length_of_snake = 1

        # Food
        self.foodx = round(random.randrange(0, self.width - self.snake_block) / 10.0) * 10.0
        self.foody = round(random.randrange(0, self.height - self.snake_block) / 10.0) * 10.0

        # Reset emotions
        self.emotions = {
            "fear": 0.0,
            "joy": 0.0,
            "sadness": 0.0
        }

        return self._get_obs()

    def step(self, action):
        """Execute one time step."""
        reward = 0
        done = False

        # 1. Apply action
        if action == 0:  # LEFT
            self.x1_change = -self.snake_block
            self.y1_change = 0
        elif action == 1:  # RIGHT
            self.x1_change = self.snake_block
            self.y1_change = 0
        elif action == 2:  # UP
            self.y1_change = -self.snake_block
            self.x1_change = 0
        elif action == 3:  # DOWN
            self.y1_change = self.snake_block
            self.x1_change = 0

        # 2. Update position
        self.x1 += self.x1_change
        self.y1 += self.y1_change

        # 3. Check for death (wall or self-collision)
        if self.x1 >= self.width or self.x1 < 0 or self.y1 >= self.height or self.y1 < 0:
            done = True
            reward = -10
            self.emotions["sadness"] = 1.0  # Spike sadness
        snake_head = [self.x1, self.y1]
        self.snake_List.append(snake_head)
        if len(self.snake_List) > self.Length_of_snake:
            del self.snake_List[0]
        if snake_head in self.snake_List[:-1]:
            done = True
            reward = -10
            self.emotions["sadness"] = 1.0

        # 4. Check for eating food
        if not done and self.x1 == self.foodx and self.y1 == self.foody:
            self.foodx = round(random.randrange(0, self.width - self.snake_block) / 10.0) * 10.0
            self.foody = round(random.randrange(0, self.height - self.snake_block) / 10.0) * 10.0
            self.Length_of_snake += 1
            reward = 10
            self.emotions["joy"] += 1.0  # Increase joy

        # 5. Update emotions
        self._update_emotions()

        # 6. Combine base reward + emotional shaping
        # You can tune these alpha values depending on how strongly you want emotions to affect the reward.
        alpha_fear = -0.1
        alpha_joy = 0.1
        alpha_sad = -0.5
        emotional_bonus = (alpha_fear * self.emotions["fear"] +
                           alpha_joy  * self.emotions["joy"]  +
                           alpha_sad  * self.emotions["sadness"])

        total_reward = reward + emotional_bonus

        # 7. Render and return
        self.render()
        obs = self._get_obs()
        return obs, total_reward, done, {"emotions": self.emotions.copy()}

    def _update_emotions(self):
        """Adjust emotions based on game state each step."""
        # Decay emotions
        for k in self.emotions:
            self.emotions[k] *= 0.95  # simple exponential decay

        # Increase fear if near wall or near self-collision
        boundary_threshold = 2 * self.snake_block
        if (self.x1 < boundary_threshold or
            self.x1 > self.width - boundary_threshold or
            self.y1 < boundary_threshold or
            self.y1 > self.height - boundary_threshold):
            self.emotions["fear"] += 0.2  # Increase fear near boundary

        # If sadness was spiked, it gradually decays but starts strong
        # Joy increments if the snake just ate food, which is handled in step()

    def _get_obs(self):
        """Construct the observation."""
        x_dir = np.sign(self.x1_change)
        y_dir = np.sign(self.y1_change)
        return np.array([self.x1, self.y1, self.foodx, self.foody, x_dir, y_dir], dtype=np.float32)

    def render(self, mode='human'):
        self.screen.fill((50, 153, 213))
        # Food
        pygame.draw.rect(self.screen, (0,255,0), [self.foodx, self.foody, self.snake_block, self.snake_block])
        # Snake
        for pos in self.snake_List:
            pygame.draw.rect(self.screen, (0,0,0), [pos[0], pos[1], self.snake_block, self.snake_block])
        pygame.display.update()

    def close(self):
        pygame.quit()
