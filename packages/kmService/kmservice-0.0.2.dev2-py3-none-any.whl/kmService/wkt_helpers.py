from shapely.geometry import shape
from shapely.wkt import loads


def wkt_to_gml_coordinates(wkt: str) -> str:
    geometry = loads(wkt)
    if geometry.geom_type in ["Point"]:
        coords = f"{round(geometry.x, 3)},{round(geometry.y, 3)}"
    elif geometry.geom_type in ["LineString", "Polygon"]:
        coords = " ".join(f"{round(x, 3)},{round(y, 3)}" for x, y in geometry.coords)
    elif geometry.geom_type == "MultiPolygon":
        coords = " ".join(
            " ".join(f"{round(x, 3)},{round(y, 3)}" for x, y in polygon.exterior.coords)
            for polygon in geometry.geoms
        )
    else:
        raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")  # NOQA: TRY003

    return coords


def remove_z_from_wkt(wkt: str) -> str:
    geometry = loads(wkt)
    if geometry.has_z:
        if geometry.geom_type == "Point":
            geometry_2d = geometry.__class__(*geometry.xy)
        elif geometry.geom_type in ["LineString", "Polygon"]:
            geometry_2d = geometry.__class__([coord[:2] for coord in geometry.coords])
        elif geometry.geom_type in ["MultiPolygon", "MultiLineString"]:
            geometry_2d = geometry.__class__(
                [
                    shape(
                        {
                            "type": g.geom_type,
                            "coordinates": [coord[:2] for coord in g.exterior.coords],
                        }
                    )
                    for g in geometry.geoms
                ]
            )
        else:
            raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")  # NOQA: TRY003
    else:
        geometry_2d = geometry
    return geometry_2d.wkt
