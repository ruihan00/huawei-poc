def detect_falls(x1, x2, y1, y2):
    # Falling code
    w = x2 - x1
    h = y2 - y1
    return w / h 

def detect_squat(y1, y2):
    return y1 / y2 > 1.5


def detect_same(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2, threshold):
    area_a = (ax2 - ax1) * (ay2 - ay1)
    
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)
    
    area_intersection = inter_width * inter_height

    overlap_ratio = area_intersection / area_a if area_a > 0 else 0

    return overlap_ratio > threshold