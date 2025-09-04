import curses
import random
import time


# Minimalist Snake Game
def main(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    snk_x = sw//4
    snk_y = sh//2
    snake = [ [snk_y, snk_x], [snk_y, snk_x-1], [snk_y, snk_x-2] ]
    food = [sh//2, sw//2]
    w.addch(food[0], food[1], curses.ACS_PI)

    key = curses.KEY_RIGHT
    score = 0

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        if key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
            pass
        else:
            break

        new_head = [snake[0][0], snake[0][1]]
        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1

        snake.insert(0, new_head)

        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [random.randint(1, sh-2), random.randint(1, sw-2)]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        if (snake[0][0] in [0, sh] or
            snake[0][1] in [0, sw] or
            snake[0] in snake[1:]):
            msg = f"Game Over! Score: {score}"
            w.addstr(sh//2, sw//2-len(msg)//2, msg)
            w.refresh()
            time.sleep(2)  # Pause for 2 seconds
            w.getch()
            break

        w.addch(snake[0][0], snake[0][1], '#')

if __name__ == "__main__":
    curses.wrapper(main)
