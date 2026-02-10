import ezdxf


def export_to_dxf(points, filepath):
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
        Xcad = y   # ĐẢO Ở ĐÂY
        Ycad = x

        # Vẽ điểm
        msp.add_point(
            (Xcad, Ycad),
            dxfattribs={"layer": "POINTS"}
        )

        # Ghi tên điểm
        txt = msp.add_text(
            str(name),
            dxfattribs={
                "height": 1.2,
                "layer": "TEXT"
            }
        )
        txt.dxf.insert = (Xcad + 1.0, Ycad + 1.0)

    doc.saveas(filepath)
