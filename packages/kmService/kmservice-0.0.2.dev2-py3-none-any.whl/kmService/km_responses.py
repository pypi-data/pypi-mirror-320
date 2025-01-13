import json
import math
from dataclasses import dataclass, field

import numpy as np
from shapely import LineString, Point

from kmService.km_models import KmValueObject
from kmService.uitils.shapely_geojson import (
    GeoJsonFeature,
    GeoJsonFeatureCollection,
    dumps,
)
from kmService.uitils.shapely_helpers import ShapelyTransform
from kmService.wkt_helpers import remove_z_from_wkt, wkt_to_gml_coordinates


@dataclass
class GeoCodeResponse:
    """
    Represents geographical code response.

    Attributes:
        number: The geographical number.
        sub_code: The geographical sub-code.
        name: The geographical name.
    """

    number: int = -9999
    sub_code: str = ""
    name: str = ""


def km_string_helper(
    hm: float, distance: float, km_lint_name: str | None = None
) -> str:
    if distance:
        distance = math.floor(distance)
        if distance > 100:
            return f"km {hm:.3f} +{distance} {f'({km_lint_name})' if km_lint_name else ''})"
        else:
            if distance < 10:
                return f"km {hm:.1f}0{distance} ({km_lint_name})"
            else:
                return f"km {hm:.1f}{distance} ({km_lint_name})"
    else:
        return "no km"


@dataclass
class KmLintResponse:
    """
    Represents kilometer lint response.

    Attributes:
        name: The kilometer lint name.
        description: The description of the kilometer lint.
    """

    puic: str = ""
    name: str = ""
    description: str = ""
    km_from: float = np.nan
    km_to: float = np.nan
    measure_points: list[float] = field(default_factory=list)
    hm_values: list[float] = field(default_factory=list)
    raai_wkt: str = ""


@dataclass
class KmLintMeasure:
    """
    Represents a kilometer lint measure.

    Attributes:
        input_point (Point): The input point.
        hm (float): The hm value.
        distance (float): The distance.
        km_lint (KmLintResponse): The kilometer lint response.
        geocode (GeoCodeResponse): The geocode response.
        raai (LineString): The raai value.
    """

    input_point: Point = field(default_factory=Point)
    hm: float = float("nan")
    distance: float = float("nan")
    km_lint: KmLintResponse = field(default_factory=KmLintResponse)
    geocode: GeoCodeResponse = field(default_factory=GeoCodeResponse)
    raai: LineString = LineString()

    @classmethod
    def from_value_object(
        cls, km_value_object: KmValueObject, input_point: Point
    ) -> "KmLintMeasure":
        self = cls()
        self.input_point = input_point

        self.km_lint = KmLintResponse(
            km_value_object.km_lint.puic,
            km_value_object.km_lint.km_lint_name,
            km_value_object.km_lint.km_lint_description,
            km_value_object.km_lint.km_from,
            km_value_object.km_lint.km_to,
            km_value_object.km_lint.measure_points,
            km_value_object.km_lint.hm_values,
            km_value_object.km_lint.geometry.wkt,
        )
        self.geocode = GeoCodeResponse(
            int(km_value_object.sub_geocode.geo_code),
            km_value_object.sub_geocode.sub_code,
            km_value_object.sub_geocode.naam,
        )
        return self

    @property
    def display(self) -> str:
        """
        Computes the kilometer value string.
        """
        return km_string_helper(self.hm, self.distance, self.km_lint.name)

    def get_geojson_features(
        self, add_raai: bool = True, add_geocode: bool = True
    ) -> list[GeoJsonFeature]:
        # """
        # Gets the GeoJSON features.
        #
        # Returns:
        #     The list of GeoJSON features.
        # """
        geocode_dict = {}
        if add_geocode:
            geocode_dict = {
                "geocode_number": self.geocode.number
                if self.geocode is not None
                else None,
                "sub_geocode": self.geocode.sub_code
                if self.geocode is not None
                else None,
                "geocode_name": self.geocode.name if self.geocode is not None else None,
            }

        features = [
            # todo: make point on line and create line between input
            GeoJsonFeature(
                [ShapelyTransform.rd_to_wgs(self.input_point)],
                {
                    "km_value": self.display,
                    "hm": self.hm,
                    "distance": self.distance,
                    "km_lint_name": self.km_lint.name,
                    "km_lint_description": self.km_lint.description,
                }
                | geocode_dict,
            ),
        ]

        if add_raai:
            features.append(
                GeoJsonFeature(
                    [ShapelyTransform.rd_to_wgs(self.raai)],
                    {"type": "raai", "hm": self.hm},
                )
            )

        return features

    def get_geojson_feature_collection(self) -> GeoJsonFeatureCollection:
        """
        Retrieve a GeoJSON FeatureCollection object.

        Returns:
            A collection of GeoJSON features.
        """
        return GeoJsonFeatureCollection(self.get_geojson_features())

    def geojson_string(self) -> str:
        """
        Gets the GeoJSON string representation.

        Returns:
            The GeoJSON string.
        """
        return dumps(self.get_geojson_feature_collection(), indent=4)

    def as_json_serializable(self):
        """Converts KmLintMeasure instance to a JSON serializable dictionary."""
        return {
            "km_value": self.display,
            "input_point_wkt": self.input_point.wkt,
            "hm": self.hm,
            "distance": self.distance,
            "km_lint": self.km_lint.__dict__,
            "geocode": self.geocode.__dict__ if self.geocode is not None else None,
            "raai_geometry_wkt": self.raai.wkt if self.raai is not None else None,
        }


