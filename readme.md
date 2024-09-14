

# 🕹️ Pacman Game

Welcome to the **Pacman Game**! This project is a Python implementation of the classic Pacman game, built using the [Pygame](https://www.pygame.org) library. The game includes various features like ghosts chasing Pacman, power-ups, and dynamic mazes.

<img width="752" alt="image" src="https://github.com/user-attachments/assets/16a6e53b-e08f-4abf-b0b3-e59a21c51116">  <!-- Replace with your actual screenshot -->

## 🚀 Features

- **Classic Pacman Mechanics**: Navigate Pacman through a dynamically generated maze while avoiding ghosts.
- **Ghost AI**: Ghosts use different algorithms (BFS, DFS, Random Walk) to chase Pacman.
- **Power-ups**: Collect **lightning** to gain a temporary speed boost and the ability to eat ghosts for extra points.
- **Multiple Levels**: Each level increases in difficulty, with more obstacles and faster ghosts.
- **Scoring System**: Earn points by collecting coins, cherries, and eating ghosts when powered up.
- **Dynamic Maze**: The maze is generated differently for each level, providing a new challenge each time.

## 🎮 How to Play

1. **Move Pacman** using the arrow keys (`←`, `→`, `↑`, `↓`).
2. **Collect coins** to increase your score.
3. **Avoid ghosts** or use a lightning power-up to temporarily eat them for extra points.
4. **Advance to the next level** by collecting all the coins or reaching a score of 300.

## 🛠️ Setup

### Prerequisites

- Python 3.6+
- [Pygame](https://www.pygame.org/) library

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/pacman-game.git
   cd pacman-game
   ```

2. Install the required dependencies:

   ```bash
   pip install pygame
   ```

3. Run the game:

   ```bash
   python main.py
   ```

## 📂 Project Structure

```bash
├── pacman.py           # Main game script
├── README.md           # Project documentation
└── assets/             # Directory for additional assets.
```

## 🤖 Ghost AI

Each ghost uses a different search algorithm:
- **BFS (Breadth-First Search)**: Finds the shortest path to Pacman.
- **DFS (Depth-First Search)**: Explores the maze randomly, looking for Pacman.
- **Random Walk**: Moves in random directions, making the ghost less predictable.

## ✨ Power-ups

- **Lightning**: When Pacman eats a lightning power-up, he becomes faster and turns green. The ghosts turn blue and run away from Pacman. You can eat ghosts for extra points during this time. The effect lasts for 7 seconds, with Pacman blinking from green to yellow when the effect is about to end.

## 📈 Scoring

- **+1 point** for each coin collected.
- **+100 points** for each cherry collected.
- **+200 points** for each ghost eaten when powered up.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).


## 🗨️ Acknowledgments

- Inspired by the classic **Pacman** game.
- Built with ❤️ using [Pygame](https://www.pygame.org) .

