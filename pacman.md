# Pac-Man

## Overview
Pac-Man is a classic arcade maze game where the player navigates a character through a maze, eating all the dots while avoiding four roaming ghosts. Power pellets temporarily turn the tables, allowing Pac-Man to chase and eat the ghosts for bonus points. The game loops through increasingly difficult levels as all dots are cleared.

## Genre
Maze / Action

## Gameplay Mechanics
- The player controls Pac-Man through a fixed single-screen maze filled with dots (pellets).
- Pac-Man must eat every dot in the maze to advance to the next level.
- Four ghosts (Blinky, Pinky, Inky, Clyde) roam the maze and chase Pac-Man using distinct AI behaviors.
- Four larger **Power Pellets** are located in the maze corners. Eating one causes all ghosts to enter a frightened state, making them edible for a short duration.
- Occasionally, a bonus fruit item appears in the center of the maze for extra points.
- The game loops continuously, increasing ghost speed and reducing frightened-state duration each level.

## Player Controls
| Key | Action |
|-----|--------|
| Arrow Up / `W` | Move Up |
| Arrow Down / `S` | Move Down |
| Arrow Left / `A` | Move Left |
| Arrow Right / `D` | Move Right |
| `Q` | Quit game |
| `P` | Pause game |

## Enemies & Obstacles
| Enemy | ASCII Char | Behavior |
|-------|-----------|----------|
| Blinky (Red Ghost) | `R` | Directly chases Pac-Man |
| Pinky (Pink Ghost) | `P` | Targets 4 tiles ahead of Pac-Man |
| Inky (Blue Ghost) | `B` | Unpredictable; uses Blinky's position as a reference |
| Clyde (Orange Ghost) | `O` | Chases when far, scatters when close |
| Walls | `#` | Impassable maze boundaries |

When a ghost is in **frightened mode** (after a Power Pellet is eaten), it is rendered as `F` and can be eaten by Pac-Man.

## Scoring System
| Event | Points |
|-------|--------|
| Eat a dot (pellet) | 10 |
| Eat a Power Pellet | 50 |
| Eat a ghost (1st) | 200 |
| Eat a ghost (2nd) | 400 |
| Eat a ghost (3rd) | 800 |
| Eat a ghost (4th) | 1600 |
| Bonus fruit (Cherry) | 100 |
| Bonus fruit (Strawberry) | 300 |

Ghost eat multiplier resets after each Power Pellet. A bonus life is awarded at 10,000 points.

## Win & Lose Conditions
- **Win (Level Complete):** Eat all dots and Power Pellets in the maze to advance to the next level.
- **Lose a Life:** Pac-Man is touched by a ghost in normal or scatter mode.
- **Game Over:** All lives are lost (player starts with 3 lives).

## Terminal / Curses Implementation Notes

### ASCII Character Map
| Element | Character | Notes |
|---------|-----------|-------|
| Pac-Man | `C` | Can animate between `C` and `(` to suggest mouth |
| Dot (pellet) | `.` | Fills most of the open paths |
| Power Pellet | `*` | Placed in the four maze corners |
| Wall | `#` | Forms the maze boundary and internal dividers |
| Ghost (normal) | `G` or initial letter (`R`, `P`, `B`, `O`) | Color via curses color pairs |
| Ghost (frightened) | `F` | Rendered in blue if terminal supports color |
| Ghost (eaten/eyes) | `e` | Returns to ghost house |
| Bonus fruit | `@` | Appears briefly in the center |
| Ghost house door | `-` | Ghosts exit/enter here |
| Empty path | ` ` (space) | After dot is eaten |

### Curses Rendering Approach
- Use `curses.initscr()` and `curses.curs_set(0)` to hide the cursor.
- Use `curses.color_pair()` to assign distinct colors to each ghost and UI elements if the terminal supports color (`curses.has_colors()`).
- The maze is stored as a 2D list of characters and redrawn each game tick using `stdscr.addstr()`.
- Game loop runs at approximately 10 FPS using `stdscr.timeout(100)` for non-blocking input.
- The maze layout is defined as a multiline string constant and parsed into a grid at startup.
- Ghost AI uses simple pathfinding (BFS or rule-based direction choices) targeting Pac-Man's current or predicted position.
- Score, lives, and level are displayed in a status bar at the top or bottom of the screen using a dedicated curses window or line.
- Minimum recommended terminal size: **28 rows × 56 columns**.