@dataclass
class KmResponse:
    """
    Represents a response containing kilometer measures.

    Attributes:
        input_point (Point): The input point associated with the response.
        km_measures (List[KmLintMeasure]): A list of kilometer measures.
    """

    input_point: Point = Point()
    km_measures: list[KmLintMeasure] = field(default_factory=list)

    @property
    def has_km_measure(self) -> bool:
        """
        Check if the response contains at least one kilometer measure.
        """
        if len(self.km_measures) != 0:
            return True
        return False

    @property
    def multiple_km_measure(self) -> bool:
        """
        Check if the response contains multiple kilometer measures.
        """
        if len(self.km_measures) != 1:
            return True
        return False

    @property
    def display(self) -> str:
        """
        Computes the kilometer value string, if multiple response returns one string separated by a ', '.
        """
        if self.multiple_km_measure:
            return ", ".join(
                [
                    km_string_helper(_.hm, _.distance, _.km_lint.name)
                    for _ in self.km_measures
                ]
            )

        return [
            km_string_helper(_.hm, _.distance, _.km_lint.name) for _ in self.km_measures
        ][0]

    def get_geojson_features(
        self, add_raai: bool = True, add_geocode: bool = True
    ) -> list[GeoJsonFeature]:
        # """
        # Generate a list of GeoJSON features from the kilometer measures.
        #
        # Returns:
        #     A list of GeoJSON features representing the kilometer measures.
        # """
        geojson_features = []
        for item in self.km_measures:
            geojson_features.extend(item.get_geojson_features(add_raai, add_geocode))
        return geojson_features

    def get_geojson_feature_collection(
        self, add_raai: bool = True, add_geocode: bool = True
    ) -> GeoJsonFeatureCollection:
        """
        Retrieve a GeoJSON FeatureCollection object.

        Returns:
            A collection of GeoJSON features.
        """
        return GeoJsonFeatureCollection(
            self.get_geojson_features(add_raai, add_geocode)
        )

    def geojson_string(self, add_raai: bool = True, add_geocode: bool = True) -> str:
        """
        Generate GeoJSON string representation of the response.

        Returns:
            GeoJSON string representing the kilometer measures.
        """
        return dumps(
            self.get_geojson_feature_collection(add_raai, add_geocode), indent=4
        )

    def geojson_dict(self, add_raai: bool = True, add_geocode: bool = True) -> dict:
        """
        Generate GeoJSON dict representation of the response.

        Returns:
            GeoJSON dict representing the kilometer measures.
        """
        return json.loads(
            dumps(self.get_geojson_feature_collection(add_raai, add_geocode), indent=4)
        )

    def as_json_serializable(self) -> dict:
        """Converts KmResponse instance to a JSON serializable dictionary."""
        return {
            "input_point_wkt": self.input_point.wkt,
            "km_value": self.display,
            "km_measures": [
                measure.as_json_serializable() for measure in self.km_measures
            ],
        }

    def imx_kilometer_ribbons(self) -> str:
        """
        Generate XML string representation of kilometer ribbons, supports multiple results on newline.

        Returns:
            XML string describing the kilometer ribbons.
        """
        return "\n".join(
            [
                f"""<KilometerRibbon puic="{item.km_lint.puic}" name="{item.km_lint.name}" kmFrom="{item.km_lint.km_from}" kmTo="{item.km_lint.km_to}" description="{item.km_lint.description}">
        <!--KmRibbon added by kmService open-imx.nl, see docs for the accuracy disclaimer-->
        <Metadata originType="Unknown" source="open-imx.nl" lifeCycleStatus="Unknown" isInService="Unknown"/>
        <Location>
            <GeographicLocation dataAcquisitionMethod="Unknown">
                <gml:LineString srsName="EPSG:28992">
                    <gml:coordinates>{wkt_to_gml_coordinates(remove_z_from_wkt(item.km_lint.raai_wkt))}</gml:coordinates>
                </gml:LineString>
            </GeographicLocation>
        </Location>
        <Measures>{" ".join(f"{num:.8f}" for num in item.km_lint.measure_points)}</Measures>
    </KilometerRibbon>"""
                for item in self.km_measures
            ]
        )

    def imx_ribbon_locations(self) -> str:
        """
        Generate XML string for ribbon locations, supports multiple results on newline.

        Returns:
            XML string describing ribbon locations.
        """
        return "\n".join(
            [
                f"<!--KmValue km {item.display} added by kmService open-imx.nl, see docs for the accuracy disclaimer-->\n"
                f'<KmRibbonLocation kmRibbonRef="{item.km_lint.puic}" value="{int(item.hm * 1000 + item.distance)}"/>'
                for item in self.km_measures
            ]
        )


