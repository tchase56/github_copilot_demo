"""Pac-Man implemented in Python using the curses library."""

import curses
import random
from collections import deque

# ---------------------------------------------------------------------------
# Maze definition
# ---------------------------------------------------------------------------

MAZE_STR = """\
############################
#*...........##...........*#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#..........................#
#.####.##.########.##.####.#
#.####.##.########.##.####.#
#......##....##....##......#
######.##### ## #####.######
######.##### ## #####.######
######.##          ##.######
######.## ###--### ##.######
######.## #GGGGGG# ##.######
      .   #GGGGGG#   .      
######.## #GGGGGG# ##.######
######.## ######## ##.######
######.##          ##.######
######.## ######## ##.######
######.## ######## ##.######
#............##............#
#.####.#####.##.#####.####.#
#.####.#####.##.#####.####.#
#*..##.......  .......##..*#
###.##.##.########.##.##.###
###.##.##.########.##.##.###
#......##....##....##......#
#.##########.##.##########.#
#.##########.##.##########.#
#*.........................*#
############################"""

# Pac-Man and ghost starting positions (row, col) in maze coordinates
PACMAN_START = (23, 14)
GHOST_STARTS = [
    {"name": "blinky", "char": "R", "color_pair": 2, "row": 13, "col": 13, "release_tick": 0},
    {"name": "pinky",  "char": "P", "color_pair": 3, "row": 14, "col": 13, "release_tick": 30},
    {"name": "inky",   "char": "B", "color_pair": 4, "row": 13, "col": 14, "release_tick": 60},
    {"name": "clyde",  "char": "O", "color_pair": 5, "row": 14, "col": 14, "release_tick": 90},
]

# Color pair indices
COLOR_DEFAULT   = 1  # White on Black
COLOR_BLINKY    = 2  # Red on Black
COLOR_PINKY     = 3  # Magenta on Black
COLOR_INKY      = 4  # Cyan on Black
COLOR_CLYDE     = 5  # Yellow on Black
COLOR_PACMAN    = 6  # Yellow on Black
COLOR_WALL      = 7  # Blue on Black
COLOR_FRIGHTENED = 8 # Blue on Black (bright)
COLOR_FRUIT     = 9  # Green on Black

DIRS = {
    "UP":    (-1,  0),
    "DOWN":  ( 1,  0),
    "LEFT":  ( 0, -1),
    "RIGHT": ( 0,  1),
}

OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

SCATTER_CORNERS = {
    "blinky": (0,  27),
    "pinky":  (0,   0),
    "inky":   (29, 27),
    "clyde":  (29,  0),
}

FRUIT_DOT_THRESHOLD = 70
FRUIT_DURATION = 100
GHOST_RELEASE_ROW = 11  # row just above ghost house door


# ---------------------------------------------------------------------------
# Maze helpers
# ---------------------------------------------------------------------------

def parse_maze(maze_str: str) -> list[list[str]]:
    """Parse the MAZE_STR constant into a 2D list of characters.

    Args:
        maze_str (str): The multiline maze string.

    Returns:
        list[list[str]]: 2D grid where each element is a single character.
    """
    lines = maze_str.split("\n")
    # Pad all lines to the same width
    width = max(len(line) for line in lines)
    return [list(line.ljust(width)) for line in lines]


def is_wall(maze: list[list[str]], row: int, col: int) -> bool:
    """Check whether a maze cell is a wall.

    Args:
        maze (list[list[str]]): The 2D maze grid.
        row (int): Row index.
        col (int): Column index.

    Returns:
        bool: True if the cell is a wall (#).
    """
    rows = len(maze)
    cols = len(maze[0])
    if row < 0 or row >= rows or col < 0 or col >= cols:
        return True
    return maze[row][col] == "#"


