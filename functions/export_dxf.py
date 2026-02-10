import ezdxf
from ezdxf.enums import TextEntityAlignment


def export_to_dxf(points, output_path, cross_size=0.5):
    """
    points: List[(name, x, y)]
    cross_size: độ dài mỗi nhánh dấu +
    """

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for name, x, y in points:
        x = float(x)
        y = float(y)

        # --- Vẽ dấu + (KHÔNG ĐẢO XY) ---
        msp.add_line(
            (x - cross_size, y),
            (x + cross_size, y)
        )
        msp.add_line(
            (x, y - cross_size),
            (x, y + cross_size)
        )

        # --- Ghi tên điểm ---
        txt = msp.add_text(
            str(name),
            dxfattribs={"height": cross_size * 1.2}
        )

        txt.set_pos(
            (x + cross_size * 1.2, y + cross_size * 1.2),
            align=TextEntityAlignment.LEFT
        )

    doc.saveas(output_path)
