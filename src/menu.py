from src.app_module import ozellikler,icon_directory

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import  QLabel,  QPushButton, QDialog

from src.fixed_schedule import FixedSchedule
from src.library import Library
from src.movies import CinemaLib


class Menu(QDialog): # menü pencere sınıfı

    # Widget özelleştirme
    def customize_widget(self, widget, geometry=(0, 0, 0, 0), features=(25, "transparent", "black"), border=0, text=""):
        widget.setGeometry(QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
        widget.setStyleSheet(ozellikler(boyut=features[0], arkaplan_rengi=features[1], renk=features[2]) + "border: {}px "
                                                                  "solid white;border-radius: 15px; box-shadow: 0 0 10px "
                                                                                "rgba(255, 255, 255, 0.7);".format(border))
        widget.setText(text)

    # kütüphane penceresini açan fonksiyon
    def go_to_library(self):
        library = Library()
        library.exec_()
        del library

    def go_to_cinelib(self):
        cinelib = CinemaLib("user")
        self.close()

    # sabit program penceresini açan fonksiyon
    def go_to_fixed_schedule(self):
        schedule = FixedSchedule()
        schedule.exec_()
        del schedule


    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) #QDialog help kısmı gizleniyor.
        self.init_ui()

    # ekran içeriği oluşturma
    def exists(self,funct,title,index,icon,color): # başlık, icon gibi bilgilerle özelleştiriliyor.
        background = QLabel(self) # buton arka planı
        background.setPixmap(QPixmap(icon_directory + icon))

        button = QPushButton(self) # pencereye bağlayan buton
        button.setText(title)
        button.setStyleSheet(ozellikler(arkaplan_rengi="transparent",renk=color,boyut=50))
        button.clicked.connect(funct)

        if index < 2: #üstteki ikili yerleştiriliyor.
            background.setGeometry(QRect(index*800, 0, 800, 450))
            button.setGeometry(QRect(index*800, 0, 800, 450))
        else: # alttaki ikili yerleştiriliyor.
            background.setGeometry(QRect((index-2)*800, 450, 800, 450))
            button.setGeometry(QRect((index-2)*800, 450, 800, 450))

    def init_ui(self):
        # ekran içeriği oluşturuluyor.
        self.exists(self.go_to_library,"Library",0,"library1.jpg","white")
        self.exists(self.go_to_cinelib, "Movies", 1,"movie1.jpg","white")
        self.exists(self.go_to_library, "Goals", 2,"goal_round1.jpg","white")
        self.exists(self.go_to_fixed_schedule, "Program", 3,"schedule1.jpg","white")

        self.setWindowIcon(QIcon(icon_directory+"menu_icon.png"))
        self.setWindowTitle("MENÜ")
        self.setFixedSize(1600, 900)