

from textual.app import App

from .connections import get_connection

from .startsc import StartSc



class IPyTerm(App):
    """An INDI terminal."""

    SCREENS = {"startsc": StartSc}

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]

    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        CONNECTION = get_connection()
        self.push_screen('startsc')
        CONNECTION.app = self
        CONNECTION.startsc = self.get_screen('startsc', StartSc)
        # Check the RXQUE every 0.1 of a second
        self.set_interval(1 / 10, CONNECTION.check_rxque)

    def action_quit(self) -> None:
        """An action to quit the program."""
        CONNECTION = get_connection()
        if CONNECTION.is_alive():
            CONNECTION.txque.put(None)
            CONNECTION.clientthread.join()
        self.exit(0)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
            )
