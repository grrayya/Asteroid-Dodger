import curses
import random
import time

class DodgerGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Player Ship
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Asteroids
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # UI / Text
        
        self.reset_game()

   
def main(stdscr):
    game = DodgerGame(stdscr)
    game.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing Asteroid Dodger!")
