from textual.widget import Widget
from textual.message import Message
from rich.color import Color
from collections import deque
import random


class PlayerStatus(Message):
    def __init__(self, sender: Widget, message_list):
        super().__init__(sender)
        self.message_list = message_list


class Player:
    def __init__(self, w, h) -> None:
        self.map_size = (h, w)
        self.set_player()

        self.message = []

    def set_player(self):
        self.facing: tuple = (0, 1)
        self.prev_facing: tuple = (0, 1)
        x, y = self.map_size
        x, y = x // 2, y // 2
        w = [(y, x - 1), (y, x), (y, x + 1)]
        self.body: deque = deque(w)
        self.body_set: set = set(w)
        self.color: Color = Color.from_rgb(0, 10, 40)
        self.alive: bool = True

        self.set_food()

    def set_food(self):
        self.food = Food(self.map_size, self)

    @staticmethod
    def c_tup(t1, t2):
        return any([x == -y for x, y in zip(t1, t2)])

    def die(self):
        self.color = Color.from_rgb(255, 0, 0)
        self.alive = False
        self.message.append("Die")

    def eat(self):
        self.food.set_food(self.body)
        self.message.append("Eat")

    def move(self):
        if not self.alive:
            return
        self.prev_facing = self.facing
        new_pos = tuple(map(sum, zip(self.body[-1], self.facing)))
        # If end of map
        if not all([0 <= x < xx for x, xx in zip(new_pos, self.map_size)]):
            self.die()
            return

        # If food
        if new_pos == self.food.pos:
            self.eat()
        else:
            p = self.body.popleft()
            self.body_set.remove(p)

        # If eating it self
        if new_pos in self.body_set:
            self.die()
            return

        self.body.append(new_pos)
        self.body_set.add(new_pos)

    def direction(self, tup):
        if self.c_tup(tup, self.prev_facing):
            return
        self.facing = tup

    def reset(self):
        self.set_player()
        self.message.append("Reset")

    def segment_color(self, num, x, y):
        if not self.alive:
            return Color.from_rgb(255, 0, 0)

        r, g, b = self.color.get_truecolor()
        n = len(self.body)
        h, w = self.map_size
        # r, g, b = (min(r, 255), min(g + num, 255), min(b + num * 2, 255))
        return Color.from_rgb(255 - y * 4, 255 - x * 4, 60 + min(num * 10, 180))

    def display(self, mat):
        w, h = len(mat[0]), len(mat)
        for i, xy in enumerate(self.body):
            yy, xx = xy
            if 0 <= xx < w and 0 <= yy < h:
                mat[yy][xx] = self.segment_color(i, xx, yy)

        self.food.display(mat)


class Food:
    def __init__(self, map_size, snake: Player) -> None:
        self.map_size = map_size
        self.set_food(snake.body_set)

    def set_food(self, snake_body):
        # Very dirty
        while True:
            rx = random.randint(0, self.map_size[1])
            ry = random.randint(0, self.map_size[0])
            pos = (ry, rx)
            if pos not in snake_body:
                self.pos = pos
                break
        self.color: Color = Color.from_rgb(100, 100, 255)

    def display(self, mat):
        mat[self.pos[0]][self.pos[1]] = self.color
