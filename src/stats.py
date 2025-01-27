import sqlite3
from functools import partial

from src.app_module import ozellikler, icon_directory, aylar_sozlugu, cursor, conn

from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QHBoxLayout


class Stats(QDialog):

    def change(self,change_year):
        button = self.sender()

        if button == self.prev_button:
            change_year -= 1
        else:
            change_year += 1

        cursor.execute(f"update change set ChangeStatsYear = ?",(change_year,))

        conn.commit()

        self.restart()

    def customize_widget(self, widget, geometry=(0, 0), features=(25, "transparent", "black"), border=0, text=""):
        widget.setFixedSize(geometry[0], geometry[1])
        widget.setStyleSheet(
            ozellikler(boyut=features[0], arkaplan_rengi=features[1], renk=features[2]) + "border: {}px "
                                                                                          "solid black;border-radius: 15px; box-shadow: 0 0 10px "
                                                                                          "rgba(255, 255, 255, 0.7);".format(
                border))
        widget.setText(text)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.v_box = QVBoxLayout()
        self.h_box = QHBoxLayout()

        self.yearly_water_intake_list = list()
        self.yearly_read_pages_list = list()

        self.init_ui()

    def create_label(self,geometry):
        label = QLabel(self)
        self.customize_widget(widget=label,geometry=geometry,border=3)
        return label

    def create_graphic(self):
        i = 0
        max_intake_value = max(self.yearly_water_intake_list)
        max_pages_value = max(self.yearly_read_pages_list)

        while i < 2:
            table = self.create_label((720,550))
            self.h_box.addWidget(table)
            i += 1

        while i < 26:
            x = i*60
            empty_bar = self.create_label((35,450))
            if i < 14:
                empty_bar.setGeometry(x-50,273,35,450)
            else:
                empty_bar.setGeometry(x,273,35,450)
            i += 1
        i = 2
        while i < 26:
            try:
                x = i*60
                month_number = i - 14
                if i< 14:
                    y = int(273 * 1.64 * (self.yearly_water_intake_list[month_number]) / max_intake_value)
                    filled_bar = self.create_label((35, y))
                    filled_bar.setStyleSheet(ozellikler(
                        arkaplan_rengi="blue") + "border: 0px " + "solid black;border-radius: 15px; box-shadow: 0 0 10px "
                                                                  "rgba(255, 255, 255, 0.7);")
                    filled_bar.setGeometry(x-50,720-y,35,y)
                else:
                    y = int(273 * 1.64 * (self.yearly_read_pages_list[month_number]) / max_pages_value)
                    filled_bar = self.create_label((35, y))
                    filled_bar.setStyleSheet(ozellikler(
                        arkaplan_rengi="brown") + "border: 0px " + "solid black;border-radius: 15px; box-shadow: 0 0 10px "
                                                                  "rgba(255, 255, 255, 0.7);")
                    filled_bar.setGeometry(x, 720 - y, 35, y)
            except ZeroDivisionError:
                y = 0
            i += 1
    def restart(self):
        self.close()
        stats = Stats()
        stats.exec_()
        del stats

    def sum_of_Water(self):
        yearly_water_intake = list()
        month = 1
        while month < 13:
            sum = 0
            that_month = aylar_sozlugu.get(month) + " " + str(self.year)
            try:
                cursor.execute(f"select WaterIntake from water where Date like '%{that_month}%'")
                data = cursor.fetchall()
                for water_tuple in data:
                    for water_intake in water_tuple:
                        sum += water_intake
                if sum == int(sum):
                    sum = int(sum)
            except sqlite3.OperationalError:
                pass

            yearly_water_intake.append(sum)
            month += 1

        return yearly_water_intake

    def sum_of_pages(self):
        yearly_read_pages = list()
        month = 1
        while month < 13:
            sum = 0
            that_month = aylar_sozlugu.get(month) + " " + str(self.year)
            try:
                cursor.execute(f"select PageCount from pages where Date like '%{that_month}%'")
                data = cursor.fetchall()
                for page_tuple in data:
                    for water_intake in page_tuple:
                        sum += water_intake

                if sum == int(sum):
                    sum = int(sum)

            except sqlite3.OperationalError:
                pass

            yearly_read_pages.append(sum)
            month += 1
        return yearly_read_pages

    def init_ui(self):
        """self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(icon_directory+"yearly_goals1.png"))
        self.photo.setGeometry(QRect(0, 0, 1600, 900))"""

        v_box = QVBoxLayout()
        h_box1 = QHBoxLayout()
        h_box2 = QHBoxLayout()

        cursor.execute("select ChangeStatsYear from change")
        change_year = cursor.fetchone()[0]


        self.year = QDate.currentDate().year() + change_year

        self.year_label = QLabel(self)
        self.customize_widget(widget=self.year_label,geometry=(200,50),features=(60,"transparent","black"),text=str(self.year))

        self.prev_button = QPushButton()
        self.prev_button.setObjectName("prev")

        self.next_button = QPushButton()
        self.next_button.setObjectName("next")

        self.yearly_water_intake_list = self.sum_of_Water()
        self.yearly_read_pages_list = self.sum_of_pages()

        buttons = [self.prev_button, self.next_button]

        h_box2.addStretch()
        for button in buttons:
            button.setIcon(QIcon(icon_directory+button.objectName() + ".png"))
            button.setIconSize(QSize(50, 50))
            button.setStyleSheet(ozellikler(arkaplan_rengi="transparent") +
                                 "border: 1px solid black;"
                                 "border-radius: 15px;"
                                 "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);")
            h_box2.addWidget(button)
            button.clicked.connect(partial(self.change,change_year))
        h_box2.addStretch()

        h_box1.addStretch()
        h_box1.addWidget(self.year_label)
        h_box1.addStretch()

        self.create_graphic()

        v_box.addLayout(h_box1)
        v_box.addStretch()
        v_box.addLayout(self.h_box)
        v_box.addStretch()
        v_box.addLayout(h_box2)

        self.setLayout(v_box)

        self.setWindowTitle("İSTATİSTİKLER")

        self.setWindowIcon(QIcon(icon_directory+"stats_icon.png"))
        self.setFixedSize(1600, 900)