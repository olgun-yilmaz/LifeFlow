from functools import partial
from src.app_module import ozellikler, icon_directory, cursor

from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QWidget,QPushButton, QLineEdit, QLabel

from datetime import datetime
#gerekli modüller import ediliyor.

class Go(QWidget): # yıllar arası geçiş yapılmasını sağlayan pencere sınıfı

    def __init__(self):
        super().__init__()
        self.now = datetime.now()
        self.that_year = datetime.strftime(self.now, "%Y") # içinde bulunulan yıl
        self.entered_year = int(self.that_year)  # gidilecek yılın default değeri
        self.init_ui()


    # go butonu fonksiyonu
    def click(self): 

        if not self.text_area.text() == "": # girdi yapılmadığı takdirde işlem yapma.
            fix = int(self.that_year) - (int(self.that_year) % 1000) #  ilk iki basamak bulunuyor.
            self.entered_year = fix + int(self.text_area.text()) # son iki basamağa göre gidilecek yıl
            go = self.entered_year - int(self.that_year) # gidilmek istenen yılın, içinde bulunulan yıldan uzaklığı
            cursor.execute(f"update change set ChangeYear = {go}")
        self.close() # Go penceresi görevini tamamladı ve kapatılıyor.


    # yalnızca iki basamak girilmesini sağlayan fonksiyon.
    def max_character(self, text_edit): 
            text = text_edit.text()
            if len(text) > 2:
                text_edit.setText(text[:2])
                text_edit.setCursorPosition(2) # imleç son basamakta kalsın.

    # Widget özelleştirme
    def customize_widget(self, widget, geometry = (0,0,0,0), features=(30,"transparent","black"), text =""):
        widget.setGeometry(QRect(geometry[0],geometry[1],geometry[2],geometry[3]))
        widget.setStyleSheet(ozellikler(boyut=features[0],arkaplan_rengi=features[1],renk=features[2])+"border-radius: 15px; "
                                   "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);")
        widget.setText(text)

    def init_ui(self):
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap(icon_directory+"calendar_wallp1.jpg")) # pencere arka planı
        self.background.setGeometry(0, 0, 400,400)

        self.go_button = QPushButton(self)
        self.go_button.setIcon(QIcon(icon_directory+"go.png"))
        self.go_button.setIconSize(QSize(120,60))

        self.customize_widget(widget=self.go_button,geometry=(150,120,120,60))

        self.text_area = QLineEdit(self) # son iki basamağın girildiği kısım
        self.customize_widget(widget=self.text_area,geometry=(260,45,60,30),text=str(int(self.that_year)-2000))

        int_validator = QIntValidator(10, 99, self) # tam sayı ve iki basamak kontrolü yapılıyor
                                                    # örneğin siz 4 girdiğinizde  04 olarak alıyor
                                                    # ve 2004 yılına gidiyorsunuz.
        self.text_area.setValidator(int_validator)
        self.text_area.setFocus() # pencere input alanına tıklanmış halde açılıyor.

        self.stabil_label = QLabel(self) # sabit olarak ilk iki haneyi tutan label
        self.customize_widget(widget=self.stabil_label,geometry=(218,46,60,30),text="20")

        self.info = QLabel(self) # yıl yazısını tutan label
        self.customize_widget(widget=self.info,geometry=(100,30,120,60),text="YIL : ")

        self.text_area.textChanged.connect(partial(self.max_character, self.text_area)) # kontrol bağlantısı
        self.go_button.clicked.connect(self.click) # buton bağlantısı

        self.setWindowIcon(QIcon(icon_directory+"go.png")) # pencere ikonu

        self.setFixedSize(400,200) # sabit pencere boyutu

        self.setWindowTitle("YILLAR ARASI GEÇİŞ")

        self.show()
