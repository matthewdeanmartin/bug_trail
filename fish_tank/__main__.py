# Fish Tank Main File
import logging
import os
import random
import sys
import time

import fish_tank.best_fish as best_fish
from fish_tank.basic_classes import Fish, Tank

logger = logging.getLogger(__name__)


# the hook is called with type, exception, traceback
def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def main():
    logger.info("Starting fish tank")
    os.system("cls" if os.name == "nt" else "clear")

    tank_width, tank_height = 80, 24
    tank = Tank(tank_width, tank_height)

    for _ in range(random.randint(5, 10)):
        fish = Fish(
            random.choice(best_fish.fish), random.randint(0, tank_width - 2), random.randint(0, tank_height - 1)
        )
        if fish.emoji == "🦈":
            logger.warning(f"There is a shark, watch out: {fish}")
        tank.add_fish(fish)

    while True:
        tank.update()
        os.system("cls" if os.name == "nt" else "clear")
        tank.render()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
