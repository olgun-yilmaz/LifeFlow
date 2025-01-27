import sys
from PyQt5.QtWidgets import QApplication

from src.calendar import Ajanda


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ajanda = Ajanda()
    sys.exit(app.exec_())