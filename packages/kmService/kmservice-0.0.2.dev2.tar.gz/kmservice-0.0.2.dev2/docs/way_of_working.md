# Kilometer Service

## Determining Kilometer Value
We primary use **RVT method**, all geometry are handled with shapely.

### Data source
- The kilometer service relies on GIS data supplied by ProRail, accessible through [Referentiesysteem_004](https://mapservices.prorail.nl/arcgis/rest/services/Referentiesysteem_004/FeatureServer) the following feature layers are used:
    - Kilometerlintvlak
    - Hectometerpunt (geocode)
    - Geocodesubgebied

### Data processing
- It scrapes all features layers from the feature service in memory.
- We do some post processing on the raai feature:
    - extended the line and will be trimmed on polygons of the km vlak. This ensures that a raai stretch belong to the corresponding area.
    - Some raaien do not align perfectly with the hectometer points. We adjust the raai so that it aligns with the hectometer point. This ensures consistency across the data sources.
- On some locations a hm point does not have a raai, we need to add the raai manualy. (this is still a todo/ future feature)

## Geocodes and kilometer lint
The geocode is assigned to an area surrounding the railway, indicating (a segment of) an open track or a railway station/yard and are used for location determination.

The "kilometerlint" (kilometer 'ribbon') encompasses a significantly larger expanse, frequently spanning extensive lengths of railway tracks, thereby traversing numerous stations and lines along the way.


??? example
    For example, the ribbon from Harlingen Haven to Nieuweschans spans from Harlingen through geocode 001, then traverses through the station Leeuwarden (geocode 550), continues via geocode 002 to Groningen (geocode 501), and further towards the German border travering some more geocodes."


The "km lint" system provides a structured framework for distance measurement and location referencing.
Below, we elucidate the fundamental components of this referencing system:

- **Kilometer Lint:** The line that delineates the central axis of all railway tracks within the kilometerlint, serving as a universal representation of their trajectory on a global scale.
- **HM Points:** The kilometer lint is subdivided into hectometer points, with each hectometer representing 100 meters. In certain instances, such as curves, the distance between two hectometer points may vary from 100 meters. These points serve as calibration markers for the line.
- **Raaien:** Small lines perpendicular to the kilometer lint at regular intervals, corresponding to hectometer points. These markers act as visual cues on maps, aiding in the precise identification of their position along the track. This us used on 1:1000 maps (before the computer era).

> ![geocode, kmlint raai and points](km_lin_raai_geocode.png)
> Map of reference features: <span style="color:blue">km lint in blue</span>, <span style="color:green">km polygon in green</span>, <span style="color:purple">geocode in purple</span>, the massive green dot indicates the connection point of two kilometer linten. Source ProRail GIS feature service.

!!! info
    - Essentially, hectometers in the reference system represent 100 meters, but deviations are frequently encountered. These deviations may arise from expansions in the rail network or from realigning a curve. In such instances, the start and end kilometering remain unchanged, and any differences are addressed by stretching or compressing the kilometering at the site.
    - Through the use of hectometer raaien, kilometering from geocodes and/or kilometerlint can be depicted on drawings. Hectometer raaien are exclusively suitable for this purpose. They are manually drawn, taking into consideration the alignment of the track. Hectometer raaien intersect the track as minimally as possible and are not directly linked to the hectometer points of the railway centerline. As a result, there may be a slight deviation from the actual kilometering.

### Reference system

Traditionally, geocodes along with kilometering are used to pinpoint the location of objects along the Dutch railway network.

!!! example
    The combination 808/101.140 for geocode/kilometer signifies the precise location of an object along the tracks. Here, [808](https://en.wikipedia.org/wiki/Roland_TR-808) designates the area, in this instance 'VAM-terrein Wijster', while 101.140 denotes the specific location along the kilometerlint.

Using the geocodes and kilometer ribbon data, non-overlapping polygons are generated, except for instances at track intersection structures such as flyovers.
Objects falling within a polygon are attributed to the associated ribbon, enabling correlation with the kilometer ribbon and distance measurement along it.

!!! info
    The example provided could also be denoted as "VAM Aansl. – VAM - terrein Wijster km 101.140". However, using the full name of the kilometer ribbon can be bulky. To streamline this, we utilize the abbreviation, resulting in "Vama-Vam 101.140".

The geocode and kilometerlint information is organized and provided through a GIS dataset: ***```Referentiesysteem```***. This dataset is utilized for various purposes, including the management and upkeep of railway lines.

!!! warning
    While this system provides a level of accuracy, it inherently carries a margin of error and **cannot be relied upon for measuring distances along paths, especially for safety purposes**


## Determining Kilometer Value
The kilometer value of an object belonging to a stretch can be determined in two ways:

- Linear Referencing Method
- RVT Method

Each method has its own advantages and disadvantages.

### Linear Referencing Method
[Linear Referencing](https://en.wikipedia.org/wiki/Linear_referencing) is a GIS method for objects projection along a line. The distance along this line corresponds to the kilometer value.

!!! info
    it's important to note that this approach deviates from the standard for km values on the OBE drawings!

Objects are assigned kilometering based on a projection perpendicular from the railway centerline. In most cases, this method yields precise results.
However, deviations occur in certain instances, such as curves and areas where railway tracks are wide. In the example below, both scenarios apply.
The actual distance between the provided coordinates (green points) is 40.59 meters. However, when calculating the distance based on values derived from the railway centerline (red numbers), the length is 56.14 meters.
>![linear_referenceing_projection](linear_referenceing_projection.png)
> Projection of provided coordinates of a switch onto the kilometering of the railway centerline.


### RVT Method

todo: Explain where it's used for

- Begin by examining the adjacent km raaien between the object and choose the raai with the lowest hectometer value.
- Extend the raai to cover a larger area so we can measure perpendicular distance from the raai to the object.
- In some cases we have more than 100 meters between 2 raaien, sur-plus meters are represented as ```hectometer + xxx meters``` (e.g., 98.000 +105m). This notation clarifies that the measurement should commence from a hectometer point.

!!! Danger
    **This method reduces significant errors, but it still lacks precision, making it advisable to avoid using it for calculating critical lengths. In this case we should measure the distance over the track layout.**

