import curses
import random
import time
import json

class DodgerGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        self.score_file = "dodger_scores.json"
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        
        self.reset_game()

    def fetch_leaderboard(self):
        try:
            with open(self.score_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def commit_score(self):
        if self.score == 0:
            return
            
        board = self.fetch_leaderboard()
        board.append(self.score)
        board.sort(reverse=True)
        top_five = board[:5]
        
        try:
            with open(self.score_file, "w") as f:
                json.dump(top_five, f)
        except IOError:
            pass

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
        
        self.rocks = []
        self.beams = []
        self.max_beams = 3  
        
        self.buffs = []            
        self.spread_active = False  
        self.spread_expiry = 0     

    def process_input(self):
        next_key = self.stdscr.getch()
        
        if next_key in (ord('p'), ord('P')):
            self.paused = not self.paused
            return
            
        if next_key in (ord('q'), ord('Q')):
            self.game_over = True
            return

        if not self.paused:
            if next_key == curses.KEY_LEFT:
                self.player_x = max(2, self.player_x - 2)
            elif next_key == curses.KEY_RIGHT:
                self.player_x = min(self.sw - 4, self.player_x + 2)
            elif next_key == ord(' '):  
                if self.spread_active:
                    if len(self.beams) <= 6:
                        self.beams.append([self.player_y - 1, self.player_x - 1])
                        self.beams.append([self.player_y - 1, self.player_x])     
                        self.beams.append([self.player_y - 1, self.player_x + 1]) 
                else:
                    if len(self.beams) < self.max_beams:
                        self.beams.append([self.player_y - 1, self.player_x])

    def update_logic(self):
        if self.paused: return

        active_beams = []
        for beam_y, beam_x in self.beams:
            beam_y -= 1
            if beam_y > 0:  
                active_beams.append([beam_y, beam_x])
        self.beams = active_beams

        falling_rocks = []
        for rock_y, rock_x in self.rocks:
            rock_y += 1 
            
            if rock_y == self.player_y and (self.player_x - 1 <= rock_x <= self.player_x + 1):
                self.game_over = True
                return
                
            if rock_y >= self.sh - 1:
                self.score += 1
                if self.score % 10 == 0:
                    self.spawn_rate = min(40, self.spawn_rate + 2)
                    self.speed = max(40, self.speed - 5)
            else:
                falling_rocks.append([rock_y, rock_x])
                
        self.rocks = falling_rocks
        
        rocks_after_hit = []
        spent_beams = set()
        
        for rock_y, rock_x in self.rocks:
            destroyed = False
            for idx, (beam_y, beam_x) in enumerate(self.beams):
                if idx in spent_beams: 
                    continue
                
                if beam_x == rock_x and (beam_y == rock_y or beam_y == rock_y - 1):
                    destroyed = True
                    spent_beams.add(idx)
                    self.score += 2  
                    
                    if random.random() < 0.15:
                        self.buffs.append([rock_y, rock_x])
                    break
                
            if not destroyed:
                rocks_after_hit.append([rock_y, rock_x])
                
        self.rocks = rocks_after_hit
        self.beams = [b for idx, b in enumerate(self.beams) if idx not in spent_beams]
        
        falling_buffs = []
        for buff_y, buff_x in self.buffs:
            buff_y += 1
            if buff_y == self.player_y and (self.player_x - 1 <= buff_x <= self.player_x + 1):
                self.spread_active = True
                self.spread_expiry = time.time() + 5.0 
                self.score += 5
            elif buff_y < self.sh - 1:
                falling_buffs.append([buff_y, buff_x])
        self.buffs = falling_buffs

        if self.spread_active and time.time() > self.spread_expiry:
            self.spread_active = False
        
        if random.randint(1, 100) <= self.spawn_rate:
            spawn_x = random.randint(1, self.sw - 2)
            self.rocks.append([1, spawn_x])

    def draw(self):
        self.stdscr.clear()
        
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        self.stdscr.addstr(0, 2, f" Score: {self.score} ")
        
        if self.spread_active:
            self.stdscr.addstr(0, 15, " Shots: [ SPREAD ] ")
        else:
            available_ammo = self.max_beams - len(self.beams)
            self.stdscr.addstr(0, 15, f" Shots: {'|' * available_ammo:<3} ")
            
        if self.paused:
            self.stdscr.addstr(self.sh // 2, self.sw // 2 - 4, " PAUSED ")
        self.stdscr.attroff(curses.color_pair(3))

        self.stdscr.attron(curses.color_pair(4))
        for beam_y, beam_x in self.beams:
            try: self.stdscr.addch(beam_y, beam_x, '|')
            except curses.error: pass
        self.stdscr.attroff(curses.color_pair(4))

        self.stdscr.attron(curses.color_pair(5))
        for buff_y, buff_x in self.buffs:
            try: self.stdscr.addch(buff_y, buff_x, 'W')
            except curses.error: pass
        self.stdscr.attroff(curses.color_pair(5))

        self.stdscr.attron(curses.color_pair(2))
        for rock_y, rock_x in self.rocks:
            try: self.stdscr.addch(rock_y, rock_x, '*')
            except curses.error: pass
        self.stdscr.attroff(curses.color_pair(2))

        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(self.player_y, self.player_x - 1, self.ship_sprite)
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))
        
        self.stdscr.refresh()

    def show_game_over_screen(self):
        self.commit_score()
        board = self.fetch_leaderboard()
        
        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        
        center_y = self.sh // 2
        
        msg_crash = " CRASHED! "
        msg_score = f" Final Score: {self.score} "
        
        self.stdscr.addstr(center_y - 6, (self.sw - len(msg_crash)) // 2, msg_crash)
        self.stdscr.addstr(center_y - 5, (self.sw - len(msg_score)) // 2, msg_score)
        
        if board:
            self.stdscr.addstr(center_y - 3, (self.sw - 13) // 2, "TOP 5 SCORES:")
            for rank, run_score in enumerate(board, 1):
                row = f"{rank}. {run_score}"
                self.stdscr.addstr(center_y - 2 + rank, (self.sw - len(row)) // 2, row)

        msg_prompt = " Press 'R' to Restart or 'Q' to Quit "
        self.stdscr.addstr(center_y + 5, (self.sw - len(msg_prompt)) // 2, msg_prompt)
        
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
            else:
                self.show_game_over_screen()

def main(stdscr):
    game = DodgerGame(stdscr)
    game.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing Asteroid Dodger!")
