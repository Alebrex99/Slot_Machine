"""Qt signal bridge for thread-safe GUI updates from the network layer.

The TCP server runs in a background thread and must never call Qt widget
methods directly. Instead it emits signals on this bridge; slots in
MainWindow receive them on the main thread and update the UI safely.

Usage in MainWindow.__init__():
    self.bridge = SignalBridge()
    self.bridge.set_coins_signal.connect(self.on_remote_set_coins)
    self.bridge.send_message_signal.connect(self.on_remote_message)
"""
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBridge(QObject):
    """Carries all signals emitted by the future TCP server thread."""

    # Emitted when researcher sends SET_COINS <amount>
    set_coins_signal = pyqtSignal(float)

    # Emitted when researcher sends SEND_MSG <text>
    send_message_signal = pyqtSignal(str)
