import easyocr
import re

# --- OCR: nhóm theo dòng từ bounding box để giữ đúng thứ tự STT X Y ---
def auto_ocr_extract(filepath):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(filepath, detail=1)  # giữ bounding box

    items = []
    heights = []
    for bbox, text, conf in results:
        (tl_x, tl_y) = bbox[0]
        (bl_x, bl_y) = bbox[3]
        mid_y = (tl_y + bl_y) / 2
        height = abs(bl_y - tl_y)
        items.append({
            "text": text.replace(",", ".").strip(),
            "x": tl_x,
            "mid_y": mid_y
        })
        heights.append(height)

    # --- Tính ngưỡng tự động theo chiều cao chữ trung bình ---
    y_threshold = sum(heights) / len(heights) * 0.6 if heights else 10

    # --- Nhóm theo dòng (theo mid_y) ---
    items.sort(key=lambda item: item["mid_y"])
    lines = []
    if items:
        current_line = [items[0]]
        for item in items[1:]:
            if abs(item["mid_y"] - current_line[0]["mid_y"]) < y_threshold:
                current_line.append(item)
            else:
                current_line.sort(key=lambda it: it["x"])
                lines.append(current_line)
                current_line = [item]
        current_line.sort(key=lambda it: it["x"])
        lines.append(current_line)

    # --- Lọc từng dòng: giả định form cố định STT X Y, bỏ phần tử thứ 4 nếu có ---
    parsed = []
    debug = []
    for line in lines:
        texts = [re.sub(r"[^0-9\.]", "", item["text"]) for item in line]
        nums = [txt for txt in texts if re.fullmatch(r"\d+\.\d+", txt)]

        # Nếu có hơn 3 số ➝ bỏ phần dư
        if len(nums) > 3:
            debug.append(f"⚠️ Bỏ giá trị thứ 4 trở đi – {nums[3:]} từ {nums}")
            nums = nums[:3]

        # Nếu có 3 số và số đầu tiên > 500000 thì coi là X Y Z → gán STT tự động
        if len(nums) == 3:
            try:
                f0 = float(nums[0])
                f1 = float(nums[1])
                f2 = float(nums[2])
                if f0 > 500000:
                    debug.append(f"🔁 Chuyển từ X Y Z sang STT X Y – {nums}")
                    nums = [str(len(parsed)+1)] + nums[:2]
                elif f2 < 1000 and f1 > 500000:
                    debug.append(f"⚠️ Dòng nghi là STT X Z, bị loại – {nums}")
                    continue
            except:
                pass

        elif len(nums) == 2:
            nums.insert(0, str(len(parsed)+1))  # Gán STT tự động nếu thiếu

        if len(nums) == 3:
            try:
                x_val = float(nums[1])
                y_val = float(nums[2])
                if 500000 <= x_val <= 2650000 and 330000 <= y_val <= 670000:
                    parsed.append(nums)
                else:
                    debug.append(f"❌ Loại: ngoài miền X/Y – {nums}")
            except:
                debug.append(f"❌ Lỗi chuyển số – {nums}")
        else:
            debug.append(f"❌ Không đủ số – {texts}")

    if debug:
        with open("ocr_debug.log", "w", encoding="utf-8") as f:
            f.write("\n".join(debug))

    return "\n".join(" ".join(row) for row in parsed)
