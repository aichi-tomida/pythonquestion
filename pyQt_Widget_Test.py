import datetime
import os
import sys
import time

import PIL.ExifTags as ExifTags
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QCheckBox,
                             QGridLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QRadioButton, QTableWidget,
                             QTableWidgetItem, QWidget)

'''
写真管理
'''

_getfail = '取得不具合'
_datetimeformat = '%Y/%m/%d %H:%M:%S'

# 仮ファイルリスト（本来はglobで取得）
_filepiclist = [r"S:\picture\2020-08-02\IMG20200802114557.jpg",r"S:\picture\2020-08-02\IMG20200802114656.jpg"]

# 画像ファイルの撮影日取得
def getShotdate(path):
  try:
      # 画像ファイルを開く
      im = Image.open(path)
      # EXIF情報を辞書型で得る
      exif = {
        ExifTags.TAGS[k]: v
        for k, v in im._getexif().items()
        if k in ExifTags.TAGS
      }
      shot_tags = exif["DateTimeOriginal"]
      return shot_tags

  except Exception as e:
    print (e)
    return _getfail

# ファイル作成日時
def getfilectime(file):
    # ファイル作成日時
    ct = os.path.getctime(file)
    cd = datetime.datetime.fromtimestamp(ct).strftime(_datetimeformat)
    return cd

# ファイル更新日時
def getfilemtime(file):
    mt = os.path.getmtime(file)
    md = datetime.datetime.fromtimestamp(mt).strftime(_datetimeformat)
    return md


class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)

        # 本来は glob
        paths = _filepiclist
        time.sleep(0.5)
        paths.sort(key=os.path.getmtime, reverse=False)

        listchks= []
        listpaths= []
        listfilename= []
        listshotdate = []
        liststrshotdate = []
        listplace = []
        listext = []

        for f in paths:
          # チェックボックス用 (暫定で空白)
          listchks.append('')

          # フルパス
          listpaths.append(str(f))

          # 撮影日を取得
          shottime = getShotdate(f)
          if shottime == _getfail:
            shottimevalue = datetime.datetime.strptime(getfilemtime(f), _datetimeformat)
          else:
            try:
               # Exifは年月日も : 区切り
               shottimevalue = datetime.datetime.strptime(shottime,'%Y:%m:%d %H:%M:%S')
            except Exception as e:
               # 取得できない場合は更新日時
               shottimevalue = datetime.datetime.strptime(getfilemtime(f), _datetimeformat)

          listshotdate.append(str(shottimevalue))
          liststrshotdate.append(shottimevalue)

          # ファイル名
          filename = os.path.basename(f)
          listext.append(os.path.splitext(f)[1])
          listfilename.append(str(filename))
          listplace.append('')

        # 初期
        table_data_ = {'0':listchks,'1':listpaths,'2':listshotdate}

        # 初期値
        table_data_file = table_data_

        # 行数、列数を変更する
        self.setRowCount(len(paths))
        self.setColumnCount(len(table_data_))

        # 初期値をセット
        self.data = table_data_file
        self.setData()

        # 列のサイズ調整
        self.resizeColumnsToContents()
        # 行のサイズ調整
        self.resizeRowsToContents()

        row_count = self.rowCount()

        for r in range(row_count):
          # https://doc.qt.io/qt-5/qcheckbox.html#checkState
          # https://tm8r.hateblo.jp/entry/2017/12/14/000000
          chkbox = QCheckBox(self)
          chkbox.setText('対象')
          # こちらの checkState は上手く取得できている（次も含む）
          print('chkbox.checkState before', chkbox.checkState(), sep='\t')
          chkbox.setObjectName(f"checkBox_{r}")
          chkbox.setChecked(True) # チェックボックスの値のセット(チェック状態にする)
          print('chkbox.checkState after', chkbox.checkState(), sep='\t')
          self.setCellWidget(r, 0, chkbox)
          item = self.item(r, 6)

          # for c in range(1,3):
          #   item = self.item(r, c)
          #   # 編集不可・選択不可にする
          #   item.setFlags(Qt.NoItemFlags)

    def setData(self):
        horHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)

class window(QWidget):
  def __init__(self, parent = None):
    # ウィンドウ
    super(window, self).__init__(parent)
    windowWidth = 1300
    windowHeight = 700

    self.move(10,10)
    self.resize(windowWidth,windowHeight)
    self.setWindowTitle("写真管理")

    # テーブル
    # 本来は glob
    paths = _filepiclist
    paths.sort(key=os.path.getmtime, reverse=True)
    table_data_file = {}

    self.table = TableView(table_data_file, 1, 1, self)
    self.table.setStyleSheet("QTableView{gridline-color: black;color:green;background-color: azure;}")
    self.table.resize(windowWidth - 100,windowHeight - 300)
    self.table.move(20,20)

    # ボタンの設置
    self.button = QPushButton('チェック', self)
    self.button.setStyleSheet("QPushButton{color:black;background-color:gray;}")
    self.button.setStyleSheet("QPushButton:pressed{color:teal;background-color:coral;}")
    self.button.move(windowWidth - 300,windowHeight - 50)
    self.button.clicked.connect(self.checkwork)

    self.button2 = QPushButton('終了', self)
    self.button2.setStyleSheet("QPushButton{color:black;background-color:gold;}")
    self.button2.move(windowWidth - 100,windowHeight - 50)
    self.button2.clicked.connect(self.exit)

    # 初期アクティブセル
    self.table.setCurrentCell(0,4)

  # 行カウント
  def checkwork(self):
    rowPosition = self.table.rowCount()

    intcheck = 0

    for r in range(0,rowPosition):

        # 解決対策 1 → 解消せず　
        # chkbox = QCheckBox(self)
        # print('chkbox.checkState', chkbox.checkState(), sep='\t')

        # 不具合？の箇所=エラーとはならず、チェック時は 2 になるはずだが 2にならない
        item = self.table.item(r, 0)
        print('チェック状態', item.text(),sep='\t')
        print('チェック状態', item.checkState(),sep='\t')
        for c in range(0,2):
          item = self.table.item(r, c)
          if item.checkState() == 2:
            intcheck += 1

    # メッセージボックス
    QMessageBox.information(None, "check", f"チェック済みは{intcheck}個あります。 ", QMessageBox.Ok)

  # 値を変える
  def change_table_val(self):
    # 行カウント
    rowPosition = self.table.rowCount()
    # 列カウント
    colPosition = self.table.columnCount()


  # 画面を終了させる
  def exit(self):
        self.close()

  # キーボードの制御
  def keyPressEvent(self, e):
        # F12を押すと画面が閉じる
        if e.key() == Qt.Key_F12:
            exit(self)


def main():
   app = QApplication(sys.argv)
   ex = window()
   # ウィンドウ表示
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
