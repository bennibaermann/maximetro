maximetro
=========

maximetro is a traffic game inspired by Mini Metro(*). It is writen in Python
using Pygame. Should be multi user some day (in the far future).

Stil in early pre-alpha. I plan to make a more strategical game than Mini Metro
is.

Gameplay 
--------

Just click around to get a feeling for the game. You should build stations and lines. Than
railcars run on them and transport passengers to ther destinations. You gain
money for delivered passengers. Building stations and lines costs money.
The buttons at the right delete or add tracks to existing lines.

But keep in mind: The game is stil in very early development. some settings are sometimes more
optimized for development than for actual gameplay.

Installation 
------------

You need python and pygame. Under Debian/Ubuntu and similar systems the
following should work:

	apt-get install python python-pygame 
	git clone https://github.com/bennibaermann/maximetro.git 
	maximetro/maximetro.py 

I have no idea how to install in other systems. But in general you need
python and pygame and than clone the git repository (or download the
zip from github). The underlying technologies (SDL, Pygame, Python) are all 
very portable, so it should be possible to run it more or less on any system
which runs python.

PROBLEM: There is a problem with pygame in the moment. I use a patched version.
Workaround: uncomment the two lines in config.py with OTHERSTATIONS and SHAPES.

Have fun.

(*) http://dinopoloclub.com/minimetro/
