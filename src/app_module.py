import os

from PyQt5.QtCore import QSize, pyqtSignal, QTimer
from PyQt5.QtWidgets import QPushButton, QTextEdit
from bs4 import BeautifulSoup
import sqlite3

if not os.path.exists('UserData'):
    os.mkdir('UserData')

conn = sqlite3.connect("UserData/database.db")
cursor = conn.cursor()


def create_week_connection(list_length):
    task_columns = ",".join([f"box_{i} TEXT"
                             for i in range(list_length)])
    weekQuery = f"create table if not exists week (Date TEXT UNIQUE,{task_columns})"
    cursor.execute(weekQuery)
    conn.commit()

    try:
        cursor.execute("insert into week (Date) values (?)", ("fixed_program",))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # fixed_week zaten oluşturulduysa işlem yapma.

class CustomTextEdit(QTextEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class RoundButton(QPushButton):
    def __init__(self,x=100,y=60,text="Go"):
        super().__init__()
        self.setFixedSize(x,y)
        self.setText(text)
        self.setStyleSheet(f"""
    QPushButton {{
        border-radius: {y//2}px;
        background-color: grey;
        color: white;
    }}
    QPushButton:hover {{
        background-color: #45a049;
    }}
""")



class AnimatedButton(QPushButton):
    def __init__(self, text, x=240, y=50):
        super().__init__(text)
        self.default_size = QSize(x, y)  # Varsayılan boyut
        self.hovered_size = QSize(int(x * 1.2), int(y * 1.25))  # Üzerine gelindiğinde boyut
        self.setFixedSize(self.default_size)  # Başlangıçta varsayılan boyutu ayarla

    def enterEvent(self, event):
        # Fare butonun üzerine geldiğinde boyutu büyüt
        self.setFixedSize(self.hovered_size)
        super(AnimatedButton, self).enterEvent(event)

    def leaveEvent(self, event):
        # Fare butonun üzerinden ayrıldığında boyutu eski haline getir
        self.setFixedSize(self.default_size)
        super(AnimatedButton, self).leaveEvent(event)

positive_list = ["angry", "decreased", "dizziness", "fear"]


def styledrb(x=0, y=0):
    a = "QRadioButton::indicator {"
    b = "  width: {}px;".format(x)
    c = "  height: {}px;".format(y)
    d = "  border: none;"
    e = "}"
    return a + b + c + d + e

ozellikler = lambda yazi_tipi="Segoe Print", boyut=16, kalinlik="light", renk="black",\
arkaplan_rengi=None:("font-family: {}; font-size: {}px; font-weight: {}; color: {};background-color: {};"
     .format(yazi_tipi, boyut, kalinlik, renk,arkaplan_rengi))

def setcheckbox_icon(checkbox,path,x=24,y=24):
    checkbox.setStyleSheet(f'''
        QCheckBox::indicator {{
            width: {x}px;
            height: {y}px;
            border-image: url({path});
        }}
    ''')

def update_html_style(html_content,renk = "black"):
    # BeautifulSoup ile HTML içeriğini işle
    soup = BeautifulSoup(html_content, 'html.parser')

    # Gereksiz <style> etiketlerini temizle
    for style_tag in soup.find_all('style'):
        style_tag.decompose()

    # İçerideki gereksiz inline stilleri temizle
    for tag in soup.find_all(True):  # 'True' burada tüm etiketleri seçer
        if 'style' in tag.attrs:
            tag.attrs.pop('style')

    # Stil tanımını oluştur
    def styled_fonx(color) :
            css_template = f"""
            <style type="text/css">
                body {{
                    font-family: "Comic sans MS";
                    font-size: 20px;
                    color: {color};
                }}
                p {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
            """
            return css_template
    style = styled_fonx(color=renk)

    # Eğer <head> etiketi mevcut değilse oluştur
    if soup.head is None:
        head_tag = soup.new_tag('head')
        soup.html.insert(0, head_tag)
        soup.head.append(BeautifulSoup(style, 'html.parser'))
    else:
        soup.head.insert(0, BeautifulSoup(style, 'html.parser'))

    # Temizlenmiş ve güncellenmiş HTML içeriğini döndür
    return str(soup)

haftanin_gunleri = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]

aylar_sozlugu = {1 : "Ocak", 2 : "Şubat",3 : "Mart", 4 : "Nisan",5 : "Mayıs", 6 : "Haziran",
                 7 : "Temmuz", 8 : "Ağustos",9 : "Eylül", 10 : "Ekim",11 : "Kasım", 12 : "Aralık"}

renkler_sozlugu = {"golden": "#c5c500", "dolar yeşili": "#207e16", "soft gri": "#dedede","gece laciverti":"#132753",
                   "bence mor":"#6a136a","bulut mavisi":"#42c7c7","hacker yeşili":"#009100","uyarı kırmızısı":"#c10000"}

renk_sec = lambda renk : renkler_sozlugu.get(renk)

get_features = lambda font="Segoe Print", size=17, color="black",background_color="transparent",\
                      border=0,border_color="black":("font-family: {}; font-size: {}px; color: {};background-color: {};border: {}px solid {};"
     .format(font, size, color, background_color,border,border_color))

icon_directory = "app_icons/"

userDataFolder = "UserData/"
if not  os.path.exists(userDataFolder):
    os.mkdir(userDataFolder)

def create_row(current_date,table="day"):
    def decarator(func):
        def wrapper(*args,**kwargs):
            try:
                cursor.execute(f"insert into {table} (Date) values (?)", (current_date,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # oluştuysa yok sayacak.
            func(*args,**kwargs)
        return wrapper
    return decarator


timer = QTimer()
timer.setSingleShot(True)


def on_text_changed():
    timer.start(500)  # 0.5 sn

def clear_folder(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path,file)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

def is_data_exists(table):
    cursor.execute(f"select * from {table}")
    data = cursor.fetchone()
    if data is None:
        return False
    return True
