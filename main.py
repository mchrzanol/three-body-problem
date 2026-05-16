# Plik startowy aplikacji - tu uruchamiamy program

import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg

from gui import ThreeBodyWindow


def main():
    # Ustawienia jakości renderowania
    pg.setConfigOptions(antialias=True, useOpenGL=False)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ThreeBodyWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
