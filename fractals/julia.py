from PyQt5.QtGui import QImage, QPixmap, QColor
import numpy as np
import math


def clamp_int(v, lo=0, hi=255):
    iv = int(round(v))
    if iv < lo:
        return lo
    if iv > hi:
        return hi
    return iv


class JuliaGenerator:
    def __init__(self, width=900, height=600):
        self.width = int(width)
        self.height = int(height)
        self.theme = "Ocean"
        self.user_color = QColor(130, 30, 255)

    def get_theme_color(self, t):
        if self.theme == "Ocean":
            r = 20 + 60 * math.sin(t + 0.0)
            g = 80 + 100 * math.sin(t + 1.0)
            b = 150 + 100 * math.sin(t + 2.0)
        elif self.theme == "Fire":
            r = 150 + 100 * math.sin(t + 0.0)
            g = 40 + 120 * math.sin(t + 1.5)
            b = 10 + 40 * math.sin(t + 3.0)
        elif self.theme == "Ice":
            r = 180 + 40 * math.sin(t + 0.0)
            g = 220 + 30 * math.sin(t + 1.0)
            b = 255 + 0 * math.sin(t + 0.0)
        elif self.theme == "Neon":
            r = 180 + 70 * math.sin(t + 0.0)
            g = 20 + 200 * math.sin(t + 1.0)
            b = 200 + 50 * math.sin(t + 2.0)
        elif self.theme == "Pastel":
            r = 200 + 30 * math.sin(t + 0.0)
            g = 180 + 40 * math.sin(t + 1.0)
            b = 200 + 50 * math.sin(t + 2.0)
        elif self.theme == "Custom":
            ur = self.user_color.red()
            ug = self.user_color.green()
            ub = self.user_color.blue()
            r = ur * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t + 0.0)))
            g = ug * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t + 1.0)))
            b = ub * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t + 2.0)))
        else:
            v = 127.5 * (1 + math.sin(t))
            r = g = b = v

        return QColor(clamp_int(r), clamp_int(g), clamp_int(b))

    def get_theme_color_numpy(self, t_array):
        r = np.zeros_like(t_array)
        g = np.zeros_like(t_array)
        b = np.zeros_like(t_array)
        
        if self.theme == "Ocean":
            r = 150 + 100 * np.sin(t_array + 0.0)
            g = 40 + 120 * np.sin(t_array + 1.5)
            b = 10 + 40 * np.sin(t_array + 3.0)
        elif self.theme == "Fire":
            r = 20 + 60 * np.sin(t_array + 0.0)
            g = 80 + 100 * np.sin(t_array + 1.0)
            b = 150 + 100 * np.sin(t_array + 2.0)
        elif self.theme == "Ice":
            r = 200 + 30 * np.sin(t_array + 0.0)
            g = 180 + 40 * np.sin(t_array + 1.0)
            b = 200 + 50 * np.sin(t_array + 2.0)
        elif self.theme == "Neon":
            r = 180 + 70 * np.sin(t_array + 0.0)
            g = 20 + 200 * np.sin(t_array + 1.0)
            b = 200 + 50 * np.sin(t_array + 2.0)
        elif self.theme == "Pastel":
            r = 180 + 40 * np.sin(t_array + 0.0)
            g = 220 + 30 * np.sin(t_array + 1.0)
            b = 255 + 0 * np.sin(t_array + 0.0)
        elif self.theme == "Custom":
            ub = self.user_color.red()
            ug = self.user_color.green()
            ur = self.user_color.blue()
            r = ur * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(t_array + 0.0)))
            g = ug * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(t_array + 1.0)))
            b = ub * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(t_array + 2.0)))
        else:
            v = 127.5 * (1 + np.sin(t_array))
            r = g = b = v
        
        r = np.clip(np.round(r), 0, 255).astype(np.uint8)
        g = np.clip(np.round(g), 0, 255).astype(np.uint8)
        b = np.clip(np.round(b), 0, 255).astype(np.uint8)
        
        return r, g, b

    def generate_numpy(self, center_x=0.0, center_y=0.0, zoom=1.0, max_iter=200, 
                    cx_param=0.0, cy_param=0.0, base_color=None, width=900, height=600):
        
        original_theme = self.theme
        
        if base_color is not None and isinstance(base_color, QColor):
            self.user_color = base_color
            self.theme = "Custom"
        
        self.width = int(width)
        self.height = int(height)
        
        x_range = 4.0 / zoom
        y_range = 3.0 / zoom
        
        x_min = center_x - x_range / 2
        x_max = center_x + x_range / 2
        y_min = center_y - y_range / 2
        y_max = center_y + y_range / 2
        
        x = np.linspace(x_min, x_max, self.width)
        y = np.linspace(y_min, y_max, self.height)
        
        c = cx_param + cy_param * 1j
        z = x + y[:, None] * 1j
        
        iterations = np.zeros(z.shape, dtype=np.int32)
        mask = np.ones(z.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = z[mask] * z[mask] + c
            diverged = np.abs(z) > 2.0
            iterations[diverged & mask] = i
            mask = mask & (~diverged)
        
        z_abs = np.abs(z)
        log_z = np.log(np.where(z_abs > 1e-10, z_abs, 1e-10))
        mu = iterations - np.log2(np.where(log_z > 1e-10, log_z, 1e-10))
        mu = np.where(np.isfinite(mu), mu, iterations)
        
        t_array = mu * 0.12
        
        r, g, b = self.get_theme_color_numpy(t_array)
        
        inside_mask = mask
        r[inside_mask] = 0
        g[inside_mask] = 0
        b[inside_mask] = 0
        
        img_array = np.stack([r, g, b], axis=2)
        
        height, width, channels = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        q_image = q_image.convertToFormat(QImage.Format_RGB32)
        
        self.theme = original_theme
        
        yield QPixmap.fromImage(q_image)
        
    def generate(self, max_iter=200, zoom=1.0, cx_param=0.0, cy_param=0.0, base_color=None, center_x=0.0, center_y=0.0):
        if base_color is not None and isinstance(base_color, QColor):
            self.user_color = base_color

        img = QImage(self.width, self.height, QImage.Format_RGB32)

        x_range = 4.0 / zoom
        y_range = 3.0 / zoom

        xs = np.linspace(center_x - x_range / 2, center_x + x_range / 2, self.width)
        ys = np.linspace(center_y - y_range / 2, center_y + y_range / 2, self.height)

        for y_idx, cy in enumerate(ys):
            for x_idx, cx in enumerate(xs):
                zx = cx
                zy = cy
                it = 0

                while zx * zx + zy * zy < 4.0 and it < max_iter:
                    zx, zy = zx * zx - zy * zy + cx_param, 2.0 * zx * zy + cy_param
                    it += 1

                if it >= max_iter:
                    img.setPixelColor(x_idx, y_idx, QColor(0, 0, 0))
                else:
                    zn = math.sqrt(zx * zx + zy * zy)
                    if zn == 0 or zn <= 0 or not math.isfinite(zn):
                        mu = float(it)
                    else:
                        mu = it - math.log(max(1e-10, math.log(zn))) / math.log(2.0)

                    t = mu * 0.12

                    color = self.get_theme_color(t)
                    img.setPixelColor(x_idx, y_idx, color)

            yield QPixmap.fromImage(img)

        yield QPixmap.fromImage(img)
