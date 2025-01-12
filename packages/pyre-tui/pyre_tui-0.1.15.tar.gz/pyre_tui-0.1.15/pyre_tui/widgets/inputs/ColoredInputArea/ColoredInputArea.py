import sys

from rich._palettes import EIGHT_BIT_PALETTE, STANDARD_PALETTE, WINDOWS_PALETTE
from rich.color import ANSI_COLOR_NAMES, Color
from rich.style import Style
from textual.widgets import TextArea

from ....logic.Debouncer import Debouncer
from ....logic.GlobalState import GlobalState
from ....logic.RegexLogic import RegexLogic
from ....widgets.widgets.GroupsArea.GroupsArea import GroupsArea
from ....widgets.inputs.SubstitutionInputArea.SubstitutionInputArea import SubstitutionInputArea

IS_WINDOWS = sys.platform == "win32"


class ColoredInputArea(TextArea):
    DEFAULT_CSS = """
    ColoredInputArea {
        width: 50%;
    }
    
    ColoredInputArea:disabled {
        opacity: 100% !important;
    }
    """

    BORDER_TITLE = "Test String"

    BINDINGS = [
        ("escape", "drop_focus_input"),
    ]

    def action_drop_focus_input(self):
        self.disabled = True

        from ....widgets.widgets.Help.Help import Help
        GlobalState().help_ui = [
            ("<Shift + :>", "Commands Input"),
        ]
        self.app.query_one(Help).help_labels = GlobalState().help_ui

    def __init__(self, *args, **kwargs):
        super().__init__(disabled=True, *args, **kwargs)
        self.debouncer = Debouncer(0.5)
        rich_colors = sorted((v, k) for k, v in ANSI_COLOR_NAMES.items())

        for color_number, name in rich_colors:
            palette = self.get_current_pallet(color_number)
            color = palette[color_number]
            self._theme.syntax_styles[name] = Style(color=Color.from_rgb(*color))

    def highlight(
        self, row: int, start_column: int, end_column: int, color: str
    ) -> None:
        self._highlights[row].append((start_column, end_column, color))

    @staticmethod
    def get_current_pallet(color_number):
        if IS_WINDOWS and color_number < 16:
            return WINDOWS_PALETTE
        return STANDARD_PALETTE if color_number < 16 else EIGHT_BIT_PALETTE

    async def on_text_area_changed(self):
        await self.debouncer.debounce(self.process_input)

    def process_input(self):
        RegexLogic().update_text(self.text)
        self.app.query_one(GroupsArea).groups = GlobalState().groups
        self._highlights.clear()

        if not GlobalState().groups:
            return

        for _, position, _ in GlobalState().groups:
            start, end = position.split("-")
            self.highlight(0, int(start), int(end), "green")
        
        if GlobalState().regex_method == "substitution":
            self.app.query_one(SubstitutionInputArea).output_text = GlobalState().substitution_output
