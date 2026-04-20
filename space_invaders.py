"""Terminal-based Space Invaders game using Python curses."""

import curses
import random
import time
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROWS = 5
COLS = 11
ALIEN_CHARS = ["\\o/", "(o)", "(o)", "/o\\", "/o\\"]
ALIEN_POINTS = [30, 20, 20, 10, 10]
UFO_CHAR = "<UFO>"
PLAYER_CHAR = "^"
PLAYER_LASER_CHAR = "|"
ALIEN_LASER_CHAR = "!"
SHIELD_CHAR = "#"
LIVES_CHAR = "\u2665"  # ♥

# Color pair indices
COLOR_ALIEN_TOP = 1
COLOR_ALIEN_MID = 2
COLOR_ALIEN_BOT = 3
COLOR_PLAYER = 4
COLOR_PLAYER_LASER = 5
COLOR_ALIEN_LASER = 6
COLOR_SHIELD = 7
COLOR_UFO = 8
COLOR_HUD = 9

# Shield layout: 4 shields, each 3 rows × 4 cols of '#'
SHIELD_ROWS = 3
SHIELD_COLS = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def init_colors() -> None:
    """Initialize curses color pairs for all game elements.

    Returns:
        None
    """
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_ALIEN_TOP, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_ALIEN_MID, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_ALIEN_BOT, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_PLAYER, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_PLAYER_LASER, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_ALIEN_LASER, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_SHIELD, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_UFO, curses.COLOR_MAGENTA, -1)
    curses.init_pair(COLOR_HUD, curses.COLOR_WHITE, -1)


def alien_color(row: int) -> int:
    """Return curses color pair attribute for a given alien row index.

    Args:
        row (int): Alien grid row (0–4).

    Returns:
        int: Curses color attribute.
    """
    if row == 0:
        return curses.color_pair(COLOR_ALIEN_TOP)
    elif row in (1, 2):
        return curses.color_pair(COLOR_ALIEN_MID)
    else:
        return curses.color_pair(COLOR_ALIEN_BOT)


# ---------------------------------------------------------------------------
# Game State
# ---------------------------------------------------------------------------