def valid_move(maze: list[list[str]], row: int, col: int) -> bool:
    """Check whether Pac-Man can move to a given cell.

    Pac-Man cannot enter walls or the ghost house door/interior.

    Args:
        maze (list[list[str]]): The 2D maze grid.
        row (int): Target row.
        col (int): Target column.

    Returns:
        bool: True if Pac-Man can occupy this cell.
    """
    rows = len(maze)
    cols = len(maze[0])
    if row < 0 or row >= rows:
        return False
    col = col % cols  # tunnel wrap
    cell = maze[row][col]
    return cell not in ("#", "-", "G")


def ghost_valid_move(maze: list[list[str]], row: int, col: int) -> bool:
    """Check whether a ghost can move to a given cell.

    Ghosts can pass through the ghost house door and interior.

    Args:
        maze (list[list[str]]): The 2D maze grid.
        row (int): Target row.
        col (int): Target column.

    Returns:
        bool: True if a ghost can occupy this cell.
    """
    rows = len(maze)
    cols = len(maze[0])
    if row < 0 or row >= rows:
        return False
    col = col % cols
    return maze[row][col] != "#"


def bfs_next_step(
    maze: list[list[str]],
    start: tuple[int, int],
    target: tuple[int, int],
    valid_fn,
) -> tuple[int, int]:
    """Find the next step from start toward target using BFS.

    Args:
        maze (list[list[str]]): The 2D maze grid.
        start (tuple[int, int]): Starting (row, col).
        target (tuple[int, int]): Target (row, col).
        valid_fn: Callable(maze, row, col) -> bool for move validity.

    Returns:
        tuple[int, int]: The (row, col) of the first step toward the target,
            or start if no path exists.
    """
    cols = len(maze[0])
    if start == target:
        return start

    visited = {start}
    # Queue items: (current_pos, first_step)
    queue: deque[tuple[tuple[int, int], tuple[int, int]]] = deque()

    for direction in DIRS.values():
        nr, nc = start[0] + direction[0], (start[1] + direction[1]) % cols
        if valid_fn(maze, nr, nc) and (nr, nc) not in visited:
            visited.add((nr, nc))
            queue.append(((nr, nc), (nr, nc)))

    while queue:
        pos, first = queue.popleft()
        if pos == target:
            return first
        for direction in DIRS.values():
            nr, nc = pos[0] + direction[0], (pos[1] + direction[1]) % cols
            if valid_fn(maze, nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), first))

    return start  # no path found, stay put


# ---------------------------------------------------------------------------
# State initialisation
# ---------------------------------------------------------------------------

def init_state(level: int, score: int = 0, lives: int = 3, bonus_life_awarded: bool = False) -> dict:
    """Build the initial game state for a given level.

    Args:
        level (int): Current level number (1-indexed).
        score (int): Carry-over score between levels.
        lives (int): Carry-over life count.
        bonus_life_awarded (bool): Whether the 10k bonus life has been given.

    Returns:
        dict: Complete game state dictionary.
    """
    maze = parse_maze(MAZE_STR)
    dots_remaining = sum(row.count(".") + row.count("*") for row in maze)

    # Find ghost house door position for fruit spawn
    fruit_pos = (0, 0)
    for r, row in enumerate(maze):
        for c, ch in enumerate(row):
            if ch == "-":
                fruit_pos = (r, c)
                break

    ghosts = []
    for g in GHOST_STARTS:
        ghosts.append({
            "name":        g["name"],
            "char":        g["char"],
            "color_pair":  g["color_pair"],
            "row":         g["row"],
            "col":         g["col"],
            "dir":         "UP",
            "mode":        "house",       # waiting inside ghost house
            "release_tick": g["release_tick"],
            "move_counter": 0,
        })

    ghost_speed = max(1, 3 - (level - 1))  # move every N ticks
    frightened_duration = max(30, 100 - (level - 1) * 10)

    return {
        "maze":                maze,
        "original_maze":       parse_maze(MAZE_STR),
        "pacman":              {"row": PACMAN_START[0], "col": PACMAN_START[1], "dir": "LEFT", "next_dir": "LEFT"},
        "ghosts":              ghosts,
        "score":               score,
        "lives":               lives,
        "level":               level,
        "dots_remaining":      dots_remaining,
        "frightened_timer":    0,
        "frightened_duration": frightened_duration,
        "ghost_eat_multiplier": 1,
        "fruit_timer":         0,
        "fruit_pos":           fruit_pos,
        "fruit_spawned":       False,
        "game_over":           False,
        "paused":              False,
        "tick":                0,
        "ghost_speed":         ghost_speed,
        "phase_timer":         0,   # ticks in current scatter/chase phase
        "phase":               "scatter",  # scatter or chase
        "bonus_life_awarded":  bonus_life_awarded,
        "dots_eaten":          0,
    }


