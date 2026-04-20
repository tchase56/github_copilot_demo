# Space Invaders — Implementation Instructions

Implement a terminal-based Space Invaders game in Python using `curses`, following the specification in [space_invaders.md](../../space_invaders.md).

## Requirements

### File
- Create the implementation in `space_invaders.py` at the project root.
- All functions, classes, and methods must include **Google-style docstrings**.
- All function and method signatures must include **type hints**.

---

## Game Structure

### Entry Point
- Wrap the game in `curses.wrapper(main)` for safe terminal setup and teardown.
- `main(stdscr)` initializes the game state and starts the game loop.

### Game Loop
- Run at approximately 20 FPS using `time.sleep(0.05)`.
- Each frame: handle input → update state → detect collisions → redraw screen.

---

## Screen Layout

```
Score: 0000        Hi: 0000        Lives: ♥ ♥ ♥
<UFO>                                            (row 1, when active)
\o/  \o/  \o/  ...                               (rows 3–7, alien grid)
(o)  (o)  (o)  ...
/o\  /o\  /o\  ...
  ████   ████   ████   ████                      (shields row)
                ^                                (player row, second to last)
```

---

## Components

### Player Cannon
- Represented by `^`.
- Moves left/right along the bottom row.
- Fires a single laser upward (`|`); only one player laser active at a time.
- Has 3 lives, displayed as `♥ ♥ ♥` in the HUD.

### Alien Grid
- 5 rows × 11 columns stored in a 2D list.
- Row types and point values:
  - Row 0 (top): `\o/` — 30 points
  - Rows 1–2 (mid): `(o)` — 20 points
  - Rows 3–4 (bottom): `/o\` — 10 points
- Aliens march left and right; when the leftmost or rightmost alive alien reaches the screen edge, the entire grid descends one row and reverses direction.
- March speed increases as alien count decreases (reduce `time.sleep` interval proportionally).
- Aliens periodically fire lasers (`!`) downward; choose a random alive alien each firing interval.

### Mystery UFO
- Represented by `<UFO>`.
- Spawns at a random interval and traverses row 1 horizontally.
- Awards 50–300 random points when shot.
- Disappears when it exits the screen or is destroyed.

### Shields
- Four shields near the bottom of the screen, each stored as a 2D character array of `#` blocks.
- Individual `#` blocks are destroyed (replaced with a space) on hit by either a player laser or an alien laser.

### Lasers
- **Player laser**: travels upward one row per frame; destroyed on hitting an alien, shield block, or top of screen.
- **Alien lasers**: travel downward one row per frame; destroyed on hitting the player, a shield block, or the bottom of screen.

---

## Collision Detection

Each frame, check:
1. **Player laser vs. aliens**: if laser position matches an alien cell, remove the alien, add points to score, remove the laser.
2. **Player laser vs. UFO**: if laser hits UFO position, award bonus points, remove UFO, remove laser.
3. **Player laser vs. shields**: if laser hits a `#` block, replace with space, remove laser.
4. **Alien lasers vs. player**: if any alien laser matches the player position, decrement lives, reset player position, remove laser.
5. **Alien lasers vs. shields**: same erosion logic as player laser.
6. **Aliens reaching bottom**: if any alien's row ≥ player row, trigger game over.

---

## Controls

| Key          | Action            |
|--------------|-------------------|
| `←` / `a`   | Move cannon left  |
| `→` / `d`   | Move cannon right |
| `Space`      | Fire laser        |
| `q`          | Quit game         |

Use `curses.cbreak()` and `stdscr.nodelay(True)` for non-blocking input.

---

## Colors

Use `curses.color_pairs` to assign distinct colors:
- Top-row aliens: cyan
- Mid-row aliens: green
- Bottom-row aliens: yellow
- Player cannon: white (bold)
- Player laser: white
- Alien lasers: red
- Shields: green
- UFO: magenta
- HUD text: white

---

## Win & Lose Conditions

- **Next wave**: all aliens cleared → reset alien grid with increased base speed, increment wave counter.
- **Lose a life**: player hit by alien laser → decrement lives, brief pause, respawn player.
- **Game over**: lives reach 0 or any alien reaches the player row → display "GAME OVER", show final score, wait for `q` or `Enter` to exit.

---

## High Score
- Track the high score in memory for the session.
- Display alongside the current score in the HUD each frame.