class GameState:
    """Encapsulates the full mutable state of a Space Invaders game session.

    Attributes:
        height (int): Terminal height in rows.
        width (int): Terminal width in columns.
        score (int): Current score.
        hi_score (int): Session high score.
        lives (int): Remaining player lives.
        wave (int): Current wave number (1-based).
        player_col (int): Column of the player cannon.
        player_row (int): Row of the player cannon.
        player_laser (Optional[list[int]]): [row, col] of active player laser, or None.
        alien_grid (list[list[bool]]): 2D grid indicating alive aliens.
        alien_top_row (int): Screen row of the topmost alien grid row.
        alien_left_col (int): Screen column of the leftmost alien grid column.
        alien_dir (int): +1 moving right, -1 moving left.
        alien_lasers (list[list[int]]): List of [row, col] for active alien lasers.
        shields (list[list[list[str]]]): List of 4 shields; each is a 2D char array.
        shield_positions (list[tuple[int, int]]): Top-left (row, col) of each shield.
        ufo_col (Optional[int]): Current column of the UFO, or None if inactive.
        ufo_dir (int): UFO direction (+1 right, -1 left).
        ufo_timer (int): Frames until next UFO spawn.
        alien_fire_timer (int): Frames until next alien fires.
        base_sleep (float): Base frame sleep duration (decreases with wave/alien count).
        game_over (bool): Whether the game has ended.
    """

    def __init__(self, height: int, width: int, hi_score: int = 0) -> None:
        """Initialize a new game state.

        Args:
            height (int): Terminal height.
            width (int): Terminal width.
            hi_score (int): Carried-over high score from previous games.
        """
        self.height = height
        self.width = width
        self.score = 0
        self.hi_score = hi_score
        self.lives = 3
        self.wave = 1
        self.game_over = False

        self.player_row = height - 2
        self.player_col = width // 2
        self.player_laser: Optional[list] = None

        self.alien_grid: list[list[bool]] = [
            [True] * COLS for _ in range(ROWS)
        ]
        self.alien_top_row = 3
        self.alien_left_col = 2
        self.alien_dir = 1

        self.alien_lasers: list[list[int]] = []

        self.shields = self._make_shields()

        self.ufo_col: Optional[int] = None
        self.ufo_dir = 1
        self.ufo_timer = random.randint(200, 400)

        self.alien_fire_timer = 30
        self.base_sleep = 0.05

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _make_shields(self) -> list[list[list[str]]]:
        """Build four shields as 2D character arrays.

        Returns:
            list[list[list[str]]]: Four shields, each SHIELD_ROWS × SHIELD_COLS.
        """
        shields = []
        for _ in range(4):
            shield = [[SHIELD_CHAR] * SHIELD_COLS for _ in range(SHIELD_ROWS)]
            shields.append(shield)
        return shields

    def _shield_positions(self) -> list[tuple[int, int]]:
        """Compute top-left (row, col) screen positions for the four shields.

        Returns:
            list[tuple[int, int]]: Four (row, col) tuples.
        """
        shield_row = self.player_row - 4
        total_shield_width = 4 * SHIELD_COLS + 3 * 4  # shields + gaps of 4
        start_col = (self.width - total_shield_width) // 2
        positions = []
        for i in range(4):
            col = start_col + i * (SHIELD_COLS + 4)
            positions.append((shield_row, col))
        return positions

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def alien_count(self) -> int:
        """Return the number of alive aliens.

        Returns:
            int: Count of alive aliens.
        """
        return sum(1 for row in self.alien_grid for alive in row if alive)

    @property
    def frame_sleep(self) -> float:
        """Return the adjusted sleep time based on remaining aliens and wave.

        Returns:
            float: Sleep duration in seconds.
        """
        total = ROWS * COLS
        remaining = max(1, self.alien_count)
        scale = remaining / total
        # Speed up as aliens die; at minimum ~4× faster than base
        return max(0.01, self.base_sleep * (0.25 + 0.75 * scale))

    def reset_wave(self) -> None:
        """Reset the alien grid and speed for the next wave.

        Returns:
            None
        """
        self.wave += 1
        self.alien_grid = [[True] * COLS for _ in range(ROWS)]
        self.alien_top_row = 3
        self.alien_left_col = 2
        self.alien_dir = 1
        self.alien_lasers = []
        self.player_laser = None
        self.ufo_col = None
        self.ufo_timer = random.randint(200, 400)
        self.base_sleep = max(0.02, self.base_sleep - 0.005)

    def respawn_player(self) -> None:
        """Reset player position after losing a life.

        Returns:
            None
        """
        self.player_col = self.width // 2
        self.player_laser = None


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


def handle_input(stdscr: "curses._CursesWindow", state: GameState) -> bool:
    """Read keyboard input and mutate game state accordingly.

    Args:
        stdscr (curses._CursesWindow): The curses screen window.
        state (GameState): Current game state.

    Returns:
        bool: True if the game should continue, False if the player quit.
    """
    key = stdscr.getch()
    if key == ord("q"):
        return False
    if key in (curses.KEY_LEFT, ord("a")):
        state.player_col = max(0, state.player_col - 1)
    elif key in (curses.KEY_RIGHT, ord("d")):
        state.player_col = min(state.width - 1, state.player_col + 1)
    elif key == ord(" ") and state.player_laser is None:
        state.player_laser = [state.player_row - 1, state.player_col]
    return True


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def update_player_laser(state: GameState) -> None:
    """Move the player laser upward one row.

    Args:
        state (GameState): Current game state.

    Returns:
        None
    """
    if state.player_laser is None:
        return
    state.player_laser[0] -= 1
    if state.player_laser[0] < 0:
        state.player_laser = None


