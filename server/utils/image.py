def strip_base64_prefix(img):
    """Remove "data:image/webp;base64,"""
    base64_img = img.split(",")[1]
    return base64_img
