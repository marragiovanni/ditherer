import os
from utils import DEFAULT_W, DEFAULT_H, CONTROLPANEL_W
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QToolBar, QMessageBox, QFileDialog, QComboBox, QLabel, QSlider, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import * 
from dithering import * 

class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__()  

        # WINDOW TITLE AND SIZE
        self.setWindowTitle("DITHERER")
        self.setWindowIcon(QIcon("ICON.png"))
        self.setGeometry(100, 100, DEFAULT_W, DEFAULT_H)

        self.f = QFont("Arial", 16)

        self.setFont(self.f)

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # IMAGE and INPUTS
        self.label = QLabel() 
        self.img = None 
        self.imagePath = ""
        self.originalImage = QImage(self.imagePath) # original 
        self.displayImage = QPixmap(self.imagePath) # visualized
        
        # LAYOUT 
        mainLayout = QHBoxLayout()

        # Display image to Layout
        mainLayout.addWidget(self.label, stretch=3)  
        self.label.setScaledContents(False) 
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        # TOOLBAR
        toolbar = QToolBar("Main toolbar")
        toolbar.setFixedHeight(36)
        self.addToolBar(toolbar)
        # - Open
        openAction = QAction("Open", self)
        openAction.setStatusTip("Open an image")
        openAction.triggered.connect(self.open_image)
        toolbar.addAction(openAction)

        # - Save
        saveAction = QAction("Save", self)
        saveAction.setStatusTip("Save image on disk")
        saveAction.triggered.connect(self.save_image)
        toolbar.addAction(saveAction)

        # - Undo
        undoAction = QAction("Undo", self)
        undoAction.setStatusTip("Undo last action")
        undoAction.triggered.connect(self.undo)
        toolbar.addAction(undoAction)

        # - Redo
        redoAction = QAction("Redo", self)
        redoAction.setStatusTip("Redo last action")
        redoAction.triggered.connect(self.redo)
        toolbar.addAction(redoAction)

        # - About me
        aboutAction = QAction("About", self)
        aboutAction.setStatusTip("About me")
        aboutAction.triggered.connect(self.about_me)
        toolbar.addAction(aboutAction)


        # PANEL 
        sidePanel = QWidget()  # widget
        sidePanel.setFixedWidth(CONTROLPANEL_W)
        sideLayout = QVBoxLayout(sidePanel) 

        # QCOMBOBOX
        self.type_of_dithering = QComboBox()
        self.type_of_dithering.addItem('Floyd-steinberg')
        self.type_of_dithering.addItem('Random')
        self.type_of_dithering.addItem('Bayer')
        self.type_of_dithering.currentTextChanged.connect(self.update_ui)
        sideLayout.addWidget(self.type_of_dithering)

        # APPLY AND DEFAULT BUTTONS
        buttonsLayout = QHBoxLayout()
        self.apply = QPushButton("Apply")
        self.apply.clicked.connect(self.apply_action)

        self.default = QPushButton("Default")
        self.default.clicked.connect(self.default_action)
        buttonsLayout.addWidget(self.apply)
        buttonsLayout.addWidget(self.default)
        sideLayout.addLayout(buttonsLayout)

        self.dither_intensity = 0.0
        self.threshold_value = 0 
        self.matrix_idx = '2x2'

        # SLIDERS
        self.dithering_intensity = self.create_slider_group("Dithering Intensity", 0, 10, 1)
        sideLayout.addWidget(self.dithering_intensity)
        
        self.quantization_threshold = self.create_slider_group("Threshold", 0, 255, 2)
        sideLayout.addWidget(self.quantization_threshold)

        self.grid_dimension = self.create_slider_group("Grid Dimension", 1, 3, 3)
        sideLayout.addWidget(self.grid_dimension)

        sideLayout.addStretch()

        mainLayout.addWidget(sidePanel, stretch=1)

        # Container
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)
        self.update_ui()



    def open_image(self): 
        fd = QFileDialog.getOpenFileName(self, "Open File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)",)
        if fd[0] != "": 
            self.imagePath = fd[0]
        else:
            return 
        
        self.img = load_img_as_rgb(self.imagePath) # RGB format'

        self.originalImage = QImage(self.imagePath)
        self.displayImage = QPixmap.fromImage(self.originalImage)
 
        self.displayImage = self.displayImage.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  

        self.label.setPixmap(self.displayImage) 

        # Clear undo/redo stacks when opening new image
        self.undo_stack.clear()
        self.redo_stack.clear()

        if not self.displayImage.isNull(): 
            self.setWindowTitle(f"DITHERER - IMAGE LOADED ~ {self.imagePath}") # modifico il titolo della finestra aggiungendo l'url 
        else: 
            self.setWindowTitle(f"DITHERER - URL ERROR - NO IMAGE LOADED")

    def save_image(self): 
        if self.imagePath == "": 
            QMessageBox.warning(self, "Error", "No image to save!")
            return
        self.img = self.img.convert('RGB')
        self.originalImage = self.originalImage.convertToFormat(QImage.Format.Format_RGB888)
        fd = QFileDialog.getSaveFileName(self, "Save File", "", "Image (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*)",)
        if fd[0]: 
            if "." not in os.path.basename(fd[0]): 
                fd[0] += ".png"
            self.originalImage.save(fd[0])

    def about_me(self): 
        about_text = """
        <h1>Ditherer</h1>
        <p>An application to apply dithering algorithms to your images.</p>
        <p>Visit <a href='https://github.com/marragiovanni'> my Github Page </a> to see other things I do.</p>
        """
        QMessageBox.about(self, "About Ditherer", about_text)

    def undo(self):
        if self.undo_stack:
            # Save current state to redo stack
            current_state = {
                'image': self.img.copy(),
                'display': self.displayImage.copy(),
                'original': self.originalImage.copy()
            }
            self.redo_stack.append(current_state)

            # Restore previous state
            previous_state = self.undo_stack.pop()
            self.img = previous_state['image']
            self.displayImage = previous_state['display']
            self.originalImage = previous_state['original']
            self.label.setPixmap(self.displayImage)

    def redo(self):
        if self.redo_stack:
            # Save current state to undo stack
            current_state = {
                'image': self.img.copy(),
                'display': self.displayImage.copy(),
                'original': self.originalImage.copy()
            }
            self.undo_stack.append(current_state)

            # Restore next state
            next_state = self.redo_stack.pop()
            self.img = next_state['image']
            self.displayImage = next_state['display']
            self.originalImage = next_state['original']
            self.label.setPixmap(self.displayImage)


    def apply_action(self):
        if not self.displayImage.isNull():
            # Save current state before applying changes
            current_state = {
                'image': self.img.copy(),
                'display': self.displayImage.copy(),
                'original': self.originalImage.copy()
            }
            self.undo_stack.append(current_state)
            self.redo_stack.clear()  # Clear redo stack when new action is performed

            self.img = self.img.convert('L')
            if self.type_of_dithering.currentText() == "Floyd-steinberg":
                self.img = floyd_steinberg_dither(self.img, 'L', self.dither_intensity)
            elif self.type_of_dithering.currentText() == "Random": 
                self.img = random_dither(self.img, self.dither_intensity)
            else: 
                self.img = bayer_dither(self.img, self.matrix_idx, self.threshold_value)
            
            data = self.img.tobytes('raw', 'L')

            self.originalImage = QImage(data, self.img.width, self.img.height, QImage.Format.Format_Grayscale8)    
            self.displayImage = QPixmap.fromImage(self.originalImage)
            self.displayImage = self.displayImage.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(self.displayImage)    


    def default_action(self): 
        if not self.displayImage.isNull(): 
            self.img = load_img_as_rgb(self.imagePath) 
            data = self.img.tobytes("raw", "RGB")

            self.originalImage = QImage(data, self.img.width, self.img.height, QImage.Format.Format_RGB888)    

            self.displayImage = QPixmap.fromImage(self.originalImage)
            self.displayImage = self.displayImage.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(self.displayImage)

    def update_matrix_idx(self, value): 
            if value == 1: 
                self.matrix_idx = '2x2'
            elif value == 2: 
                self.matrix_idx = '4x4'
            else: 
                self.matrix_idx = '8x8'

    def update_ui(self):
        if self.type_of_dithering.currentText() == "Floyd-steinberg":
            self.dithering_intensity.show()
            self.quantization_threshold.hide()
            self.grid_dimension.hide()
        elif self.type_of_dithering.currentText() == "Random": 
            self.dithering_intensity.show()
            self.quantization_threshold.hide()
            self.grid_dimension.hide()            
        elif self.type_of_dithering.currentText() == "Bayer":
            self.quantization_threshold.show()
            self.grid_dimension.show()
            self.dithering_intensity.hide()



    def create_slider_group(self, label_text, min_val, max_val, step=None): 
        group = QGroupBox(label_text)
        layout = QVBoxLayout()
        label = QLabel(f"{min_val}")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)

        slider.valueChanged.connect(lambda val: label.setText(f"{val}"))   
        if step == 1: 
            slider.valueChanged.connect(lambda val: setattr(self, 'dither_intensity' , val / 10))
        elif step == 2: 
            slider.valueChanged.connect(lambda val: setattr(self, 'threshold_value' , val))
        elif step == 3: 
            slider.valueChanged.connect(self.update_matrix_idx)

        layout.addWidget(label) 
        layout.addWidget(slider)
        group.setLayout(layout)
        return group
    
    


            