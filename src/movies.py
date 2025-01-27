import os
import sqlite3
from functools import partial

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, \
    QMessageBox, QCheckBox

from src.add_movie import NewMovie,Movie
from src.app_module import icon_directory, RoundButton, get_features, timer, setcheckbox_icon, userDataFolder, cursor, \
    conn


class CinemaLib(QWidget):
    def __init__(self,username):
        super().__init__()

        self.username = username
        self.current_window_index = int()

        self.create_connection()
        self.v_box = QVBoxLayout()
        self.h_box = QHBoxLayout()

        self.movie_list = list()
        self.rate_box_list = list()
        self.movie_counter = 0
        self.rate_counter = 0

        self.showing_widgets = list()
        self.sort_control = False
        self.init_ui()

    def create_new_push_button(self, icon_name="edit_button", x=25, y=25):
        button = QPushButton(self)
        button.setObjectName(str(self.movie_list[self.movie_counter]))
        button.setIcon(QIcon(icon_directory+icon_name + ".png"))
        button.setIconSize(QSize(x, y))
        button.setStyleSheet(get_features(background_color="transparent"))
        return button

    def create_new_checkbox(self,icon_name = "unrated",x=25,y=25,number=0):
        check_box = QCheckBox(self)
        check_box.setObjectName(str(number)+icon_name)
        check_box.setStyleSheet(get_features(background_color="transparent"))
        return check_box

    def showSearchResults(self,dbQuery):
        cursor.execute(dbQuery)

        data = cursor.fetchall()

        self.movie_counter = 0

        try:
            for i in data:
                movie = Movie(i[1], i[2], i[3], i[4],i[5])
                self.movie_list.append(movie)
        except IndexError:
            pass
        while self.movie_counter < len(self.movie_list):
            movie_name_label = QLabel(self)
            self.customize_widget(widget=movie_name_label, size=(300, 100),
                                  text=str(self.movie_list[self.movie_counter]).upper())

            movie_year_label = QLabel(self)
            self.customize_widget(widget=movie_year_label, size=(50, 100), text=str(self.movie_list[self.movie_counter]
                                                                                    .year))

            movie_category_label = QLabel(self)
            self.customize_widget(widget=movie_category_label, size=(120, 100),
                                  text=self.movie_list[self.movie_counter].category.upper())

            widgets = [movie_name_label, movie_year_label, movie_category_label]
            self.showing_widgets.append(widgets)

            self.search_result_label = QLabel(self)

            rate_box_list = list()  # her filme ait rate grubu ayrı listelerde tutuluyor.

            current_movie = self.movie_list[self.movie_counter]

            for box in range(10):
                rate_box = self.create_new_checkbox(icon_name="unrated", number=self.rate_counter)
                if current_movie.rating >= self.rate_counter:
                    setcheckbox_icon(checkbox=rate_box, path=icon_directory + "rated.png", x=25, y=25)
                else:
                    setcheckbox_icon(checkbox=rate_box, path=icon_directory + "unrated.png", x=25, y=25)
                rate_box_list.append(rate_box)
                widgets.append(rate_box)
                rate_box.clicked.connect(partial(self.get_rate, rate_box_list, current_movie))
                self.rate_counter += 1

            self.rate_counter = 0  # yeni liste için rate sayacı sıfırlanıyor.

            h_box = QHBoxLayout()
            for widget in widgets:
                h_box.addWidget(widget)
                h_box.addStretch()
            h_box.addStretch()
            self.v_box.addLayout(h_box)
            self.movie_counter += 1
        self.v_box.addStretch()
        search_result_layout = QHBoxLayout()
        search_result_layout.addStretch()

        result_text = f"{len(self.movie_list)} sonuç bulundu".upper()
        if len(self.movie_list) == 0:
            result_text = "EŞLEŞEN SONUÇ YOK!"

        while True: # result_label' a text yerleştirilene kadar.
            try:
                self.customize_widget(widget=self.search_result_label, size=(200, 100),
                                      text=result_text)
                break
            except AttributeError:
                self.search_result_label = QLabel(self)

        search_result_layout.addWidget(self.search_result_label)
        self.v_box.addLayout(search_result_layout)


    def search(self,search_bar):
        if search_bar.text().strip() == str():
            pass
        else:
            self.clear_screen()
            self.showSearchResults(dbQuery=f"select * from {self.username} where name like '%{search_bar.text().strip()}%'")

    def clear_screen(self):
        for widgets in self.showing_widgets:
            for widget in widgets:
                widget.setParent(None)
        try:
            self.search_result_label.setParent(None)
        except AttributeError:
            pass
        self.movie_list = list()

    def sort(self):
        self.movie_counter = 0
        button = self.sender()
        type = button.objectName()[:button.objectName().index("-")]

        if self.sort_control:
            dbQuery = f"select * from {self.username} order by {type} DESC limit 10 offset {(self.current_window_index - 1) * 10};"
            self.sort_control = False
        else:
            dbQuery = f"select * from {self.username} order by {type} ASC limit 10 offset {(self.current_window_index - 1) * 10}"
            self.sort_control = True

        self.clear_screen()
        self.show_the_movies(dbQuery=dbQuery)

    def find_the_last_page(self):
        cursor.execute(f"select count(*) from {self.username}")
        movie_count = cursor.fetchone()[0]

        if movie_count == 0:
            return 1
        elif movie_count % 10 == 0:
            return int(movie_count/10)
        else:
            return int(movie_count//10)+1

    def get_active_window_index(self):
        try:
            cursor.execute("select CurrentPage from users where Username = ?",(self.username,))
            self.current_window_index = cursor.fetchone()[0]
        except (sqlite3.OperationalError,TypeError):
            cursor.execute("CREATE TABLE IF NOT EXISTS users (Username TEXT , CurrentPage INT)")
            conn.commit()

            self.current_window_index = 1
            cursor.execute("INSERT INTO users (Username, CurrentPage) VALUES (?,?)",
                           (self.username,self.current_window_index))
            conn.commit()

    def change_window(self):
        button = self.sender()
        control = bool()
        if button.objectName() == "prev" and self.current_window_index > 1:
            self.current_window_index -= 1
            control = True
        elif button.objectName() == "next" and self.current_window_index < self.find_the_last_page():
            self.current_window_index += 1
            control = True
        if control:
            cursor.execute("update users set CurrentPage = ? where Username = ?",
                           (self.current_window_index,self.username))
            conn.commit()
            self.restart()

    def get_rate(self,rate_box_list,movie):
        rate_box = self.sender()
        rating =  int(rate_box.objectName()[0])

        for box in rate_box_list:
            if box == rate_box:
                is_checked = rate_box.objectName()[1:]
                if is_checked == "unrated":
                    rate_box.setObjectName(str(rating)+is_checked[2:])
                else:
                    rate_box.setObjectName(str(rating)+"un"+is_checked)
                    rating = -1
        movie.rating = rating
        cursor.execute(f"update {self.username} set rating = ? where Name = ?",
                            (movie.rating, movie.name,))
        conn.commit()
        for box in rate_box_list:
            if rate_box.objectName()[1:] == "rated":
                if int(box.objectName()[0]) <= rating:
                    box.setChecked(True)
                    setcheckbox_icon(box,path=icon_directory+"rated.png",x=25,y=25)
                else:
                    box.setChecked(False)
                    setcheckbox_icon(box,path=icon_directory+"unrated.png",x=25,y=25)
            else:
                box.setChecked(False)
                setcheckbox_icon(box, path=icon_directory + "unrated.png", x=25, y=25)


    def show_the_movies(self,dbQuery):
        cursor.execute(dbQuery)

        data = cursor.fetchall()

        try:
            for i in data:
                movie = Movie(i[1], i[2], i[3],i[4],i[5])
                self.movie_list.append(movie)
        except IndexError:
            pass
        while self.movie_counter < len(self.movie_list):
            delete_button = self.create_new_push_button(icon_name="delete_button")
            delete_button.clicked.connect(self.del_movie)
            
            edit_button = self.create_new_push_button(icon_name="edit_button")
            edit_button.clicked.connect(self.edit_movie)
            
            movie_name_label = QLabel(self)
            self.customize_widget(widget=movie_name_label,size=(300,100),
                                  text=str(self.movie_counter + 1 + (self.current_window_index-1)*10) + ". " + str(self.movie_list[self.movie_counter]).upper())

            movie_year_label = QLabel(self)
            self.customize_widget(widget=movie_year_label, size=(50, 100),text=str(self.movie_list[self.movie_counter]
                                                                                   .year))

            movie_category_label = QLabel(self)
            self.customize_widget(widget=movie_category_label, size=(120, 100),
                                  text=self.movie_list[self.movie_counter].category.upper())

            widgets = [movie_name_label,movie_year_label,movie_category_label,edit_button,delete_button]
            self.showing_widgets.append(widgets)

            rate_box_list = list() # her filme ait rate grubu ayrı listelerde tutuluyor.

            current_movie = self.movie_list[self.movie_counter]

            for box in range(10):
                rate_box = self.create_new_checkbox(icon_name="unrated",number=self.rate_counter)
                if current_movie.rating >= self.rate_counter:
                    setcheckbox_icon(checkbox=rate_box, path=icon_directory + "rated.png", x=25, y=25)
                else:
                    setcheckbox_icon(checkbox=rate_box, path=icon_directory + "unrated.png", x=25, y=25)
                rate_box_list.append(rate_box)
                widgets.append(rate_box)
                rate_box.clicked.connect(partial(self.get_rate, rate_box_list,current_movie))
                self.rate_counter += 1

            self.rate_counter = 0 # yeni liste için rate sayacı sıfırlanıyor.

            h_box = QHBoxLayout()
            for widget in widgets:
                h_box.addWidget(widget)
                h_box.addStretch()
            h_box.addStretch()
            self.v_box.addLayout(h_box)
            self.v_box.addStretch()
            self.movie_counter += 1
        self.v_box.addStretch()
        self.create_navigation_items()

    def restart(self):
        self.close()
        cine_lib = CinemaLib(self.username)

    def create_navigation_items(self):
        next_button = QPushButton(self)
        next_button.setObjectName("next")
        prev_button = QPushButton(self)
        prev_button.setObjectName("prev")

        self.page_label = QLabel(self)
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setText(str(self.current_window_index)+"/"+str(self.find_the_last_page()))
        self.page_label.setStyleSheet(get_features(size=80,color="white"))

        navigation_widgets = [prev_button,self.page_label,next_button]
        self.showing_widgets.append(navigation_widgets)
        navigation_layout = QHBoxLayout()
        navigation_layout.addStretch()
        for widget in navigation_widgets:
            if widget.objectName() == "prev" or widget.objectName() == "next":
                widget.setIcon(QIcon(icon_directory+widget.objectName()+".png"))
                widget.setIconSize(QSize(50,50))
                widget.clicked.connect(self.change_window)
            navigation_layout.addWidget(widget)
        navigation_layout.addStretch()
        self.v_box.addLayout(navigation_layout)

    def create_connection(self):
        dbQuery = (f"create table if not exists {self.username} (id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT,"
                   f"Year INT,Category TEXT,Rating INT,Content TEXT)")

        cursor.execute(dbQuery)

        conn.commit()

    disconnect = lambda self: conn.close()

    def customize_widget(self, widget, size = (0,0), features=(16, "transparent", "white", 0 , "black"), text=""):
            widget.setFixedSize(size[0],size[1])
            widget.setStyleSheet(
            get_features(size=features[0],background_color=features[1],color=features[2],
                         border=features[3],border_color=features[4]))
            widget.setText(text)

    def add_movie(self, movie_name="",year="",category="SEÇ..."):
        new_movie = NewMovie(username=self.username,movie_name=movie_name,year=str(year),category=category)
        new_movie.exec_()
        if new_movie.state:
            cursor.execute("update users set CurrentPage = ? where Username = ?",
                           (self.find_the_last_page(), self.username))
            conn.commit()
            self.restart()
        del new_movie

    def edit_movie(self):
        movie_name = self.sender().objectName()
        cursor.execute(f"select Year,Category from {self.username} where Name = ?",(movie_name,))
        data = cursor.fetchone()
        year = data[0]
        category = data[1].upper()

        self.add_movie(movie_name=movie_name.upper(),year=year,category=category)

    def del_movie(self):
        movie_name = self.sender().objectName() # silme butonuna filmin adı verilir.
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Onay Penceresi")
        msgBox.setText("{} filmini silmek istediğinizden emin misiniz?".format(movie_name))

        yes_button = msgBox.addButton('Evet', QMessageBox.YesRole)
        no_button = msgBox.addButton('Hayır', QMessageBox.NoRole)

        msgBox.setDefaultButton(no_button)

        msgBox.exec_()

        if msgBox.clickedButton() == yes_button:
            cursor.execute(f"delete from {self.username} where Name = ?", (movie_name,))
            conn.commit()
            QMessageBox.information(self, "SİLME İŞLEMİ", "{} filmi başarıyla silindi!".format(movie_name))
        del msgBox
        self.restart()

    def init_ui(self):
        window_background = QLabel(self)
        window_background.setPixmap(QPixmap(icon_directory+"cinema_background.jpg"))
        window_background.setFixedSize(1600,900)

        add_button = QPushButton(self)
        add_button.setIcon(QIcon(icon_directory+"add_button.png"))
        add_button.setIconSize(QSize(100,60))
        add_button.setStyleSheet(get_features())
        add_button.clicked.connect(partial(self.add_movie,))

        self.h_box.addWidget(add_button)
        self.h_box.addStretch()

        search_bar = QLineEdit(self)
        self.customize_widget(widget=search_bar,size=(900,60))
        search_bar.setStyleSheet(get_features(border=2,color="white",border_color="white"))
        self.h_box.addWidget(search_bar)
        self.h_box.setSpacing(20)

        search_button = RoundButton(text="ARA")
        self.h_box.addWidget(search_button)
        self.h_box.addStretch()
        search_button.clicked.connect(partial(self.search,search_bar))

        sort_layout = QHBoxLayout()

        name_sort_button = QPushButton(self)
        self.customize_widget(widget=name_sort_button,size=(300,100),text="FİLM")
        name_sort_button.setObjectName("name-sort")

        year_sort_button = QPushButton(self)
        self.customize_widget(widget=year_sort_button,size=(120,100),text="YIL")
        year_sort_button.setObjectName("year-sort")

        category_sort_button = QPushButton(self)
        self.customize_widget(widget=category_sort_button,size=(120,100),text="KATEGORİ")
        category_sort_button.setObjectName("category-sort")

        rating_sort_button = QPushButton(self)
        self.customize_widget(widget=rating_sort_button,size=(250,100),text="RATING")
        rating_sort_button.setObjectName("rating-sort")

        sort_buttons = [name_sort_button,year_sort_button,category_sort_button,rating_sort_button]
        for sort_button in sort_buttons:
            sort_button.setStyleSheet(get_features(size=22,color="white"))
            sort_layout.addWidget(sort_button)
            if sort_button.objectName() == "category-sort" or sort_button.objectName() == "rating-sort":
                sort_layout.addStretch()
            sort_button.clicked.connect(self.sort)

        self.v_box.addLayout(self.h_box)
        self.v_box.addLayout(sort_layout)

        self.get_active_window_index()
        self.show_the_movies(dbQuery = f"select * from {self.username} limit 10 offset {(self.current_window_index-1)*10}")

        self.setLayout(self.v_box)
        self.setFixedSize(1600,900)
        self.setWindowTitle("CINEMA LIB")
        self.setWindowIcon(QIcon(icon_directory+"movie_icon.png"))
        self.show()