import curses
import random
import time

PLAYER = "A"
INVADER = "M"
BULLET = "|"
EMPTY = " "

INVADER_ROWS = 3
INVADER_COLS = 8

MOVE_DELAY = 0.1
BULLET_DELAY = 0.05


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(0)
    sh, sw = stdscr.getmaxyx()

    # Player
    px = sw // 2
    py = sh - 2

    # Invaders
    invaders = set()
    for row in range(INVADER_ROWS):
        for col in range(INVADER_COLS):
            invaders.add((2 + row, 4 + col * 4))
    invader_dir = 1

    # Bullets
    bullets = []
    score = 0
    last_bullet_time = 0
    last_move_time = 0

    while True:
        stdscr.clear()
        # Draw invaders
        for y, x in invaders:
            stdscr.addstr(y, x, INVADER)
        # Draw player
        stdscr.addstr(py, px, PLAYER)
        # Draw bullets
        for by, bx in bullets:
            stdscr.addstr(by, bx, BULLET)
        # Draw score
        stdscr.addstr(0, 2, f"Score: {score}")
        stdscr.refresh()

        # Input
        key = stdscr.getch()
        if key == ord("q"):
            break
        elif key == curses.KEY_LEFT and px > 0:
            px -= 1
        elif key == curses.KEY_RIGHT and px < sw - 1:
            px += 1
        elif key == ord(" ") and time.time() - last_bullet_time > BULLET_DELAY:
            bullets.append([py - 1, px])
            last_bullet_time = time.time()

        # Move invaders
        if time.time() - last_move_time > MOVE_DELAY:
            edge = False
            for y, x in invaders:
                if (invader_dir == 1 and x >= sw - 2) or (invader_dir == -1 and x <= 1):
                    edge = True
                    break
            new_invaders = set()
            for y, x in invaders:
                if edge:
                    new_invaders.add((y + 1, x))
                else:
                    new_invaders.add((y, x + invader_dir))
            invaders = new_invaders
            if edge:
                invader_dir *= -1
            last_move_time = time.time()

        # Move bullets
        new_bullets = []
        for by, bx in bullets:
            by -= 1
            if by < 1:
                continue
            hit = False
            for iy, ix in list(invaders):
                if (by, bx) == (iy, ix):
                    invaders.remove((iy, ix))
                    score += 1
                    hit = True
                    break
            if not hit:
                new_bullets.append([by, bx])
        bullets = new_bullets

        # Check for game over
        for y, x in invaders:
            if y >= py:
                stdscr.addstr(sh // 2, sw // 2 - 5, "GAME OVER")
                stdscr.refresh()
                time.sleep(2)
                return
        if not invaders:
            stdscr.addstr(sh // 2, sw // 2 - 5, "YOU WIN!")
            stdscr.refresh()
            time.sleep(2)
            return
        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)
