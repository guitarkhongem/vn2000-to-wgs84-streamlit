import re

def parse_coordinates(text):
    if not text:
        return [], []

    lines = text.strip().splitlines()
    coords = []
    errors = []
    auto_index = 1

    for line in lines:
        line = line.strip().replace(",", ".")
        tokens = re.split(r'[\t\s]+', line)
        tokens = [t for t in tokens if t]

        try:
            # --- Dạng E12345678 N56781234 ---
            if len(tokens) == 2 and re.match(r"^[EN]\d{8}$", tokens[0]) and re.match(r"^[EN]\d{8}$", tokens[1]):
                x, y = None, None
                for t in tokens:
                    if t.startswith("E"):
                        y = int(t[1:])
                    elif t.startswith("N"):
                        x = int(t[1:])
                if x is not None and y is not None:
                    coords.append([f"Điểm {auto_index}", float(x), float(y), 0.0])
                    auto_index += 1
                else:
                    raise ValueError("Không tách được E/N")

            # --- Dạng STT X Y H ---
            elif len(tokens) == 4:
                stt, x, y, h = tokens
                coords.append([stt, float(x), float(y), float(h)])

            # --- Dạng STT X Y ---
            elif len(tokens) == 3:
                stt, x, y = tokens
                coords.append([stt, float(x), float(y), 0.0])

            # --- Dạng X Y (không STT) ---
            elif len(tokens) == 2:
                x, y = map(float, tokens)
                coords.append([f"Điểm {auto_index}", x, y, 0.0])
                auto_index += 1

            # --- Dạng X Y H (không STT) ---
            elif len(tokens) == 3:
                x, y, h = map(float, tokens)
                coords.append([f"Điểm {auto_index}", x, y, h])
                auto_index += 1

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
