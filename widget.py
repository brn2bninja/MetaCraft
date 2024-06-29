from PySide6.QtWidgets import *
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont, QIcon
from newwindow import *

import os
import math
import numpy as np
from sklearn.metrics import r2_score
from collections import OrderedDict
import matplotlib.pyplot as plt

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaCraft")
        self.setWindowIcon(QIcon("appicon.png"))
        self.font = QFont("Times", 10.5)
        self.setFont(self.font)
        self.linewidth = 100
        self.setGeometry(700, 500, 500, 700)
        self.order_nfd = [0, 1, 2]
        self.fnum = 4
        self.sorted = False
        
        # 1. Groupbox for metalens design parameters
        MetadesignBox = QGroupBox("Metalens Design Parameters")
        
        wave_layout = self.selectWave()
        pol_layout  = self.selectPol()
        nfd_layout  = self.recieveNFD()
        THA_layout  = self.recieveTHA()
        
        designParam_layout = QVBoxLayout()
        designParam_layout.addLayout(wave_layout)
        designParam_layout.addLayout(pol_layout)
        designParam_layout.addLayout(nfd_layout)
        designParam_layout.addLayout(THA_layout)
        MetadesignBox.setLayout(designParam_layout)
        
        # 2. CheckBox for Material Selection
        MaterialCheckBox = self.selectMaterial()
        
        # 3. Search Button
        self.searchButton = QPushButton("Search")
        self.searchButton.setFixedSize(120, 120)
        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.searchButton.clicked.connect(self.setAdditionalLayout)
        
        # 4. Result Box
        ResultBox = self.popResult()
        
        # 5. Export Section
        ExportBox = self.exportData()
        
        # Layout 2-3
        layout23 = QVBoxLayout()
        layout23.addWidget(MaterialCheckBox)
        layout23.addWidget(self.searchButton)
        
        # User-input Layout 
        layout_input = QHBoxLayout()
        layout_input.addWidget(MetadesignBox)
        layout_input.addLayout(layout23)
        
        # Total layout
        layout_total = QVBoxLayout()
        layout_total.addLayout(layout_input)
        layout_total.addWidget(ResultBox)
        layout_total.addWidget(ExportBox)
        self.setLayout(layout_total)
    
    def selectWave(self):
        # Wavelength label
        wlLabel = QLabel("Wavelength (nm)")
        
        # Combobox for wavelength domain
        self.wlDomain = QComboBox(self)
        self.wlDomain.addItems(["Visible", "Near Infrared", "Ultra Violet"])
        
        # Combobox for wavelength value
        self.wlValue = QComboBox(self)
        self.wlValue.setFixedWidth(50)
        wl_vis = [str(i) for i in range(400, 701, 5)] + ["532", "632.8"]
        wl_nir = ["900", "940", "980", "1550"]
        wl_uv =  ["248", "266", "325", "384"]
        self.wlValue.addItems(wl_vis)
        def update_wlValue():
            selected_domain = self.wlDomain.currentText()
            if selected_domain == "Visible":
                self.wlValue.clear()
                self.wlValue.addItems(wl_vis)
            elif selected_domain == "Near Infrared":
                self.wlValue.clear()
                self.wlValue.addItems(wl_nir)
            elif selected_domain == "Ultra Violet":
                self.wlValue.clear()
                self.wlValue.addItems(wl_uv)
        self.wlDomain.currentTextChanged.connect(update_wlValue)
        
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(wlLabel); wave_layout.addWidget(self.wlDomain); wave_layout.addWidget(self.wlValue)
        
        return wave_layout

    def selectPol(self):
        # Polarization label
        polLabel = QLabel("Polarization Dependency")
        
        # Combobox for polarization dependency
        self.pol_dependency = QComboBox(self)
        self.pol_dependency.addItems(["Dependent", "Independent"])
        
        # Combobox for polarization value
        self.polValue = QComboBox(self)
        self.polValue.addItems(["RCP", "LCP"])
        def update_polValue():
            selected_dependency = self.pol_dependency.currentText()
            if selected_dependency == "Dependent":
                # Set polarization
                self.polValue.clear()
                self.polValue.addItems(["RCP", "LCP"])
                
            elif selected_dependency == "Independent":
                # Set polarization
                self.polValue.clear()
                self.polValue.addItems(["Co-pol", "Cross-pol"])
        self.pol_dependency.currentTextChanged.connect(update_polValue)
        
        pol_layout = QHBoxLayout()
        pol_layout.addWidget(polLabel); pol_layout.addWidget(self.pol_dependency); pol_layout.addWidget(self.polValue)
        
        return pol_layout

    def recieveNFD(self):
        # NA, F, D label
        naLabel = QLabel("Numerical Aperture")
        fLabel = QLabel("Focal Length (um)")
        dLabel = QLabel("Diameter (um)")

        # Line edit for NA, F, D
        self.naEntry = QLineEdit('0.1')
        self.naEntry.setFixedWidth(self.linewidth)
        self.naEntry.setAlignment(Qt.AlignRight)
        self.naEntry.editingFinished.connect(self.n_edited)
        self.fEntry = QLineEdit('250')
        self.fEntry.setFixedWidth(self.linewidth)
        self.fEntry.setAlignment(Qt.AlignRight)
        self.fEntry.editingFinished.connect(self.f_edited)
        self.dEntry = QLineEdit('50')  
        self.dEntry.setFixedWidth(self.linewidth)
        self.dEntry.setAlignment(Qt.AlignRight)
        self.dEntry.editingFinished.connect(self.d_edited)      
        
        na_layout = QHBoxLayout()
        na_layout.addWidget(naLabel); na_layout.addWidget(self.naEntry)
        f_layout = QHBoxLayout()
        f_layout.addWidget(fLabel); f_layout.addWidget(self.fEntry)
        d_layout = QHBoxLayout()
        d_layout.addWidget(dLabel); d_layout.addWidget(self.dEntry)
        
        nfd_layout = QVBoxLayout()
        nfd_layout.addLayout(na_layout); nfd_layout.addLayout(f_layout); nfd_layout.addLayout(d_layout)  
        
        return nfd_layout
    
    def recieveTHA(self):
        # Transmittance, Height, Aspect Ratio label
        tLabel = QLabel("Minimum Transmittance (%)")
        hLabel = QLabel("Maximum Height (nm)")
        arLabel = QLabel("Maximum Aspect Ratio")
        # Line edit for Transmittance, Height, Aspect Ratio
        self.tEntry = QLineEdit('50')
        self.tEntry.setFixedWidth(self.linewidth)
        self.tEntry.setAlignment(Qt.AlignRight)
        self.hEntry = QLineEdit('700')
        self.hEntry.setFixedWidth(self.linewidth)
        self.hEntry.setAlignment(Qt.AlignRight)
        self.arEntry = QLineEdit('35')
        self.arEntry.setFixedWidth(self.linewidth)
        self.arEntry.setAlignment(Qt.AlignRight)
        t_layout = QHBoxLayout()
        t_layout.addWidget(tLabel); t_layout.addWidget(self.tEntry)
        h_layout = QHBoxLayout()
        h_layout.addWidget(hLabel); h_layout.addWidget(self.hEntry)
        ar_layout = QHBoxLayout()
        ar_layout.addWidget(arLabel); ar_layout.addWidget(self.arEntry)
        
        tha_layout = QVBoxLayout()
        tha_layout.addLayout(t_layout); tha_layout.addLayout(h_layout); tha_layout.addLayout(ar_layout)

        return tha_layout
    
    def selectMaterial(self):
        MaterialCheckBox = QGroupBox("Material Selection")
        mat_uv = ["Select All", "SiNx (High)", "SiNx (Mid)", "SiNx (Low)", "ZrO2 (PER)"]
        mat_vis = ["Select All", "a-Si (Vis)", "TiO2", "TiO2 (PER)", "Si (PER)"]
        mat_nir = ["Select All", "a-Si (NIR)", "Si (PER)"]
        
        self.mat_layout = QVBoxLayout()
        mat_selected = mat_vis
        for mat in mat_selected:
            self.mat_layout.addWidget(QCheckBox(mat))
        
        def update_mat():
            num_w = self.mat_layout.count()
            for i in range(num_w):
                self.mat_layout.itemAt(i).widget().deleteLater()
            if self.wlDomain.currentText() == "Ultra Violet":
                mat_selected = mat_uv
            elif self.wlDomain.currentText() == "Visible":
                mat_selected = mat_vis
            elif self.wlDomain.currentText() == "Near Infrared":
                mat_selected = mat_nir
            
            for mat in mat_selected:
                self.mat_layout.addWidget(QCheckBox(mat))
        self.wlDomain.currentTextChanged.connect(update_mat)
        
        def click_all():
            if self.mat_layout.itemAt(0).widget().isChecked():
                for i in range(1, self.mat_layout.count()):
                    self.mat_layout.itemAt(i).widget().setChecked(True)
            else:
                for i in range(1, self.mat_layout.count()):
                    self.mat_layout.itemAt(i).widget().setChecked(False)
        self.mat_layout.itemAt(0).widget().checkStateChanged.connect(click_all)
        MaterialCheckBox.setLayout(self.mat_layout)
        
        return MaterialCheckBox
    
    def popResult(self):
        ResultBox = QGroupBox("Result")
        ResultBox_layout = QVBoxLayout()
        self.result = QListWidget()
        self.result.lineWrapMode = QTextEdit.WidgetWidth
        sort_label = QLabel("Sort by ")
        
        self.sort_choice = QComboBox()
        self.sort_choice.addItems(["Transmittance", "FoM"])
        def update_sortingmethod():
            selected_dependency = self.pol_dependency.currentText()
            if selected_dependency == "Dependent":
                self.sort_choice.clear()
                self.sort_choice.addItems(["Transmittance", "FoM"])
                self.result.setSelectionMode(QAbstractItemView.SingleSelection)
            elif selected_dependency == "Independent":
                self.sort_choice.clear()
                self.sort_choice.addItems(["Transmittance", "FoM (fast)", "FoM (exact)"])
                self.result.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.pol_dependency.currentTextChanged.connect(update_sortingmethod)
        
        self.sort_button = QPushButton("Sort")
        self.sort_button.clicked.connect(self.sortButtonClicked)
        
        self.details_or_rotationlevel = QHBoxLayout()
        self.details_or_rotationlevel.addWidget(QPushButton("Show Details"))
                
        Result_additional_layout = QHBoxLayout()
        Result_additional_layout_1 = QHBoxLayout()
        Result_additional_layout_1.addWidget(sort_label)
        Result_additional_layout_1.addWidget(self.sort_choice)
        Result_additional_layout_1.addWidget(self.sort_button)
        
        self.Result_additional_layout_2 = QHBoxLayout()
        Result_additional_layout_3 = QHBoxLayout()
        self.plot_fig = QPushButton("Plot Figure")
        self.plot_fig.clicked.connect(self.plotFigure)
        Result_additional_layout_3.addWidget(self.plot_fig)
        
        Result_additional_layout.addLayout(Result_additional_layout_1)
        Result_additional_layout.addLayout(self.Result_additional_layout_2)
        Result_additional_layout.addLayout(Result_additional_layout_3)
        
        ResultBox_layout.addWidget(self.result)
        ResultBox_layout.addLayout(Result_additional_layout)
        ResultBox.setLayout(ResultBox_layout)
        return ResultBox
    
    def exportData(self):
        ExportBox = QGroupBox("Export Data")

        # File Name
        file_name_layout = QHBoxLayout()
        fname_label = QLabel("File Name")
        self.export_file_name = QLineEdit()
        file_name_layout.addWidget(fname_label)
        file_name_layout.addWidget(self.export_file_name)
        
        # GDS options
        gds_layout = QVBoxLayout()
        self.Cbox_modify_gds = QCheckBox("Modify GDS")
        self.Cbox_reverse_pattern = QCheckBox("Reverse Pattern")
        gds_layout.addWidget(self.Cbox_modify_gds)
        gds_layout.addWidget(self.Cbox_reverse_pattern)        
        
        # File + GDS layout
        file_gds_layout = QHBoxLayout()
        file_gds_layout.addLayout(file_name_layout)
        file_gds_layout.addLayout(gds_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.lumerical_button = QPushButton("Export to Lumerical")
        self.lumerical_button.clicked.connect(self.export_FDTD)
        self.VirtualLab_button = QPushButton("Export to VirtualLab")
        self.VirtualLab_button.clicked.connect(self.export_VirtualLab)
        self.GDS_button = QPushButton("Export to GDS")
        self.GDS_button.clicked.connect(self.export_GDS)
        button_layout.addWidget(self.lumerical_button)
        button_layout.addWidget(self.VirtualLab_button)
        button_layout.addWidget(self.GDS_button)
        
        # Total layout
        export_layout = QVBoxLayout()
        export_layout.addLayout(file_gds_layout)
        export_layout.addLayout(button_layout)
        
        ExportBox.setLayout(export_layout)
        return ExportBox
    
    @Slot()
    def n_edited(self):   
        na = float(self.naEntry.text())
        f = float(self.fEntry.text())
        D = float(self.dEntry.text())
        
        self.order_nfd[0] = 0
        min_val = min(self.order_nfd[1], self.order_nfd[2]); one_idx = self.order_nfd.index(min_val)
        max_val = max(self.order_nfd[1], self.order_nfd[2]); two_idx = self.order_nfd.index(max_val)
        self.order_nfd[one_idx] = 1; self.order_nfd[two_idx] = 2

        # F was the last to be editted -> Change F
        if self.order_nfd[1] == 2:
            F = D / (2 * math.tan(math.asin(na))) if D != 0 and na != 0 else 250e-6
            self.fEntry.setText(str(round(F, self.fnum)))
            
        # D was the last to be editted -> Change D
        elif self.order_nfd[2] == 2:
            D = 2 * f * math.tan(math.asin(na)) if f != 0 and na != 0 else 500e-6
            self.dEntry.setText(str(round(D, self.fnum)))
    
    @Slot()
    def f_edited(self):   
        na = float(self.naEntry.text())
        f = float(self.fEntry.text())
        D = float(self.dEntry.text())
        
        self.order_nfd[1] = 0
        min_val = min(self.order_nfd[2], self.order_nfd[0]); one_idx = self.order_nfd.index(min_val)
        max_val = max(self.order_nfd[2], self.order_nfd[0]); two_idx = self.order_nfd.index(max_val)
        self.order_nfd[one_idx] = 1; self.order_nfd[two_idx] = 2

        # NA was the last to be editted -> Change NA
        if self.order_nfd[0] == 2:
            NA = math.sin(math.atan(D / (2 * f))) if D != 0 and f != 0 else 0.71
            self.naEntry.setText(str(round(NA, self.fnum)))
            
        # D was the last to be editted -> Change D
        elif self.order_nfd[2] == 2:
            D = 2 * f * math.tan(math.asin(na)) if f != 0 and na != 0 else 500e-6
            self.dEntry.setText(str(round(D, self.fnum)))
    
    @Slot()
    def d_edited(self):   
        na = float(self.naEntry.text())
        f = float(self.fEntry.text())
        D = float(self.dEntry.text())
        
        self.order_nfd[2] = 0
        min_val = min(self.order_nfd[0], self.order_nfd[1]); one_idx = self.order_nfd.index(min_val)
        max_val = max(self.order_nfd[0], self.order_nfd[1]); two_idx = self.order_nfd.index(max_val)
        self.order_nfd[one_idx] = 1; self.order_nfd[two_idx] = 2

        # NA was the last to be editted -> Change NA
        if self.order_nfd[0] == 2:
            NA = math.sin(math.atan(D / (2 * f))) if D != 0 and f != 0 else 0.71
            self.naEntry.setText(str(round(NA, self.fnum)))
        
        # F was the last to be editted -> Change F
        elif self.order_nfd[1] == 2:
            F = D / (2 * math.tan(math.asin(na))) if D != 0 and na != 0 else 250e-6
            self.fEntry.setText(str(round(F, self.fnum)))

    def searchButtonClicked(self):
        # Change status
        self.setWindowTitle("MetaCraft (Now Searching...)")
        
        # Clear the result
        self.result.clear()
        pol = self.pol_dependency.currentText()
        wl_domain = self.wlDomain.currentText()
        wl = int(self.wlValue.currentText())
        na = float(self.naEntry.text())
        min_T = float(self.tEntry.text())
        max_H = int(self.hEntry.text())
        max_AR = float(self.arEntry.text())
        nm = 1e-9
        num_gap = 90
        
        num_checked_mat = 0
        list_checked_materials = []
        for i in range(self.mat_layout.count()):
            if self.mat_layout.itemAt(i).widget().isChecked():
                num_checked_mat += 1
                list_checked_materials.append(self.mat_layout.itemAt(i).widget().text())
        if wl_domain == "Ultra Violet":
            str_wl_domain = "UV"
        elif wl_domain == "Visible":
            str_wl_domain = "Vis"
        elif wl_domain == "Near Infrared":
            str_wl_domain = "NIR"
        
        selected_rst_dict = {}
        list_for_print = []
        if pol == "Dependent":
            for mat in list_checked_materials:
                # Rect: H-P-L-W-T-phase
                print(os.path.abspath(os.getcwd()))
                rst = np.load(f'../../Materials/{str_wl_domain}_{mat.replace(" ","")}_{wl}_rectangle.npy')
                cond1 = rst[:, 0] <= max_H * nm
                cond2 = rst[:, 1] <= (wl * nm)  / (2 * na)
                cond3 = np.all(rst[:, 0].reshape(-1, 1) / rst[:, [2, 3]] <= max_AR, axis=1)
                cond4 = rst[:, 4] >= min_T / 100
                rst = rst[cond1 & cond2 & cond3 & cond4]
                list_for_print = [f'{mat},  H: {int(round(arr[0]/nm, -1))} nm,  P: {int(round(arr[1]/nm, -1))} nm,  X: {int(round(arr[2]/nm, -1))} nm,  Y: {int(round(arr[3]/nm, -1))} nm,  T: {100*arr[4]: .1f} %,  φ: {arr[5]: .2f} rad' for arr in rst]
                self.result.addItems(list_for_print)
                numel = len(list_for_print)
                key = f'{mat}-{numel}'
                selected_rst_dict[key] = rst
                
        elif pol == "Independent":
            co_cross = self.polValue.currentText()
            if co_cross == 'Co-pol':
                for mat in list_checked_materials:
                    rst_total = np.zeros((0, 6))
                    for shape in ['circle', 'square']:  
                        # rst: H-P-R(X)-T-phase-shape(1 for circle 2for square)
                        rst = np.load(f'../../Materials/{str_wl_domain}_{mat.replace(" ","")}_{wl}_{shape}.npy')
                        rst_shape = np.ones_like(rst[:, 2]) if shape == 'circle' else 2 * np.ones_like(rst[:, 2])
                        rst = np.concatenate((rst, rst_shape.reshape(-1, 1)), axis=1)
                        rst_total = np.concatenate((rst_total, rst), axis=0)
                    cond1 = rst_total[:, 0] <= max_H * nm
                    cond2 = rst_total[:, 1] <= (wl * nm)  / (2 * na)
                    cond3 = (rst_total[:, 0] / rst_total[:, 2] <= max_AR)
                    cond4 = rst_total[:, 3] >= min_T / 100
                    rst = np.array(rst_total[cond1 & cond2 & cond3 & cond4])
                    hp_unique = np.unique(rst[:, [0, 1]], axis=0)
                    for hp in hp_unique:
                        rst_temp = rst[np.all(rst[:, [0, 1]] == hp, axis=1)]
                        rst_temp_phase = np.sort(rst_temp[:, 4])
                        phase_diff = np.abs(rst_temp_phase - np.roll(rst_temp_phase, -1))
                        phase_diff[phase_diff > np.pi] -= 2 * np.pi
                        max_phase_diff = np.max(np.abs(phase_diff))
                        num_section = np.unique(rst_temp_phase // (np.pi/4)).shape[0]
                        lambda x: 'circle' if x ==1 else 'square'
                        if (max_phase_diff < np.pi/4) and (num_section == 8):     # Check 2pi phase coverage
                            def rorl(x):
                                return 'R' if x == 1 else 'L'
                            def circleorsquare(x):
                                return 'circle' if x == 1 else 'square'
                            list_for_print = [f'{mat}-{circleorsquare(arr[-1])},  H: {int(round(arr[0]/nm, -1))} nm,  P: {int(round(arr[1]/nm, -1))} nm,  {rorl(arr[-1])}: {int(round(arr[2]/nm, -1))} nm,  T: {100*arr[3]: .1f} %,  φ: {arr[4]: .2f} rad' for arr in rst_temp]
                            self.result.addItems(list_for_print)
                            self.result.addItem('\n' + '-' * num_gap + '\n')
                            
                            # key: "mat-H-P-numel"
                            # value: H-P-R(X)-T-phase-shape(1 or 2)
                            key = f'{mat}-{int(round(hp[0]/nm, -1))}-{int(round(hp[1]/nm, -1))}-{rst_temp.shape[0]}'
                            selected_rst_dict[key] = rst_temp
                    
            elif co_cross == 'Cross-pol':
                for mat in list_checked_materials:
                    # Rect: H-P-L-W-Tr-Tl-phase
                    rst_ar = np.load(f'../../Materials/{str_wl_domain}_{mat.replace(" ","")}_{wl}_rectangle.npy')
                    cond1 = rst_ar[:, 0] <= max_H * nm
                    cond2 = rst_ar[:, 1] <= (wl * nm)  / (2 * na)
                    cond3 = np.all(rst_ar[:, 0].reshape(-1, 1) / rst_ar[:, [2, 3]] <= max_AR, axis=1)
                    cond4 = rst_ar[:, 4] >= min_T / 100
                    rst_selected = np.array(rst_ar[cond1 & cond2 & cond3 & cond4])
                    hp_unique = np.unique(rst_selected[:, [0, 1]], axis=0)
                    rst_selected_90 = np.copy(rst_selected)
                    rst_selected_90[:, 2] = np.copy(rst_selected[:, 3]); rst_selected_90[:, 3] = np.copy(rst_selected[:, 2])
                    rst_selected_90[:, 5] += math.pi
                    rst_selected_90[:, 5][rst_selected_90[:, 5] > math.pi] -= 2 * math.pi
                    rst_total = np.concatenate((rst_selected, rst_selected_90), axis=0)
                    for hp in hp_unique:
                        rst_temp = rst_total[np.all(rst_total[:, [0, 1]] == hp, axis=1)]
                        rst_temp_phase = np.sort(rst_temp[:, 5])
                        phase_diff = np.abs(rst_temp_phase - np.roll(rst_temp_phase, -1))
                        phase_diff[phase_diff > np.pi] -= 2 * np.pi
                        max_phase_diff = np.max(np.abs(phase_diff))
                        num_section = np.unique(rst_temp_phase // (np.pi/4)).shape[0]
                        if (max_phase_diff < np.pi/4) and (num_section == 8):     # Check 2pi phase coverage
                            # key: "mat-H-P-numel"
                            key = f'{mat}-{int(round(hp[0]/nm, -1))}-{int(round(hp[1]/nm, -1))}-{rst_temp.shape[0]}'
                            selected_rst_dict[key] = rst_temp
                            
                            list_for_print = [f'{mat},  H: {key.split("-")[1]} nm,  P: {key.split("-")[2]} nm,  X: {int(round(arr[2]/nm, -1))} nm,  Y: {int(round(arr[3]/nm, -1))} nm,  T: {100*arr[4]: .1f} %,  φ: {arr[5]: .2f} rad' for arr in rst_temp]
                            # Add list to result
                            self.result.addItems(list_for_print)
                            self.result.addItem('\n' + '-' * num_gap + '\n')
                            
            
        # Display the result
        if list_for_print == []:
            self.result.addItem("No result found")
        elif pol == "Independent":
            self.result.takeItem(self.result.count()-1)
        
        self.setWindowTitle("MetaCraft")
    
        # Update selected dictionary & self.sorted
        self.sorted = False
        self.selected_rst_dict = selected_rst_dict
                                                 
    def sortButtonClicked(self):
        # Change status
        self.setWindowTitle("MetaCraft (Now Calculating...)")
        
        # Clear the result
        self.result.clear()
        pol = self.pol_dependency.currentText()
        D = self.dEntry.text()
        max_H = int(self.hEntry.text())
        max_AR = float(self.arEntry.text())
        nm = 1e-9
        
        sorted_rst_dict = {}
        rst_dict = self.selected_rst_dict
        sort_choice = self.sort_choice.currentText()
        list_for_print = []
        if pol == "Dependent":
            if sort_choice == "Transmittance":
                for mat_numel, rst_ar in rst_dict.items():
                    rst_ar = rst_ar[np.argsort(-rst_ar[:, 4])]
                    sorted_rst_dict[mat_numel] = rst_ar
                    mat = mat_numel.split("-")[0]
                    list_for_print = [f'{mat},  H: {int(round(arr[0]/nm, -1))} nm,  P: {int(round(arr[1]/nm, -1))} nm,  X: {int(round(arr[2]/nm, -1))} nm,  Y: {int(round(arr[3]/nm, -1))} nm,  T: {100*arr[4]: .1f} %,  φ: {arr[5]: .2f} rad' for arr in rst_ar]
                    self.result.addItems(list_for_print)
                self.sorted_rst_dict = sorted_rst_dict
            elif sort_choice == "FoM":
                for mat_numel, rst_ar in rst_dict.items():
                    FOM = rst_ar[:, 4]*0.5 + (1 - rst_ar[:, 0] / max_H) * 0.25 + (1 - rst_ar[:, 0]/ np.min([rst_ar[:, 2], rst_ar[:, 3]]) / max_AR) * 0.25
                    rst_ar = np.concatenate((rst_ar, FOM.reshape(-1, 1)), axis=1)
                    rst_ar = rst_ar[np.argsort(-rst_ar[:, -1])]
                    sorted_rst_dict[mat_numel] = rst_ar
                    mat = mat_numel.split("-")[0]
                    list_for_print = [f'{mat},  H: {int(round(arr[0]/nm, -1))} nm,  P: {int(round(arr[1]/nm, -1))} nm,  X: {int(round(arr[2]/nm, -1))} nm,  Y: {int(round(arr[3]/nm, -1))} nm,  T: {100*arr[4]: .1f} %,  φ: {arr[5]: .2f} rad' for arr in rst_ar]     
                    self.result.addItems(list_for_print)
                self.sorted_rst_dict = sorted_rst_dict
                
        elif pol == "Independent":
            if sort_choice == "Transmittance":
                for key, rst_ar in rst_dict.items():
                    meanAR, meanT = self.get_attributes(rst_ar)
                    # Replace key to "mat-H-P-meanAR-meanT-numel"
                    numel = key.split("-")[-1]
                    new_key = f'{key[:-(len(numel)+1)]}-{float(meanAR) :.1f}-{float(meanT) :.1f}-{numel}'
                    sorted_rst_dict[new_key] = rst_ar
                self.sorted_rst_dict = OrderedDict(sorted(sorted_rst_dict.items(), key=lambda x: float(x[0].split('-')[-2]), reverse=True))
                list_for_print = [f'{key.split("-")[0]},  H: {key.split("-")[1]} nm,  P: {key.split("-")[2]} nm,  mean AR: {key.split("-")[3]},  mean T: {key.split("-")[4]} %' for key in self.sorted_rst_dict.keys()]
                self.result.addItems(list_for_print)
                
            elif sort_choice == "FoM (fast)":
                for key, rst_ar in rst_dict.items():
                    P = int(key.split("-")[2]) * nm; D = float(self.dEntry.text()) * 1e-6; num_x = math.floor(D / P)
                    phase_ideal = self.gen_phase_map(P, D, num=num_x)
                    phase_meta = self.set_metalens(rst_ar, phase_ideal)
                    meanAR, meanT, FOM = self.get_attributes(rst_ar, phase_ideal, phase_meta)
                    # Replace key to "mat-H-P-meanAR-meanT-FOM-numel"
                    numel = key.split("-")[-1]
                    new_key = f'{key[:-(len(numel)+1)]}-{float(meanAR) :.1f}-{float(meanT) :.1f}-{float(FOM) :.4f}-{numel}'
                    sorted_rst_dict[new_key] = rst_ar
                self.sorted_rst_dict = OrderedDict(sorted(sorted_rst_dict.items(), key=lambda x: float(x[0].split('-')[-2]), reverse=True))
                list_for_print = [f'{key.split("-")[0]},  H: {key.split("-")[1]} nm,  P: {key.split("-")[2]} nm,  mean AR: {key.split("-")[3]},  mean T: {key.split("-")[4]} %,  FOM: {key.split("-")[5]}' for key in self.sorted_rst_dict.keys()]
                self.result.addItems(list_for_print)
            
            elif sort_choice == "FoM (exact)":
                p_idx = 4 if self.polValue.currentText() == 'Co-pol' else 5
                for key, rst_ar in rst_dict.keys():
                    P = int(key.split("-")[2]) * 1e-9; D = float(self.dEntry.text()) * 1e-6; nx = math.floor(D / P)
                    phase_ideal = self.gen_phase_map(P, D, num=nx)
                    phase_meta = self.set_metalens(rst_ar, phase_ideal)
                    meanAR, meanT, FOM = self.get_attributes(rst_ar, phase_ideal, phase_meta)
                    half_nx = round(nx / 2)
                    for i in range(half_nx):
                        for j in range(i, half_nx):
                            if ((i-(nx-1)/2)**2 + (j-(nx-1)/2)**2 <= (nx/2)**2):    # Within the circle, and one half of the quadrant
                                phase_within_range = [p for p in rst_ar[:, p_idx] if np.abs(phase_ideal[i,j]-p) < np.pi/4]
                                for phase_k in phase_within_range:     # Replace phase
                                    temp_phase_meta = np.copy(phase_meta)
                                    idx1 = np.array([i,      i, j,      j, nx-1-i, nx-1-i, nx-1-j, nx-1-j])
                                    idx2 = np.array([j, nx-1-j, i, nx-1-i,      j, nx-1-j,      i, nx-1-i])
                                    temp_phase_meta[idx1, idx2] = phase_k
                                    temp_meanAR, temp_meanT, temp_FOM = self.get_attributes(rst_ar, phase_ideal, temp_phase_meta)
                                    if temp_FOM > FOM:
                                        meanT = temp_meanT
                                        meanAR = temp_meanAR
                                        FOM = temp_FOM
                                        phase_meta = temp_phase_meta
                    
                    # Replace key to "mat-H-P-meanAR-meanT-FOM-numel"
                    numel = key.split("-")[-1]
                    new_key = f'{key[:-(len(numel)+1)]}-{float(meanAR) :.1f}-{float(meanT) :.1f}-{float(FOM) :.4f}-{numel}'
                    sorted_rst_dict[new_key] = rst_ar
                self.sorted_rst_dict = OrderedDict(sorted(sorted_rst_dict.items(), key=lambda x: float(x[0].split('-')[5]), reverse=True))
                list_for_print = [f'{key.split("-")[0]},  H: {key.split("-")[1]} nm,  P: {key.split("-")[2]} nm,  mean AR: {key.split("-")[3]},  mean T: {key.split("-")[4]} %,  FOM: {key.split("-")[5]}' for key in sorted_rst_dict.keys()]
                self.result.addItems(list_for_print)
            
        # Display the result
        if list_for_print == []:
            self.result.addItem("No result found")
        self.setWindowTitle("MetaCraft")
        # Update self.sorted
        self.sorted = True
        
    def gen_phase_map(self, p, d, **kwargs):
        wl = int(self.wlValue.currentText()) * 1e-9; f= float(self.fEntry.text()) * 1e-6
        if 'num' in kwargs.keys(): # 2D phase map
            num_x = kwargs['num']
            r = p * np.linspace(-(num_x-1)/2, (num_x-1)/2, num_x)        
            xv, yv = np.meshgrid(r, r)
            required_phase = -2*math.pi / wl * (np.sqrt(f**2 + xv**2 + yv**2) - f)
            required_phase[xv**2 + yv**2 > (d/2)**2] = np.nan

        elif 'gap' in kwargs.keys(): # 1D phase map
            r = np.arange(-d/2, d/2+kwargs['gap'], kwargs['gap'])
            required_phase = -2*math.pi / wl * (np.sqrt(f**2 + r**2) - f)
        required_phase = required_phase % (2*math.pi)
        required_phase[required_phase > math.pi] -= 2 * math.pi

        return required_phase
        
        
    def set_metalens(self, rst_ar, phase_ideal, **kwargs):
        if self.pol_dependency.currentText() == "Dependent":
            level = int(self.rotation_level.text())
            phase_pb = np.round(phase_ideal / (2*math.pi/level)) * (2*math.pi/level)
            return phase_pb
        elif self.pol_dependency.currentText() == "Independent":
            phase_ideal_flat = np.expand_dims(phase_ideal.flatten(), 1)    # 2D: [N^2, 1]/ 1D: [N, 1]
            p_idx = 4 if self.polValue.currentText() == 'Co-pol' else 5
            phase_meta = np.expand_dims(rst_ar[:, p_idx], 0)      # [1, M]               
            phase_diff = phase_ideal_flat - phase_meta           # 2D:[N^2, M] / 1D: [N, M]
            phase_diff[phase_diff > math.pi] -= 2 * math.pi
            phase_diff[phase_diff < - math.pi] += 2 * math.pi
            arg_phase_real = np.argmin(np.abs(phase_diff), axis=1) # 2D: [N^2] / 1D: [N]
            phase_meta = np.transpose(phase_meta) # [M, 1]
            phase_real = phase_meta[arg_phase_real] # 2D: [N^2] / 1D: [N]
            if phase_ideal.ndim == 2:
                nan_i, nan_j = np.where(np.isnan(phase_ideal))
                phase_real = phase_real.reshape(phase_ideal.shape)  # [N, N]  
                phase_real[nan_i, nan_j] = np.nan                
                if 'get_idx' in kwargs.keys():
                    arg_phase_real += 1
                    arg_phase_real = arg_phase_real.reshape(phase_ideal.shape)  # [N, N]  
                    arg_phase_real[nan_i, nan_j] = 0 
                    return phase_real, arg_phase_real
        return phase_real           
    
    
    # For pol-independent
    # def get_attributes(self, rst, phase_ideal, phase_meta):
    def get_attributes(self, *args):
        if len(args) == 1:
            rst_ar = args[0]
        elif len(args) == 3:
            rst_ar = args[0]
            phase_ideal = args[1]
            phase_meta = args[2]
        
        if self.polValue.currentText() == 'Co-pol':
            mean_AR = np.mean(rst_ar[:, 0] / rst_ar[:, 2])
            mean_T = np.mean(rst_ar[:, 3])
            if self.sort_choice.currentText() == "Transmittance":
                return mean_AR, 100 * mean_T
        elif self.polValue.currentText() == 'Cross-pol':
            mean_AR = np.mean(rst_ar[:, 0] / np.min(rst_ar[:, [2,3]], axis=1))
            mean_T = np.mean(rst_ar[:, 4])
            if self.sort_choice.currentText() == "Transmittance":
                return mean_AR, 100 * mean_T
        max_AR = float(self.arEntry.text())
        H = rst_ar[0, 0] * 1e-9
        max_H = int(self.hEntry.text())
        
        nonnan_phase_meta = phase_meta[~np.isnan(phase_meta)]
        nonnan_phase_ideal = phase_ideal[~np.isnan(phase_ideal)]
        R2 = r2_score(nonnan_phase_meta, nonnan_phase_ideal)
        FOM = R2/3 + mean_T/3 + (1 - mean_AR/max_AR)/6 + (1 - H/max_H)/6
        
        return mean_AR, 100 * mean_T, FOM
    
    def setAdditionalLayout(self):
        if self.pol_dependency.currentText() == "Dependent":
            # Set Result layout: Rotation Level
            for i in reversed(range(self.Result_additional_layout_2.count())):
                self.Result_additional_layout_2.itemAt(i).widget().deleteLater()
            self.Result_additional_layout_2.addWidget(QLabel("Rotation Level"))
            self.rotation_level = QLineEdit("8")
            self.Result_additional_layout_2.addWidget(self.rotation_level)
        elif self.pol_dependency.currentText() == "Independent":
            for i in reversed(range(self.Result_additional_layout_2.count())):
                self.Result_additional_layout_2.itemAt(i).widget().deleteLater()
            self.showDetailsButton = QPushButton("Show Lens Details")
            self.showDetailsButton.clicked.connect(self.showDetails)
            self.Result_additional_layout_2.addWidget(self.showDetailsButton)
    
    
    def showDetails(self): # Only activated when pol-independent
        D = float(self.dEntry.text()) * 1e-6
        rst_ar, _, P = self.Independent_resultselection('display.')
        num = math.floor(D / P)
        phase_ideal = self.gen_phase_map(P, D, num=num)
        _, metaatom_idx = self.set_metalens(rst_ar, phase_ideal, get_idx=True)
        metaatom_list = rst_ar[:, 2:6]
        co_cross = self.polValue.currentText()
        self.w = DetailWindow(metaatom_idx, metaatom_list, co_cross)
        self.w.show()
        
        
    def plotFigure(self):
        gap = 10e-9 
        D = float(self.dEntry.text()) * 1e-6
        if self.pol_dependency.currentText() == "Dependent":
            rst_ar, _, P = self.Dependent_resultselection('to plot.')
        elif self.pol_dependency.currentText() == "Independent":
            rst_ar, _, P = self.Independent_resultselection('to plot.')
        phase_ideal_1d = self.gen_phase_map(P, D, gap=gap)
        phase_meta = self.set_metalens(rst_ar, phase_ideal_1d)
        plt.figure()
        r = np.arange(-D/2, D/2+gap, gap)
        plt.plot(r*1e6, phase_ideal_1d, 'k:'); plt.plot(r*1e6, phase_meta, 'ro', markersize=5)
        plt.xlabel("Radial Coordinate (μm)"); plt.ylabel("Phase (rad)")
        plt.show()
    
    
    def export_FDTD(self):
        fname = "../../Export/" + self.export_file_name.text() + ".lsf"
        f = open(fname, 'w')
        D = float(self.dEntry.text()) * 1e-6; fl = float(self.fEntry.text()) * 1e-6; lam = int(self.wlValue.currentText()) * 1e-9
        if self.pol_dependency.currentText() == "Dependent":
            rst_ar, key, P = self.Dependent_resultselection('to export.')
            mat = key.split("-")[0]
            mat = ''.join(mat.split(" "))
            cpval = self.polValue.currentText()
            h = rst_ar[0]
            l = rst_ar[2]
            w = rst_ar[3]
            num = math.floor(D / P)
            xlin = P * np.linspace(-(num-1)/2, (num-1)/2, num)
            ylin = np.copy(xlin)
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta = self.set_metalens(rst_ar, phase_ideal, get_index=True)
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    else:
                        x = xlin[i]; y = ylin[j]
                        f.write(f'addrect;')                
                        f.write(f'set("render type","wireframe");'); f.write(f'set("detail",0);')
                        f.write(f'set("x", {x :.2e});'); f.write(f'set("x span", {l :.3e});')
                        f.write(f'set("y", {y :.2e});'); f.write(f'set("y span", {w :.3e});')
                        f.write(f'set("z min", {-h});'); f.write(f'set("z max", 0);')
                        f.write(f'set("material","{mat}");')
                        f.write(f'set("first axis","z");')
                        if cpval == 'RCP':
                            f.write(f'set("rotation 1", {-phase_meta[i, j] / 2});\n')
                        elif cpval == 'LCP':
                            f.write(f'set("rotation 1", {phase_meta[i, j] / 2});\n')
                                            
        elif self.pol_dependency.currentText() == "Independent":
            rst_ar, key, P = self.Independent_resultselection('to export.')
            co_cross = self.polValue.currentText()
            mat = key.split("-")[0]
            mat = ''.join(mat.split(" "))
            h = int(key.split("-")[1]) * 1e-9
            num = math.floor(D / P)
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta, metaatom_idx_2d = self.set_metalens(rst_ar, phase_ideal, get_idx=True)
            # Set starting index to 0
            metaatom_idx_2d -= 1
            xlin = P * np.linspace(-(num-1)/2, (num-1)/2, num)
            ylin = np.copy(xlin)
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    else:
                        x = xlin[i]; y = ylin[j]
                        if co_cross == 'Co-pol':
                            shape = rst_ar[metaatom_idx_2d[i, j], 5]
                            l = rst_ar[metaatom_idx_2d[i, j], 2]
                            if shape == 1:
                                f.write(f'addcircle;')
                                f.write(f'set("render type","wireframe");'); f.write(f'set("detail",0);')
                                f.write(f'set("x", {x :.2e});'); f.write(f'set("y", {y :.2e});')
                                f.write(f'set("radius", {l/2 :.3e});')
                            elif shape == 2:
                                f.write(f'addrect;')                
                                f.write(f'set("render type","wireframe");'); f.write(f'set("detail",0);')
                                f.write(f'set("x",{x :.2e});'); f.write(f'set("x span", {l :.3e});')
                                f.write(f'set("y",{y :.2e});'); f.write(f'set("y span", {l :.3e});')
                            f.write(f'set("z min", {-h});'); f.write(f'set("z max", 0);')
                            f.write(f'set("material","{mat}");')

                        elif co_cross == 'Cross-pol':
                            l = rst_ar[metaatom_idx_2d[i, j], 2]
                            w = rst_ar[metaatom_idx_2d[i, j], 3]
                            f.write(f'addrect;')                
                            f.write(f'set("render type","wireframe");'); f.write(f'set("detail",0);')
                            f.write(f'set("x",{x :.2e});'); f.write(f'set("x span", {l :.3e});')
                            f.write(f'set("y",{y :.2e});'); f.write(f'set("y span", {w :.3e});')
                            f.write(f'set("z min", {-h});'); f.write(f'set("z max", 0);')
                            f.write(f'set("material","{mat}");')
                            f.write(f'set("first axis","z");')
        
        f.write(f'\nselect("FDTD");\n')
        f.write(f'set("x span", {D :.4e});\n'); f.write(f'set("y span", {D :.4e});\n')
        f.write(f'set("z max", {fl + 1.5 * lam :.2e});\n')
        f.write(f'set("z min", {-h - 5 * lam :.2e});\n\n')

        f.write(f'select("substrate");\n')
        f.write(f'set("x span", {2*D :.4e});\n'); f.write(f'set("y span", {2*D :.4e});\n')
        f.write(f'set("z max", {-h :.2e});\n'); f.write(f'set("z min", {-h - 3 *lam :.2e});\n\n')

        f.write(f'select("source_x");\n')
        f.write(f'set("enabled",1);\n')
        f.write(f'set("x span",{D*2 :.4e});\n'); f.write(f'set("y span", {2*D :.4e});\n')
        f.write(f'set("z", {-h-lam :.2e});\n')
        f.write(f'set("center wavelength", {lam});\n')
        f.write(f'setglobalsource("center wavelength", {lam*1e9});\n\n')

        f.write(f'select("source_y");\n')
        f.write(f'set("enabled",0);\n')
        f.write(f'set("x span", {D*2 :.4e});\n'); f.write(f'set("y span", {D*2 :.4e});\n')
        f.write(f'set("z", {-h-lam :.2e});\n')
        f.write(f'set("center wavelength", {lam});\n')
        f.write(f'setglobalsource("center wavelength", {lam});\n\n')

        f.write(f'select("monitor_xy");\n')
        f.write(f'set("x span", {D :.4e});\n'); f.write(f'set("y span", {D :.4e});\n')
        f.write(f'set("z",{fl});\n\n')

        f.write(f'select("monitor_xz");\n')
        f.write(f'set("x span",{D :.4e});\n')
        f.write(f'set("z max", {fl + 1.5* lam});\n')
        f.write(f'set("z min", {-h-lam*5});\n\n')

        f.write(f'save("{fname}");\n')
        f.write(f'save("{fname + "_x"}");\n\n')

        f.write(f'select("source_x");\n')
        f.write(f'set("enabled",0);\n')
        f.write(f'select("source_y");\n')
        f.write(f'set("enabled",1);\n')
        f.write(f'save("{fname + "_y"}");\n\n')
        f.write(f'addjob("{fname+"_x"}");\n'); f.write(f'addjob("{fname+"_y"}");\n')
        f.write(f'runjobs;\n')
        f.close()
        
    
    def export_VirtualLab(self):
        D = float(self.dEntry.text()) * 1e-6

        if self.pol_dependency.currentText() == "Dependent":
            rst_ar, key, P = self.Dependent_resultselection('to export.')
            num = math.floor(D / P)
            export_phase = np.zeros([num, num])
            export_T = np.zeros([num, num])
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta = self.set_metalens(rst_ar, phase_ideal, get_idx=True)
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    export_phase[i, j] = phase_meta[i,j] + rst_ar[5]
                    export_T[i, j] = rst_ar[4]
                    
        elif self.pol_dependency.currentText() == "Independent":
            rst_ar, key, P = self.Independent_resultselection('to export.')
            num = math.floor(D / P)
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta, metaatom_idx_2d = self.set_metalens(rst_ar, phase_ideal, get_idx=True)
            # Set starting index to 0
            metaatom_idx_2d -= 1
            co_cross = self.polValue.currentText()
            idx_T = 3 if co_cross == 'Co-pol' else 4
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    else:
                        export_phase[i, j] = phase_meta[i,j]
                        export_T[i, j] = rst_ar[metaatom_idx_2d[i, j], idx_T]
        
        f_phase = "../../Export/" + self.export_file_name.text() + "_phase.txt"
        np.savetxt(f_phase, export_phase, fmt='%.4f', delimiter='\t')
        f_T = "../../Export/" + self.export_file_name.text() + "_abs^2.txt"
        np.savetxt(f_T, export_T, fmt='%.4f', delimiter='\t')
    
    def export_GDS(self):
        fname = "../../Export/" + self.export_file_name.text() + ".txt"
        D = float(self.dEntry.text()) * 1e-6; f = float(self.fEntry.text()) * 1e-6; lam = int(self.wlValue.currentText()) * 1e-9
        f = open(fname, 'w')
        f.write(f'HEADER 3;\n')
        f.write(f'BGNLIB;\n')
        f.write(f'LIBNAME {fname};\n')
        f.write(f'UNITS 1.000000e+000 1.000000e-009;\n')
        f.write(f'BGNSTR;\n')
        f.write(f'STRNAME {fname[:-4]};\n')
        if self.pol_dependency.currentText() == "Dependent":
            rst_ar, key, P = self.Dependent_resultselection('to export.')
            cpval = self.polValue.currentText()
            l = (rst_ar[2]) * 1e9
            w = (rst_ar[3]) * 1e9
            num = math.floor(D / P)
            xlin = 1e9 * P * np.linspace(-(num-1)/2, (num-1)/2, num)
            ylin = np.copy(xlin)
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta = self.set_metalens(rst_ar, phase_ideal, get_index=True)
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    else:
                        x = xlin[i]; y = ylin[j]
                    if cpval == 'RCP':
                        alpha = -phase_meta[i, j]/2
                    elif cpval == 'LCP':
                        alpha = phase_meta[i, j]/2
                    
                    xh = l/2; yh = w/2
                    x1 = -xh; y1 = yh
                    x2 = -xh; y2 = -yh
                    x3 = xh; y3 = -yh
                    x4 = xh; y4 = yh

                    f.write(f'BOUNDARY\n')
                    f.write(f'LAYER 46;\n')
                    f.write(f'DATATYPE 46;\n')
                    f.write(f'XY\n')                    
                    if self.Cbox_reverse_pattern.isChecked():
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(y + P/2*1e9)}\n')
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(x1*math.sin(alpha) + y1*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x2*math.cos(alpha) - y2*math.sin(alpha) + x)}\t:\t{round(x2*math.sin(alpha) + y2*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x3*math.cos(alpha) - y3*math.sin(alpha) + x)}\t:\t{round(x3*math.sin(alpha) + y3*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x4*math.cos(alpha) - y4*math.sin(alpha) + x)}\t:\t{round(x4*math.sin(alpha) + y4*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(x1*math.sin(alpha) + y1*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(y + P/2*1e9)}\n')
                        f.write(f'{round(x + P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                        f.write(f'{round(x + P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                        f.write(f'{round(x - P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                        f.write(f'{round(x - P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(y + P/2*1e9)}\n')
                    else:
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(x1*math.sin(alpha) + y1*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x2*math.cos(alpha) - y2*math.sin(alpha) + x)}\t:\t{round(x2*math.sin(alpha) + y2*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x3*math.cos(alpha) - y3*math.sin(alpha) + x)}\t:\t{round(x3*math.sin(alpha) + y3*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x4*math.cos(alpha) - y4*math.sin(alpha) + x)}\t:\t{round(x4*math.sin(alpha) + y4*math.cos(alpha) + y)}\n')
                        f.write(f'{round(x1*math.cos(alpha) - y1*math.sin(alpha) + x)}\t:\t{round(x1*math.sin(alpha) + y1*math.cos(alpha) + y)}\n')
                    f.write(f'ENDEL\n')
                    
        elif self.pol_dependency.currentText() == "Independent":
            rst_ar, key, P = self.Independent_resultselection('to export.')
            co_cross = self.polValue.currentText()
            num = math.floor(D / P)
            phase_ideal = self.gen_phase_map(P, D, num=num)
            phase_meta, metaatom_idx_2d = self.set_metalens(rst_ar, phase_ideal, get_idx=True)
            # Set starting index to 0       
            metaatom_idx_2d -= 1
            xlin = 1e9 * P * np.linspace(-(num-1)/2, (num-1)/2, num)
            ylin = np.copy(xlin)
            for i in range(num):
                for j in range(num):
                    if np.isnan(phase_meta[i,j]):
                        continue
                    else:
                        x = xlin[i]; y = ylin[j]
                        if co_cross == 'Co-pol':
                            shape = rst_ar[metaatom_idx_2d[i, j], 5]
                            theta = 2*math.pi/16
                            f.write(f'BOUNDARY\n')
                            f.write(f'LAYER 46;\n')
                            f.write(f'DATATYPE 46;\n')
                            f.write(f'XY\n')
                            if shape == 1:
                                atom_D = rst_ar[metaatom_idx_2d[i, j], 2] * 1e9
                                l = atom_D*math.tan(theta/2)
                                f.write(f'{round(x)}\t:\t{round(y+atom_D/2)}\n')
                                f.write(f'{round(x-l/2)}\t:\t{round(y+atom_D/2)}\n')
                                x_temp = round(x-l/2); y_temp = round(y+atom_D/2)
                                for k in range(1, 14+1):
                                    f.write(f'{round(x_temp-l*math.cos(theta*k))}\t:\t{round(y_temp-l*math.sin(theta*k))}\n')
                                    x_temp = x_temp-l*math.cos(theta*k); y_temp = y_temp-l*math.sin(theta*k)
                                f.write(f'{round(x+l/2)}\t:\t{round(y+atom_D/2)}\n')
                                f.write(f'{round(x)}\t:\t{round(y+atom_D/2)}\n')
                                if self.Cbox_reverse_pattern.isChecked():
                                    f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x + P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x + P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                    f.write(f'{round(x - P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                    f.write(f'{round(x - P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x)}\t:\t{round(y+atom_D/2)}\n')
                                f.write(f'ENDEL\n')
                                
                            elif shape == 2:
                                atom_L = rst_ar[metaatom_idx_2d[i, j], 2] * 1e9
                                f.write(f'{round(x)}\t:\t{round(y + atom_L/2)}\n')
                                f.write(f'{round(x - atom_L/2)}\t:\t{round(y + atom_L/2)}\n')
                                f.write(f'{round(x - atom_L/2)}\t:\t{round(y - atom_L/2)}\n')
                                f.write(f'{round(x + atom_L/2)}\t:\t{round(y - atom_L/2)}\n')
                                f.write(f'{round(x + atom_L/2)}\t:\t{round(y + atom_L/2)}\n')
                                f.write(f'{round(x)}\t:\t{round(y + atom_L/2)}\n')
                                if self.Cbox_reverse_pattern.isChecked():
                                    f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x + P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x + P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                    f.write(f'{round(x - P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                    f.write(f'{round(x - P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                    f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x)}\t:\t{round(y + atom_L/2)}\n')
                                f.write(f'ENDEL\n')
                        
                        elif co_cross == 'Cross-pol':
                            l = (rst_ar[metaatom_idx_2d[i, j], 2]) * 1e9
                            w = (rst_ar[metaatom_idx_2d[i, j], 3]) * 1e9  
                            xh = l/2; yh = w/2
                            
                            x1 = -xh; y1 = yh
                            x2 = -xh; y2 = -yh
                            x3 = xh; y3 = -yh
                            x4 = xh; y4 = yh 
                            
                            f.write(f'BOUNDARY\n')
                            f.write(f'LAYER 46;\n')
                            f.write(f'DATATYPE 46;\n')
                            f.write(f'XY\n')
                            f.write(f'{round(x + x1)}\t:\t{round(y + y1)}\n')
                            f.write(f'{round(x + x2)}\t:\t{round(y + y2)}\n')
                            f.write(f'{round(x + x3)}\t:\t{round(y + y3)}\n')
                            f.write(f'{round(x + x4)}\t:\t{round(y + y4)}\n')
                            if self.Cbox_reverse_pattern.isChecked():
                                f.write(f'{round(x)}\t:\t{round(y + yh)}\n')
                                f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x + P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x + P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                f.write(f'{round(x - P/2*1e9)}\t:\t{round(y - P/2*1e9)}\n')
                                f.write(f'{round(x - P/2*1e9)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x)}\t:\t{round(y + P/2*1e9)}\n')
                                f.write(f'{round(x)}\t:\t{round(y + yh)}\n')
                            f.write(f'{round(x + x1)}\t:\t{round(y + y1)}\n')
                            f.write(f'ENDEL\n')
                        
        f.write(f'ENDSTR\n')
        f.write(f'ENDLIB\n')
        f.close()
    
        
    def Dependent_resultselection(self, warningstr):
        rst_dict = self.selected_rst_dict if self.sorted == False else self.sorted_rst_dict
        num_row = self.result.currentRow()
        if num_row == -1:
            raise ValueError("Please select the result " + warningstr)
        list_key = list(rst_dict)
        list_int = [int(key.split("-")[-1]) for key in list_key]
        for i in range(len(list_int)):
            if sum(list_int[:i]) <= (num_row+1) < sum(list_int[:i+1]):
                key = list_key[i]
                break
        rst_ar = rst_dict[key][num_row]
        P = float(rst_ar[1])
        
        return rst_ar, key, P
        
        
    def Independent_resultselection(self, warningstr):
        rst_dict = self.selected_rst_dict if self.sorted == False else self.sorted_rst_dict
        qidxes = self.result.selectedIndexes()
        if qidxes == []:    # No selection
            raise ValueError("Please select the result to " + warningstr) 
        list_key = list(rst_dict)
        list_int = [int(key.split("-")[-1]) for key in list_key]
        
        idxes = [qidx.row() for qidx in qidxes]
        if self.sorted == False:
            idxes.sort()
            list_accum = [-1]
            for i in range(len(list_int)):
                list_accum.append(sum(list_int[:(i+1)]) + i)
            for i in range(len(list_accum)):
                if (list_accum[i] < idxes[0]) and (idxes[-1] < list_accum[i+1]):
                    key = list_key[i]
                    idxes = [idx - (list_accum[i] + 1) for idx in idxes]
                    break
            if key == None:
                raise ValueError("You have selected the line separator. Please select the result " + warningstr)
            rst_ar = rst_dict[key][idxes]
        else:
            key = list_key[idxes[0]]
            rst_ar = rst_dict[key]
            
        P = int(key.split("-")[2]) * 1e-9
        
        return rst_ar, key, P