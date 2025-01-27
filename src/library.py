import os.path
import shutil

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QRadioButton

from src.add_book import AddBook, Book
from src.edit_book import EditBook
from src.app_module import (styledrb, ozellikler, icon_directory, cursor, conn)


class Library(QDialog):
    def add_book(self):
        new_book = AddBook(self.book_list)
        new_book.exec_()
        if new_book.flag:
            self.restart()
        del new_book

    def edit_book(self):
        book_name = self.sender().objectName()
        cursor.execute("SELECT TotalPages FROM library WHERE name = ?", (book_name,))
        pages = cursor.fetchone()[0]

        book = EditBook(self.book_list,book_name,pages)
        book.exec_()
        if book.flag:
            self.restart()

    def create_connection(self):
        dbQuery = (f"create table if not exists library (id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT,"
                   f"TotalPages INT,isSelected INT,isRead TEXT,isEnable INT)")
        cursor.execute(dbQuery)
        conn.commit()

    disconnect = lambda self: conn.close()

    def choose(self):
        selected_button = self.sender()
        selected_book = selected_button.objectName()
        update_query = """
        update library set isSelected = case
        when Name = ? then 1 
        else 0 end
            """
        cursor.execute(update_query, (selected_book,))

        conn.commit()

        for rb in self.radio_buttons:
            index = self.radio_buttons.index(rb)
            state = True
            if self.is_enable_list[index] == 0:
                state = False
            rb.setEnabled(state)
            if rb is selected_button:
                rb.setIcon(QIcon(icon_directory + "selected_book.png"))
                rb.setStyleSheet(styledrb())
            else:
                rb.setIcon(QIcon())
                rb.setStyleSheet(styledrb(25, 25))
            rb.setIconSize(QSize(25, 25))

    def create_new_push_button(self, icon_name="edit_button", book_name="book", x=25, y=25):
        button = QPushButton(self)
        button.setObjectName(book_name)
        button.setIcon(QIcon(icon_directory + icon_name + ".png"))
        button.setIconSize(QSize(x, y))
        button.setStyleSheet(ozellikler(arkaplan_rengi="transparent"))
        return button

    def create_new_label(self, book_name="book", icon="unread_check"):
        label = QLabel(self)
        label.setObjectName(book_name)
        label.setPixmap(QPixmap(icon_directory + icon + ".png"))
        label.setFixedSize(25, 25)
        label.setStyleSheet(ozellikler(arkaplan_rengi="transparent"))
        self.check_labels.append(label)
        return label

    def create_new_radio_button(self, book_name):
        button = QRadioButton()
        button.setObjectName(book_name)
        button.setIconSize(QSize(25, 25))
        button.setStyleSheet(styledrb(x=25, y=25))
        self.radio_buttons.append(button)
        return button

    def create_shelf(self):
        counter = 0
        vBoxes = list()
        for i in range(2):
            v_box = QVBoxLayout()
            vBoxes.append(v_box)
        while self.shelf_counter < len(self.book_list) and counter < 40:
            current_book = self.book_list[self.shelf_counter]

            delete_button = self.create_new_push_button(icon_name="delete_button", book_name=current_book.name)
            delete_button.clicked.connect(self.delete_book)

            edit_button = self.create_new_push_button(icon_name="edit_button", book_name=current_book.name)
            edit_button.clicked.connect(self.edit_book)

            check_book_label = self.create_new_label(icon=current_book.is_read, book_name=current_book.name)

            selected_button = self.create_new_radio_button(book_name=current_book.name)
            selected_button.clicked.connect(self.choose)

            state = current_book.is_selected

            if state == 1:
                selected_button.setChecked(True)
                selected_button.setIcon(QIcon(icon_directory + "selected_book.png"))
                selected_button.setStyleSheet(styledrb(0, 0, ))

            new_shelf = QLabel(self)
            new_shelf.setStyleSheet(
                ozellikler(boyut=20, arkaplan_rengi="transparent", renk="black"))

            new_shelf.setText(str(self.shelf_counter + 1) + ". " + current_book.name + "-" +
                              str(current_book.total_pages))
            new_shelf.setFixedWidth(350)

            widgets = [selected_button, new_shelf, edit_button, delete_button, check_book_label]
            h_box = QHBoxLayout()
            for widget in widgets:
                h_box.addWidget(widget)  # widgetlar yerleşti
            counter += 1
            h_box.addStretch()

            if counter < 21:
                vBoxes[0].addLayout(h_box)

            else:
                h_box.addStretch()
                vBoxes[1].addLayout(h_box)

            for vbox in vBoxes:
                self.h_box.addLayout(vbox)

            self.shelf_counter += 1
        self.v_box.addLayout(self.h_box)
        self.v_box.addStretch()

    def customize_widget(self, widget, geometry=(0, 0, 0, 0), features=(25, "transparent", "black"), border=0, text=""):
        widget.setGeometry(QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
        widget.setStyleSheet(
            ozellikler(boyut=features[0], arkaplan_rengi=features[1], renk=features[2]) + "border: {}px "
                                                                                          "solid white;border-radius: 15px; box-shadow: 0 0 10px "
                                                                                          "rgba(255, 255, 255, 0.7);".format(
                border))
        widget.setText(text)

    def delete_book(self):
        book_name = self.sender().objectName()

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Onay Penceresi")
        msgBox.setText(f"{book_name} kitabını silmek istediğinizden emin misiniz?")

        evet_button = msgBox.addButton('Evet', QMessageBox.YesRole)
        hayir_button = msgBox.addButton('Hayır', QMessageBox.NoRole)

        msgBox.setDefaultButton(hayir_button)

        msgBox.exec_()

        if msgBox.clickedButton() == evet_button:
            cursor.execute("delete from library where name = ?", (book_name,))
            conn.commit()
            QMessageBox.information(self, 'Bilgi', f'{book_name} kitabı başarıyla silindi!')
            self.restart()
            del msgBox

    def get_the_books(self):
        cursor.execute("select * from library")
        data = cursor.fetchall()

        for i in data:
            book = Book(name=i[1], total_pages=i[2], is_selected=i[3], is_read=i[4], is_enable=i[5])
            self.book_list.append(book)
            self.is_enable_list.append(book.is_enable)

    def restart(self):
        self.close()
        library = Library()
        library.exec_()
        del library

    def __init__(self):
        super().__init__()
        self.create_connection()
        self.v_box = QVBoxLayout()
        self.h_box = QHBoxLayout()
        self.shelf_counter, self.button_counter = 0, 0
        self.current_book = str()

        self.radio_buttons, self.is_enable_list = list(), list()
        self.check_labels, self.book_list = list(), list()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.init_ui()

    def init_ui(self):
        self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(icon_directory + "heaven2.jpg"))
        self.photo.setGeometry(QRect(0, 0, 1600, 900))
        self.setWindowTitle("KÜTÜPHANE")

        add_button = self.create_new_push_button("add_button", x=50, y=50)
        add_button.clicked.connect(self.add_book)

        self.get_the_books()
        self.create_shelf()

        self.v_box.addWidget(add_button)

        self.setLayout(self.v_box)
        self.setWindowIcon(QIcon(icon_directory + "book_icon.png"))
        self.setFixedSize(1600, 900)