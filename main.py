import sys
import os
import resources_rc
from PyQt5.QtWidgets import QApplication, QDialog, QColorDialog, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import QFile, QPropertyAnimation, QEasingCurve
from PyQt5.uic import loadUi
from PyQt5.QtGui import QMovie, QIcon, QImage
from PIL import Image

from fractals.mandelbrot import MandelbrotGenerator
from fractals.julia import JuliaGenerator
from fractals.Lsystem import LSystemGenerator
from fractals.koha import KochGenerator
from fractals.lsystem_presets import L_SYSTEM_PRESETS

from utils.zoom_dialog import ZoomDialog


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FractalMainWindow(QDialog):
    def __init__(self):
        super().__init__()
          
        self.selected_julia_color = None
        self.selected_mandel_color = None
        self.mandel = MandelbrotGenerator()
        self.julia = JuliaGenerator()
        self.lsystem = LSystemGenerator()
        self.koch = KochGenerator()
        self.lsystem_frames = []

        self.load_ui()
        self.load_styles()
        self.setup_animations()
        self.connect_functionality()
        self.setWindowIcon(QIcon(resource_path("resources/img/icon.png")))

        self.lblStartXY = QLabel(self.lblFractalDisplay)
        self.lblStartXY.setStyleSheet("color: green; font-weight: bold; background-color: rgba(0,0,0,50%);")
        self.lblStartXY.setGeometry(5, 5, 200, 20)
        self.lblStartXY.hide()

        self.lblEndXY = QLabel(self.lblFractalDisplay)
        self.lblEndXY.setStyleSheet("color: red; font-weight: bold; background-color: rgba(0,0,0,50%);")
        self.lblEndXY.setGeometry(5, 30, 200, 20)
        self.lblEndXY.hide()

        gif_path = resource_path("resources/gif/dance.gif")
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.lblFractalDisplay.setMovie(self.movie)
            self.movie.start()
        else:
            self.movie = None
        self.lblFractalDisplay.setScaledContents(True)
    
    def load_ui(self):
        from utils.clean_spinBox import CleanSpinBox
        from PyQt5 import QtWidgets
        QtWidgets.QDoubleSpinBox = CleanSpinBox

        ui_path = resource_path("ui/main.ui")
        ui_file = QFile(ui_path)

        if ui_file.open(QFile.ReadOnly):
            loadUi(ui_file, self)
            ui_file.close()
        else:
            print("UI file not found:", ui_path)


    def load_styles(self):
        style_path = resource_path("resources/stylesheet.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print("Stylesheet not found:", style_path)


    def setup_animations(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        self._animation_done = False

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_animation_done", False):
            self.animation.start()
            self._animation_done = True


    def connect_functionality(self):
        self.comboFractal.currentIndexChanged.connect(self.stackedWidget.setCurrentIndex)
        self.btnGenerate.clicked.connect(self.generate_fractal)
        self.btnSave.clicked.connect(self.save_image)
        self.btnZoomVideo.clicked.connect(self.open_zoom_dialog)
        self.btnZoomVideo_2.clicked.connect(self.open_zoom_dialog)
        self.comboColorTheme.currentTextChanged.connect(self.change_theme)
        self.comboColorTheme_2.currentTextChanged.connect(self.change_theme)
        self.btnResetPalette.clicked.connect(self.reset_palette)
        self.comboPresetsLSystem.currentTextChanged.connect(self.apply_lsystem_preset)
        self.connect_linked_controls()

    def change_theme(self, theme):
        self.mandel.theme = theme
        self.julia.theme = theme

        if theme == "Custom":
            if self.comboFractal.currentIndex() == 0:
                self.pick_color("Mandelbrot")
            elif self.comboFractal.currentIndex() == 1:
                self.pick_color("Julia")

    def pick_color(self, fractal_name):
        dialog = QColorDialog(self)
        style_path = resource_path("resources/stylesheet.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                dialog.setStyleSheet(f.read())


        if dialog.exec_() == QColorDialog.Accepted:
            color = dialog.selectedColor()
            if color.isValid():
                if fractal_name == "Mandelbrot":
                    self.selected_mandel_color = color
                    self.comboColorTheme.setCurrentText("Custom")
                elif fractal_name == "Julia":
                    self.selected_julia_color = color
                    self.comboColorTheme_2.setCurrentText("Custom")

    def connect_linked_controls(self):

        self.spinIterationsMandelbrot.valueChanged.connect(self.spinIterationsMandelbrot_2.setValue)
        self.spinIterationsMandelbrot_2.valueChanged.connect(self.spinIterationsMandelbrot.setValue)

        self.spinIterationsJulia.valueChanged.connect(self.spinIterationsJulia_2.setValue)
        self.spinIterationsJulia_2.valueChanged.connect(self.spinIterationsJulia.setValue)

        self.spinIterationsLSystem.valueChanged.connect(self.spinIterationsLSystem_2.setValue)
        self.spinIterationsLSystem_2.valueChanged.connect(self.spinIterationsLSystem.setValue)

        self.spinAngleLSystem_2.valueChanged.connect(self.spinAngleLSystem.setValue)
        self.spinAngleLSystem.valueChanged.connect(self.spinAngleLSystem_2.setValue)

        self.spinLengthLSystem.valueChanged.connect(self.spinLengthLSystem_2.setValue)
        self.spinLengthLSystem_2.valueChanged.connect(self.spinLengthLSystem.setValue)

        self.spinLevelKoch.valueChanged.connect(self.spinLevelKoch_2.setValue)
        self.spinLevelKoch_2.valueChanged.connect(self.spinLevelKoch.setValue)

        self.spinThicknessKoch.valueChanged.connect(self.spinThicknessKoch_2.setValue)
        self.spinThicknessKoch_2.valueChanged.connect(self.spinThicknessKoch.setValue)

    def parse_rule_field(self, text: str):
        t = text.strip()
        if not t:
            return None
        for sep in ("->", "→"):
            if sep in t:
                left, right = t.split(sep, 1)
                return (left.strip(), right.strip())
        return ("", t)


    def parse_rules_from_ui(self, axiom: str, fields: list):
        control = set("+-[]")
        symbols = [ch for ch in axiom if ch.isalpha() and ch not in control]
        seen, unique = set(), []
        for s in symbols:
            if s not in seen:
                seen.add(s)
                unique.append(s)

        rules = {}
        idx = 0
        for field in fields:
            parsed = self.parse_rule_field(field)
            if not parsed:
                continue
            left, right = parsed
            if not left:
                if idx < len(unique):
                    left = unique[idx]
                    idx += 1
                else:
                    continue
            rules[left] = right
        return rules

    def reset_palette(self):
        if hasattr(self, "comboColorTheme"):
            idx = self.comboColorTheme.findText("Ocean")
            if idx != -1:
                self.comboColorTheme.setCurrentIndex(idx)
            elif self.comboColorTheme.count() > 0:
                self.comboColorTheme.setCurrentIndex(0)

        self.selected_mandel_color = None
        self.selected_julia_color = None

        gif_path = resource_path("resources/gif/dance.gif")
        self.movie = QMovie(gif_path)
        self.lblFractalDisplay.setMovie(self.movie)
        self.lblFractalDisplay.setScaledContents(True)
        self.movie.start()

    def generate_fractal(self):
        if self.movie:
            self.movie.stop()

        if self.comboFractal.currentIndex() == 0:
            self.generate_mandelbrot()
        elif self.comboFractal.currentIndex() == 1:
            self.generate_julia()
        elif self.comboFractal.currentIndex() == 2:
            self.generate_lsystem()
        elif self.comboFractal.currentIndex() == 3:
            self.generate_koch() 

    def animate_frames(self, generator, capture_frames=False, frame_store=None):
        for pix in generator:
            if capture_frames and frame_store is not None:
                frame_store.append(pix.toImage().copy())
            self.lblFractalDisplay.setPixmap(pix)
            QApplication.processEvents()
            QApplication.processEvents()

    def generate_julia(self):
        self.lsystem_frames = []
        iterations = self.spinIterationsJulia.value()
        zoom = self.spinZoomJulia.value()
        cx = self.spinCRealJulia.value()
        cy = self.spinCImagJulia.value()
        center_x = self.spinCenterXJulia.value()
        center_y = self.spinCenterYJulia.value()

        if iterations > 5000:
            reply = QMessageBox.warning(
                self,
                "Warning",
                "High iteration counts (>5000) may slow down fractal generation.\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        base_color = self.selected_julia_color

        gen = self.julia.generate(
            max_iter=iterations,
            zoom=zoom,
            cx_param=cx,
            cy_param=cy,
            center_x=center_x,
            center_y=center_y,
            base_color=base_color
        )

        self.animate_frames(gen)

    def generate_mandelbrot(self):
        self.lsystem_frames = []
        iterations = int(self.spinIterationsMandelbrot.value())
        if iterations > 5000:
            reply = QMessageBox.warning(
                self,
                "Warning",
                "High iteration counts (>5000) may slow down fractal generation.\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        zoom = float(self.spinZoomMandelbrot.value())
        ox = float(self.spinCenterXMandelbrot.value())
        oy = float(self.spinCenterYMandelbrot.value())

        base_color = self.selected_mandel_color

        gen = self.mandel.generate(
            max_iter=iterations,
            zoom=zoom,
            offset_x=ox,
            offset_y=oy,
            base_color=base_color
        )

        self.animate_frames(gen)

    def generate_lsystem(self):
        self.lsystem_frames = []
        iterations = self.spinIterationsLSystem.value()
        angle = self.spinAngleLSystem.value()
        length = self.spinLengthLSystem.value()
        axiom = self.lineAxiomLSystem.text()

        fields = [
            self.lineRuleALSystem.text(),
            self.lineRuleBLSystem.text(),
            self.lineRuleCLSystem.text(),
        ]
        rules = self.parse_rules_from_ui(axiom, fields)

        gen = self.lsystem.generate(
            iterations=iterations,
            angle_deg=angle,
            step=length,
            axiom=axiom,
            rules=rules
        )
        self.animate_frames(gen, capture_frames=True, frame_store=self.lsystem_frames)



    def apply_lsystem_preset(self):
        preset = self.comboPresetsLSystem.currentText()

        if preset not in L_SYSTEM_PRESETS:
            return

        cfg = L_SYSTEM_PRESETS[preset]

        self.lineAxiomLSystem.setText(cfg["axiom"])

        rule_items = list(cfg["rules"].items())

        self.lineRuleALSystem.setText(f"{rule_items[0][0]} -> {rule_items[0][1]}" if len(rule_items) > 0 else "")
        self.lineRuleBLSystem.setText(f"{rule_items[1][0]} -> {rule_items[1][1]}" if len(rule_items) > 1 else "")
        self.lineRuleCLSystem.setText(f"{rule_items[2][0]} -> {rule_items[2][1]}" if len(rule_items) > 2 else "")

        self.spinAngleLSystem.setValue(int(cfg["angle"]))
        self.spinIterationsLSystem.setValue(int(cfg["iterations"]))
        self.spinLengthLSystem.setValue(int(cfg["length"]))

    def generate_koch(self):
        self.lsystem_frames = []
        level = self.spinLevelKoch.value()
        thickness = self.spinThicknessKoch.value()
        fractal_type = self.comboTypeKoch.currentText().lower()

        gen = self.koch.generate(
            level=level,
            thickness=thickness,
            type=fractal_type
        )
        self.animate_frames(gen)

    def open_zoom_dialog(self):
        self.zoom_dialog = ZoomDialog(
            parent=self,
            mandel=self.mandel,
            julia=self.julia,
            lblFractal=self.lblFractalDisplay
        )
        self.zoom_dialog.show()


    def save_image(self):
        pix = None
        if hasattr(self, "lblFractalDisplay") and self.lblFractalDisplay.pixmap() is not None:
            pix = self.lblFractalDisplay.pixmap()
        elif hasattr(self, "labelFractal") and self.labelFractal.pixmap() is not None:
            pix = self.labelFractal.pixmap()

        if pix is None:
            return

        filters = "PNG Image (*.png);;JPEG Image (*.jpg)"
        if self.comboFractal.currentIndex() == 2:
            filters = "GIF Animation (*.gif);;" + filters

        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save image",
            "",
            filters
        )

        if path:
            lower = path.lower()
            if lower.endswith(".gif") and self.comboFractal.currentIndex() == 2:
                self.save_lsystem_gif(path)
            else:
                pix.save(path)

    def qimage_to_pil(self, qimg: QImage) -> Image.Image:
        qimg = qimg.convertToFormat(QImage.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        return img.copy()

    def save_lsystem_gif(self, path: str):
        if not getattr(self, "lsystem_frames", None):
            QMessageBox.information(self, "Info", "Сначала сгенерируйте L-system, чтобы сохранить анимацию.")
            return
        frames = self.lsystem_frames
        step = max(1, len(frames) // 80)
        picked = [frames[i] for i in range(0, len(frames), step)]
        if picked and picked[-1] is not frames[-1]:
            picked.append(frames[-1])
        pil_frames = [self.qimage_to_pil(frame) for frame in picked]
        if not pil_frames:
            QMessageBox.information(self, "Info", "Нет кадров для сохранения.")
            return
        
        pil_frames[0].save(
            path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=50,
            loop=0,
            optimize=False,
        )

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Fractal Generator")

    window = FractalMainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
