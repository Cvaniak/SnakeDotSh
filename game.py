from textual.widget import Widget
from textual.message import Message
from rich.segment import Segment
from rich.style import Style
from rich.color import Color
from rich.console import Console
from rich.console import ConsoleOptions
from rich.console import (
    Console,
    ConsoleOptions,
    RenderResult,
    RenderableType,
)
from game_objects import Player, PlayerStatus


class Display:
    def __init__(self, w=60, h=60):
        self.matrix = [[Color.from_rgb(y, x, 0) for y in range(h)] for x in range(w)]
        self.w = w
        self.h = h

    def update(self):
        w, h = self.w, self.h
        for y in range(h):
            for x in range(w):
                self.matrix[y][x] = Color.from_rgb(y, x, 0)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        for y in range(0, self.h, 2):
            for x in range(self.w):
                bgcolor = self.matrix[y][x]
                color = self.matrix[y + 1][x]

                yield Segment("▄", Style(bgcolor=bgcolor, color=color))
            yield Segment.line()


class Game(Widget):
    """The digital display of the calculator."""

    def __init__(self, player: Player, w=60, h=60, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_interval(0.03, self.update)
        self.set_interval(0.2, self.compute)
        self.display = Display(w, h)
        self.player = player
        self.w = w
        self.h = h

    async def compute(self):
        self.player.move()
        if self.player.message:
            await self.player_status_change(self.player.message)
            self.player.message = []

    def update(self):
        self.display.update()
        if self.player:
            self.player.display(self.display.matrix)
        self.refresh()

    def render(self) -> RenderableType:
        return self.display

    async def player_status_change(self, message_list):
        await self.emit(PlayerStatus(self, message_list))
