#GEREKLİ MODÜLLER IMPORT EDİLİYOR.
from functools import partial

from src.app_module import get_features, icon_directory, conn, cursor

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QMessageBox, QTextEdit, QDialog, QMenu, QAction, QToolBar, \
    QActionGroup
from datetime import datetime

class Movie:
    def __init__(self, name, year,category,rating,content):
        self.name = name
        self.year = year
        self.category = category
        self.rating = rating
        self.content = content

    __str__ = lambda self: ("{}".format(self.name))


class NewMovie(QDialog):  # film ekleme penceresi sınıfı

    def __init__(self,username,movie_name = str(),year = str(), category = "SEÇ..."):
        super().__init__()
        self.username = username
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.movie_names = list()
        self.area_counter = 0
        self.now = datetime.now()

        self.movie_name = movie_name
        self.year = year
        self.category = category

        self.category_text = "KATEGORİ : "
        self.chosen_category = str()
        self.that_year = int(datetime.strftime(self.now, "%Y"))  # içinde bulunulan yıl
        self.state = False
        self.init_ui()

    def get_category(self):
        toolbar = QToolBar(self)

        action_group = QActionGroup(self)

        action1 = QAction('animasyon', self)

        action2 = QAction('bilim kurgu', self)

        action3 = QAction('dram', self)

        action4 = QAction("gerilim", self)

        action5 = QAction("komedi", self)

        action6 = QAction("korku", self)

        action7 = QAction("macera", self)

        action8 = QAction("romantik", self)

        action9 = QAction("diğer",self)

        action_list = [action1, action2, action3, action4, action5, action6, action7, action8,action9]

        def apply():
            chosen_action = self.sender()
            for action in action_list:
                if action == chosen_action:
                    self.chosen_category = action.text()
                    action.setIcon(QIcon(icon_directory + action.text() + ".png"))
                    self.info_category.setText(self.category_text+self.chosen_category.upper())
                else:
                    action.setIcon(QIcon(icon_directory + "bw_"+action.text() + ".png"))

        for action in action_list:
            action.setIcon(QIcon(icon_directory + "bw_"+action.text() + ".png"))
            action.setToolTip(action.text())
            action.triggered.connect(apply)
            action_group.addAction(action)
            toolbar.addAction(action)

        toolbar.setGeometry(20,200,550,130)
        toolbar.show()

    def get_all_movies(self):
        cursor.execute(f"select * from {self.username}")
        data = cursor.fetchall()
        for i in data:
            self.movie_names.append(i[0])

    def save_movie(self):
        self.get_all_movies()
        self.get_category()
        movie_name = self.movie_name_edit.toPlainText()
        try:
            year = int(self.year_edit.text())
        except ValueError:
            year = 0
        text_length = len(movie_name)
        movie = Movie(name=movie_name, year=year, category=self.chosen_category, rating=-1,content= "")
        if text_length < 3:
            QMessageBox.warning(self, 'Uyarı', 'Karakter uzunluğu 3 ile 108 arasında olmalıdır.')
        elif movie.name in self.movie_names:
            QMessageBox.warning(self, 'Uyarı', 'Film zaten sistemde kayıtlı!')
        elif year > self.that_year or year < 1920:
            QMessageBox.warning(self, "Uyarı", "Lütfen yapım yılını doğru girdiğinizden emin olun!")
        elif self.chosen_category == str():
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kategori seçin!")
        else:
            cursor.execute(f"insert into {self.username} (Name,Year,Category,Rating,Content) values(?,?,?,?,?)",
                           (movie.name, movie.year, movie.category, movie.rating,movie.content,))
            QMessageBox.information(self, "KAYDEDİLDİ", "{} filmi CineLib'e eklendi!".format(movie.name))
            conn.commit()
            self.state = True
            self.close()

    def customize_text_area(self):
        text_length = len(self.movie_name_edit.toPlainText())
        if text_length > 109:
            QMessageBox.warning(self, 'Uyarı', 'Film isminin uzunluğu 5 ile 108 karakter arasında olmalıdır.')


    def customize_widget(self, widget, geometry=(0, 0, 0, 0), features=(25, "transparent", "black"),
                         text=""):  #WIDGETLAR ÖZELLEŞTİRİLİYOR
        widget.setGeometry(QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
        widget.setStyleSheet(
            get_features(size=features[0], background_color=features[1], color=features[2]) + "border-radius: 15px; "
                                                                                          "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);")
        widget.setText(text)

    def init_ui(self):
        """window_background = QLabel(self)
        window_background.setPixmap(QPixmap(icon_directory+"beautiful.jpg"))  #PENCERE ARKA PLANI
        window_background.setGeometry(0, 0, 700,400)"""

        self.ok_button = QPushButton(self)  #BUTON
        self.ok_button.setIcon(QIcon(icon_directory+"ok.png"))
        self.ok_button.setIconSize(QSize(120, 60))

        self.customize_widget(widget=self.ok_button, geometry=(300, 320, 120, 60))

        self.year_edit = QLineEdit(self)  # yapım yılını gir
        self.year_edit.setText(self.year)

        self.movie_name_edit = QTextEdit(self)  # filmin adını
        try:
            self.movie_name_edit.setText(self.movie_name)
        except TypeError:
            pass

        edit_areas = [self.movie_name_edit, self.year_edit]
        for edit_area in edit_areas:
            self.customize_widget(widget=edit_area, geometry=(
            190 + int(self.area_counter * 3 / 5), self.area_counter * 2 + 15, 510 - self.area_counter * 3,
            100 - self.area_counter))
            if self.area_counter == 0:
                edit_area.setTextInteractionFlags(Qt.TextEditorInteraction)
                edit_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                edit_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                edit_area.setFocus()  # PENCERE AÇILIR AÇILMAZ İMLECİN INPUT ALANINDA OLMASINI SAĞLIYOR
                edit_area.textChanged.connect(self.customize_text_area)
            else:
                int_validator = QIntValidator(1920, self.that_year, self)
                edit_area.setValidator(int_validator)
            self.area_counter += 50

        info_movie = QLabel(self)
        self.customize_widget(widget=info_movie, geometry=(20, 10, 160, 60), text="FİLM ADI : ") # film adı yazısı

        info_year = QLabel(self)
        self.customize_widget(widget=info_year, geometry=(20, 120, 250, 40), text="YAPIM YILI : ")

        self.info_category = QLabel(self)
        self.customize_widget(widget=self.info_category,geometry=(20,170,340,100),text=self.category_text+self.category)

        self.ok_button.clicked.connect(self.save_movie)  #BUTON BAĞLANTISI

        self.get_category()

        self.setWindowIcon(QIcon(icon_directory+"movie_icon.png"))  #PENCERE İKONU

        self.setFixedSize(700, 400)  #SABİTLENMİŞ PENCERE BOYUTU

        self.setWindowTitle("FİLM EKLE")
