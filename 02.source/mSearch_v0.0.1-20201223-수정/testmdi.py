# PYQT5 를 이용하기 위한 모듈갱신
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import sys


import csv
import subprocess



class Form(QDialog):
 def __init__(self, parent=None):
    super(Form, self).__init__(parent)

    self.le = QLineEdit()
    self.le.setObjectName("host")
    self.lee = QLineEdit()
    self.lee.setObjectName("hosta")

    self.pb = QPushButton()
    self.pb.setObjectName("connect")
    self.pb.setText("inject")

    layout = QFormLayout()
    layout.addWidget(self.le)
    layout.addWidget(self.lee)
    layout.addWidget(self.pb)

    self.setLayout(layout)
    self.connect(self.pb, SIGNAL("clicked()"), self.button_click)
    self.setWindowTitle("Stuck-at-0")

 def button_click(self):
    # shost is a QString object
    n = int(self.le.text())
    line = str(self.lee.text())
    print(n, line)
    with open('main.txt', 'r') as files:
        # read a list of lines into data
        data = files.readlines()

    # now inject fault in nth level, note that you have to add a newline
    print
    data[1]
    if line in data[0]:
        data.insert(n + 1, '0' + ',' + line + '\n')
    # and write everything back
    with open('main.txt', 'w') as files:
        files.writelines(data)
    res = subprocess.call(['python stuck.py'], shell=True)
    res = subprocess.call(['python comp.py'], shell=True)

class UserWindow(QMainWindow):
    def __init__(self):
        super(UserWindow, self).__init__()
        self.ctr_frame = QtGui.QWidget()
        self.specTable = QtGui.QTableView()
        self.specModel = QtGui.QStandardItemModel(self)
        self.specList = self.createSpecTable()
        self.initUI()

def specData(self):
    with open('tests.csv', 'rb') as csvInput:
        for row in csv.reader(csvInput):
            if row > 0:
                items = [QtGui.QStandardItem(field) for field in row]
                self.specModel.appendRow(items)

def createSpecTable(self):
    # This is a test header - different from what is needed
    specHdr = ['Test', 'Date', 'Time', 'Type']
    self.specData()
    specM = specTableModel(self.specModel, specHdr, self)
    self.specTable.setModel(specM)
    self.specTable.setShowGrid(False)
    v_head = self.specTable.verticalHeader()
    v_head.setVisible(False)
    h_head = self.specTable.horizontalHeader()
    h_head.setStretchLastSection(True)
    self.specTable.sortByColumn(3, Qt.DescendingOrder)
    return self.specTable

def initUI(self):

    self.specList.setModel(self.specModel)
    p_grid = QtGui.QGridLayout()
    p_grid.setSpacing(5)
    p_grid.addWidget(self.specList, 2, 5, 13, 50)
    self.ctr_frame.setLayout(p_grid)
    self.setCentralWidget(self.ctr_frame)
    self.statusBar()
    bar = self.menuBar()
    menu_item1 = bar.addMenu("Circuit Details")
    fault_inject = bar.addMenu("Fault Injection")

    fault_inject_sa = fault_inject.addMenu("Stuck-at Fault")
    fault_inject_sa.addAction("Stuck-at-0")
    fault_inject_sa.addAction("Stuck-at-1")

    fault_inject_bridge = fault_inject.addMenu("Bridging Fault")
    fault_inject_bridge.addAction("Bridging-OR")
    fault_inject_bridge.addAction("Bridging-AND")

    fault_inject_cross = fault_inject.addMenu("Crosspoint Fault")
    fault_inject_cross.addAction("Crosspoint-Appearance")
    fault_inject_cross.addAction("Crosspoint-Dissappearence")

    fault_inject_mgf = fault_inject.addMenu("Missing Gate Fault")
    fault_inject_mgf.addAction("Single-MGF")
    fault_inject_mgf.addAction("Multiple-MGF")
    fault_inject_mgf.addAction("Repeated-MGF")
    fault_inject_mgf.addAction("Partial-MGF")
    self.setWindowTitle('Truth Table')
    fault_inject.triggered[QAction].connect(self.fault_injection)

def fault_injection(self, q):
    print("triggered")

    if q.text() == "Stuck-at-0":
        print(q.text())
        exx = Form()
        self.mdi.addSubWindow(exx)
        exx.show()

    if q.text() == "Stuck-at-1":
        print(q.text())
    if q.text() == "Bridging-OR":
        print(q.text())
    if q.text() == "Bridging-AND":
        print(q.text())
    if q.text() == "Crosspoint-Appearance":
        print(q.text())
    if q.text() == "Crosspoint-Dissappearence":
        print(q.text())
    if q.text() == "Single-MGF":
        print(q.text())
    if q.text() == "Multiple-MGF":
        print(q.text())
    if q.text() == "Repeated-MGF":
        print(q.text())
    if q.text() == "Partial-MGF":
        print(q.text())