# ---------------------------------------------------------------------------
# Pac-Man movement
# ---------------------------------------------------------------------------

def move_pacman(state: dict) -> None:
    """Apply the buffered direction input and advance Pac-Man one tile.

    Args:
        state (dict): The current game state (mutated in place).
    """
    maze = state["maze"]
    pac = state["pacman"]
    cols = len(maze[0])

    dr, dc = DIRS[pac["next_dir"]]
    nr, nc = pac["row"] + dr, (pac["col"] + dc) % cols
    if valid_move(maze, nr, nc):
        pac["dir"] = pac["next_dir"]
        pac["row"], pac["col"] = nr, nc
    else:
        # Try to continue in current direction
        dr, dc = DIRS[pac["dir"]]
        nr, nc = pac["row"] + dr, (pac["col"] + dc) % cols
        if valid_move(maze, nr, nc):
            pac["row"], pac["col"] = nr, nc


# ---------------------------------------------------------------------------
# Ghost movement
# ---------------------------------------------------------------------------

def _ghost_target(ghost: dict, state: dict) -> tuple[int, int]:
    """Compute the target tile for a ghost in chase or scatter mode.

    Args:
        ghost (dict): The ghost state dictionary.
        state (dict): The full game state.

    Returns:
        tuple[int, int]: Target (row, col).
    """
    pac = state["pacman"]
    maze = state["maze"]
    rows = len(maze)
    cols = len(maze[0])

    if state["phase"] == "scatter":
        return SCATTER_CORNERS[ghost["name"]]

    # Chase mode targets
    name = ghost["name"]
    if name == "blinky":
        return (pac["row"], pac["col"])
    elif name == "pinky":
        dr, dc = DIRS[pac["dir"]]
        return (pac["row"] + 4 * dr, (pac["col"] + 4 * dc) % cols)
    elif name == "inky":
        blinky = next((g for g in state["ghosts"] if g["name"] == "blinky"), None)
        dr, dc = DIRS[pac["dir"]]
        pivot_r = pac["row"] + 2 * dr
        pivot_c = (pac["col"] + 2 * dc) % cols
        if blinky:
            target_r = pivot_r + (pivot_r - blinky["row"])
            target_c = (pivot_c + (pivot_c - blinky["col"])) % cols
            return (max(0, min(rows - 1, target_r)), target_c)
        return (pac["row"], pac["col"])
    else:  # clyde
        dist = abs(ghost["row"] - pac["row"]) + abs(ghost["col"] - pac["col"])
        if dist > 8:
            return (pac["row"], pac["col"])
        return SCATTER_CORNERS["clyde"]


