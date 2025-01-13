import asyncio
import itertools
import random

import nest_asyncio
import numpy as np
from shapely.affinity import translate
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

from kmService import KmLintMeasure
from kmService.km_models import KmValueObject
from kmService.km_responses import (
    KmResponse,
    ProjectionInputResponse,
    ProjectionResponse,
)
from kmService.km_service_builder import KmServiceBuilder
from kmService.uitils.shapely_geojson import (
    GeoJsonFeature,
    GeoJsonFeatureCollection,
    dumps,
)
from kmService.uitils.shapely_helpers import ShapelyTransform

nest_asyncio.apply()


class KmService:
    """
    A service class for calculating kilometers and related features.
    """

    def __init__(self):
        self._value_objects_dict: dict[str, KmValueObject] = {}

    @classmethod
    async def factory(cls):
        """
        Factory method to create an instance of KmService.

        Returns:
            KmService: An instance of KmService.
        """
        self = cls()
        km_service = await KmServiceBuilder.factory(
            "https://maps.prorail.nl/arcgis/rest/services/Referentiesysteem/FeatureServer"
        )
        self._value_objects_dict = km_service.value_objects
        return self

    async def _get_raaien_to_measure(self, point: Point) -> KmResponse:
        # in some cases we can have more than  one set of raaien (flyover situation)
        async def process(point_, item_):
            if point_.within(item_.geometry):
                init_response = KmLintMeasure.from_value_object(item_, point)

                # find closest 2 raaien pick lowest
                distance_raai_to_point = dict(
                    sorted(
                        {
                            raai.geometry_corrected.distance(point): raai
                            for raai in item_.km_raaien
                        }.items()
                    )
                )
                closest_two_raaien = [
                    distance_raai_to_point[k] for k in list(distance_raai_to_point)[:2]
                ]
                if closest_two_raaien[0].hectometer < closest_two_raaien[1].hectometer:
                    init_response.raai = closest_two_raaien[0].geometry_corrected
                    init_response.hm = closest_two_raaien[0].hectometer
                    return init_response
                else:
                    init_response.raai = closest_two_raaien[1].geometry_corrected
                    init_response.hm = closest_two_raaien[1].hectometer
                    return init_response

        tasks = []
        tasks.extend(
            [process(point, item) for item in self._value_objects_dict.values()]
        )
        result = await asyncio.gather(*tasks)
        return KmResponse(point, [item for item in result if item is not None])

    async def _get_km_async(self, x: float, y: float) -> KmResponse:
        point = Point(x, y)
        responses = await self._get_raaien_to_measure(point)
        for response in responses.km_measures:
            projection_point = response.raai.interpolate(response.raai.project(point))
            distance = projection_point.distance(point)
            response.distance = distance
        return responses

    def get_km(self, x: float, y: float) -> KmResponse:
        """
        Retrieves kilometer responses based on the provided coordinates.

        Args:
            x: The x-coordinate.
            y: The y-coordinate.

        Returns:
            A list of kilometer responses.
        """
        response = asyncio.run(self._get_km_async(x, y))
        return response

    async def _get_km_batch_async(self, point_list) -> list[KmResponse]:
        tasks = [self._get_km_async(point[0], point[1]) for point in point_list]
        results = await asyncio.gather(*tasks)
        return [result for result in results]

    def get_km_batch(self, point_list: list[list[int | float]]) -> list[KmResponse]:
        """
        Retrieves KM responses synchronously for a batch of points.

        Args:
            point_list: A list of lists containing the coordinates of points.

        Returns:
            A list of lists containing KM responses for each point.
        """
        response = asyncio.run(self._get_km_batch_async(point_list))
        return response

    def get_lint_names(self) -> list[str]:
        """
        Get all lint names.

        Returns:
            A list of unique lint names.
        """
        return list(
            set(
                [
                    value.km_vlak.km_lint_naam
                    for key, value in self._value_objects_dict.items()
                ]
            )
        )

    def project_point(
        self, lint_name: str, hm: float, m: int, line_geometry: LineString
    ) -> ProjectionResponse:
        """

        Get a projected point on the line.

        !!! warning "This feature is experimental and may not be suitable for production use."
            ***Api and response models will change!***
            Ensure to thoroughly test this feature with your data before deploying it.

        !!! info "Way of working"

            1. Get all raaien associated with the input lint.
            2. Find the closest raaien: the one before and after the specified kilometer measure.
            3. Calculate reference and target raai: based on the hm found before and after.
                a. if no next we use raai before and negative distance to project.
            4. Find nearest points of the reference line and the target line.
            5. Calculate movement vector from the nearest points.
            6. Move the reference line towards the target line.
            j. Calculate projected point: intersection point of the input line geometry with the moved reference line.

        Args:
            lint_name: The name of the lint.
            hm: Hectometer value to measure from.
            m: Distance in meters to measure.
            line_geometry: The geometry of the line, should match the projected kilometering line.

        Returns:
            ProjectionResponse: Response containing projected point information.
        """

        lint_raaien = list(
            itertools.chain.from_iterable(
                [
                    value.km_raaien
                    for key, value in self._value_objects_dict.items()
                    if key.endswith(lint_name)
                ]
            )
        )

        # Initialize variables to hold the objects before and after the input value
        object_before = None
        object_after = None

        # Initialize variables to hold the minimum differences
        min_difference_before = float("inf")
        min_difference_after = float("inf")

        # get raai of interest
        raai_to_project_from = [_ for _ in lint_raaien if _.hectometer == hm][0]

        # debug geojson
        reference_line = raai_to_project_from.geometry_corrected

        # Iterate through the list of objects get raai before and after...
        for obj in lint_raaien:
            difference = abs(obj.hectometer - hm)
            if obj.hectometer < hm and difference < min_difference_before:
                min_difference_before = difference
                object_before = obj
            elif obj.hectometer > hm and difference < min_difference_after:
                min_difference_after = difference
                object_after = obj

        # Determine the line to project towards
        if object_after:
            target_line = object_after.geometry_corrected
        elif object_before:
            # use before and make movement negative so offset point the right direction
            target_line = object_before.geometry_corrected
            m *= -1
        else:
            raise NotImplementedError("can not handle single raai in lint.")

        # Find the nearest points on both lines
        nearest_point_reference, nearest_point_target = nearest_points(
            reference_line, target_line
        )

        # Calculate the vector from the reference line's starting point to the nearest point on the target line
        dx_nearest = (
            nearest_point_target.coords[0][0] - nearest_point_reference.coords[0][0]
        )
        dy_nearest = (
            nearest_point_target.coords[0][1] - nearest_point_reference.coords[0][1]
        )
        unit_direction_nearest = np.array([dx_nearest, dy_nearest]) / np.linalg.norm(
            [dx_nearest, dy_nearest]
        )

        # Define the distance to move the reference line
        distance = (
            m - 0.001 if m < 0 else m + 0.001 if m > 0 else m
        )  # Adjust it a bit so it is not just under.

        # Move the reference line towards the target line
        movement_vector_nearest = unit_direction_nearest * distance
        moved_reference_line = translate(
            reference_line, movement_vector_nearest[0], movement_vector_nearest[1]
        )

        projected_point = line_geometry.intersection(moved_reference_line)
        if projected_point.is_empty:
            raise ValueError("input line geometry does not intersect the km_line")  # noqa TRY003
        return ProjectionResponse(
            input_data=ProjectionInputResponse(
                input_line=line_geometry,
                input_lint_name=lint_name,
                input_hm=hm,
                input_distance=m,
            ),
            km_line=moved_reference_line,
            km_point=projected_point,
            reference_line=reference_line,
        )

    def map_geojson_string(
        self, lint_names: list[str] | None = None, file_name: str | None = None
    ) -> str:
        """
        Generates GeoJSON output based on the data stored in KmService that can be used to plot a coverage map.

        Args:
            lint_names: A list of lint names to filter the data. If None, all data will be included.
            file_name: The name of the output file. If None, the GeoJSON string will be returned instead of writing to a file.

        Returns:
            str: A GeoJSON string representing the data.
        """

        def add_feature():
            features.append(
                GeoJsonFeature(
                    [ShapelyTransform.rd_to_wgs(value.geometry)],
                    {
                        "color": picked_color,
                        "fill-color": "transparent",
                        "fill-opacity": 0.5,
                    },
                )
            )

            for item in value.matched:
                # plot red if not matched
                if not item[1]:
                    features.append(
                        GeoJsonFeature(
                            [ShapelyTransform.rd_to_wgs(item[0].geometry)],
                            {
                                "color": "red",
                                "radius": "5px",
                                "type": "mismatched_hm_point",
                                "hm": item[0].hectometer,
                            },
                        )
                    )  # | item[0].__dict__))
                else:
                    features.append(
                        GeoJsonFeature(
                            [ShapelyTransform.rd_to_wgs(item[0].geometry)],
                            {
                                "color": picked_color,
                                "radius": "1px",
                                "type": "matched_hm_point",
                                "hm": item[0].hectometer,
                            },
                        )
                    )
                    features.append(
                        GeoJsonFeature(
                            [ShapelyTransform.rd_to_wgs(item[1].geometry)],
                            {
                                "color": "#c9c9c9",
                                "type": "matched_raai",
                                "hm": item[1].hectometer,
                            },
                        )
                    )
                    # all so plot corrected so we can see the movement
                    features.append(
                        GeoJsonFeature(
                            [ShapelyTransform.rd_to_wgs(item[1].geometry_corrected)],
                            {
                                "color": picked_color,
                                "type": "moved_raai",
                                "hm": item[1].hectometer,
                            },
                        )
                    )

        colors = [
            "#1F77B4",
            "#AEC7E8",
            "#FF7F0E",
            "#FFBB78",
            "#2CA02C",
            "#98DF8A",
            "#FF9896",
            "#9467BD",
            "#C5B0D5",
            "#8C564B",
            "#C49C94",
            "#E377C2",
            "#F7B6D2",
            "#7F7F7F",
            "#C7C7C7",
            "#BCBD22",
            "#DBDB8D",
            "#17BECF",
            "#9EDAE5",
        ]

        features: list[GeoJsonFeature] = []
        for key, value in self._value_objects_dict.items():
            picked_color = random.choice(colors)
            if lint_names is not None:
                if value.km_vlak.km_lint_naam in lint_names:
                    add_feature()
            else:
                add_feature()

        geojson_string = dumps(GeoJsonFeatureCollection(features))
        if file_name is not None:
            with open(file_name, "w") as text_file:
                text_file.write(geojson_string)
        return geojson_string


def get_km_service() -> KmService:
    """
    Retrieves an instance of KmService using asyncio.

    Returns:
        KmService: An instance of KmService.
    """
    return asyncio.run(KmService.factory())
