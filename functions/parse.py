import re

def parse_coordinates(text):
    if not text:
        return [], []

    lines = text.strip().splitlines()
    coords = []
    errors = []
    auto_index = 1
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        tokens = re.split(r'[\t\s,]+', line)
        tokens = [t.replace(",", ".") for t in tokens]
        tokens = [t for t in tokens if t]
        # bỏ ký tự dẫn ở STT (>, #, ...)
        tokens[0] = re.sub(r'^[^0-9A-Za-z]+', '', tokens[0])
        # nếu dư token ở cuối (ghi chú) → bỏ
        tokens = tokens[:4]

        # --- Gom 3 dòng đơn ---
        if len(tokens) == 1 and i + 2 < len(lines):
            try:
                x = float(lines[i].strip().replace(",", "."))
                y = float(lines[i+1].strip().replace(",", "."))
                h = float(lines[i+2].strip().replace(",", "."))
                coords.append([f"Điểm {auto_index}", x, y, h])
                auto_index += 1
                i += 3
                continue
            except:
                pass

        # --- X=..., Y=... ---
        if re.fullmatch(r"[Xx]=[0-9]*\.?[0-9]+", line) and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.fullmatch(r"[Yy]=[0-9]*\.?[0-9]+", next_line):
                try:
                    x_raw = float(line.split("=")[1])
                    y_raw = float(next_line.split("=")[1])

                    x_ok = 500_000 <= x_raw <= 2_650_000
                    y_ok = 330_000 <= y_raw <= 670_000
                    x_swap_ok = 500_000 <= y_raw <= 2_650_000
                    y_swap_ok = 330_000 <= x_raw <= 670_000

                    if not (x_ok and y_ok) and (x_swap_ok and y_swap_ok):
                        x, y = y_raw, x_raw
                    else:
                        x, y = x_raw, y_raw

                    coords.append([f"Điểm {auto_index}", x, y, 0.0])
                    auto_index += 1
                    i += 2
                    continue
                except Exception as e:
                    errors.append([line, f"Lỗi: {e}"])

        # --- Dòng chứa E/N tách biệt ---
        if len(tokens) == 1 and re.fullmatch(r"[EN]\d{8}", tokens[0]):
            if i + 1 < len(lines):
                next_tokens = re.split(r'[\t\s]+', lines[i+1].strip())
                next_tokens = [t for t in next_tokens if t]
                if len(next_tokens) == 1 and re.fullmatch(r"[EN]\d{8}", next_tokens[0]):
                    x, y = None, None
                    for t in [tokens[0], next_tokens[0]]:
                        if t.startswith("E"):
                            y = int(t[1:])
                        elif t.startswith("N"):
                            x = int(t[1:])
                    if x is not None and y is not None:
                        coords.append([f"Điểm {auto_index}", float(x), float(y), 0.0])
                        auto_index += 1
                        i += 2
                        continue
            errors.append([line, "Thiếu dòng mã hiệu E/N kèm theo"])
            i += 1
            continue

        # --- Dòng chứa E/N cùng dòng ---
        if len(tokens) == 2 and all(re.fullmatch(r"[EN]\d{8}", t) for t in tokens):
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
                errors.append([line, "Không tách được E/N"])
            i += 1
            continue

        # --- STT X Y H / STT X Y / X Y H / X Y ---
        try:
            if len(tokens) == 4:
                stt, x, y, h = tokens
                coords.append([stt, float(x), float(y), float(h)])
            elif len(tokens) == 3:
                # Phân biệt STT X Y vs X Y H
                is_stt = re.fullmatch(r"\d+", tokens[0]) is not None
                is_float2 = re.fullmatch(r"-?\d+(\.\d+)?", tokens[1]) and re.fullmatch(r"-?\d+(\.\d+)?", tokens[2])
                if is_stt and is_float2:
                    stt, x, y = tokens
                    coords.append([stt, float(x), float(y), 0.0])
                else:
                    x, y, h = map(float, tokens)
                    coords.append([f"Điểm {auto_index}", x, y, h])
                    auto_index += 1
            elif len(tokens) == 2:
                x, y = map(float, tokens)
                coords.append([f"Điểm {auto_index}", x, y, 0.0])
                auto_index += 1
            else:
                raise ValueError("Không đúng định dạng")
        except Exception as e:
            errors.append([line, f"Lỗi: {e}"])
        i += 1

    # --- Lọc miền hợp lệ ---
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
