"""Foreground Vision Farm

Farm approach: Using OpenCV it will track the name of the mob.
Currently it's aiming to all lv 150 mobs in Neo Casdadia, but it can be extended.
"""
from threading import Thread

from utils.helpers import print_logo
from Gui import Gui
from Bot import Bot

# Instances
gui = Gui("DarkAmber")
bot = Bot()


def main():
    gui_window = gui.init()
    Thread(target=bot.farm_thread, args=(gui_window,), daemon=True).start()
    gui.loop(bot)
    gui.close()


if __name__ == "__main__":
    print_logo("Flyff FVF")
    main()
