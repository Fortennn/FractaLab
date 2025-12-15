import cv2
import numpy as np

def save_frames_to_video(frames, path, fps=30):
    if not frames:
        return

    valid_frames = [frame for frame in frames if frame is not None]
    if not valid_frames:
        return

    w = valid_frames[0].width()
    h = valid_frames[0].height()
    
    if w % 2 != 0:
        w -= 1
    if h % 2 != 0:
        h -= 1
    
    fourcc_options = [
        cv2.VideoWriter_fourcc(*'mp4v'),
        cv2.VideoWriter_fourcc(*'avc1'),
        cv2.VideoWriter_fourcc(*'X264'),
        cv2.VideoWriter_fourcc(*'MJPG')
    ]
    
    out = None
    for fourcc in fourcc_options:
        try:
            out = cv2.VideoWriter(path, fourcc, fps, (w, h))
            if out.isOpened():
                print(f"Using codec: {fourcc}")
                break
            else:
                out.release()
                out = None
        except:
            if out:
                out.release()
            out = None
    
    if out is None:
        print("Failed to create video writer")
        return

    for pix in valid_frames:
        if pix.width() != w or pix.height() != h:
            pix = pix.scaled(w, h, aspectRatioMode=1, transformMode=1)
        
        img = pix.toImage().convertToFormat(4)
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        arr = np.frombuffer(ptr, np.uint8).reshape(h, w, 4)
        
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        
        out.write(arr)

    out.release()