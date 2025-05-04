def shoelace_area(points):
    """
    Tính diện tích đa giác từ các đỉnh (X, Y) bằng Shoelace formula sau khi dịch về trọng tâm.
    Input:
        points: List of (x, y) tuples (phải theo thứ tự chu vi đa giác)
    Output:
        Diện tích (float, đơn vị như đầu vào)
    """
    if len(points) < 3:
        return 0.0

    # Bước 1: Tìm trọng tâm
    n = len(points)
    x_c = sum(p[0] for p in points) / n
    y_c = sum(p[1] for p in points) / n

    # Bước 2: Dịch tất cả các đỉnh về gốc tọa độ bằng cách trừ trọng tâm
    shifted = [(x - x_c, y - y_c) for x, y in points]

    # Bước 3: Áp dụng công thức Shoelace
    area = 0.0
    for i in range(n):
        x0, y0 = shifted[i]
        x1, y1 = shifted[(i + 1) % n]  # vòng lại đỉnh đầu
        area += x0 * y1 - x1 * y0

    return abs(area) / 2
