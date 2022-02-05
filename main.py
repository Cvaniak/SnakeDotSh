from rich.align import Align
from rich.console import (
    RenderableType,
)

from rich.align import Align
from rich.console import RenderableType

from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import Footer, Header
from textual import events

from textual.app import App
from rich.panel import Panel

from game_objects import PlayerStatus, Player
from game import Game


class StatusWidget(Widget):
    alive: Reactive = Reactive(True)
    points: Reactive = Reactive(0)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                (
                    f"Alive: [b red]{self.alive}[/b red] :red_heart:"
                    f"\n\n\n\n"
                    f"Points: [b red]{self.points}[/b red] :glowing_star:"
                ),
                vertical="middle",
            ),
            title="Status",
            style="yellow",
        )


class Layout(GridView):
    def __init__(
        self,
        w: int,
        h: int,
        game: Game,
        player: Player,
        status: StatusWidget,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.w = w
        self.h = h
        self.game = game
        self.player = player
        self.status = status

    def on_mount(self) -> None:

        # Attributes to store the current calculation
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(1)
        self.grid.set_align("center", "center")

        # One pixel in y is twice size
        w, h = self.w, self.h // 2
        # Create rows / columns / areas
        self.grid.add_column("gamw", min_size=w, max_size=w)
        self.grid.add_row("gamh", min_size=h, max_size=h)
        self.grid.add_column("panel", max_size=30)
        self.grid.add_areas(game="gamw,gamh", panel="panel,gamh")
        # Place out widgets in to the layout
        self.grid.place(game=self.game)
        self.grid.place(panel=self.status)


class SimpleApp(App):
    async def action_up(self) -> None:
        self.player.direction((-1, 0))

    async def action_down(self) -> None:
        self.player.direction((1, 0))

    async def action_right(self) -> None:
        self.player.direction((0, 1))

    async def action_left(self) -> None:
        self.player.direction((0, -1))

    async def action_reset(self) -> None:
        self.player.reset()

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "reset()", "Reset")
        await self.bind("k", "up()", "Up")
        await self.bind("j", "down()", "Down")
        await self.bind("h", "left()", "Left")
        await self.bind("l", "right()", "Right")

    async def on_mount(self) -> None:
        w, h = 60, 60
        self.status = StatusWidget()
        self.player = Player(w, h)
        self.game = Game(self.player, w, h)
        self.layout = Layout(w, h, self.game, self.player, self.status)

        style_fh = "white on rgb(111,22,44)"
        await self.view.dock(Header(style=style_fh), edge="top")
        # Fix style of footer
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.layout, edge="left")

    async def handle_player_status(self, message: PlayerStatus):
        if "Reset" in message.message_list:
            self.status.alive = True
            self.status.points = 0
        if "Die" in message.message_list:
            self.status.alive = False
        if "Eat" in message.message_list:
            self.status.points += 1


SimpleApp.run()
