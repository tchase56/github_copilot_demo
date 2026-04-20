# Pac-Man Implementation Instructions

Implement a fully playable Pac-Man game in Python using the `curses` library based on the game description in `pacman.md`. Save the implementation to `pacman.py`.

---

## Project Requirements

- Language: Python 3
- Library: `curses` (standard library, no external dependencies)
- Output file: `pacman.py`
- Entry point: `if __name__ == "__main__": curses.wrapper(main)`
- Follow all docstring and type hint conventions defined in the repository's `copilot-instructions.md`.

---

## Maze Layout

Define the maze as a multiline string constant `MAZE` (28 rows × 28 columns of cells, each cell rendered as 2 characters wide for readability). Parse it into a 2D list at startup.

Use the following ASCII characters:
| Char | Meaning |
|------|---------|
| `#`  | Wall |
| `.`  | Dot (pellet) |
| `*`  | Power Pellet |
| ` `  | Empty path (no dot) |
| `-`  | Ghost house door |
| `G`  | Ghost house interior (spawn zone) |

Place Power Pellets (`*`) near the four corners of the open maze area. The ghost house is a small enclosed room in the center of the maze with a single `-` door tile at the top.

---

## ASCII Character Map (Rendering)

| Element | Char | curses Color Pair |
|---------|------|------------------|
| Pac-Man | `C` / `(` (alternating) | Yellow on Black |
| Dot | `.` | White on Black |
| Power Pellet | `*` | White on Black (bold) |
| Wall | `#` | Blue on Black |
| Blinky (ghost) | `R` | Red on Black |
| Pinky (ghost) | `P` | Magenta on Black |
| Inky (ghost) | `B` | Cyan on Black |
| Clyde (ghost) | `O` | Yellow on Black |
| Frightened ghost | `F` | Blue on Black |
| Eaten ghost (eyes) | `e` | White on Black |
| Bonus fruit | `@` | Green on Black |
| Ghost house door | `-` | White on Black |

---

## Game State

Maintain the following state variables:

- `maze`: `list[list[str]]` — current maze grid (dots removed as eaten)
- `pacman`: `dict` with keys `row`, `col`, `dir` (current direction), `next_dir` (buffered input)
- `ghosts`: `list[dict]` — each with `row`, `col`, `dir`, `mode` (`chase`, `scatter`, `frightened`, `eaten`), `name`, `char`, `color_pair`
- `score`: `int`
- `lives`: `int` (start: 3)
- `level`: `int` (start: 1)
- `dots_remaining`: `int`
- `frightened_timer`: `int` (ticks remaining in frightened mode)
- `ghost_eat_multiplier`: `int` (resets to 1 after each Power Pellet)
- `fruit_timer`: `int` (ticks fruit is visible; 0 = not visible)
- `fruit_pos`: `tuple[int, int]`
- `game_over`: `bool`
- `paused`: `bool`
- `tick`: `int` (frame counter for animations)

---

## Game Loop

Use `stdscr.timeout(100)` for a ~10 FPS loop. Each iteration:

1. Read input (`stdscr.getch()`).
2. Handle `q` → quit, `p` → toggle pause.
3. Buffer directional input into `pacman['next_dir']`.
4. If not paused:
   a. Move Pac-Man (apply `next_dir` if valid, else continue current dir).
   b. Check dot/Power Pellet/fruit collection.
   c. Move ghosts.
   d. Check Pac-Man ↔ ghost collisions.
   e. Decrement timers (`frightened_timer`, `fruit_timer`).
   f. Check win condition (all dots eaten).
5. Render the frame.

---

## Movement & Collision

- Pac-Man and ghosts cannot move through `#` walls.
- Pac-Man can pass through the ghost house door (`-`) only when respawning.
- Implement **tunnel wrap**: if a row has open space at column 0 or the last column, moving off one edge wraps to the other.
- A move is valid if the target cell is not `#` (and not `-` for normal Pac-Man movement).

---

## Ghost AI

Implement four ghost modes:

### Chase Mode
- **Blinky**: Target = Pac-Man's exact position.
- **Pinky**: Target = 4 tiles ahead of Pac-Man in his current direction.
- **Inky**: Target = 2 tiles ahead of Pac-Man, reflected through Blinky's position.
- **Clyde**: If distance to Pac-Man > 8 tiles, target Pac-Man. Else, target scatter corner (bottom-left).

### Scatter Mode
Each ghost targets a fixed corner of the maze:
- Blinky → top-right
- Pinky → top-left
- Inky → bottom-right
- Clyde → bottom-left

