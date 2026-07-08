# Asteroid-Dodger

Asteroid Dodger (Terminal Space Shooter)
Dodge asteroids, there is an amo mecanic, and power-ups the game also gets progressively faster.

3-shot ammo limit. Lasers reload instantly if they hit an asteroid, rewarding accuracy, but missed shots force you to wait until they leave the screen.

Destroying asteroids gives a 15% chance to drop a green W (Weapon) power-up. Catch it for a 5-second "Spread Shot" buff with infinite ammo.

The game accelerates and spawn rates increase every 10 points.

Utilizes curses color pairs and precise coordinate tracking for a clean, flicker-free retro aesthetic.

to run 
requires Python 3.

Clone or download the repository.

Open your terminal, navigate to the folder, and run:

Bash
python dodger.py
Windows Users: The standard Python library on Windows does not include curses natively. You will need to install the Windows port before running:

Bash
pip install windows-curses


Controls
Left / Right Arrow Keys: Move your ship (<A>)
Spacebar: Fire Lasers (|)
P: Pause / Unpause
R: Restart (on Game Over screen)
Q: Quit Game
