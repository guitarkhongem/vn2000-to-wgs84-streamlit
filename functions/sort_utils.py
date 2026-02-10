import re

def sort_point_name(val):
    """
    Sort key an toàn cho cột 'Tên điểm'
    - Ưu tiên giá trị có số
    - So theo số tăng dần
    - Sau đó mới tới chữ
    """
    s = str(val).strip()
    m = re.search(r"\d+", s)
    if m:
        return (0, int(m.group()))
    return (1, s.lower())
