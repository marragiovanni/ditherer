from dithering import floyd_steinberg_dither, random_dither, bayer_dither
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal 

class DitherWorker(QObject): 
    # signals to communicate with the main thread   
    finished = pyqtSignal(object) # Send PIL image with effects 
    error = pyqtSignal(str)       # Send eventual error messages 
    
    def __init__(self, img, method, params): 
        super().__init__()
        self.img = img
        self.method = method 
        self.params = params 

    def run(self): 
        try: 
            working_img = self.img.convert('L') 
            if self.method == "Floyd-steinberg": 
                processed_img = floyd_steinberg_dither(working_img, self.params['intensity']) 
            elif self.method == "Random": 
                processed_img = random_dither(working_img, self.params["intensity"]) 
            else: 
                processed_img = bayer_dither(working_img, self.params["matrix_idx"], self.params["threshold"])             
            self.finished.emit(processed_img) 
        except Exception as e:  
            self.error.emit(str(e)) 

