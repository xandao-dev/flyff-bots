"""Foreground Vision Farm

Farm approach: Using OpenCV it will track the name of the mob.
Currently it's aiming to all lv 150 mobs in Neo Cascada, but it can be extended.
"""
from Bot import Bot
from Gui import Gui
from utils.helpers import print_logo

# Instances
gui = Gui()
bot = Bot()


def main():
    gui.init()
    gui.loop(bot)
    gui.close()


if __name__ == "__main__":
    print_logo("Flyff FVF")
    main()
