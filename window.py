import os
from utils import DEFAULT_W, DEFAULT_H, CONTROLPANEL_W
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QToolBar, QMessageBox, QFileDialog, QComboBox, QLabel, QSlider, QGroupBox
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import *
from dithering import load_img_as_rgb 
from worker import DitherWorker
from pathlib import Path 

BASE_DIR = Path(__file__).resolve().parent 
ICON_PATH = str(BASE_DIR / "ICON.png") 

class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__()  

        # WINDOW TITLE AND SIZE
        self.setWindowTitle("DITHERER")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(100, 100, DEFAULT_W, DEFAULT_H)

        self.f = QFont("Arial", 16)

        self.setFont(self.f)

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # IMAGE and INPUTS
        self.label = QLabel() 
        self.img = None 
        self.imagePath = None
        self.originalImage = QImage() # original 
        self.displayImage = QPixmap() # visualized
        
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
        self.group_intensity, self.slider_intensity = self.create_slider_group("Diffusion Strength", 0, 10) 
        sideLayout.addWidget(self.group_intensity) 
        
        self.group_threshold, self.slider_threshold = self.create_slider_group("Threshold", 0, 255)
        sideLayout.addWidget(self.group_threshold) 
        
        self.group_grid, self.slider_grid = self.create_slider_group("Grid Dimension", 1, 3) 
        sideLayout.addWidget(self.group_grid) 

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
        if self.img is None: 
            QMessageBox.warning(self, "Error", "No image to save!") 
            return 

        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Images (*.png);;Images (*.jpg)") 

        if path:
            if not Path(path).suffix: 
                path += ".png"
            # save PIL image 
            self.img.convert('RGB').save(path) 

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
            self.redo_stack.append(self.img.copy()) # PIL Image 

            # Restore the previous image 
            self.img = self.undo_stack.pop() 

            # Recreate visualization starting from restored PIL 
            self._sync_gui_with_img()

    def redo(self):
        if self.redo_stack:
            # Save current state to undo stack
            self.undo_stack.append(self.img.copy())            
            
            # Restore next image
            self.img = self.redo_stack.pop() 
            
            # Recreate visualization 
            self._sync_gui_with_img() 
    
    # Sync PILLOW with GUI of Qt
    def _sync_gui_with_img(self): 
        if self.img is None: 
            return 
        
        # The image has to be in a manageable format (Grayscale or RGB).
        # If 'L' (Grayscale) so after dithering, use Format_Grayscale8 
        # If 'RGB'  use Format_RGB888

        width, height = self.img.size
        if self.img.mode == 'L': 
            data = self.img.tobytes('raw', 'L') 
            format = QImage.Format.Format_Grayscale8
            bytes_per_line = width 
        else: 
            # Fallback on RGB 
            temp_rgb = self.img.convert('RGB') 
            data = temp_rgb.tobytes('raw', 'RGB') 
            format = QImage.Format.Format_RGB888
            bytes_per_line = width * 3 
        
        # Create a safe QImage 
        qimg = QImage(data, width, height, bytes_per_line, format)
        self.originalImage = qimg.copy() # make a copy just to be safe 

        self.displayImage = QPixmap.fromImage(self.originalImage) 
        self.update_display()
    
    def resizeEvent(self, event): 
        # Method that get called each time the user resize window 
        super().resizeEvent(event)
        if self.img: 
            self.update_display() 

    def apply_action(self):
        if self.img is None:
            return 
        
        self.apply.setEnabled(False) 
        self.apply.setText('Processing...') 

        # Parameters 
        params = {
                'intensity': self.slider_intensity.value() / 10.0,
                'threshold': self.slider_threshold.value(), 
                'matrix_idx': {1: '2x2', 2: '4x4', 3: '8x8'}.get(self.slider_grid.value(), '2x2')
        }
        method = self.type_of_dithering.currentText()
        
        # Config thread and worker 
        self.thread = QThread() 
        self.worker = DitherWorker(self.img.copy(), method, params)
        self.worker.moveToThread(self.thread) 

        # Signal link 
        self.thread.started.connect(self.worker.run) 
        self.worker.finished.connect(self.on_dither_finished) 
        self.worker.error.connect(self.on_dither_error) 
        
        # Clean up memory 
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater) 

        self.thread.start() 
    
    def on_dither_finished(self, processed_img): 
        # Save state for Undo ( Only PIL object is saved because it's lighter )  
        self.undo_stack.append(self.img.copy())
        self.redo_stack.clear() 

        self.img = processed_img
        self._sync_gui_with_img() 

        # Reactivate button 
        self.apply.setEnabled(True)
        self.apply.setText("Apply") 
    
    def on_dither_error(self, message): 
        QMessageBox.critical(self, "Error", f"Dithering failed: {message}")
        self.apply.setEnabled(True) 
        self.apply.setText("Apply") 

    def update_display(self): 
        if not self.displayImage.isNull(): 
            scaled_pixmap = self.displayImage.scaled(
                self.label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap) 


    def default_action(self): 
        if not self.displayImage.isNull(): 
            self.img = load_img_as_rgb(self.imagePath) 
            data = self.img.tobytes("raw", "RGB")

            self.originalImage = QImage(data, self.img.width, self.img.height, QImage.Format.Format_RGB888).copy() 

            self.displayImage = QPixmap.fromImage(self.originalImage)
            self.displayImage = self.displayImage.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(self.displayImage)


    def update_ui(self):
        method = self.type_of_dithering.currentText() 
        
        self.group_intensity.hide() 
        self.group_threshold.hide()
        self.group_grid.hide()

        if method == "Floyd-steinberg":
            self.group_intensity.setTitle("Diffusion Strength") 
            self.group_intensity.show() 
        elif method == "Random":
            self.group_intensity.setTitle("Noise intensity") 
            self.group_intensity.show() 
        elif method == "Bayer":
            self.group_threshold.show()
            self.group_grid.show() 


    def create_slider_group(self, label_text, min_val, max_val): 
        group = QGroupBox(label_text)
        layout = QVBoxLayout()
        label = QLabel(f"{min_val}")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)

        slider.valueChanged.connect(lambda val: label.setText(f"{val}"))   

        layout.addWidget(label) 
        layout.addWidget(slider)
        group.setLayout(layout)
       
        return group, slider
    
