import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.theme import apply_palette, DARK
from ui.icons import app_icon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Explorador de Archivos")
    app.setWindowIcon(app_icon())
    apply_palette(app, DARK)
    window = MainWindow()
    window.setWindowIcon(app_icon())
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()