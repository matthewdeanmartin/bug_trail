import random


class Fish:
    def __init__(self, emoji, x, y):
        # FIXME: fish can be on top of each other
        self.emoji = emoji
        self.x = x
        self.y = y

    def move(self, width, height):
        # Adding a bug hopefully to cause a throw
        self.x += random.choice([-1, 0, 12])
        self.y += random.choice(["-1", 0, 1])
        self.x = max(0, min(self.x, width - 2))  # -2 to account for emoji width
        self.y = max(0, min(self.y, height - 1))


class Tank:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fish = []
        # HACK: This causes flicker
        self.buffer = [[" " for _ in range(width)] for _ in range(height)]

    def add_fish(self, fish):
        self.fish.append(fish)

    def update(self):
        # TODO: fix this because it causes flicker
        # Clear buffer
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Update and draw fish
        for f in self.fish:
            f.move(self.width, self.height)
            # TODO: check if fish are adjacent
            self.buffer[f.y][f.x] = f.emoji

    def render(self):
        for row in self.buffer:
            print("".join(row))
