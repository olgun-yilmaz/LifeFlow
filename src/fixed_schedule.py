import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit

from src.app_module import haftanin_gunleri, icon_directory, ozellikler, cursor, conn, create_week_connection


# gerekli modüller import edildi.

class FixedSchedule(QDialog):  # FixedSchedule sınıfı
    def __init__(self): 
        super().__init__()
        self.columnCount = 8  # sütun sayısı
        self.list_length = self.columnCount * len(haftanin_gunleri)

        create_week_connection(list_length=self.list_length)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # QDialog help kısmı gizleniyor.

        self.v_box = QVBoxLayout()

        self.tasks_list = list()  # görev kutucuklarının içeriklerini tutan liste

        self.init_ui()


    def autosave_tasks(self):  # görev kutucuklarının içeriğini otomatik kaydeden fonksiyon

        text_edit = self.sender()  # üzerinde değişiklik yapılan kutucuk
        index = int(text_edit.objectName()) - 1  # kutucuğun indexi

        self.tasks_list[index] = text_edit.toPlainText()  # liste güncelleniyor.

        cursor.execute(f"update week set box_{index} = ? where Date = ?",(text_edit.toPlainText(),"fixed_program"))
        conn.commit()


    def create_week(self):
        width, height = 226, 57  # her bir kutucuğun yatay ve dikey boyutları
        hBoxes = list()

        cursor.execute("select * from week where Date = ?",("fixed_program",))
        data =  cursor.fetchone()
        i = 1
        while i < len(data):
            if data[i] is None:
                box = ""
            else:
                box = data[i]
            self.tasks_list.append(box)
            i += 1

        for i in range(self.columnCount + 1):  # sütun sayısına göre layout oluşturma işlemi
            h_box = QHBoxLayout()
            hBoxes.append(h_box)

        for i in range(7):
            label = QLabel(self)  # tablonun en üst kısmı için label oluşturma işlemi
            label.setFixedSize(width, height + 41)

            self.customize_widget(widget=label, text=haftanin_gunleri[i].upper(),
                                  border=2)  # haftanın günleri için label
            hBoxes[0].addWidget(label)  # aynı hizaya yerleştirme işlemi

        counter = 1

        while counter < self.columnCount + 1:  # tüm sütunlar taranana dek döngüye devam et.
            for i in range(7):
                text_edit = QTextEdit(self)

                text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # kaydırma kapatılıyor.
                text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

                text_edit.setObjectName(str((i + 1) + 7 * (counter - 1)))  # kutucuk numaralandırma

                text_edit.setFixedSize(width, height * 3 // 2 + 15)  # kutucuk boyutları

                content = str()
                try:
                    content = self.tasks_list[i + 7 * (counter - 1)]  # kutucuğun içeriği listeden alınıyor.
                except IndexError:
                    pass

                self.customize_widget(widget=text_edit, features=[25, "transparent", "white"], border=2, text=content)

                hBoxes[counter].addWidget(text_edit)  # kutucuklar yerleştiriliyor.
                text_edit.textChanged.connect(
                    self.autosave_tasks)  # değişiklik yapılması halinde kutucuktaki güncellemeleri kaydeden fonksiyon çağrılıyor.

            counter += 1

        for i in range(self.columnCount + 1):
            self.v_box.addLayout(hBoxes[i])  # satırlar layout'a yerleştiriliyor.

    def customize_widget(self, widget, features=(33, "transparent", "white"), border=0, text=""):
        # widget'ları özelleştiren fonksiyon
        widget.setStyleSheet(
            ozellikler(boyut=features[0], arkaplan_rengi=features[1],
                           renk=features[2]) + "border: {}px solid white".format(border))
        widget.setText(text)

    def init_ui(self):
        self.background = QLabel(self) # arka plan ekleniyor.
        self.background.setPixmap(QPixmap(icon_directory + "technological-exploration-settlement1.jpg"))
        self.background.setFixedSize(1600, 900)
        self.setFixedSize(1600, 900) # arka plan boyutu ve pencere boyutu sabitleniyor.
        self.create_week()
        self.setLayout(self.v_box)
        self.setWindowIcon(QIcon(icon_directory + "calendar_icon.png")) # pencere ikonu
        self.setWindowTitle("FIXED PROGRAM") # pencere başlığı