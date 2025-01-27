#GEREKLİ MODÜLLER IMPORT EDİLİYOR.
from src.app_module import ozellikler, icon_directory, cursor, conn

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QMessageBox, QTextEdit, QDialog

class Book:
    def __init__(self,name,total_pages,is_selected,is_read,is_enable):
        self.name = name
        self.total_pages = total_pages
        self.is_selected = is_selected
        self.is_read = is_read
        self.is_enable = is_enable

class AddBook(QDialog):  #KİTAP EKLEYEN SINIF

    def __init__(self, book_list):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.books = list()
        for book in book_list:
            self.books.append(book.name)
        self.area_counter = 0
        self.flag = False
        self.init_ui()

    def save_book(self):
        self.flag = True
        book_name = self.book_name_edit.toPlainText()
        pages = self.pages_edit.text()
        text_length = len(book_name)
        if text_length < 3:
            QMessageBox.warning(self, 'Uyarı', 'Karakter uzunluğu 3 ile 108 arasında olmalıdır.')
        elif book_name in self.books:
            QMessageBox.warning(self, 'Uyarı', 'Kitap zaten sistemde kayıtlı!')
        elif len(pages) == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen sayfa sayısı giriniz!")

        else:
            new_book = Book(name=self.book_name_edit.toPlainText(),total_pages=int(self.pages_edit.text()),
                            is_selected=0,is_read="unread",is_enable=1)
            cursor.execute("insert into library (Name,TotalPages,isSelected,isRead,isEnable) values (?,?,?,?,?)",
                           (new_book.name,new_book.total_pages,new_book.is_selected,new_book.is_read,new_book.is_enable))
            conn.commit()

            QMessageBox.information(self, 'Bilgi', 'Başarıyla kaydedildi!')
            self.close()

    def customize_text_area(self):
        text_length = len(self.book_name_edit.toPlainText())
        if text_length > 109:
            QMessageBox.warning(self, 'Uyarı', 'Kitap isminin uzunluğu 5 ile 108 karakter arasında olmalıdır.')


    def customize_widget(self, widget, geometry=(0, 0, 0, 0), features=(25, "transparent", "white"),
                         text=""):  #WIDGETLAR ÖZELLEŞTİRİLİYOR
        widget.setGeometry(QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
        widget.setStyleSheet(
            ozellikler(boyut=features[0], arkaplan_rengi=features[1], renk=features[2]) + "border-radius: 15px; "
                                                                                          "box-shadow: 0 0 10px rgba(255, 255, 255, 0.7);")
        widget.setText(text)

    def init_ui(self):
        self.photo = QLabel(self)
        self.photo.setPixmap(QPixmap(icon_directory+"beautiful.jpg"))  #PENCERE ARKA PLANI
        self.photo.setGeometry(0, 0, 700, 250)

        self.ok_button = QPushButton(self)  #BUTON
        self.ok_button.setIcon(QIcon(icon_directory+"ok.png"))
        self.ok_button.setIconSize(QSize(120, 60))

        self.customize_widget(widget=self.ok_button, geometry=(300, 170, 120, 60))

        self.pages_edit = QLineEdit(self)  # TOPLAM SAYFA SAYISI GİR
        self.book_name_edit = QTextEdit(self)  # KİTAP ADI GİR

        edit_areas = [self.book_name_edit, self.pages_edit]
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
                int_validator = QIntValidator(10, 9999, self)
                edit_area.setValidator(int_validator)
            self.area_counter += 50

        self.info_book = QLabel(self)
        self.customize_widget(widget=self.info_book, geometry=(20, 10, 160, 60), text="KİTAP ADI : ")  #KİTAP ADI YAZISI

        self.info_page = QLabel(self)
        self.customize_widget(widget=self.info_page, geometry=(20, 120, 250, 40), text="SAYFA SAYISI : ")

        self.ok_button.clicked.connect(self.save_book)  #BUTON BAĞLANTISI

        self.setWindowIcon(QIcon(icon_directory+"book_icon.png"))  #PENCERE İKONU

        self.setFixedSize(700, 250)  #SABİTLENMİŞ PENCERE BOYUTU

        self.setWindowTitle("KİTAP EKLE")
