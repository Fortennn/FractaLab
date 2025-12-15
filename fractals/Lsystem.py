from PyQt5.QtGui import QImage, QPainter, QPen, QColor, QPixmap
import math


class LSystemGenerator:
    def __init__(self, width: int = 900, height: int = 600):
        self.width = int(width)
        self.height = int(height)

    def _expand(self, axiom: str, rules: dict, iterations: int) -> str:
        if iterations < 0:
            raise ValueError("Iterations must be non-negative")
        if not axiom:
            raise ValueError("Axiom must be non-empty")

        word = axiom
        for _ in range(iterations):
            word = "".join(rules.get(ch, ch) for ch in word)
            if len(word) > 500_000:
                break
        return word

    def generate(
        self,
        iterations: int,
        angle_deg: float,
        step: float,
        axiom: str,
        rules: dict,
        thickness: int = 1,
        auto_scale: bool = True,
        draw_chars: str | None = None,
    ):

        instructions = self._expand(axiom, rules, iterations)
        angle = math.radians(angle_deg)
        if draw_chars is None:
            control = set("+-[]")
            draw_candidates = []
            for ch in axiom:
                if ch.isalpha() and ch not in control:
                    draw_candidates.append(ch)
            for repl in rules.values():
                for ch in repl:
                    if ch.isalpha() and ch not in control:
                        draw_candidates.append(ch)
            draw_set = set(draw_candidates) or {"F"}
        else:
            draw_set = set(draw_chars)

        img = QImage(self.width, self.height, QImage.Format_RGB32)
        img.fill(QColor(255, 255, 255))
        painter = QPainter(img)
        pen = QPen(QColor(0, 0, 0), thickness)
        painter.setPen(pen)

        x = y = 0.0
        heading = -math.pi / 2
        stack = []

        min_x = max_x = x
        min_y = max_y = y

        if auto_scale:
            for cmd in instructions:
                if cmd in draw_set:
                    nx = x + step * math.cos(heading)
                    ny = y + step * math.sin(heading)
                    x, y = nx, ny
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                elif cmd == "+":
                    heading += angle
                elif cmd == "-":
                    heading -= angle
                elif cmd == "[":
                    stack.append((x, y, heading))
                elif cmd == "]" and stack:
                    x, y, heading = stack.pop()

            bbox_w = max_x - min_x
            bbox_h = max_y - min_y
            if bbox_w > 0 and bbox_h > 0:
                sx = (self.width - 40) / bbox_w
                sy = (self.height - 40) / bbox_h
                scale = min(sx, sy)
            else:
                scale = 1.0
        else:
            scale = 1.0

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        x = self.width / 2.0 - center_x * scale
        y = self.height / 2.0 - center_y * scale
        heading = -math.pi / 2
        stack = []

        counter = 0
        for cmd in instructions:
            if cmd in draw_set:
                nx = x + step * math.cos(heading) * scale
                ny = y + step * math.sin(heading) * scale
                painter.drawLine(int(x), int(y), int(nx), int(ny))
                x, y = nx, ny
            elif cmd == "+":
                heading += angle
            elif cmd == "-":
                heading -= angle
            elif cmd == "[":
                stack.append((x, y, heading))
            elif cmd == "]" and stack:
                x, y, heading = stack.pop()

            counter += 1
            if counter % 80 == 0:
                yield QPixmap.fromImage(img)

        painter.end()
        yield QPixmap.fromImage(img)
