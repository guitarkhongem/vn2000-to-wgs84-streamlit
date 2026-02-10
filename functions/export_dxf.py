import ezdxf

def export_to_dxf(points, filename, cross_size=1.0):
    """
    points: list[(name, X, Y)]
    cross_size: kích thước dấu +
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for name, x, y in points:
        # ---- Vẽ dấu cộng (+) ----
        msp.add_line(
            (x - cross_size, y),
            (x + cross_size, y),
        )
        msp.add_line(
            (x, y - cross_size),
            (x, y + cross_size),
        )

        # ---- Ghi tên điểm ----
        msp.add_text(
            str(name),
            dxfattribs={
                "height": cross_size * 1.2,
                "insert": (x + cross_size * 1.5, y + cross_size * 1.5),
            }
        )

    doc.saveas(filename)
