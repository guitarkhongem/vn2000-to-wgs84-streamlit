import ezdxf


def export_to_dxf(points, filepath, cross_size=0.5):
    """
    points: list of (name, x, y)
        x = Northing (BẮC)
        y = Easting  (ĐÔNG)

    DXF:
        X = Easting
        Y = Northing
    """

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Layers
    if "POINTS" not in doc.layers:
        doc.layers.new(name="POINTS", dxfattribs={"color": 1})
    if "TEXT" not in doc.layers:
        doc.layers.new(name="TEXT", dxfattribs={"color": 3})

    for name, x, y in points:
        # ✅ ĐẢO ĐÚNG THEO QUY ƯỚC CỦA BẠN
        Xcad = float(y)   # Easting
        Ycad = float(x)   # Northing

        # ===== DẤU + =====
        msp.add_line(
            (Xcad - cross_size, Ycad),
            (Xcad + cross_size, Ycad),
            dxfattribs={"layer": "POINTS"}
        )
        msp.add_line(
            (Xcad, Ycad - cross_size),
            (Xcad, Ycad + cross_size),
            dxfattribs={"layer": "POINTS"}
        )

        # ===== TÊN ĐIỂM =====
        msp.add_text(
            str(name),
            dxfattribs={
                "height": cross_size * 3,
                "layer": "TEXT",
                "insert": (Xcad + cross_size * 1.2, Ycad + cross_size * 1.2)
            }
        )

    doc.saveas(filepath)
