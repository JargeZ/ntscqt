def resize_to_height(wh, target_h):
    w, h = wh
    k = target_h/h
    return int(w * k) // 2 * 2, target_h
