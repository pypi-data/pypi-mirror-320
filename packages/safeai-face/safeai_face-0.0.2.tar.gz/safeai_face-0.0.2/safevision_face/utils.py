import cv2

def padding_image(image, x1, y1, x2, y2, padding=5):
    h, w = image.shape[:2]
    x1 = max(x1 - padding, 0)
    y1 = max(y1 - padding, 0)
    x2 = min(x2 + padding, w)
    y2 = min(y2 + padding, h)
    return x1, y1, x2, y2
