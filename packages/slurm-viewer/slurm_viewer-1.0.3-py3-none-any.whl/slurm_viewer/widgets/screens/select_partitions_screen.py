from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, SelectionList
from textual.widgets.selection_list import Selection


class SelectPartitionScreen(ModalScreen):
    BINDINGS = [
        ('delete', 'deselect_all'),
        ('insert', 'select_all'),
        ('escape', 'pop_screen')
    ]

    DEFAULT_CSS = """
    SelectPartitionScreen {
        align: center middle;
        width: auto;
        height: auto;
    }
    
    SelectPartitionScreen VerticalScroll {
        max-height: 80%;
        height: auto;
        width: 50;
    }
    
    SelectPartitionScreen SelectionOrderList {
        align: center middle;
        height: 100%;
        width: 100%;
    }
    
    SelectPartitionScreen Horizontal {
        width: auto;
        height: auto;
    }
    
    SelectPartitionScreen Horizontal Button {
        width: 25;
        height: auto;
    }
    """

    def __init__(self, partitions: list[str], selected_partitions: list[str]) -> None:
        super().__init__()
        self.partitions = partitions
        self.selected_partitions = selected_partitions

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            selections = [Selection(x, x, x in self.selected_partitions) for x in self.partitions]
            yield SelectionList[str](*selections)
        with Horizontal():
            yield Button('Ok', variant='success', id='ok')
            yield Button('Cancel', variant='warning', id='cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss(self.result())
        else:
            self.dismiss(None)

    def action_deselect_all(self) -> None:
        self.query_one(SelectionList).deselect_all()

    def action_select_all(self) -> None:
        self.query_one(SelectionList).select_all()

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def result(self) -> list[str]:
        data: list[str] = self.query_one(SelectionList).selected
        return data
