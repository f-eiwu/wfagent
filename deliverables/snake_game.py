import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [((WINDOW_WIDTH // 2), (WINDOW_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % WINDOW_WIDTH),
               (cur[1] + (y * GRID_SIZE)) % WINDOW_HEIGHT)

        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 3
        self.positions = [((WINDOW_WIDTH // 2), (WINDOW_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def render(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color,
                           (p[0], p[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, DARK_GREEN,
                           (p[0], p[1], GRID_SIZE, GRID_SIZE), 1)

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != DOWN:
                    self.direction = UP
                elif event.key == pygame.K_DOWN and self.direction != UP:
                    self.direction = DOWN
                elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                    self.direction = LEFT
                elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                    self.direction = RIGHT


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                        random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def render(self, surface):
        pygame.draw.rect(surface, self.color,
                        (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, (200, 0, 0),
                        (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE), 1)


def draw_grid(surface):
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)


def main():
    # Create the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    snake = Snake()
    food = Food()

    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_r:
                    snake.reset()
                    food.randomize_position()

        # Update snake
        snake.update()

        # Check if snake ate food
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 10
            food.randomize_position()

        # Draw everything
        screen.fill(BLACK)
        draw_grid(screen)
        snake.render(screen)
        food.render(screen)

        # Draw score
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        screen.blit(score_text, (5, 5))

        # Draw instructions
        instructions_font = pygame.font.Font(None, 24)
        instructions = instructions_font.render('Use Arrow Keys to Move | R to Restart', True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, 5))

        # Update display
        pygame.display.update()

        # Control game speed
        clock.tick(10)


if __name__ == '__main__':
    main()