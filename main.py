import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow, apply_palette, DARK


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Explorador de Archivos")
    apply_palette(app, DARK)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()