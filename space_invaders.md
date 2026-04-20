# Space Invaders

## Overview
Space Invaders is a classic fixed-shooter arcade game originally released by Taito in 1978. The player controls a laser cannon that moves horizontally across the bottom of the screen, fending off descending waves of alien invaders. The game ends when the aliens reach the bottom of the screen or all player lives are lost.

## Genre
Fixed Shooter

## Gameplay Mechanics
- A grid of alien invaders (5 rows × 11 columns) marches left and right across the screen, descending one row each time they reach a screen edge.
- The aliens progressively speed up as their numbers decrease.
- The player shoots upward at the aliens from the bottom of the screen.
- Four destructible shields near the bottom of the screen provide partial cover from alien fire.
- Occasionally, a mystery UFO flies across the top of the screen for bonus points.
- The game loops with increasing difficulty after all aliens are cleared.

## Player Controls
| Key         | Action            |
|-------------|-------------------|
| `←` / `a`  | Move cannon left  |
| `→` / `d`  | Move cannon right |
| `Space`     | Fire laser        |
| `q`         | Quit game         |

## Enemies & Obstacles
| Element          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Bottom-row aliens | Weakest alien type; worth fewest points.                                   |
| Mid-row aliens   | Medium alien type; worth moderate points.                                   |
| Top-row aliens   | Strongest alien type; worth most points.                                    |
| Alien lasers     | Aliens periodically fire downward at the player.                            |
| Shields          | Four partially destructible barriers; eroded by both player and alien fire. |
| Mystery UFO      | Flies across the top of the screen at random intervals for bonus points.    |

## Scoring System
| Target           | Points       |
|------------------|--------------|
| Bottom-row alien | 10           |
| Mid-row alien    | 20           |
| Top-row alien    | 30           |
| Mystery UFO      | 50–300 (random) |

- Score accumulates as aliens are destroyed.
- A high score is tracked and displayed throughout the game.

## Win & Lose Conditions
**Win:** Clear all aliens from the screen to advance to the next (faster) wave.

**Lose:**
- An alien laser hits the player cannon (lose a life; 3 lives total).
- Any alien reaches the bottom row of the screen.
- All lives are lost — game over.

## Terminal / Curses Implementation Notes

### Screen Layout
```
Score: 0000        Hi: 0000        Lives: ♥ ♥ ♥
[UFO row]          ?????
[Alien grid]       5 rows × 11 columns
[Shields]          ████  ████  ████  ████
[Player row]       ^
```

### ASCII Character Map
| Element           | ASCII Representation |
|-------------------|----------------------|
| Top-row alien     | `\o/`                |
| Mid-row alien     | `(o)`                |
| Bottom-row alien  | `/o\`                |
| Mystery UFO       | `<UFO>`              |
| Player cannon     | `^`                  |
| Player laser      | `\|`                 |
| Alien laser       | `!`                  |
| Shield block      | `#`                  |
| Destroyed block   | ` ` (space)          |

### Curses Implementation Notes
- Use `curses.wrapper()` for safe terminal setup and teardown.
- Use `curses.cbreak()` and `nodelay(True)` for non-blocking key input.
- Maintain a game loop with `time.sleep(0.05)` to control frame rate (~20 FPS).
- Track alien grid positions in a 2D list; redraw only changed cells each frame using `stdscr.addstr()`.
- Shields are stored as 2D char arrays; overwrite individual characters with a space upon hit.
- Use `curses.color_pairs` to differentiate alien rows, shields, the player, and lasers with distinct colors.
- Collision detection: compare row/col coordinates of lasers against alien, shield, and player positions each frame.
- Alien march speed increases by reducing the sleep interval as the alien count decreases.
- UFO spawns on a timer or random interval and traverses row 1 with a fixed horizontal step per frame.
