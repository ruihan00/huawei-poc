def detect_falls(x1, x2, y1, y2):
    # Falling code
    w = x2 - x1
    h = y2 - y1
    return w / h > 1.4
