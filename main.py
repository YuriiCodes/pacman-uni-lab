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
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (173, 216, 230)

TOTAL_SCORE_TO_WIN = 500
# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pacman')


# Define Pacman class
class Pacman:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.speed = TILE_SIZE
        self.direction = (0, 0)
        self.powered_up = False  # Track if Pacman is powered up
        self.power_up_time = 0  # Time remaining for power-up
        self.blinking = False  # To blink Pacman near the end of power-up

    def move(self, maze):
        # Adjust speed based on power-up state
        # logic for speed power up can be done here
        movement_speed = self.speed * (1 if self.powered_up else 1)

        # Move one step at a time to ensure no skipping through walls
        for step in range(movement_speed // self.speed):
            new_rect = self.rect.move(self.direction[0] * self.speed, self.direction[1] * self.speed)
            if not self.collide_with_walls(new_rect, maze):
                self.rect = new_rect
            else:
                break  # Stop moving if we hit a wall

    def collide_with_walls(self, new_rect, maze):
        for wall in maze.walls:
            if new_rect.colliderect(wall):
                return True
        return False
    def update_power_up(self):
        """Update Pacman's power-up state and handle blinking."""
        if self.power_up_time > 0:
            self.power_up_time -= 1
            if self.power_up_time == 120:  # 5 seconds remaining (60 FPS)
                self.blinking = True
            elif self.power_up_time == 0:
                self.powered_up = False
                self.blinking = False

    def draw(self, screen):
        # Pacman blinks green to yellow when the power-up is about to expire
        if self.blinking and self.power_up_time % 10 < 5:
            color = YELLOW
        else:
            color = GREEN if self.powered_up else YELLOW
        pygame.draw.ellipse(screen, color, self.rect)



# Define Ghost class
class Ghost:
    def __init__(self, x, y, color, algorithm='bfs', speed_factor=2):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.original_color = color  # Store the original color
        self.color = color  # This will be used to change the color when powered up
        self.algorithm = algorithm
        self.speed_factor = speed_factor  # Higher speed_factor makes the ghost move less often
        self.steps = 0  # Track steps to control movement frequency
        self.dead = False  # Track if the ghost is "dead"

    def move_away_from_pacman(self, pacman, maze):
        """Move the ghost away from Pacman."""
        start = (self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for direction in directions:
            next_step = (start[0] + direction[0], start[1] + direction[1])
            if 0 <= next_step[0] < ROWS and 0 <= next_step[1] < COLS and maze.grid[next_step[0]][next_step[1]] == 0:
                return [start, next_step]
        return [start]

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
        if pacman.powered_up:
            path = self.move_away_from_pacman(pacman, maze)  # Move away from Pacman
            self.color = LIGHT_BLUE  # Turn blue when Pacman is powered up
        else:
            self.color = self.original_color  # Restore the original color when power-up ends

            # Use the selected algorithm for this ghost
            if self.algorithm == 'bfs':
                path = self.bfs((self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE),
                                (pacman.rect.y // TILE_SIZE, pacman.rect.x // TILE_SIZE), maze)
            elif self.algorithm == 'dfs':
                path = self.dfs((self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE),
                                (pacman.rect.y // TILE_SIZE, pacman.rect.x // TILE_SIZE), maze)
            else:  # Random walk
                path = self.random_walk((self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE), maze)

        # Slow down the ghost movement based on its speed_factor
        if len(path) > 1:
            self.steps += 1
            if self.steps % self.speed_factor == 0:  # Move only every few frames
                self.rect.topleft = (path[1][1] * TILE_SIZE, path[1][0] * TILE_SIZE)

    def draw(self, screen):
        if not self.dead:  # Don't draw if ghost is dead
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
        self.lightnings = []
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # Load the lightning image
        self.lightning_img = pygame.image.load('assets/lightning.webp').convert_alpha()
        self.lightning_img = pygame.transform.scale(self.lightning_img, (TILE_SIZE, TILE_SIZE))  # Resize to fit tiles

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
        empty_tiles = [(row, col) for row in range(ROWS) for col in range(COLS) if self.grid[row][col] == 0]
        random.shuffle(empty_tiles)
        self.coins = [Coin(col * TILE_SIZE + TILE_SIZE // 4, row * TILE_SIZE + TILE_SIZE // 4) for row, col in
                      empty_tiles[3:]]  # All but 3 for cherries

        self.cherries = [empty_tiles.pop() for _ in range(3)]  # 3 cherries

        # Add lightnings to empty spaces
        self.lightnings = [empty_tiles.pop() for _ in range(2)]  # 2 lightning power-ups

    #     remove cherries and lightnings from coins
        for cherry in self.cherries:
            for coin in self.coins[:]:
                if coin.rect.collidepoint(cherry[1] * TILE_SIZE + TILE_SIZE // 2, cherry[0] * TILE_SIZE + TILE_SIZE // 2):
                    self.coins.remove(coin)
        for lightning in self.lightnings:
            for coin in self.coins[:]:
                if coin.rect.collidepoint(lightning[1] * TILE_SIZE + TILE_SIZE // 2, lightning[0] * TILE_SIZE + TILE_SIZE // 2):
                    self.coins.remove(coin)

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, wall)
        for coin in self.coins:
            coin.draw(screen)
        # Draw cherries
        for cherry in self.cherries:
            x = cherry[1] * TILE_SIZE + TILE_SIZE // 2
            y = cherry[0] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, RED, (x - 5, y), TILE_SIZE // 6)  # First red circle
            pygame.draw.circle(screen, RED, (x + 5, y), TILE_SIZE // 6)  # Second red circle

            # Draw lightnings using the image
        for lightning in self.lightnings:
            x = lightning[1] * TILE_SIZE
            y = lightning[0] * TILE_SIZE
            screen.blit(self.lightning_img, (x, y))  # Blit the image at the correct position


def next_level_screen():
    """Display next level screen with a button to continue."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render('Next Level', True, WHITE)
    next_level_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 300, 70)
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
    replay_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 250, 70)
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
    score = 0  # Initialize score

    # Font for score and level display
    font = pygame.font.Font(None, 36)

    # Place 3 ghosts in the center of the screen with different search algorithms and speeds
    ghosts = [
        Ghost(SCREEN_WIDTH // 2 - TILE_SIZE, SCREEN_HEIGHT // 2 - TILE_SIZE, PINK, 'bfs', speed_factor=2),
        Ghost(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, RED, 'dfs', speed_factor=2),
        Ghost(SCREEN_WIDTH // 2 + TILE_SIZE, SCREEN_HEIGHT // 2, PURPLE, 'random', speed_factor=2)
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

        # Check for collision with cherries
        for cherry in maze.cherries[:]:
            cherry_rect = pygame.Rect(cherry[1] * TILE_SIZE, cherry[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if pacman.rect.colliderect(cherry_rect):
                maze.cherries.remove(cherry)
                score += 100

        # Check for collision with lightnings
        for lightning in maze.lightnings[:]:
            lightning_rect = pygame.Rect(lightning[1] * TILE_SIZE, lightning[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if pacman.rect.colliderect(lightning_rect):
                maze.lightnings.remove(lightning)
                pacman.powered_up = True
                pacman.power_up_time = 420  # 7 seconds (60 FPS * 7)
                pacman.blinking = False

        # Update Pacman's power-up timer
        pacman.update_power_up()

        # Check for collision with ghosts during power-up
        for ghost in ghosts[:]:
            if pacman.rect.colliderect(ghost.rect) and pacman.powered_up and not ghost.dead:
                ghost.dead = True  # Ghost dies
                ghosts.remove(ghost)
                score += 200  # Pacman earns 200 points

        # Check if all coins are collected or score >= TOTAL_SCORE_TO_WIN to complete the level
        if not maze.coins or score >= TOTAL_SCORE_TO_WIN:
            LEVEL += 1
            if next_level_screen():
                game_loop()
            else:
                return

        # Move ghosts toward Pacman while avoiding collisions with each other
        for ghost in ghosts:
            ghost.move_toward_pacman(pacman, maze, ghosts)

        # Check for collision with ghosts when Pacman is not powered up
        for ghost in ghosts:
            if pacman.rect.colliderect(ghost.rect) and not pacman.powered_up:
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
        screen.blit(level_text, (150, 10))

        # Refresh the screen
        pygame.display.flip()
        clock.tick(10)



# Run the game loop
if __name__ == "__main__":
    game_loop()

# Quit Pygame
pygame.quit()
