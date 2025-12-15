from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from utils.zoom_video import save_frames_to_video
from utils.video_thread import VideoGenerationThread

class ZoomDialog(QDialog):
    def __init__(self, mandel, parent=None, julia=None, lblFractal=None):
        
        from PyQt5 import QtWidgets
        from utils.clean_spinBox import CleanSpinBox
        QtWidgets.QDoubleSpinBox = CleanSpinBox

        super().__init__(parent)
        loadUi("ui/zoom.ui", self)
        self.mandel = mandel
        self.julia = julia
        self.parent = parent
        self.lblFractal = lblFractal
        self.video_thread = None

        self.btnGenerateVideo.clicked.connect(self.generate_video)

        self._selecting_start = None

    def get_gen_func(self):
        if self.parent.comboFractal.currentIndex() == 0:
            gen_obj = self.mandel
            gen_obj.theme = self.parent.comboColorTheme.currentText()
            base_color = getattr(self.parent, "selected_mandel_color", None)

            def mandel_numpy_wrapper(ox, oy, zoom, iters):
                return gen_obj.generate_numpy(
                    max_iter=iters,
                    zoom=zoom,
                    offset_x=ox,
                    offset_y=oy,
                    base_color=base_color
                )
                
            gen_func = mandel_numpy_wrapper
            
        elif self.parent.comboFractal.currentIndex() == 1:
            gen_obj = self.julia
            gen_obj.theme = self.parent.comboColorTheme_2.currentText()
            
            
            base_color = None
            base_color = getattr(self.parent, "selected_julia_color", None)
            
            cx = self.parent.spinCRealJulia.value()
            cy = self.parent.spinCImagJulia.value()
            
            def julia_numpy_wrapper(ox, oy, zoom, iters):
                return gen_obj.generate_numpy(
                    max_iter=iters,
                    zoom=zoom,
                    cx_param=cx,
                    cy_param=cy,
                    base_color=base_color,
                    center_x=ox,
                    center_y=oy
                )
                
            gen_func = julia_numpy_wrapper
        else:
            gen_func = None
            
        return gen_func

    def generate_video(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Video (*.mp4)")
        if not path:
            return
        
        endX = self.endXSpinBox.value()
        endY = self.endYSpinBox.value()
        startZoom = self.spinStartZoom.value()
        endZoom = self.spinEndZoom.value()
        iterations = self.spinIterations.value()
        n_frames = self.spinFrames.value()        
        startX = endX - (0.05 / endZoom)
        startY = endY - (0.05 / endZoom)

        self.btnGenerateVideo.setEnabled(False)
        self.btnGenerateVideo.setText("Generating...")

        gen_func = self.get_gen_func()
        if gen_func is None:
            QMessageBox.warning(self, "Error", "Unsupported fractal type")
            self.btnGenerateVideo.setEnabled(True)
            self.btnGenerateVideo.setText("Generate Video")
            return

        self.video_thread = VideoGenerationThread(
            gen_func=gen_func,
            start_params=(startX, startY, startZoom),
            end_params=(endX, endY, endZoom),
            iterations=iterations,
            n_frames=n_frames
        )
        
        self.video_thread.progress_updated.connect(self.progressBar.setValue)
        self.video_thread.finished_generation.connect(
            lambda frames: self.on_video_generated(frames, path)
        )
        self.video_thread.error_occurred.connect(self.on_generation_error)
        
        self.video_thread.start()

    def on_video_generated(self, frames, path):
        if frames:
            try:
                save_frames_to_video(frames, path)
                QMessageBox.information(self, "Done", f"Video saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save video:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No frames were generated")
            
        self.btnGenerateVideo.setEnabled(True)
        self.btnGenerateVideo.setText("Generate Video")

    def on_generation_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Generation failed:\n{error_msg}")
        self.btnGenerateVideo.setEnabled(True)
        self.btnGenerateVideo.setText("Generate Video")
