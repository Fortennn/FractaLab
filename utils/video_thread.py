from PyQt5.QtCore import QThread, pyqtSignal

class VideoGenerationThread(QThread):
    progress_updated = pyqtSignal(int)
    finished_generation = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, gen_func, start_params, end_params, iterations, n_frames):
        super().__init__()
        self.gen_func = gen_func
        self.start_params = start_params
        self.end_params = end_params
        self.iterations = iterations
        self.n_frames = min(n_frames, 600)
        self.frames = []
        
    def run(self):
        start_x, start_y, start_zoom = self.start_params
        end_x, end_y, end_zoom = self.end_params
        
        frames = []
        
        for i in range(self.n_frames):
            if self.isInterruptionRequested():
                break
                
            t = i / (self.n_frames - 1) if self.n_frames > 1 else 0
            t_smooth = self.smooth_step(t)
            
            current_x = start_x + (end_x - start_x) * t_smooth
            current_y = start_y + (end_y - start_y) * t_smooth
            current_zoom = start_zoom * (end_zoom / start_zoom) ** t_smooth
            
            adaptive_iters = max(50, min(self.iterations, int(100 + current_zoom * 2)))
            
            frame_generator = self.gen_func(
                current_x, current_y, current_zoom, adaptive_iters
            )
            
            final_frame = None
            for frame in frame_generator:
                final_frame = frame
                
            if final_frame:
                frames.append(final_frame)
            
            progress = int((i + 1) / self.n_frames * 100)
            self.progress_updated.emit(progress)
            
        self.finished_generation.emit(frames)

    def smooth_step(self, t):
        return t * t * (3 - 2 * t)