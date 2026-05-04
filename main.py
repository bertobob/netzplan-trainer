import sys
from PyQt6.QtWidgets import QApplication
from ui.gui import Gui
from controller import NetzplanController


def main():
    app = QApplication(sys.argv)
    controller = NetzplanController()
    gui = Gui(controller=controller)
    controller.gui = gui
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
