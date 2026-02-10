import ezdxf

def export_to_dxf(points, out_path, cross_size=0.5):
    """
    points: list of (name, X, Y)
    cross_size: nửa chiều dài dấu cộng (đơn vị mét)
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for name, x, y in points:
        # --- Dấu cộng (+) ---
        msp.add_line(
            (x - cross_size, y),
            (x + cross_size, y),
            dxfattribs={"layer": "POINTS"}
        )
        msp.add_line(
            (x, y - cross_size),
            (x, y + cross_size),
            dxfattribs={"layer": "POINTS"}
        )

        # --- Tên điểm ---
        msp.add_text(
            name,
            dxfattribs={
                "height": cross_size * 2,
                "layer": "LABELS"
            }
        ).set_pos((x + cross_size * 1.2, y + cross_size * 1.2))

    doc.saveas(out_path)