def move_ghosts(state: dict) -> None:
    """Move all ghosts according to their current mode and AI.

    Args:
        state (dict): The current game state (mutated in place).
    """
    maze = state["maze"]
    cols = len(maze[0])
    tick = state["tick"]

    # Update scatter/chase phase
    if state["frightened_timer"] == 0:
        state["phase_timer"] += 1
        if state["phase"] == "scatter" and state["phase_timer"] >= 70:
            state["phase"] = "chase"
            state["phase_timer"] = 0
        elif state["phase"] == "chase" and state["phase_timer"] >= 200:
            state["phase"] = "scatter"
            state["phase_timer"] = 0

    for ghost in state["ghosts"]:
        # Handle ghost house release
        if ghost["mode"] == "house":
            if tick >= ghost["release_tick"]:
                ghost["mode"] = "scatter"
                ghost["row"] = GHOST_RELEASE_ROW
                ghost["col"] = 14
                ghost["dir"] = "LEFT"
            continue

        # Throttle ghost speed
        ghost["move_counter"] = ghost.get("move_counter", 0) + 1
        speed = state["ghost_speed"]
        if ghost["mode"] == "frightened":
            speed = max(speed + 1, 3)
        if ghost["move_counter"] < speed:
            continue
        ghost["move_counter"] = 0

        if ghost["mode"] == "eaten":
            # Return to ghost house
            house_center = (13, 13)
            next_pos = bfs_next_step(maze, (ghost["row"], ghost["col"]), house_center, ghost_valid_move)
            if next_pos == (ghost["row"], ghost["col"]) or next_pos == house_center:
                ghost["mode"] = "chase"
                ghost["row"], ghost["col"] = house_center
            else:
                ghost["row"], ghost["col"] = next_pos
            continue

        if ghost["mode"] == "frightened":
            # Move randomly, prefer no backtracking
            opposite = OPPOSITE[ghost["dir"]]
            options = []
            for dname, (dr, dc) in DIRS.items():
                nr, nc = ghost["row"] + dr, (ghost["col"] + dc) % cols
                if ghost_valid_move(maze, nr, nc) and dname != opposite:
                    options.append((dname, nr, nc))
            if not options:
                # Allow backtracking as fallback
                for dname, (dr, dc) in DIRS.items():
                    nr, nc = ghost["row"] + dr, (ghost["col"] + dc) % cols
                    if ghost_valid_move(maze, nr, nc):
                        options.append((dname, nr, nc))
            if options:
                chosen = random.choice(options)
                ghost["dir"] = chosen[0]
                ghost["row"], ghost["col"] = chosen[1], chosen[2]
            continue

        # Chase / scatter: BFS toward target, no reversing
        target = _ghost_target(ghost, state)
        opposite = OPPOSITE[ghost["dir"]]

        # Build valid positions excluding reverse
        best = None
        best_dist = float("inf")
        for dname, (dr, dc) in DIRS.items():
            if dname == opposite:
                continue
            nr, nc = ghost["row"] + dr, (ghost["col"] + dc) % cols
            if ghost_valid_move(maze, nr, nc):
                dist = abs(nr - target[0]) + abs(nc - target[1])
                if dist < best_dist:
                    best_dist = dist
                    best = (dname, nr, nc)
        if best is None:
            # Forced to reverse
            dr, dc = DIRS[opposite]
            nr, nc = ghost["row"] + dr, (ghost["col"] + dc) % cols
            if ghost_valid_move(maze, nr, nc):
                best = (opposite, nr, nc)

        if best:
            ghost["dir"] = best[0]
            ghost["row"], ghost["col"] = best[1], best[2]


# ---------------------------------------------------------------------------
# Collision & item pickup
# ---------------------------------------------------------------------------

def check_collisions(state: dict) -> None:
    """Handle all collisions: Pac-Man eating items and ghost interactions.

    Args:
        state (dict): The current game state (mutated in place).
    """
    maze = state["maze"]
    pac = state["pacman"]
    pr, pc = pac["row"], pac["col"]
    cell = maze[pr][pc]

    # Eat dot
    if cell == ".":
        maze[pr][pc] = " "
        state["score"] += 10
        state["dots_remaining"] -= 1
        state["dots_eaten"] += 1

    # Eat Power Pellet
    elif cell == "*":
        maze[pr][pc] = " "
        state["score"] += 50
        state["dots_remaining"] -= 1
        state["dots_eaten"] += 1
        state["frightened_timer"] = state["frightened_duration"]
        state["ghost_eat_multiplier"] = 1
        for ghost in state["ghosts"]:
            if ghost["mode"] not in ("house", "eaten"):
                ghost["mode"] = "frightened"
                ghost["move_counter"] = 0

    # Eat fruit
    if state["fruit_timer"] > 0 and (pr, pc) == state["fruit_pos"]:
        points = 100 if state["level"] == 1 else 300
        state["score"] += points
        state["fruit_timer"] = 0

    # Decrement frightened timer
    if state["frightened_timer"] > 0:
        state["frightened_timer"] -= 1
        if state["frightened_timer"] == 0:
            for ghost in state["ghosts"]:
                if ghost["mode"] == "frightened":
                    ghost["mode"] = state["phase"]

    # Fruit spawn
    if not state["fruit_spawned"] and state["dots_eaten"] >= FRUIT_DOT_THRESHOLD:
        state["fruit_timer"] = FRUIT_DURATION
        state["fruit_spawned"] = True
    if state["fruit_timer"] > 0:
        state["fruit_timer"] -= 1

    # Ghost collisions
    for ghost in state["ghosts"]:
        if ghost["row"] == pr and ghost["col"] == pc:
            if ghost["mode"] == "frightened":
                ghost["mode"] = "eaten"
                pts = 200 * state["ghost_eat_multiplier"]
                state["score"] += pts
                state["ghost_eat_multiplier"] *= 2
            elif ghost["mode"] not in ("eaten", "house"):
                _lose_life(state)
                return

    # Bonus life at 10,000 points
    if not state["bonus_life_awarded"] and state["score"] >= 10000:
        state["lives"] += 1
        state["bonus_life_awarded"] = True