Alternate between Chase (20 ticks) and Scatter (7 ticks) automatically each level cycle.

### Frightened Mode
- Ghost moves randomly at intersections (no backtracking preferred).
- Duration: `max(6, 10 - level)` seconds worth of ticks.
- Render as `F`.

### Eaten Mode
- Ghost returns to ghost house using BFS shortest path.
- Render as `e`.
- On reaching ghost house, reset to Chase mode.

For all non-frightened/eaten modes, use **BFS** to find the shortest path toward the target tile and take the first step. Ghosts cannot reverse direction unless forced.

---

## Scoring

Apply these point values immediately when events occur:

| Event | Points |
|-------|--------|
| Eat dot | 10 |
| Eat Power Pellet | 50 |
| Eat ghost (1st) | 200 |
| Eat ghost (2nd) | 400 |
| Eat ghost (3rd) | 800 |
| Eat ghost (4th) | 1600 |
| Bonus fruit (Cherry, level 1) | 100 |
| Bonus fruit (Strawberry, level 2+) | 300 |

- `ghost_eat_multiplier` doubles with each ghost eaten per Power Pellet; resets on next Power Pellet or level.
- Award a bonus life at 10,000 points (once per game).

---

## Fruit

- Fruit appears at the ghost house door position after 70 dots are eaten.
- It remains visible for 100 ticks (~10 seconds), then disappears.
- Eating the fruit awards points and hides it immediately.

---

## Level Progression

When `dots_remaining == 0`:
1. Increment `level`.
2. Reset maze to original layout (all dots restored).
3. Reset Pac-Man and ghosts to starting positions.
4. Increase ghost speed (reduce move-every-N-ticks threshold by 1, minimum 1).
5. Reduce frightened duration by 1 tick per level (minimum 3 ticks).

---

## Lives & Death

When Pac-Man collides with a non-frightened, non-eaten ghost:
1. Decrement `lives`.
2. If `lives == 0`: set `game_over = True`, show Game Over screen, wait for `q`.
3. Else: reset Pac-Man and all ghosts to starting positions, brief pause before resuming.

---

## Rendering

Use a dedicated `render(stdscr, state)` function:

1. **Status bar (row 0):** `Score: XXXX   Lives: X   Level: X`
2. **Maze (rows 1–N):** Draw each cell using `stdscr.addch()` with appropriate color pair.
3. **Pac-Man:** Draw `C` or `(` alternating every 2 ticks at `(pacman_row + 1, pacman_col)`.
4. **Ghosts:** Draw each ghost's character with its color pair on top of the maze cell.
5. **Fruit:** Draw `@` in green if `fruit_timer > 0`.
6. **Pause overlay:** If paused, print `PAUSED` centered on screen.
7. **Game Over overlay:** Print `GAME OVER — Press Q to quit` centered on screen.

Always call `stdscr.refresh()` at the end of each render pass. Use `try/except curses.error` around draw calls to handle terminal resize gracefully.

---

## Initialization

```python
def main(stdscr: curses.window) -> None:
    curses.curs_set(0)
    curses.start_color()
    # Initialize color pairs per ASCII Character Map table above
    # Parse MAZE string into 2D list
    # Initialize pacman, ghosts, score, lives, level
    # Run game loop
```

Initialize ghosts inside the ghost house, releasing them one-by-one (Blinky immediately, then Pinky after 30 ticks, Inky after 60, Clyde after 90).

---

## Code Structure

Organize the code into the following functions (each with full Google-style docstrings and type hints):

| Function | Purpose |
|----------|---------|
| `parse_maze(maze_str: str) -> list[list[str]]` | Parse MAZE constant into 2D grid |
| `is_wall(maze, row, col) -> bool` | Check if a cell is a wall |
| `valid_move(maze, row, col) -> bool` | Check if Pac-Man can move to a cell |
| `ghost_valid_move(maze, row, col) -> bool` | Check if a ghost can move to a cell |
| `bfs_next_step(maze, start, target, valid_fn) -> tuple[int,int]` | BFS to find next step toward target |
| `move_pacman(state) -> None` | Apply buffered direction and move Pac-Man |
| `move_ghosts(state) -> None` | Move all ghosts according to their mode |
| `check_collisions(state) -> None` | Handle Pac-Man ↔ ghost and item pickups |
| `render(stdscr, state) -> None` | Draw the full game frame |
| `init_state(level: int) -> dict` | Build initial game state for a given level |
| `main(stdscr: curses.window) -> None` | Entry point; runs the game loop |
