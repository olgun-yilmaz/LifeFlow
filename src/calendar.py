from PyQt5.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QMenu, QAction
from PyQt5.QtCore import  pyqtSlot, QDate

from src.go_to_year import *
from src.daily_routines import *
from src.app_module import *
from src.stats import Stats
from src.menu import Menu
from src.weekly_schedule import Week


class Ajanda(QMainWindow):
    def __init__(self):
        super().__init__()
        self.num_article = 10

        self.create_connection()
        self.title_list = list()
        self.font = "Comic sans MS"
        self.setGeometry(180, 80, 1600, 900)
        self.setWindowIcon(QIcon(icon_directory+"calendar_icon.png"))


        self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(icon_directory+"digital-art-moon-wallpaper1.jpg"))#digital-art-moon-wallpaper1.jpg
                                                    #technological-exploration-settlement1.jpg
        self.photo.setGeometry(0, 0, 1600, 900)

        self.prev_button = QPushButton()
        self.prev_button.setObjectName("new_prev_icon")

        self.next_button = QPushButton()
        self.next_button.setObjectName("new_next_icon")

        self.menu_button = QPushButton()
        self.menu_button.setObjectName("menu2")

        self.stats_button = QPushButton()
        self.stats_button.setObjectName("stats")

        buttons = [self.prev_button, self.next_button,self.menu_button,self.stats_button]

        for button in buttons:
            button.setIcon(QIcon(icon_directory+button.objectName() + ".png"))
            button.setIconSize(QSize(50, 50))

            if button.objectName() == "menu2":
                button.setStyleSheet(ozellikler(arkaplan_rengi="transparent"))
                button.clicked.connect(self.go_to_menu)
            elif button.objectName() == "stats":
                button.setStyleSheet(ozellikler(arkaplan_rengi="transparent"))
                button.clicked.connect(self.stats)
            else:
                button.setStyleSheet(ozellikler(arkaplan_rengi="transparent"))

                button.clicked.connect(self.change)


        h_box1 = QHBoxLayout()
        h_box1.addWidget(self.stats_button)
        h_box1.addStretch()
        h_box1.addWidget(self.prev_button)
        h_box1.addSpacing(30)
        h_box1.addWidget(self.next_button)
        h_box1.addStretch()
        h_box1.addWidget(self.menu_button)

        h_box2 = QHBoxLayout()
        v_box = QVBoxLayout()

        for i in haftanin_gunleri:
            day = QLabel(i)
            day.setStyleSheet(ozellikler(boyut=30, renk="white") +
                              "border: 2px solid white;"
                              "border-radius: 15px;"
                              "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);")
            h_box2.addWidget(day, alignment=Qt.AlignTop)

        widget = QWidget()
        self.setCentralWidget(widget)

        self.layout = QGridLayout()
        self.h_box3 = QHBoxLayout()

        self.week_counter = 1

        v_box.addLayout(self.h_box3)
        v_box.addSpacing(20)
        v_box.addLayout(h_box2)
        v_box.addLayout(self.layout)
        v_box.addSpacing(10)
        v_box.addLayout(h_box1)

        widget.setLayout(v_box)

        self.setFixedSize(1600, 900)

        self.init_ui()

        self.show()

    def create_connection(self):
        list_length = len(positive_list)
        emotion_columns = ",".join([f"is_{positive_list[i]} TEXT"
                                    for i in range(list_length)])

        article_columns = ",".join(f"article_{i} TEXT" for i in range(1,self.num_article+1))

        check_box_columns = ",".join(f"check_box_{i} INT" for i in range(1, self.num_article + 1))

        dayQuery = ("CREATE TABLE IF NOT EXISTS Day (Date TEXT UNIQUE,button_color TEXT,button_icon TEXT,"
                    f"Title TEXT,Summary TEXT,{emotion_columns},{article_columns},{check_box_columns})")
        cursor.execute(dayQuery)
        conn.commit()

        changeQuery = ("create table if not exists change (ChangeMonth INT,ChangeYear INT,"
                       "ChangeStatsYear INT)")
        cursor.execute(changeQuery)
        conn.commit()

        if not is_data_exists("change"):
            cursor.execute("insert into change (ChangeMonth,ChangeYear,ChangeStatsYear) values (0,0,0)")
            conn.commit()


    def on_date_clicked(self, date: QDate):
        clicked_date = date.toString('d MMMM yyyy')
        new_day = DailyRoutines(date=clicked_date,num_article=self.num_article)
        del new_day

    def restart(self):
        self.close()
        ajanda = Ajanda()

    def go_to_year(self):
        go = Go()
        go.go_button.clicked.connect(self.restart)

    def go_to_menu(self):
        new_menu = Menu()
        new_menu.exec_()
        del new_menu

    def go_to_week(self):
        week = self.sender().objectName()
        new_week = Week(week_number=week,month=aylar_sozlugu.get(self.month),year=self.year)
        new_week.exec_()

    def stats(self):
        stats = Stats()
        stats.exec_()
        del stats

    def init_ui(self):
        cursor.execute("select * from change")
        data = cursor.fetchone()

        change_month = data[0]
        change_year = data[1]

        self.buttons = {}
        self.text_edits = list()

        today = QDate.currentDate()  # İki
        self.that_month = today.month()
        self.month = today.month() + change_month  # Eylül
        self.year = today.year() + change_year  # İki bin yirmi dört

        self.month_label = QLabel(self)
        self.month_label.setObjectName(aylar_sozlugu.get(self.month))
        self.year_button = QPushButton(self)
        self.year_button.setObjectName(str(self.year))

        screen_objects= [self.month_label, self.year_button]

        self.h_box3.addStretch()

        for screen_object in screen_objects:
            screen_object.setText(screen_object.objectName())
            screen_object.setStyleSheet(ozellikler(renk="white",boyut=40, yazi_tipi=self.font,arkaplan_rengi="transparent"))
            self.h_box3.addWidget(screen_object)
            self.h_box3.addSpacing(10)

        self.year_button.clicked.connect(self.go_to_year)

        self.h_box3.addStretch()

        self.setWindowTitle(aylar_sozlugu.get(self.month) + " - " + str(self.year))

        first_day_of_the_month = QDate(self.year, self.month, 1)  # içinde bulunulan ayın ilk gününü bulur.
        day_count = first_day_of_the_month.daysInMonth()  # içinde bulunulan ayda kaç gün olduğunu sayar.
        which_day = first_day_of_the_month.dayOfWeek()  # ayın ilk gününün haftanın hangi günü olduğunu buluyor.

        choose = 0

        for i in range(1, which_day):
            choose += 1

            self.layout.addWidget(QWidget(), 0, i - 1)  # 0 yalnızca ilk sütunda bulunmasını sağlar.
            # i-1 de bir öncesindeki boşluğu. QWidget() de boş kutucuk sağlar.

        for day in range(1, day_count + 1):
            current_date = str(day) + " " +aylar_sozlugu.get(self.month) + " " +str(self.year)

            try:
                cursor.execute("select Title from day where Date = ?", (current_date,))
                data = cursor.fetchone()[0]
                self.title_list.append(data)
            except TypeError:
                self.title_list.append("")

            date = first_day_of_the_month.addDays(day - 1)

            layout = QVBoxLayout()

            self.day_button = QPushButton(str(day))

            self.buttons[self.day_button] = date

            self.day_edit_label = QLineEdit()
            self.day_edit_label.setMaxLength(16)
            self.day_edit_label.setFixedSize(220, 44)
            self.day_button.setFixedHeight(28)

            self.day_edit_label.setObjectName(str(day))

            if choose == which_day - 1:
                self.text_edits.append(self.day_edit_label)

            self.day_button.setStyleSheet(
                ozellikler(boyut=30, renk="white", arkaplan_rengi="transparent", yazi_tipi=self.font))

            self.open_menu_button = AnimatedButton("", x=20, y=20)

            try:
                cursor.execute("select button_color, button_icon from day where Date = ? ",(current_date,))
                data = cursor.fetchone()
                color = data[0]
                icon = data[1]
                self.open_menu_button.setIcon(QIcon(icon_directory+icon))
                self.open_menu_button.setStyleSheet(ozellikler(renk=color, boyut=10, yazi_tipi=self.font))

                self.day_edit_label.setStyleSheet(
                    ozellikler(boyut=17, arkaplan_rengi="transparent", yazi_tipi=self.font, renk=color) +
                    "border: 2px solid white;"
                    "border-radius: 15px;"
                    "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);"
                )

            except TypeError:
                self.open_menu_button.setIcon(QIcon(icon_directory + "normal.png"))
                self.open_menu_button.setStyleSheet(ozellikler(boyut=10, renk="blue"))

                self.day_edit_label.setStyleSheet(
                    ozellikler(boyut=17, arkaplan_rengi="transparent", yazi_tipi=self.font, renk="white") +
                    "border: 2px solid white;"
                    "border-radius: 15px;"
                    "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);"
                )

            h_box = QHBoxLayout()
            h_box.addStretch()
            h_box.addWidget(self.open_menu_button)
            layout.addSpacing(30)

            if (day + which_day - 2) % 7 == 0:
                week_button = RoundButton(text="week",x=50,y=30)
                week_button.setObjectName(str(self.week_counter)+".Hafta")
                week_button.clicked.connect(self.go_to_week)
                h_box1 = QHBoxLayout()
                h_box1.addWidget(week_button)
                h_box1.addWidget(self.day_button)
                layout.addLayout(h_box1)
                self.week_counter += 1
            else:
                layout.addWidget(self.day_button)
            layout.addLayout(h_box)
            layout.addWidget(self.day_edit_label)

            self.layout.addLayout(layout, (day + which_day - 2) // 7, (day + which_day - 2) % 7)

            self.open_menu_button.clicked.connect(
                partial(self.show_menu, self.open_menu_button, self.day_edit_label,current_date))

            self.day_button.clicked.connect(self.create_button_click_handler(date))

            self.day_edit_label.setText(self.title_list[day-1])

            self.day_edit_label.textChanged.connect(on_text_changed)
            timer.timeout.connect(partial(self.auto_save, self.day_edit_label,current_date))

    def show_menu(self, button, edit_label,current_date):
        menu = QMenu()

        action1 = QAction('OKUL', self)
        action1.setObjectName("orange")

        action2 = QAction('DOĞUM GÜNÜ', self)
        action2.setObjectName(renk_sec("golden"))

        action3 = QAction('SOSYAL', self)
        action3.setObjectName("blue")

        action4 = QAction("GEZİ", self)
        action4.setObjectName("green")

        action5 = QAction("AŞK", self)
        action5.setObjectName("pink")

        action6 = QAction("YATMACA", self)
        action6.setObjectName("brown")

        action7 = QAction("SPOR", self)
        action7.setObjectName("purple")

        action8 = QAction("NORMAL", self)
        action8.setObjectName("white")

        action_list = [action1, action2, action3, action4, action5, action6, action7, action8]

        @create_row(current_date=current_date)
        def apply(action,another_arg=None):
            color = action.objectName()
            icon_path = action.text().lower() + ".png"

            cursor.execute("update day set button_color = ?, button_icon = ? "
                           "where Date = ?", (color, icon_path, current_date))

            conn.commit()

            button.setIcon(QIcon(icon_directory+icon_path))
            button.setText("")
            button.setStyleSheet(ozellikler(renk=color, boyut=10, yazi_tipi=self.font))
            edit_label.setStyleSheet(
                ozellikler(boyut=17, arkaplan_rengi="transparent", yazi_tipi=self.font, renk=color) +
                "border: 2px solid white;"
                "border-radius: 15px;"
                "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);"
            )

        for action in action_list:
            action.setIcon(QIcon(icon_directory+action.text().lower() + ".png"))
            action.triggered.connect(partial(apply, action))
            menu.addAction(action)

        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec_(pos)

    def create_button_click_handler(self, date: QDate):
        def handler():
            self.on_date_clicked(date)

        return handler

    def auto_save(self, text_edit,current_date):
        @create_row(current_date=current_date)
        def inner_save():
            cursor.execute("update day set Title = ? where Date = ?",(text_edit.text(),current_date))
            conn.commit()

            index = int(text_edit.objectName())-1

            self.title_list[index] = text_edit.text()

        inner_save()

    @pyqtSlot()
    def change(self):
        sender = self.sender()

        cursor.execute("select ChangeMonth,ChangeYear from change")
        data = cursor.fetchone()
        current_month = data[0]
        current_year = data[1]

        if sender == self.prev_button:
            if self.month == 1:
                current_month = 11 + self.month - self.that_month
                current_year -= 1
            else:
                current_month -= 1

        elif sender == self.next_button:
            if self.month == 12:
                current_month = self.month - self.that_month - 11
                current_year += 1
            else:
                current_month += 1

        cursor.execute("update change set ChangeMonth = ?, ChangeYear = ?"
                       ,(current_month,current_year))
        conn.commit()

        self.restart()