import curses
import random

class DodgerGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Player Ship
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Asteroids
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # UI / Text
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Lasers
        
        self.reset_game()

    def reset_game(self):
        self.stdscr.clear()
        self.score = 0
        self.speed = 100         
        self.spawn_rate = 10     
        self.paused = False
        self.game_over = False
        
        self.player_x = self.sw // 2
        self.player_y = self.sh - 2
        self.ship_sprite = "<A>" 
        
        self.asteroids = []
        self.lasers = []  # New: Track active lasers

    def process_input(self):
        next_key = self.stdscr.getch()
        
        if next_key == ord('p') or next_key == ord('P'):
            self.paused = not self.paused
            return
            
        if next_key == ord('q') or next_key == ord('Q'):
            self.game_over = True
            return

        if not self.paused:
            if next_key == curses.KEY_LEFT:
                self.player_x = max(2, self.player_x - 2)
            elif next_key == curses.KEY_RIGHT:
                self.player_x = min(self.sw - 4, self.player_x + 2)
            elif next_key == ord(' '):  # New: Fire laser on spacebar
                # Spawn laser just above the center of the ship
                self.lasers.append([self.player_y - 1, self.player_x])

    def update_logic(self):
        if self.paused:
            return

        # 1. Move lasers up
        surviving_lasers = []
        for ly, lx in self.lasers:
            ly -= 1
            if ly > 0:  # Keep if it hasn't hit the top of the screen
                surviving_lasers.append([ly, lx])
        self.lasers = surviving_lasers

        # 2. Move asteroids down & check player collision
        surviving_asteroids = []
        for ay, ax in self.asteroids:
            ay += 1 
            
            # Check collision with player
            if ay == self.player_y and (self.player_x - 1 <= ax <= self.player_x + 1):
                self.game_over = True
                return
                
            if ay >= self.sh - 1:
                self.score += 1
                if self.score % 10 == 0:
                    self.spawn_rate = min(40, self.spawn_rate + 2)
                    self.speed = max(40, self.speed - 5)
            else:
                surviving_asteroids.append([ay, ax])
                
        self.asteroids = surviving_asteroids
        
        # 3. Check Laser-Asteroid Collisions
        new_asteroids = []
        lasers_to_remove = set()
        
        for ay, ax in self.asteroids:
            destroyed = False
            for i, (ly, lx) in enumerate(self.lasers):
                if i in lasers_to_remove: 
                    continue
                
                # Check for direct hit OR "tunneling" (they crossed paths this frame)
                if lx == ax and (ly == ay or ly == ay - 1):
                    destroyed = True
                    lasers_to_remove.add(i)
                    self.score += 2  # Bonus points for destroying an asteroid
                    break
                    
            if not destroyed:
                new_asteroids.append([ay, ax])
                
        # Update lists after collisions
        self.asteroids = new_asteroids
        self.lasers = [l for i, l in enumerate(self.lasers) if i not in lasers_to_remove]
        
        # 4. Spawn new asteroids
        if random.randint(1, 100) <= self.spawn_rate:
            spawn_x = random.randint(1, self.sw - 2)
            self.asteroids.append([1, spawn_x])

    def draw(self):
        self.stdscr.clear()
        
        # Draw Border & Score
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        self.stdscr.addstr(0, 2, f" Score: {self.score} ")
        if self.paused:
            self.stdscr.addstr(self.sh // 2, self.sw // 2 - 4, " PAUSED ")
        self.stdscr.attroff(curses.color_pair(3))

        # Draw Lasers (New)
        self.stdscr.attron(curses.color_pair(4))
        for ly, lx in self.lasers:
            try:
                self.stdscr.addch(ly, lx, '|')
            except curses.error:
                pass
        self.stdscr.attroff(curses.color_pair(4))

        # Draw Asteroids
        self.stdscr.attron(curses.color_pair(2))
        for ay, ax in self.asteroids:
            try:
                self.stdscr.addch(ay, ax, '*')
            except curses.error:
                pass
        self.stdscr.attroff(curses.color_pair(2))

        # Draw Player Ship
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(self.player_y, self.player_x - 1, self.ship_sprite)
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))
        
        self.stdscr.refresh()

    def show_game_over_screen(self):
        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        
        msg1 = " CRASHED! "
        msg2 = f" Final Score: {self.score} "
        msg3 = " Press 'R' to Restart or 'Q' to Quit "
        
        self.stdscr.addstr(self.sh // 2 - 1, (self.sw - len(msg1)) // 2, msg1)
        self.stdscr.addstr(self.sh // 2, (self.sw - len(msg2)) // 2, msg2)
        self.stdscr.addstr(self.sh // 2 + 1, (self.sw - len(msg3)) // 2, msg3)
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key in [ord('r'), ord('R')]:
                self.reset_game()
                break
            elif key in [ord('q'), ord('Q')]:
                self.game_over = True
                break

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        
        while not self.game_over:
            self.stdscr.timeout(self.speed)
            self.process_input()
            if not self.game_over:
                self.update_logic()
            if not self.game_over:
                self.draw()

def main(stdscr):
    game = DodgerGame(stdscr)
    game.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing Asteroid Dodger!")
