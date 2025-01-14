"""Provides a logo widget."""
from typing import Final

from rich.text import Text
from textual.app import App, ComposeResult, RenderResult
from textual.geometry import Size
from textual.widget import Widget

# https://github.com/davep/quizzical/blob/main/quizzical/app/widgets/logo.py

BLUE_ON_WHITE: Final[str] = 'color(21) on color(7)'
WHITE_ON_BLUE: Final[str] = 'color(7) on color(21)'

LOGO_TINY: Final[Text] = Text.assemble(
    ('L', BLUE_ON_WHITE), ('K', WHITE_ON_BLUE), ('E', WHITE_ON_BLUE), ('B', BLUE_ON_WHITE),
)

LOGO_SMALL: Final[Text] = Text.assemble(
    ('L', BLUE_ON_WHITE), ('K\n', WHITE_ON_BLUE),
    ('E', WHITE_ON_BLUE), ('B', BLUE_ON_WHITE),
)

LOGO_MEDIUM: Final[Text] = Text.assemble(
    ('   ', BLUE_ON_WHITE), ('   \n', WHITE_ON_BLUE),
    (' L ', BLUE_ON_WHITE), (' K \n', WHITE_ON_BLUE),
    (' E ', WHITE_ON_BLUE), (' B \n', BLUE_ON_WHITE),
    ('   ', WHITE_ON_BLUE), ('   ', BLUE_ON_WHITE),
)

LOGO_LARGE: Final[Text] = Text.assemble(
    ('     ', BLUE_ON_WHITE), ('     \n', WHITE_ON_BLUE),
    ('  L  ', BLUE_ON_WHITE), ('  K  \n', WHITE_ON_BLUE),
    ('     ', BLUE_ON_WHITE), ('     \n', WHITE_ON_BLUE),
    ('     ', WHITE_ON_BLUE), ('     \n', BLUE_ON_WHITE),
    ('  E  ', WHITE_ON_BLUE), ('  B  \n', BLUE_ON_WHITE),
    ('     ', WHITE_ON_BLUE), ('     ', BLUE_ON_WHITE),
)


class LkebLogoTiny(Widget):
    DEFAULT_CSS = """
    LkebLogoSmall {
        width: 4;
        height: 1;
    }
    """

    def render(self) -> RenderResult:  # type: ignore
        return LOGO_TINY

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        del container, viewport, width
        return 1


class LkebLogoSmall(Widget):
    DEFAULT_CSS = """
    LkebLogoSmall {
        width: 4;
        height: 2;
    }
    """

    def render(self) -> RenderResult:  # type: ignore
        return LOGO_SMALL

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        del container, viewport, width
        return 2


class LkebLogoMedium(Widget):
    DEFAULT_CSS = """
    LkebLogoMedium {
        width: 6;
        height: 4;
    }
    """

    def render(self) -> RenderResult:  # type: ignore
        return LOGO_MEDIUM

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        del container, viewport, width
        return 4


class LkebLogoLarge(Widget):
    DEFAULT_CSS = """
    LkebLogoLarge {
        width: 10;
        height: 6;
    }
    """

    def render(self) -> RenderResult:  # type: ignore
        return LOGO_LARGE

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        del container, viewport, width
        return 6


class TestApp(App):
    def compose(self) -> ComposeResult:
        yield LkebLogoSmall()
        yield LkebLogoMedium()
        yield LkebLogoLarge()


if __name__ == "__main__":
    TestApp().run()
