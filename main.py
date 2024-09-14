import pygame
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Define screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480  # Smaller level
TILE_SIZE = 40
ROWS = SCREEN_HEIGHT // TILE_SIZE
COLS = SCREEN_WIDTH // TILE_SIZE

# Define initial LEVEL (higher level = more obstacles)
LEVEL = 1

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pacman')


# Define Pacman class
class Pacman:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.speed = TILE_SIZE
        self.direction = (0, 0)

    def move(self, maze):
        new_rect = self.rect.move(self.direction[0] * self.speed, self.direction[1] * self.speed)
        if not self.collide_with_walls(new_rect, maze):
            self.rect = new_rect

    def collide_with_walls(self, new_rect, maze):
        for wall in maze.walls:
            if new_rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, YELLOW, self.rect)


# Define Ghost class
class Ghost:
    def __init__(self, x, y, color, algorithm='bfs', speed_factor=2):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.color = color
        self.algorithm = algorithm
        self.speed_factor = speed_factor
        self.steps = 0

    def bfs(self, start, goal, maze):
        """Breadth-First Search algorithm to find the shortest path."""
        queue = deque([start])
        came_from = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and neighbor not in came_from:
                    if maze.grid[neighbor[0]][neighbor[1]] == 0:  # Walkable
                        queue.append(neighbor)
                        came_from[neighbor] = current

        # Reconstruct the path
        current = goal
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()

        return path

    def dfs(self, start, goal, maze):
        """Depth-First Search algorithm for ghost movement."""
        stack = [(start, [])]
        visited = set()

        while stack:
            (current, path) = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            path = path + [current]
            if current == goal:
                return path

            for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and maze.grid[neighbor[0]][neighbor[1]] == 0:
                    stack.append((neighbor, path))

        return path

    def random_walk(self, start, maze):
        """Random Walk algorithm for ghost movement."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for direction in directions:
            next_step = (start[0] + direction[0], start[1] + direction[1])
            if 0 <= next_step[0] < ROWS and 0 <= next_step[1] < COLS and maze.grid[next_step[0]][next_step[1]] == 0:
                return [start, next_step]
        return [start]

    def move_toward_pacman(self, pacman, maze, ghosts):
        start = (self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE)
        goal = (pacman.rect.y // TILE_SIZE, pacman.rect.x // TILE_SIZE)

        # Use the selected algorithm for this ghost
        if self.algorithm == 'bfs':
            path = self.bfs(start, goal, maze)
        elif self.algorithm == 'dfs':
            path = self.dfs(start, goal, maze)
        else:  # Random walk
            path = self.random_walk(start, maze)

        if len(path) > 1:
            # Adjust speed by moving only every few frames
            self.steps += 1
            if self.steps % self.speed_factor == 0:
                next_step = path[1]
                next_rect = pygame.Rect(next_step[1] * TILE_SIZE, next_step[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                # Check if the next step collides with other ghosts
                if not any(ghost.rect.colliderect(next_rect) for ghost in ghosts if ghost != self):
                    self.rect.topleft = (next_step[1] * TILE_SIZE, next_step[0] * TILE_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


# Define Coin class
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE // 3, TILE_SIZE // 3)

    def draw(self, screen):
        pygame.draw.circle(screen, GOLD, self.rect.center, TILE_SIZE // 6)


# Define Maze class
class Maze:
    def __init__(self, level):
        self.walls = []
        self.coins = []
        self.cherries = []
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.generate_wide_open_maze(level)

    def generate_wide_open_maze(self, level):
        # Set boundaries to be solid walls
        for row in range(ROWS):
            for col in range(COLS):
                if row == 0 or row == ROWS - 1 or col == 0 or col == COLS - 1:
                    self.grid[row][col] = 1

        # Randomly scatter a few walls inside the grid based on LEVEL
        scatter_factor = max(2, 20 - level * 5)  # More open space at lower levels
        for row in range(2, ROWS - 2, 2):  # Only place walls every few rows
            for col in range(2, COLS - 2, 2):
                if random.randint(1, scatter_factor) == 1:
                    self.grid[row][col] = 1
                    if random.randint(0, 1) == 1:  # Add an additional vertical or horizontal wall
                        self.grid[row + random.choice([-1, 1])][col] = 1
                    else:
                        self.grid[row][col + random.choice([-1, 1])] = 1

        # Convert grid into wall rectangles for Pygame
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == 1:
                    wall = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.walls.append(wall)
                else:
                    # Add coins to empty spaces
                    self.coins.append(Coin(col * TILE_SIZE + TILE_SIZE // 4, row * TILE_SIZE + TILE_SIZE // 4))

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, wall)
        for coin in self.coins:
            coin.draw(screen)


def next_level_screen():
    """Display next level screen with a button to continue."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render('Next Level', True, WHITE)
    next_level_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, WHITE, next_level_button)
    next_text = font.render('Continue', True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
    screen.blit(next_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if next_level_button.collidepoint(event.pos):
                return True

def game_over_screen():
    """Display game over screen with replay button."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render('GAME OVER', True, WHITE)
    replay_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, WHITE, replay_button)
    replay_text = font.render('Replay', True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
    screen.blit(replay_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button.collidepoint(event.pos):
                    return True

def game_loop():
    global LEVEL
    clock = pygame.time.Clock()
    maze = Maze(LEVEL)
    pacman = Pacman(TILE_SIZE, TILE_SIZE)
    score = 0 # Initialize score
    # Font for score and level display
    font = pygame.font.Font(None, 36)

    # Place 3 ghosts in the center of the screen with different search algorithms and speeds
    ghosts = [
        Ghost(SCREEN_WIDTH // 2 - TILE_SIZE, SCREEN_HEIGHT // 2 - TILE_SIZE, PINK, 'bfs', speed_factor=4),
        # BFS Pink ghost
        Ghost(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED, 'dfs', speed_factor=3),  # DFS Red ghost
        Ghost(SCREEN_WIDTH // 2 + TILE_SIZE, SCREEN_HEIGHT // 2, PURPLE, 'random', speed_factor=2)
        # Random walk Purple ghost
    ]

    running = True
    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.direction = (1, 0)
                elif event.key == pygame.K_UP:
                    pacman.direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    pacman.direction = (0, 1)

        # Move Pacman
        pacman.move(maze)

        # Check for collision with coins
        for coin in maze.coins[:]:
            if pacman.rect.colliderect(coin.rect):
                maze.coins.remove(coin)
                score += 1

        # Check if all coins are collected to complete the level
        if not maze.coins:
            LEVEL += 1  # Increment the level
            if next_level_screen():
                game_loop()
            else:
                return

        # Move ghosts toward Pacman while avoiding collisions with each other
        for ghost in ghosts:
            ghost.move_toward_pacman(pacman, maze, ghosts)

        # Check for collision with ghosts
        for ghost in ghosts:
            if pacman.rect.colliderect(ghost.rect):
                if game_over_screen():
                    # Restart the game
                    game_loop()
                else:
                    return

        # Draw maze, Pacman, and ghosts
        maze.draw(screen)
        pacman.draw(screen)
        for ghost in ghosts:
            ghost.draw(screen)

        # Display the score and level
        score_text = font.render(f'Score: {score}', True, WHITE)
        level_text = font.render(f'Level: {LEVEL}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        # Refresh the screen
        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    game_loop()
    pygame.quit()
