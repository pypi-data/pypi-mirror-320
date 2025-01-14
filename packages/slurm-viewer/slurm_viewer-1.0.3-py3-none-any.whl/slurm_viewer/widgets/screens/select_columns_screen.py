from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import SelectionList, Button
from textual.widgets.selection_list import Selection


class SelectColumnsScreen(ModalScreen):
    BINDINGS = [
        ('delete', 'deselect_all'),
        ('insert', 'select_all'),
        ('escape', 'pop_screen')
    ]

    DEFAULT_CSS = """
    SelectColumnsScreen {
        align: center middle;
        width: auto;
        height: auto;
    }
    
    SelectColumnsScreen VerticalScroll {
        max-height: 80%;
        height: auto;
        width: 50;
    }
    
    SelectColumnsScreen SelectionOrderList {
        align: center middle;
        height: 100%;
        width: 100%;
    }
    
    SelectColumnsScreen Horizontal {
        height: auto;
        width: auto;
    }
    
    SelectColumnsScreen Button {
        width: 25;
        height: auto;
    }
    """

    def __init__(self, selected_columns: list[str], remaining_columns: list[str]) -> None:
        super().__init__()
        self.selected_columns = selected_columns
        self.remaining_columns = remaining_columns

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            selections = [Selection(x, x, True) for x in self.selected_columns]
            selections.extend([Selection(x, x, False) for x in self.remaining_columns])

            yield SelectionList[str](*selections)
        with Horizontal():
            yield Button('Ok', variant='success', id='ok')
            yield Button('Cancel', variant='warning', id='cancel')

    def action_deselect_all(self) -> None:
        self.query_one(SelectionList).deselect_all()

    def action_select_all(self) -> None:
        self.query_one(SelectionList).select_all()

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss(self.result())
        else:
            self.dismiss(None)

    def result(self) -> list[str]:
        data: list[str] = self.query_one(SelectionList).selected
        return data
