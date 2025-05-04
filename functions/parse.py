import re

def parse_coordinates(text):
    if not text:
        return [], []

    lines = text.strip().splitlines()
    coords = []
    errors = []

    for line in lines:
        line = line.strip().replace(",", ".")
        tokens = re.split(r'[\t\s]+', line)
        tokens = [t for t in tokens if t]  # bỏ trống

        try:
            if len(tokens) == 4:
                stt, x, y, h = tokens
                x, y, h = float(x), float(y), float(h)
                coords.append([stt, x, y, h])
            elif len(tokens) == 3:
                stt, x, y = tokens
                x, y = float(x), float(y)
                coords.append([stt, x, y, 0.0])
            else:
                raise ValueError("Không đúng định dạng STT X Y [H]")
        except Exception as e:
            errors.append([line, f"Lỗi: {e}"])

    # --- Lọc theo điều kiện cứng ---
    filtered = []
    for ten_diem, x, y, h in coords:
        if 500_000 <= x <= 2_650_000 and 330_000 <= y <= 670_000 and -1000 <= h <= 3200:
            filtered.append([ten_diem, x, y, h])
        else:
            reason = []
            if not (500_000 <= x <= 2_650_000):
                reason.append(f"X={x} ngoài miền")
            if not (330_000 <= y <= 670_000):
                reason.append(f"Y={y} ngoài miền")
            if not (-1000 <= h <= 3200):
                reason.append(f"H={h} ngoài miền")
            errors.append([ten_diem, x, y, h, "; ".join(reason)])

    return filtered, errors
