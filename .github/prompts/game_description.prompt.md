---
name: 'game_description'
description: 'Generate a detailed markdown description for a video game'
agent: agent
model: Claude Sonnet 4.6 (copilot)
tools: [execute, read, edit, search, web, agent, todo]
---

Your goal is to produce a detailed description of a simple, classic arcade-style video game — in the spirit of Atari games — that can be implemented and run using Python's `curses` library in a terminal. The game must be simple enough to be rendered entirely with ASCII/text characters in a terminal window.

Start by asking the user the following questions (collect all answers before proceeding):

1. **Game name**: What is the title of the game?
2. **Genre**: What simple arcade genre does the game belong to? (e.g., shooter, maze, breakout, snake, pong, platformer)
3. **Core gameplay mechanics**: Describe the main gameplay loop. Keep it simple — think single-screen or scrolling ASCII action (e.g., dodge obstacles, shoot enemies, collect items).
4. **Player controls**: How does the player control the game? (e.g., arrow keys, WASD, spacebar)
5. **Win/lose conditions**: How does the player win or lose? (e.g., survive X seconds, reach a score, lose all lives)
6. **Enemies or obstacles**: What enemies, hazards, or obstacles appear in the game?
7. **Scoring**: Is there a scoring system? How are points earned?
8. **Output filename**: What should the markdown file be named? (e.g., `my-game.md`)

Once you have all the answers, generate a well-structured markdown file with the following sections:

- Title (H1)
- Overview (brief 2–3 sentence summary)
- Genre
- Gameplay Mechanics
- Player Controls
- Enemies & Obstacles
- Scoring System
- Win & Lose Conditions
- Terminal/Curses Implementation Notes (describe how the game would be rendered in a terminal using `curses`, including ASCII character choices for game elements)

Note:
* If the user is describing an existing well known game, attempt to auto populate as many of the sections as possible based on publicly available information about that game.
* Keep the game design simple enough that it can be fully represented with ASCII characters in a terminal window using `curses`.
* If the game cannot be implemented in a terminal using `curses` due to complexity or graphical requirements inform the user. 

Then use your file creation capabilities to write the content to the filename the user specified.
