from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
import pandas as pd
import numpy as np


class DetailWindow(QWidget):
    def __init__(self, metaatomindexArray, metaatomlist, cocross):
        super().__init__()
        self.setWindowTitle("Array Window")
        self.meta_array = metaatomindexArray
        self.meta_list = metaatomlist
        self.cocross = cocross
        self.setGeometry(500, 300, 500, 600)
        
        layout = QVBoxLayout()
        arrayBox = QGroupBox('Metalens Array')
        arrayBox.setLayout(QVBoxLayout())
        arrayTable = QTableWidget(metaatomindexArray.shape[0], metaatomindexArray.shape[1])
        for i in range(metaatomindexArray.shape[0]):
            for j in range(metaatomindexArray.shape[1]):
                array_item = QTableWidgetItem(str(metaatomindexArray[i, j]))
                array_item.setTextAlignment(Qt.AlignCenter)
                arrayTable.setItem(i, j, array_item)
        array_header = arrayTable.horizontalHeader()
        array_header.setSectionResizeMode(QHeaderView.Stretch)
        arrayBox.layout().addWidget(arrayTable)
        
        listBox = QGroupBox('Metaatom List')
        listBox.setLayout(QVBoxLayout())
        listTable = QTableWidget(metaatomlist.shape[0], 4)
        if cocross == 'Co-pol':
            listTable.setHorizontalHeaderLabels(['Length (nm)', 'Transmittance', 'Phase (rad)', 'Shape'])
            for i in range(metaatomlist.shape[0]):
                l = QTableWidgetItem(f'{int(round(metaatomlist[i, 0] * 1e9, -1))}')
                l.setTextAlignment(Qt.AlignCenter)
                Tr = QTableWidgetItem(f'{metaatomlist[i, 1]: .4f}')
                Tr.setTextAlignment(Qt.AlignCenter)
                phase = QTableWidgetItem(f'{metaatomlist[i, 2]: .4f}')
                phase.setTextAlignment(Qt.AlignCenter)
                if int(metaatomlist[i, 3]) == 1:
                    Shape = QTableWidgetItem('○')
                elif int(metaatomlist[i, 3]) == 2:
                    Shape = QTableWidgetItem('□')
                Shape.setTextAlignment(Qt.AlignCenter)
                listTable.setItem(i, 0, l)
                listTable.setItem(i, 1, Tr)
                listTable.setItem(i, 2, phase)
                listTable.setItem(i, 3, Shape)
        elif cocross == 'Cross-pol':
            listTable.setHorizontalHeaderLabels(['X (nm)', 'Y (nm)', 'Transmittance', 'Phase (rad)', 'Transmittance (Cross)', 'Phase (Cross)'])
            for i in range(metaatomlist.shape[0]):
                x = QTableWidgetItem(f'{int(round(metaatomlist[i, 0] * 1e9, -1))}')
                x.setTextAlignment(Qt.AlignCenter)
                y = QTableWidgetItem(f'{int(round(metaatomlist[i, 1] * 1e9, -1))}')
                y.setTextAlignment(Qt.AlignCenter)
                Tr = QTableWidgetItem(f'{metaatomlist[i, 2]: .4f}')
                Tr.setTextAlignment(Qt.AlignCenter)
                phase = QTableWidgetItem(f'{metaatomlist[i, 3]: .4f}')
                phase.setTextAlignment(Qt.AlignCenter)
                listTable.setItem(i, 0, QTableWidgetItem(x))
                listTable.setItem(i, 1, QTableWidgetItem(y))
                listTable.setItem(i, 2, QTableWidgetItem(Tr))
                listTable.setItem(i, 3, QTableWidgetItem(phase)) 
        
        list_header = listTable.horizontalHeader()
        list_header.setSectionResizeMode(QHeaderView.Stretch)
        listBox.layout().addWidget(listTable)        
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel('File Name:'))
        self.exportLine = QLineEdit()
        export_layout.addWidget(self.exportLine)
        self.exportButton = QPushButton('Export')
        export_layout.addWidget(self.exportButton)
        self.exportButton.clicked.connect(self.export_csv)        
        layout.addWidget(arrayBox)
        layout.addWidget(listBox)
        layout.addLayout(export_layout)
        
        self.setLayout(layout)
        
        
    def export_csv(self):
        filename = self.exportLine.text()
        array_df = pd.DataFrame(np.copy(self.meta_array), dtype=int)
        array_df.to_csv('./Export/Array_' + filename + '.csv', header=False, index=False)
        
        list_df = pd.DataFrame(np.copy(self.meta_list), dtype=float, index=list(range(1, self.meta_list.shape[0]+1)))
        if self.cocross == 'Co-pol':
            list_df.columns = ['Length (nm)', 'Transmittance', 'Phase (rad)', 'Shape']
            list_df.iloc[:, 0] = list_df.iloc[:, 0].apply(lambda x: int(round(x * 1e9, -1)))
            list_df.iloc[:, 1] = list_df.iloc[:, 1].apply(lambda x: round(x, 4))
            list_df.iloc[:, 2] = list_df.iloc[:, 2].apply(lambda x: round(x, 4))
            list_df.iloc[:, 3] = list_df.iloc[:, 3].apply(lambda x: int(x))
        elif self.cocross == 'Cross-pol':
            list_df.columns = ['X (nm)', 'Y (nm)', 'Transmittance', 'Phase (rad)']
            list_df.iloc[:, 0] = list_df.iloc[:, 0].apply(lambda x: int(round(x * 1e9, -1)))
            list_df.iloc[:, 1] = list_df.iloc[:, 1].apply(lambda x: int(round(x * 1e9, -1)))
            list_df.iloc[:, 2] = list_df.iloc[:, 2].apply(lambda x: round(x, 4))
            list_df.iloc[:, 3] = list_df.iloc[:, 3].apply(lambda x: round(x, 4))
        list_df.to_csv('./Export/List_' + filename + '.csv', index=list(range(1, list_df.shape[0]+1)))
        