def update_alien_lasers(state: GameState) -> None:
    """Move all alien lasers downward one row and remove those off-screen.

    Args:
        state (GameState): Current game state.

    Returns:
        None
    """
    surviving = []
    for laser in state.alien_lasers:
        laser[0] += 1
        if laser[0] < state.height:
            surviving.append(laser)
    state.alien_lasers = surviving


def update_aliens(state: GameState, frame: int) -> None:
    """March aliens and optionally descend them on edge collision.

    Args:
        state (GameState): Current game state.
        frame (int): Current frame counter (used for march timing).

    Returns:
        None
    """
    # Determine march interval based on remaining aliens
    total = ROWS * COLS
    remaining = max(1, state.alien_count)
    march_every = max(1, int(10 * remaining / total))

    if frame % march_every != 0:
        return

    # Compute leftmost and rightmost alive columns
    alive_cols = [
        c
        for r in range(ROWS)
        for c in range(COLS)
        if state.alien_grid[r][c]
    ]
    if not alive_cols:
        return

    leftmost = state.alien_left_col + min(alive_cols) * 4
    rightmost = state.alien_left_col + max(alive_cols) * 4 + 2  # 3-char wide

    if state.alien_dir == 1 and rightmost >= state.width - 1:
        state.alien_top_row += 1
        state.alien_dir = -1
    elif state.alien_dir == -1 and leftmost <= 0:
        state.alien_top_row += 1
        state.alien_dir = 1
    else:
        state.alien_left_col += state.alien_dir


def update_alien_fire(state: GameState) -> None:
    """Decrement fire timer and spawn a new alien laser when it reaches zero.

    Args:
        state (GameState): Current game state.

    Returns:
        None
    """
    state.alien_fire_timer -= 1
    if state.alien_fire_timer > 0:
        return

    state.alien_fire_timer = random.randint(15, 40)

    # Gather alive aliens in bottom rows first (prefer bottom)
    candidates = []
    for r in range(ROWS - 1, -1, -1):
        for c in range(COLS):
            if state.alien_grid[r][c]:
                candidates.append((r, c))
        if candidates:
            break  # only fire from bottom-most row

    if not candidates:
        return

    r, c = random.choice(candidates)
    laser_row = state.alien_top_row + r + 1
    laser_col = state.alien_left_col + c * 4 + 1  # center of 3-char sprite
    state.alien_lasers.append([laser_row, laser_col])


def update_ufo(state: GameState) -> None:
    """Advance UFO position or spawn a new UFO.

    Args:
        state (GameState): Current game state.

    Returns:
        None
    """
    if state.ufo_col is None:
        state.ufo_timer -= 1
        if state.ufo_timer <= 0:
            state.ufo_dir = random.choice([-1, 1])
            state.ufo_col = 0 if state.ufo_dir == 1 else state.width - len(UFO_CHAR)
            state.ufo_timer = random.randint(200, 400)
    else:
        state.ufo_col += state.ufo_dir
        if state.ufo_col < -len(UFO_CHAR) or state.ufo_col >= state.width:
            state.ufo_col = None


# ---------------------------------------------------------------------------
# Collision Detection
# ---------------------------------------------------------------------------