@dataclass
class ProjectionInputResponse:
    """
    Represents the input response for a point.

    !!! warning "This feature is experimental and may not be suitable for production use."
        ***Api and response models will change!***
        Ensure to thoroughly test this feature with your data before deploying it.

    Args:
        input_line: The input line.
        input_lint_name: The input line name.
        input_hm: The input kilometers.
        input_distance: The input distance.

    """

    input_line: LineString
    input_lint_name: str
    input_hm: float
    input_distance: float


@dataclass
class ProjectionResponse:
    """
    Represents the response for a point.

    !!! warning "This feature is experimental and may not be suitable for production use."
        ***Api and response models will change!***
        Ensure to thoroughly test this feature with your data before deploying it.

    Args:
        input_data: The input data for the response.
        km_point: The projected kilometering point.
        km_line: The kilometering line (offset on distance of input raai).
        reference_line: The reference line, optional.
    """

    input_data: ProjectionInputResponse
    km_line: LineString
    km_point: Point
    reference_line: LineString | None = None

    def get_geojson_features(self) -> list[GeoJsonFeature]:
        features = [
            GeoJsonFeature(
                [ShapelyTransform.rd_to_wgs(self.input_data.input_line)],
                {"type": "input_line_geometry", "input_data": self.input_data.__dict__},
            ),
            GeoJsonFeature(
                [ShapelyTransform.rd_to_wgs(self.km_line)],
                {
                    "type": "km_line",
                    "km": self.input_data.input_hm,
                    "lint": self.input_data.input_lint_name,
                },
            ),
            GeoJsonFeature(
                [ShapelyTransform.rd_to_wgs(self.km_point)], {"type": "projected_point"}
            ),
        ]
        if self.reference_line:
            features.append(
                GeoJsonFeature(
                    [ShapelyTransform.rd_to_wgs(self.reference_line)],
                    {"type": "raai", "km": self.input_data.input_hm},
                )
            )
        return features

    def get_geojson_feature_collection(self) -> GeoJsonFeatureCollection:
        """
        Retrieve a GeoJSON FeatureCollection object.

        Returns:
            A collection of GeoJSON features.
        """
        return GeoJsonFeatureCollection(self.get_geojson_features())

    def geojson_string(self) -> str:
        """
        Converts the response to GeoJSON format.

        Returns:
            The GeoJSON representation of the response.
        """
        return dumps(self.get_geojson_feature_collection(), indent=4)
