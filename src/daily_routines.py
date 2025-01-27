import os
import sqlite3
from functools import partial

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QTextCursor
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QTextEdit, QPushButton, QLineEdit, QMessageBox

from bs4 import BeautifulSoup

from src.add_book import Book
from src.app_module import (setcheckbox_icon, update_html_style, ozellikler, icon_directory, timer, \
                            on_text_changed, clear_folder, cursor, conn, positive_list, create_row)

from src.library import Library


class DailyRoutines(QWidget):
    def auto_save(self, text_edit):
        text = text_edit.toPlainText()
        index = text_edit.objectName()
        if text.strip() != "":
            article_content = text_edit.toHtml()

            try:
                cursor.execute(f"INSERT INTO Day (Date,article_{index}) VALUES (?,?)",
                           (self.date,article_content))
            except sqlite3.IntegrityError:
                cursor.execute(f"UPDATE Day SET article_{index}=? WHERE Date=?",(article_content,self.date))
            finally:
                conn.commit()

    def daily_summary_auto_save(self):
        @create_row(current_date=self.date)
        def inner_save():
            summary = self.daily_summary_area.toPlainText()
            if summary == self.default_summary:
                summary = None
            cursor.execute("update day set Summary = ? where Date = ?"
                           ,(summary,self.date))
            conn.commit()
        inner_save()

    def go_to_lib(self):
        self.lib.exec_()
        self.close()

    def create_connection(self):
        pagesQuery = ("create table if not exists pages (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "Book TEXT,Date TEXT UNIQUE,PageCount INT)")
        cursor.execute(pagesQuery)
        conn.commit()

        waterQuery = ("create table if not exists water (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "Date TEXT UNIQUE,WaterIntake FLOAT,waterBox1 INT,waterBox2 INT,waterBox3 INT,"
                   "waterBox4 INT,waterBox5 INT,waterBox6 INT)")
        cursor.execute(waterQuery)
        conn.commit()

    def return_current_book(self):
        cursor.execute("select * from library where isSelected = ?", (1,))
        data = cursor.fetchone()
        current_book = Book(name=data[1],total_pages=data[2],is_selected=data[3],
                    is_read=data[4],is_enable=data[5])
        return current_book

    def pages_read_autosave(self, line_edit):
        read_page = str(line_edit.text())
        if read_page == "":
            read_page = 0
        try:
            cursor.execute("select PageCount from pages where date = ?", (self.date,))
            data = cursor.fetchall()
            if data == list():
                record_exist = False
            else:
                record_exist = True

            if not record_exist:
                cursor.execute("insert into pages (Book,Date,PageCount) values (?,?,?)",
                               (self.return_current_book().name,self.date,read_page))
                conn.commit()
            else:
                cursor.execute("update pages set PageCount = ?"
                               " where Date = ?", (read_page,self.date))
                conn.commit()

        except TypeError:
                QMessageBox.warning(self, "Uyarı", "Önce kitap seçmelisiniz!")
                self.lib.exec_()
                self.close()

    def create_check_box(self):
        new_check_box = QCheckBox(self)
        new_check_box.setObjectName(str(self.counter + 1))
        setcheckbox_icon(checkbox=new_check_box, path=icon_directory + "unchecked.png")
        self.check_boxes.append(new_check_box)
        new_check_box.setGeometry(QRect(800, self.y + (self.counter * 75), 24, 24))

        return new_check_box

    def create_water_box(self):
        self.water_counter += 1
        water_box = QCheckBox(self)
        water_box.setObjectName(f"waterBox{str(self.water_counter)}")
        setcheckbox_icon(checkbox=water_box, path=icon_directory + "empty_glass.png", x=48, y=48)
        water_box.setGeometry(80 + self.water_counter * 70, 50, 48, 48)
        return water_box


    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            text = obj.toPlainText()
            if event.key() in [Qt.Key_Enter, Qt.Key_Return] and text != "":
                self.add_new_edit()
                return True

            elif obj in self.text_edits:
                if text == "":
                    if event.key() == Qt.Key_Backspace:
                        self.delete_edit(obj)
                        return True

        return super().eventFilter(obj, event)

    def delete_edit(self, text_edit):
        no = int(text_edit.objectName()) - 1

        while  no < len(self.text_edits) - 1:
            self.text_edits[no], self.text_edits[no+1] = self.text_edits[ no+1],self.text_edits[no]
            self.check_boxes[no], self.check_boxes[ no+1] = self.check_boxes[ no+1], self.check_boxes[no]
            no += 1

        for edit in self.text_edits:
            index = self.text_edits.index(edit)
            state = self.check_boxes[index].isChecked()

            if not (edit.toPlainText().strip() == str() or edit == text_edit):
                content = edit.toHtml()
            else:
                content = None
            if state and edit != text_edit:
                state = 1
            else:
                state = None

            cursor.execute(f"UPDATE Day set article_{index+1} = ?, check_box_{index+1} = ? "
                           f"Where Date = ?", (content, state, self.date))
            conn.commit()

        self.restart()


    def restart(self):
        self.close()
        new_routine = DailyRoutines(self.max,self.date,is_restarted=True)

    def create_new_edit(self):
        if self.counter < self.max:
            new_edit = QTextEdit(self)
            new_edit.setStyleSheet(
                ozellikler(renk="black", boyut="20", arkaplan_rengi="transparent", yazi_tipi="Comic sans MS"))
            self.text_edits.append(new_edit)
            new_edit.installEventFilter(self)
            new_edit.setObjectName(str(self.counter + 1))
            new_edit.setGeometry(QRect(850, self.y + (self.counter * 75), 400, 300))
            self.counter += 1
            new_edit.setMaximumHeight(40)
            new_edit.setLineWrapMode(QTextEdit.NoWrap)
            new_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            new_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            return new_edit

    def click_emotion(self):
        emotion_box = self.sender()
        index = int(emotion_box.objectName()[0]) - 1
        emotion = self.emotion_list[index]
        if emotion[:2] == "un":
            updated_emotion = emotion[2:]
        else:
            updated_emotion = "un"+emotion
        setcheckbox_icon(emotion_box, icon_directory + updated_emotion , 50,50)
        self.emotion_list[index] = updated_emotion

        @create_row(current_date=self.date)
        def update_emotion():
            cursor.execute(f"update day set is_{positive_list[index]} = ? where Date = ?",(updated_emotion,self.date))
        update_emotion()

    def create_emotion_box(self):
            emotion_box = QCheckBox(self)
            emotion_box.setObjectName(str(self.emotion_counter+1)+". emotion")
            emotion_box.setToolTip(positive_list[self.emotion_counter])
            setcheckbox_icon(checkbox=emotion_box, path=icon_directory + "un"+positive_list[self.emotion_counter]+
                                                        ".png",x=50, y=50)
            emotion_box.setGeometry((self.emotion_counter+2) * 90, 415, 50,50)

            self.emotion_counter += 1
            emotion_box.clicked.connect(self.click_emotion)
            return emotion_box

    def show_emotion_box(self):
        emotion_counter = 0
        while emotion_counter < len(positive_list):
            emotion_box = self.create_emotion_box()
            emotion_column = positive_list[emotion_counter]
            try:
                cursor.execute(f"select is_{emotion_column} from day where Date = ?", (self.date,))
                emotion = cursor.fetchone()[0]
            except TypeError:
                emotion = "un" + positive_list[emotion_counter] + ".png"

            if emotion is None:
                emotion = "un" + positive_list[emotion_counter] + ".png"

            self.emotion_list.append(emotion)

            setcheckbox_icon(emotion_box, icon_directory + emotion, 50,50)
            emotion_counter += 1

    def fill_the_glass(self):
        water_box = self.sender()
        water_box_number = water_box.objectName()

        check = None

        if water_box.isChecked():
            setcheckbox_icon(water_box, icon_directory + "glass_of_water.png", 48, 48)
            self.daily_water_intake += 0.5
            check = 1
        else:
            self.daily_water_intake -= 0.5
            setcheckbox_icon(water_box, icon_directory + "empty_glass.png", 48, 48)

        if int(self.daily_water_intake) == self.daily_water_intake:
            self.daily_water_intake = int(self.daily_water_intake)

        try:
            cursor.execute(f"INSERT INTO water  (Date, {water_box_number}, WaterIntake) VALUES "
                           f"(?, ?, ?)",(self.date,check,self.daily_water_intake))
        except sqlite3.IntegrityError:
            cursor.execute(f"update water set {water_box_number} = ?, WaterIntake = ? where Date = ?",
                           (check, self.daily_water_intake, self.date,))
        finally:
            conn.commit()

        self.water_intake_info = "Total :  " + str(self.daily_water_intake) + " L"
        if self.water_intake_info == "Total :  0 L":
            self.water_intake_info = "Henüz hiç su tüketmediniz..."

        self.water_info_label.setText(self.water_intake_info)


    def show_water_box(self):
        while self.water_counter < 6:
            water_box = self.create_water_box()
            water_box_number = water_box.objectName()

            water_box.stateChanged.connect(self.fill_the_glass)

            cursor.execute(f"select {water_box_number} from water where Date = ?",(self.date,))
            try:
                check_box_state = cursor.fetchone()[0]
            except TypeError:
                check_box_state = None

            if check_box_state == 1:
                water_box.setChecked(True)
                setcheckbox_icon(water_box, icon_directory + "glass_of_water.png", 48, 48)

    def show_edit(self):
        while self.counter < self.max:
            cursor.execute(f"SELECT article_{self.counter+1},check_box_{self.counter+1}"
                           f" FROM Day WHERE Date = ?",(self.date,))

            data = cursor.fetchone()

            try:
                article_content = data[0]
            except TypeError:
                article_content = None

            if self.counter == 0 or not article_content is None:
                new_check_box = self.create_check_box()
                current_edit = self.create_new_edit()
            else:
                break

            state = None

            try:
                state = data[1]
            except TypeError:
                pass

            try:
                if not article_content is None:
                    if state == 1:
                        new_check_box.setChecked(True)
                        setcheckbox_icon(checkbox=new_check_box, path=icon_directory + "checked.png")
                    current_edit.setHtml(article_content)
                    new_check_box.stateChanged.connect(partial(self.cross_out, current_edit))
                else:
                    current_edit.textChanged.connect(partial(self.auto_save, current_edit))
                    new_check_box.stateChanged.connect(partial(self.cross_out, current_edit))
                    break
            except TypeError:
                current_edit.textChanged.connect(partial(self.auto_save, current_edit))
                break

        if self.is_restarted:
            last_article = self.text_edits[-1]
            last_article.setFocus()
            last_article.moveCursor(QTextCursor.End)

    def add_new_edit(self):
        if self.counter < self.max:
            new_checkbox = self.create_check_box()
            new_edit = self.create_new_edit()
            new_edit.show()
            new_checkbox.show()

            new_edit.textChanged.connect(partial(self.auto_save, new_edit))
            new_checkbox.stateChanged.connect(partial(self.cross_out, new_edit))
            new_edit.setFocus()  # ilk olarak tıklanacak edit area

    def cross_out(self, text_edit):
        if self.counter < self.max + 1:
            try:
                checkbox = self.sender()
                index = text_edit.objectName()

                if checkbox.isChecked():
                    state = 1
                    setcheckbox_icon(checkbox=checkbox, path=icon_directory + "checked.png")

                    if text_edit.toPlainText() != "":
                        article_content = text_edit.toHtml()

                        styled_article = update_html_style(html_content=article_content, renk="blue")

                        soup = BeautifulSoup(styled_article, "html.parser")
                        for p in soup.find_all("p"):
                            s_tag = soup.new_tag('s')
                            s_tag.string = p.string
                            p.string = ''  # Mevcut metni temizle
                            p.append(s_tag)
                        article_content = soup.prettify()

                        text_edit.setHtml(article_content)

                else:
                    state = None
                    setcheckbox_icon(checkbox=checkbox, path=icon_directory + "unchecked.png")
                    article_content = text_edit.toHtml()

                    article_content = update_html_style(article_content, "black")

                    text_edit.setHtml(article_content)

                try:
                    cursor.execute(f"UPDATE Day set article_{index} = ?, check_box_{index} = ? "
                            f"Where Date = ?", (article_content, state, self.date))
                    conn.commit()
                except UnboundLocalError:
                    pass

            except AttributeError:
                pass

    def getReadPageCount(self):
        cursor.execute("select PageCount from pages where Book = ?",(self.return_current_book().name,))
        all_pages = cursor.fetchall()
        sum = 0
        try:
            for page_tuple in all_pages:
                for page in page_tuple:
                    sum += page
        except TypeError:
            sum = 0
        return sum

    def pages_read_info(self):
        try:
            cursor.execute("select PageCount from pages where Date = ?",(self.date,))
            page = cursor.fetchone()[0]
        except TypeError:
            page = 0
        return page

    def daily_summary_info(self):
        try:
            cursor.execute("select Summary from day where Date = ?",(self.date,))
            text = cursor.fetchone()[0]
        except TypeError:
            text = self.default_summary

        if text is None:
            text = self.default_summary

        return text

    def readingCompletion(self):
            try:
                read_pages = self.getReadPageCount()
                total_pages = int(self.return_current_book().total_pages)

                rate = round(float(read_pages / total_pages), 2)  #2 BASAMAĞA GÖRE YUVARLA
                rate = 100 * rate

                if rate - int(rate) < 0.01:
                    rate = int(rate)
                if rate >= 100:
                    rate = 100
            except TypeError:
                rate = 0
            return rate

    def customize_widget(self, widget, geometry=(0, 0, 0, 0), features=(25, "transparent", "black"), border=0, text=""):
        try:
            widget.setGeometry(QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
            widget.setStyleSheet(
                ozellikler(boyut=features[0], arkaplan_rengi=features[1], renk=features[2]) + "border: {}px "
                                                                                              "solid black;border-radius: 15px; box-shadow: 0 0 10px "
                                                                                              "rgba(255, 255, 255, 0.7);".format(
                    border))
            widget.setText(text)
        except TypeError:
            pass

    def update_label(self):
        if self.readingCompletion() < 100:
            self.completion_label.setText("%" + str(self.readingCompletion()))
            self.completion_bar.setGeometry(QRect(150, 300, self.readingCompletion() * 3, 50))
        else:
            QMessageBox.information(self, "TEBRİKLER", "{} kitabını bitirdiniz!".format(self.return_current_book().name))
            self.completion_label.setText("%100")
            self.completion_bar.setGeometry(150,300,300,50)
            try:
                cursor.execute("update library set isRead = 'read', isEnable = 0, isSelected = 0"
                               " where name = ?",(self.return_current_book().name,))
                lib = Library()
                lib.exec_()
                self.close()
            except TypeError:
                pass

    def __init__(self, num_article=10,date='1 Nisan 2004',is_restarted=False):
        super().__init__()
        self.date = date
        self.create_connection()
        self.date = date
        self.lib = Library()
        self.month = "".join([char for char in self.date if char.isalpha()])
        self.year = self.date[len(self.date)-4:]
        self.day = self.date[:2]

        self.is_restarted = is_restarted

        self.default_summary = "GELECEĞE BİR NOT BIRAK..."

        self.water_info_label = QLabel(self)
        self.text_edits,self.check_boxes,self.emotion_list  = list(),list(),list()

        self.water_counter = 0
        self.emotion_counter = 0
        self.counter = 0
        self.max = num_article
        self.y = 90
        self.daily_water_intake = 0
        self.water_intake_info = "Henüz hiç su tüketmediniz..."
        self.init_ui()

    def init_ui(self):
        self.setGeometry(180, 80, 1300, 900)

        self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(icon_directory + "begumgroundc.jpg"))
        self.photo.setGeometry(QRect(0, 0, 1300, 900))

        title_label = QLabel(self)
        self.customize_widget(widget=title_label, geometry=(920, 20, 180, 50), text="TO DO LIST", border=2)

        self.book_box = QPushButton(self)
        self.customize_widget(self.book_box, (140, 150, 80, 80))
        self.book_box.setIcon(QIcon(icon_directory + "book.png"))
        self.book_box.setIconSize(QSize(80, 80))
        self.book_box.clicked.connect(self.go_to_lib)

        self.book_info_label = QLabel(self)
        self.customize_widget(self.book_info_label, geometry=(250, 150, 200, 50), text="SAYFA SAYISI")

        book_name_label = QLabel(self)
        try:
            current_book_name = self.return_current_book().name
        except TypeError:
            current_book_name = "SEÇİLMEDİ"
        self.customize_widget(widget=book_name_label, geometry=(170, 250, 450, 50), text="KİTAP : "+current_book_name)

        self.completion_label = QLabel(self)
        self.customize_widget(self.completion_label, geometry=(480, 300, 80,50),
                              text="%" + str(self.readingCompletion()))

        self.empty_bar = QLabel(self)
        self.customize_widget(widget=self.empty_bar,geometry=(150,300,300,50),features=(25,"transparent","black"),border=2)

        self.completion_bar = QLabel(self)
        self.customize_widget(widget=self.completion_bar, geometry=(150, 300, int(self.readingCompletion() * 3), 50),
                              features=(25,"green","black"),border=2)

        self.daily_summary_area = QTextEdit(self)
        self.customize_widget(self.daily_summary_area,geometry=(50,480,600,420),text = self.daily_summary_info())
        self.daily_summary_area.textChanged.connect(on_text_changed)
        timer.timeout.connect(self.daily_summary_auto_save)

        self.pages_area = QLineEdit(self)
        self.customize_widget(self.pages_area, geometry=(320, 195, 50, 35), border=2, text=str(self.pages_read_info()))
        int_validator = QIntValidator(0, 99, self)
        self.pages_area.setValidator(int_validator)
        self.pages_area.setFocus()
        self.pages_area.textChanged.connect(partial(self.pages_read_autosave, self.pages_area))

        self.show_edit()
        self.show_water_box()
        self.show_emotion_box()

        timer.timeout.connect(self.update_label)
        self.pages_area.textChanged.connect(on_text_changed)

        self.water_info_label = QLabel(self)
        self.customize_widget(widget=self.water_info_label, geometry=(150, 110, 415, 20),
                              features=(20, "transparent", "blue")
                              , text=self.water_intake_info)

        self.setWindowIcon(QIcon(icon_directory + "notepad_icon.png"))
        self.setWindowTitle(self.date)
        self.setFixedSize(1300, 900)
        self.show()