def check_collisions(state: GameState) -> None:
    """Detect and resolve all collisions for the current frame.

    Args:
        state (GameState): Current game state.

    Returns:
        None
    """
    shield_positions = state._shield_positions()

    # --- Player laser vs aliens ---
    if state.player_laser is not None:
        lr, lc = state.player_laser
        for r in range(ROWS):
            for c in range(COLS):
                if not state.alien_grid[r][c]:
                    continue
                ar = state.alien_top_row + r
                ac = state.alien_left_col + c * 4
                if lr == ar and ac <= lc <= ac + 2:
                    state.alien_grid[r][c] = False
                    state.score += ALIEN_POINTS[r]
                    state.hi_score = max(state.hi_score, state.score)
                    state.player_laser = None
                    break
            else:
                continue
            break

    # --- Player laser vs UFO ---
    if state.player_laser is not None and state.ufo_col is not None:
        lr, lc = state.player_laser
        if lr == 1 and state.ufo_col <= lc < state.ufo_col + len(UFO_CHAR):
            bonus = random.randint(1, 6) * 50
            state.score += bonus
            state.hi_score = max(state.hi_score, state.score)
            state.ufo_col = None
            state.player_laser = None

    # --- Player laser vs shields ---
    if state.player_laser is not None:
        lr, lc = state.player_laser
        for i, (sr, sc) in enumerate(shield_positions):
            for srow in range(SHIELD_ROWS):
                for scol in range(SHIELD_COLS):
                    if (
                        state.shields[i][srow][scol] == SHIELD_CHAR
                        and lr == sr + srow
                        and lc == sc + scol
                    ):
                        state.shields[i][srow][scol] = " "
                        state.player_laser = None
                        break
                else:
                    continue
                break
            if state.player_laser is None:
                break

    # --- Alien lasers vs player ---
    surviving_lasers = []
    for laser in state.alien_lasers:
        lr, lc = laser
        if lr == state.player_row and lc == state.player_col:
            state.lives -= 1
            state.respawn_player()
            if state.lives <= 0:
                state.game_over = True
        else:
            surviving_lasers.append(laser)
    state.alien_lasers = surviving_lasers

    # --- Alien lasers vs shields ---
    surviving_lasers = []
    for laser in state.alien_lasers:
        lr, lc = laser
        hit = False
        for i, (sr, sc) in enumerate(shield_positions):
            for srow in range(SHIELD_ROWS):
                for scol in range(SHIELD_COLS):
                    if (
                        state.shields[i][srow][scol] == SHIELD_CHAR
                        and lr == sr + srow
                        and lc == sc + scol
                    ):
                        state.shields[i][srow][scol] = " "
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
        if not hit:
            surviving_lasers.append(laser)
    state.alien_lasers = surviving_lasers

    # --- Aliens reaching player row ---
    for r in range(ROWS):
        for c in range(COLS):
            if state.alien_grid[r][c]:
                ar = state.alien_top_row + r
                if ar >= state.player_row:
                    state.game_over = True


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def safe_addstr(
    stdscr: "curses._CursesWindow",
    row: int,
    col: int,
    text: str,
    attr: int = 0,
) -> None:
    """Draw text at (row, col) without raising on boundary writes.

    Args:
        stdscr (curses._CursesWindow): The curses screen.
        row (int): Screen row.
        col (int): Screen column.
        text (str): Text to draw.
        attr (int): Curses attribute flags.

    Returns:
        None
    """
    h, w = stdscr.getmaxyx()
    if row < 0 or row >= h:
        return
    if col < 0:
        text = text[-col:]
        col = 0
    if col + len(text) > w:
        text = text[: w - col]
    if not text:
        return
    try:
        stdscr.addstr(row, col, text, attr)
    except curses.error:
        pass