class specTableModel(QAbstractTableModel):
 def __init__(self, datain, headerData, parent=None, *args):

    QAbstractTableModel.__init__(self, parent, *args)
    self.arrayData = datain
    self.headerData = headerData

 def rowCount(self, parent):
    return 0

 def columnCount(self, parent):
    return 0

 def data(self, index, role):
    if not index.isValid():
        return QVariant()
    elif role != Qt.DisplayRole:
        return QVariant()
    return QVariant(self.arraydata[index.row()][index.column()])

 def headerData(self, col, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
        return self.headerdata[col]
    return None



class MainWindow(QMainWindow):
 count = 0
 filename = 0

 def test_display(self,q):
    self.mdi.tileSubWindows()

 def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)
    self.mdi = QMdiArea()
    self.setCentralWidget(self.mdi)
    bar = self.menuBar()
    menu_item1 = bar.addMenu("About Tool")
    menu_item_tool = menu_item1.addMenu("User Manual")
    menu_item_example = menu_item1.addMenu("Example and Demos")

    menu_item2 = bar.addMenu("Reversible Computing")
    menu_item_rc = menu_item2.addMenu("RC vs Conventional")
    menu_item_rcg = menu_item2.addMenu("RC Gates")
    menu_item_rcp = menu_item2.addMenu("Properties of RC")
    menu_item_rcl = menu_item2.addMenu("RC Gate Libraries")



    menu_item = bar.addMenu("Benchmark Circuits")
    menu_item_gate = menu_item.addMenu("Functions")
    menu_item_realize = menu_item.addMenu("Realization Library")
    menu_item_nct = menu_item_realize.addMenu("NCT")
    menu_item_gt = menu_item_realize.addMenu("GT")
    menu_item_nctf = menu_item_realize.addMenu("NCTF")
    menu_item_gf = menu_item_realize.addMenu("GF")

    menu_item_4b1_5g = menu_item_gate.addMenu("4b1_5g")
    menu_item_4b1_5g.addAction("4b1_5g_1")
    menu_item_4b1_5g.addAction("4b1_5g_2")
    menu_item_4b1_5g.addAction("4b1_5g_3")
    menu_item_4b1_5g.addAction("4b1_5g_4")
    menu_item_4b1_5g.addAction("4b1_5g_5")

    menu_item_adder = menu_item_gate.addMenu("Adders")
    menu_item_adder.addAction("1bitadder(rd32)")
    menu_item_adder.addAction("5bitadder")
    menu_item_adder.addAction("8bitadder")

    menu_item_div_checker = menu_item_gate.addMenu("Divisiblity Checkers")
    menu_item_div_checker.addAction("4mod5")
    menu_item_div_checker.addAction("5mod5")

    menu_item_cyclic = menu_item_gate.addMenu("Cycle Functions")
    menu_item_cyclic.addAction("cycle10_2")
    menu_item_cyclic.addAction("cycle17_3")

    menu_item_galois = menu_item_gate.addMenu("Galois Field Multipliers")
    menu_item_galois.addAction("gf2^3mult")
    menu_item_galois.addAction("gf2^4mult")
    menu_item_galois.addAction("gf2^5mult")
    menu_item_galois.addAction("gf2^6mult")
    menu_item_galois.addAction("gf2^7mult")
    menu_item_galois.addAction("gf2^8mult")
    menu_item_galois.addAction("gf2^9mult")
    menu_item_galois.addAction("gf2^10mult")
    menu_item_galois.addAction("gf2^11mult")
    menu_item_galois.addAction("gf2^12mult")
    menu_item_galois.addAction("gf2^13mult")
    menu_item_galois.addAction("gf2^14mult")
    menu_item_galois.addAction("gf2^15mult")
    menu_item_galois.addAction("gf2^16mult")
    menu_item_galois.addAction("gf2^17mult")
    menu_item_galois.addAction("gf2^18mult")
    menu_item_galois.addAction("gf2^19mult")
    menu_item_galois.addAction("gf2^20mult")
    menu_item_galois.addAction("gf2^32mult")
    menu_item_galois.addAction("gf2^50mult")
    menu_item_galois.addAction("gf2^64mult")
    menu_item_galois.addAction("gf2^100mult")
    menu_item_galois.addAction("gf2^127mult")
    menu_item_galois.addAction("gf2^128mult")
    menu_item_galois.addAction("gf2^256mult")
    menu_item_galois.addAction("gf2^512mult")

    menu_item_hamming = menu_item_gate.addMenu("Hamming Code Functions")
    menu_item_hamming.addAction("ham3")
    menu_item_hamming.addAction("ham7")
    menu_item_hamming.addAction("ham15")

    menu_item_hbw = menu_item_gate.addMenu("Hidden Weight Coding Functions")
    menu_item_hbw.addAction("hbw4")
    menu_item_hbw.addAction("hbw5")
    menu_item_hbw.addAction("hbw6")
    menu_item_hbw.addAction("hbw7")
    menu_item_hbw.addAction("hbw8")
    menu_item_hbw.addAction("hbw9")
    menu_item_hbw.addAction("hbw10")
    menu_item_hbw.addAction("hbw11")
    menu_item_hbw.addAction("hbw12")
    menu_item_hbw.addAction("hbw13")
    menu_item_hbw.addAction("hbw14")
    menu_item_hbw.addAction("hbw15")
    menu_item_hbw.addAction("hbw16")
    menu_item_hbw.addAction("hbw20")
    menu_item_hbw.addAction("hbw50")
    menu_item_hbw.addAction("hbw100")
    menu_item_hbw.addAction("hbw200")
    menu_item_hbw.addAction("hbw500")
    menu_item_hbw.addAction("hbw1000")

    menu_item_mdd = menu_item_gate.addMenu("MDD Worst Case")
    menu_item_mdd.addAction("3_17.tfc")
    menu_item_mdd.addAction("4_49")

    menu_item_modular = menu_item_gate.addMenu("Modula Adders")
    menu_item_modular.addAction("mod5adder")
    menu_item_modular.addAction("mod1024adder")
    menu_item_modular.addAction("mod1048576adder")

    menu_item_prime = menu_item_gate.addMenu("N-th Prime")
    menu_item_prime.addAction("nth_prime3_inc")
    menu_item_prime.addAction("nth_prim4_inc")
    menu_item_prime.addAction("nth_prime5_inc")
    menu_item_prime.addAction("nth_prime6_inc")
    menu_item_prime.addAction("nth_prime7_inc")
    menu_item_prime.addAction("nth_prime8_inc")
    menu_item_prime.addAction("nth_prime9_inc")
    menu_item_prime.addAction("nth_prime10_inc")
    menu_item_prime.addAction("nth_prime11_inc")
    menu_item_prime.addAction("nth_prime12_inc")
    menu_item_prime.addAction("nth_prime13_inc")
    menu_item_prime.addAction("nth_prime14_inc")
    menu_item_prime.addAction("nth_prime15_inc")
    menu_item_prime.addAction("nth_prime16-inc")

    menu_item_permanent = menu_item_gate.addMenu("Permanent")
    menu_item_permanent.addAction("permanent1x1")
    menu_item_permanent.addAction("permanent2x2")
    menu_item_permanent.addAction("permanent3x3")
    menu_item_permanent.addAction("permanent4x4")

    menu_item_rd = menu_item_gate.addMenu("RD-Input Weight functions")
    menu_item_rd.addAction("rd53")
    menu_item_rd.addAction("rd73")
    menu_item_rd.addAction("rd84")

    menu_item_sym = menu_item_gate.addMenu("Symmetric Functions")
    menu_item_sym.addAction("6sym")
    menu_item_sym.addAction("9sym")

    menu_item_oth = menu_item_gate.addMenu("Others")
    menu_item_oth.addAction("2_4dec")
    menu_item_oth.addAction("2of5")
    menu_item_oth.addAction("xor5")

    self.setWindowTitle("Reversible Fault Testing")

    #menu_item.triggered[QAction].connect(self.truth_table_gen)

 def windowaction(self, q):
    print("triggered")
    print(q.text())

    if "New" == "New":
        MainWindow.count += 1
        sub = QMdiSubWindow()
        sub.setWidget(QTextEdit())
        sub.setWindowTitle("tst")
        self.mdi.addSubWindow(sub)
        sub.show()


# truth table display widget

def truth_table_gen(self, q):
    MainWindow.count += 1
    MainWindow.filename = q.text()
    to_readfile = open(q.text(), 'r')
    try:
        reading_file = to_readfile.read()

        writefile = open('a.tfc', 'w')
        try:
            writefile.write(reading_file)
        finally:
            writefile.close()
    finally:
        to_readfile.close()
    subprocess.call(['python truth_gen.py'], shell=True)
    exx = UserWindow()
    self.mdi.addSubWindow(exx)
    exx.show()
    self.mdi.tileSubWindows()


def main():
 app = QApplication(sys.argv)
 ex = MainWindow()
 ex.show()
 #ex.resize(1366, 750)
 sys.exit(app.exec_())


if __name__ == '__main__':
 main()