def _lose_life(state: dict) -> None:
    """Handle Pac-Man losing a life.

    Args:
        state (dict): The current game state (mutated in place).
    """
    state["lives"] -= 1
    if state["lives"] <= 0:
        state["game_over"] = True
    else:
        # Reset positions
        state["pacman"] = {"row": PACMAN_START[0], "col": PACMAN_START[1], "dir": "LEFT", "next_dir": "LEFT"}
        for i, ghost in enumerate(state["ghosts"]):
            gdef = GHOST_STARTS[i]
            ghost["row"] = gdef["row"]
            ghost["col"] = gdef["col"]
            ghost["dir"] = "UP"
            ghost["mode"] = "house"
            ghost["release_tick"] = state["tick"] + gdef["release_tick"]
            ghost["move_counter"] = 0
        state["frightened_timer"] = 0
        state["ghost_eat_multiplier"] = 1


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(stdscr: "curses.window", state: dict) -> None:
    """Draw the entire game frame to the terminal.

    Args:
        stdscr (curses.window): The curses window to render into.
        state (dict): The current game state.
    """
    stdscr.erase()
    maze = state["maze"]
    pac = state["pacman"]
    rows = len(maze)
    cols = len(maze[0])
    max_y, max_x = stdscr.getmaxyx()

    # Status bar
    status = (
        f" Score: {state['score']:<6}  Lives: {state['lives']}  Level: {state['level']} "
    )
    try:
        stdscr.addstr(0, 0, status[:max_x - 1], curses.color_pair(COLOR_DEFAULT))
    except curses.error:
        pass

    # Maze
    for r in range(rows):
        for c in range(cols):
            screen_row = r + 1
            screen_col = c
            if screen_row >= max_y or screen_col >= max_x:
                continue
            ch = maze[r][c]
            if ch == "#":
                attr = curses.color_pair(COLOR_WALL) | curses.A_BOLD
            elif ch == ".":
                attr = curses.color_pair(COLOR_DEFAULT)
            elif ch == "*":
                attr = curses.color_pair(COLOR_DEFAULT) | curses.A_BOLD
            elif ch == "-":
                attr = curses.color_pair(COLOR_DEFAULT)
            else:
                attr = curses.color_pair(COLOR_DEFAULT)
            try:
                stdscr.addch(screen_row, screen_col, ch, attr)
            except curses.error:
                pass

    # Fruit
    if state["fruit_timer"] > 0:
        fr, fc = state["fruit_pos"]
        sr, sc = fr + 1, fc
        if 0 < sr < max_y and sc < max_x:
            try:
                stdscr.addch(sr, sc, "@", curses.color_pair(COLOR_FRUIT) | curses.A_BOLD)
            except curses.error:
                pass

    # Ghosts
    for ghost in state["ghosts"]:
        if ghost["mode"] == "house":
            continue
        gr, gc = ghost["row"] + 1, ghost["col"]
        if 0 < gr < max_y and gc < max_x:
            if ghost["mode"] == "frightened":
                gch = "F"
                attr = curses.color_pair(COLOR_FRIGHTENED) | curses.A_BOLD
            elif ghost["mode"] == "eaten":
                gch = "e"
                attr = curses.color_pair(COLOR_DEFAULT)
            else:
                gch = ghost["char"]
                attr = curses.color_pair(ghost["color_pair"]) | curses.A_BOLD
            try:
                stdscr.addch(gr, gc, gch, attr)
            except curses.error:
                pass

    # Pac-Man (animate mouth)
    pac_ch = "C" if (state["tick"] // 2) % 2 == 0 else "("
    pr_s, pc_s = pac["row"] + 1, pac["col"]
    if 0 < pr_s < max_y and pc_s < max_x:
        try:
            stdscr.addch(pr_s, pc_s, pac_ch, curses.color_pair(COLOR_PACMAN) | curses.A_BOLD)
        except curses.error:
            pass

    # Overlays
    if state["paused"]:
        msg = "-- PAUSED --"
        mx = max(0, max_x // 2 - len(msg) // 2)
        my = max_y // 2
        try:
            stdscr.addstr(my, mx, msg, curses.color_pair(COLOR_DEFAULT) | curses.A_BOLD)
        except curses.error:
            pass

    if state["game_over"]:
        msg = "GAME OVER -- Press Q to quit"
        mx = max(0, max_x // 2 - len(msg) // 2)
        my = max_y // 2
        try:
            stdscr.addstr(my, mx, msg, curses.color_pair(COLOR_BLINKY) | curses.A_BOLD)
        except curses.error:
            pass

    stdscr.refresh()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(stdscr: "curses.window") -> None:
    """Entry point for the Pac-Man curses game.

    Initialises curses settings, colour pairs, and runs the main game loop.

    Args:
        stdscr (curses.window): The curses window provided by curses.wrapper.
    """
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # Initialise colour pairs
    curses.init_pair(COLOR_DEFAULT,    curses.COLOR_WHITE,   curses.COLOR_BLACK)
    curses.init_pair(COLOR_BLINKY,     curses.COLOR_RED,     curses.COLOR_BLACK)
    curses.init_pair(COLOR_PINKY,      curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(COLOR_INKY,       curses.COLOR_CYAN,    curses.COLOR_BLACK)
    curses.init_pair(COLOR_CLYDE,      curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(COLOR_PACMAN,     curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(COLOR_WALL,       curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(COLOR_FRIGHTENED, curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(COLOR_FRUIT,      curses.COLOR_GREEN,   curses.COLOR_BLACK)

    stdscr.timeout(100)  # ~10 FPS, non-blocking input

    state = init_state(level=1)

    key_to_dir = {
        curses.KEY_UP:    "UP",
        curses.KEY_DOWN:  "DOWN",
        curses.KEY_LEFT:  "LEFT",
        curses.KEY_RIGHT: "RIGHT",
        ord("w"): "UP",
        ord("s"): "DOWN",
        ord("a"): "LEFT",
        ord("d"): "RIGHT",
    }

    while True:
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        if key in (ord("p"), ord("P")):
            state["paused"] = not state["paused"]

        if key in key_to_dir:
            state["pacman"]["next_dir"] = key_to_dir[key]

        if not state["paused"] and not state["game_over"]:
            state["tick"] += 1
            move_pacman(state)
            check_collisions(state)
            move_ghosts(state)

            # Level complete
            if state["dots_remaining"] <= 0:
                new_level = state["level"] + 1
                state = init_state(
                    level=new_level,
                    score=state["score"],
                    lives=state["lives"],
                    bonus_life_awarded=state["bonus_life_awarded"],
                )

        render(stdscr, state)

        if state["game_over"]:
            # Wait for q to quit
            stdscr.timeout(-1)
            while True:
                k = stdscr.getch()
                if k in (ord("q"), ord("Q")):
                    return
                render(stdscr, state)


if __name__ == "__main__":
    curses.wrapper(main)