def draw_frame(stdscr: "curses._CursesWindow", state: GameState) -> None:
    """Clear the screen and redraw all game elements for the current frame.

    Args:
        stdscr (curses._CursesWindow): The curses screen.
        state (GameState): Current game state.

    Returns:
        None
    """
    stdscr.erase()
    shield_positions = state._shield_positions()

    # HUD
    lives_str = " ".join([LIVES_CHAR] * state.lives)
    hud = f"Score: {state.score:04d}        Hi: {state.hi_score:04d}        Lives: {lives_str}"
    safe_addstr(stdscr, 0, 0, hud, curses.color_pair(COLOR_HUD) | curses.A_BOLD)

    # UFO
    if state.ufo_col is not None:
        safe_addstr(stdscr, 1, state.ufo_col, UFO_CHAR, curses.color_pair(COLOR_UFO) | curses.A_BOLD)

    # Aliens
    for r in range(ROWS):
        for c in range(COLS):
            if not state.alien_grid[r][c]:
                continue
            ar = state.alien_top_row + r
            ac = state.alien_left_col + c * 4
            safe_addstr(stdscr, ar, ac, ALIEN_CHARS[r], alien_color(r))

    # Shields
    for i, (sr, sc) in enumerate(shield_positions):
        for srow in range(SHIELD_ROWS):
            for scol in range(SHIELD_COLS):
                ch = state.shields[i][srow][scol]
                if ch == SHIELD_CHAR:
                    safe_addstr(stdscr, sr + srow, sc + scol, ch, curses.color_pair(COLOR_SHIELD))

    # Player
    safe_addstr(
        stdscr,
        state.player_row,
        state.player_col,
        PLAYER_CHAR,
        curses.color_pair(COLOR_PLAYER) | curses.A_BOLD,
    )

    # Player laser
    if state.player_laser is not None:
        safe_addstr(
            stdscr,
            state.player_laser[0],
            state.player_laser[1],
            PLAYER_LASER_CHAR,
            curses.color_pair(COLOR_PLAYER_LASER),
        )

    # Alien lasers
    for laser in state.alien_lasers:
        safe_addstr(stdscr, laser[0], laser[1], ALIEN_LASER_CHAR, curses.color_pair(COLOR_ALIEN_LASER))

    stdscr.refresh()


def draw_game_over(stdscr: "curses._CursesWindow", state: GameState) -> None:
    """Display the game-over screen and wait for the player to acknowledge.

    Args:
        stdscr (curses._CursesWindow): The curses screen.
        state (GameState): Final game state.

    Returns:
        None
    """
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    msg1 = "GAME OVER"
    msg2 = f"Final Score: {state.score}"
    msg3 = f"High Score:  {state.hi_score}"
    msg4 = "Press  q  or  Enter  to exit"

    for i, msg in enumerate([msg1, msg2, msg3, msg4]):
        safe_addstr(stdscr, h // 2 - 2 + i, (w - len(msg)) // 2, msg, curses.A_BOLD)

    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("\n"), curses.KEY_ENTER, 10, 13):
            break


# ---------------------------------------------------------------------------
# Main Game Loop
# ---------------------------------------------------------------------------


def run_game(stdscr: "curses._CursesWindow", hi_score: int = 0) -> int:
    """Run a single game session and return the final high score.

    Args:
        stdscr (curses._CursesWindow): The curses screen.
        hi_score (int): High score carried in from a previous session.

    Returns:
        int: Updated high score after this session.
    """
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    h, w = stdscr.getmaxyx()
    state = GameState(h, w, hi_score)

    frame = 0
    while not state.game_over:
        t0 = time.monotonic()

        if not handle_input(stdscr, state):
            break

        update_player_laser(state)
        update_alien_lasers(state)
        update_aliens(state, frame)
        update_alien_fire(state)
        update_ufo(state)
        check_collisions(state)

        if state.alien_count == 0:
            state.reset_wave()

        draw_frame(stdscr, state)

        frame += 1
        elapsed = time.monotonic() - t0
        sleep_time = max(0.0, state.frame_sleep - elapsed)
        time.sleep(sleep_time)

    if state.game_over:
        draw_game_over(stdscr, state)

    return state.hi_score


def main(stdscr: "curses._CursesWindow") -> None:
    """Entry point called by curses.wrapper; manages session high score.

    Args:
        stdscr (curses._CursesWindow): The curses screen provided by wrapper.

    Returns:
        None
    """
    hi_score = 0
    hi_score = run_game(stdscr, hi_score)


if __name__ == "__main__":
    curses.wrapper(main)
