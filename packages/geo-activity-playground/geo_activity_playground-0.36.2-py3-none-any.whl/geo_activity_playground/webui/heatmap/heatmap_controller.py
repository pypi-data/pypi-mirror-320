import datetime
import io
import logging
import pathlib
from typing import Optional

import matplotlib.pylab as pl
import numpy as np
from PIL import Image
from PIL import ImageDraw

from geo_activity_playground.core.activities import ActivityRepository
from geo_activity_playground.core.config import Config
from geo_activity_playground.core.raster_map import convert_to_grayscale
from geo_activity_playground.core.raster_map import GeoBounds
from geo_activity_playground.core.raster_map import get_sensible_zoom_level
from geo_activity_playground.core.raster_map import get_tile
from geo_activity_playground.core.raster_map import OSM_TILE_SIZE
from geo_activity_playground.core.raster_map import PixelBounds
from geo_activity_playground.core.tasks import work_tracker
from geo_activity_playground.core.tiles import get_tile_upper_left_lat_lon
from geo_activity_playground.explorer.tile_visits import TileVisitAccessor
from geo_activity_playground.webui.explorer.controller import (
    bounding_box_for_biggest_cluster,
)


logger = logging.getLogger(__name__)


class HeatmapController:
    def __init__(
        self,
        repository: ActivityRepository,
        tile_visit_accessor: TileVisitAccessor,
        config: Config,
    ) -> None:
        self._repository = repository
        self._tile_visit_accessor = tile_visit_accessor
        self._config = config

        self.tile_histories = self._tile_visit_accessor.tile_state["tile_history"]
        self.tile_evolution_states = self._tile_visit_accessor.tile_state[
            "evolution_state"
        ]
        self.tile_visits = self._tile_visit_accessor.tile_state["tile_visits"]
        self.activities_per_tile = self._tile_visit_accessor.tile_state[
            "activities_per_tile"
        ]

    def render(
        self,
        kinds: list[int],
        date_start: Optional[datetime.date],
        date_end: Optional[datetime.date],
    ) -> dict:
        zoom = 14
        tiles = self.tile_histories[zoom]
        medians = tiles.median(skipna=True)
        median_lat, median_lon = get_tile_upper_left_lat_lon(
            medians["tile_x"], medians["tile_y"], zoom
        )
        cluster_state = self.tile_evolution_states[zoom]

        available_kinds = sorted(self._repository.meta["kind"].unique())

        if not kinds:
            kinds = list(range(len(available_kinds)))

        extra_args = []
        if date_start is not None:
            extra_args.append(f"date-start={date_start.isoformat()}")
        if date_end is not None:
            extra_args.append(f"date-end={date_end.isoformat()}")
        for kind in kinds:
            extra_args.append(f"kind={kind}")

        values = {
            "center": {
                "latitude": median_lat,
                "longitude": median_lon,
                "bbox": (
                    bounding_box_for_biggest_cluster(
                        cluster_state.clusters.values(), zoom
                    )
                    if len(cluster_state.memberships) > 0
                    else {}
                ),
            },
            "kinds": kinds,
            "available_kinds": available_kinds,
            "extra_args": "&".join(extra_args),
        }
        if date_start is not None:
            values["date_start"] = date_start.date().isoformat()
        if date_end is not None:
            values["date_end"] = date_end.date().isoformat()

        return values

    def _get_counts(
        self,
        x: int,
        y: int,
        z: int,
        kind: str,
        date_start: Optional[datetime.date],
        date_end: Optional[datetime.date],
    ) -> np.ndarray:
        tile_pixels = (OSM_TILE_SIZE, OSM_TILE_SIZE)
        tile_counts = np.zeros(tile_pixels, dtype=np.int32)
        if date_start is None and date_end is None:
            tile_count_cache_path = pathlib.Path(
                f"Cache/Heatmap/{kind}/{z}/{x}/{y}.npy"
            )
            if tile_count_cache_path.exists():
                try:
                    tile_counts = np.load(tile_count_cache_path)
                except ValueError:
                    logger.warning(
                        f"Heatmap count file {tile_count_cache_path} is corrupted, deleting."
                    )
                    tile_count_cache_path.unlink()
                    tile_counts = np.zeros(tile_pixels, dtype=np.int32)
            tile_count_cache_path.parent.mkdir(parents=True, exist_ok=True)
            activity_ids = self.activities_per_tile[z].get((x, y), set())
            activity_ids_kind = set()
            for activity_id in activity_ids:
                activity = self._repository.get_activity_by_id(activity_id)
                if activity["kind"] == kind:
                    activity_ids_kind.add(activity_id)
            if activity_ids_kind:
                with work_tracker(
                    tile_count_cache_path.with_suffix(".json")
                ) as parsed_activities:
                    if parsed_activities - activity_ids_kind:
                        logger.warning(
                            f"Resetting heatmap cache for {kind=}/{x=}/{y=}/{z=} because activities have been removed."
                        )
                        tile_counts = np.zeros(tile_pixels, dtype=np.int32)
                        parsed_activities.clear()
                    for activity_id in activity_ids_kind:
                        if activity_id in parsed_activities:
                            continue
                        parsed_activities.add(activity_id)
                        time_series = self._repository.get_time_series(activity_id)
                        for _, group in time_series.groupby("segment_id"):
                            xy_pixels = (
                                np.array(
                                    [group["x"] * 2**z - x, group["y"] * 2**z - y]
                                ).T
                                * OSM_TILE_SIZE
                            )
                            im = Image.new("L", tile_pixels)
                            draw = ImageDraw.Draw(im)
                            pixels = list(map(int, xy_pixels.flatten()))
                            draw.line(pixels, fill=1, width=max(3, 6 * (z - 17)))
                            aim = np.array(im)
                            tile_counts += aim
                tmp_path = tile_count_cache_path.with_suffix(".tmp.npy")
                np.save(tmp_path, tile_counts)
                tile_count_cache_path.unlink(missing_ok=True)
                tmp_path.rename(tile_count_cache_path)
        else:
            activity_ids = self.activities_per_tile[z].get((x, y), set())
            for activity_id in activity_ids:
                activity = self._repository.get_activity_by_id(activity_id)
                if not activity["kind"] == kind:
                    continue
                if date_start is not None and activity["start"] < date_start:
                    continue
                if date_end is not None and date_end < activity["start"]:
                    continue
                time_series = self._repository.get_time_series(activity_id)
                for _, group in time_series.groupby("segment_id"):
                    xy_pixels = (
                        np.array([group["x"] * 2**z - x, group["y"] * 2**z - y]).T
                        * OSM_TILE_SIZE
                    )
                    im = Image.new("L", tile_pixels)
                    draw = ImageDraw.Draw(im)
                    pixels = list(map(int, xy_pixels.flatten()))
                    draw.line(pixels, fill=1, width=max(3, 6 * (z - 17)))
                    aim = np.array(im)
                    tile_counts += aim
        return tile_counts

    def _render_tile_image(
        self,
        x: int,
        y: int,
        z: int,
        kinds_ids: list[int],
        date_start: Optional[datetime.date],
        date_end: Optional[datetime.date],
    ) -> np.ndarray:
        tile_pixels = (OSM_TILE_SIZE, OSM_TILE_SIZE)
        tile_counts = np.zeros(tile_pixels)
        available_kinds = sorted(self._repository.meta["kind"].unique())
        for kind_id in kinds_ids:
            kind = available_kinds[kind_id]
            tile_counts += self._get_counts(x, y, z, kind, date_start, date_end)

        tile_counts = np.sqrt(tile_counts) / 5
        tile_counts[tile_counts > 1.0] = 1.0

        cmap = pl.get_cmap(self._config.color_scheme_for_heatmap)
        data_color = cmap(tile_counts)
        data_color[data_color == cmap(0.0)] = 0.0  # remove background color

        map_tile = np.array(get_tile(z, x, y, self._config.map_tile_url)) / 255
        map_tile = convert_to_grayscale(map_tile)
        map_tile = 1.0 - map_tile  # invert colors
        for c in range(3):
            map_tile[:, :, c] = (1.0 - data_color[:, :, c]) * map_tile[
                :, :, c
            ] + data_color[:, :, c]
        return map_tile

    def render_tile(
        self,
        x: int,
        y: int,
        z: int,
        kind_ids: list[int],
        date_start: Optional[datetime.date],
        date_end: Optional[datetime.date],
    ) -> bytes:
        f = io.BytesIO()
        pl.imsave(
            f,
            self._render_tile_image(x, y, z, kind_ids, date_start, date_end),
            format="png",
        )
        return bytes(f.getbuffer())

    def download_heatmap(
        self,
        north: float,
        east: float,
        south: float,
        west: float,
        kind_ids: list[int],
        date_start: Optional[datetime.date],
        date_end: Optional[datetime.date],
    ) -> bytes:
        geo_bounds = GeoBounds(south, west, north, east)
        tile_bounds = get_sensible_zoom_level(geo_bounds, (4000, 4000))
        pixel_bounds = PixelBounds.from_tile_bounds(tile_bounds)

        background = np.zeros((*pixel_bounds.shape, 3))
        for x in range(tile_bounds.x1, tile_bounds.x2):
            for y in range(tile_bounds.y1, tile_bounds.y2):
                tile = (
                    np.array(
                        get_tile(tile_bounds.zoom, x, y, self._config.map_tile_url)
                    )
                    / 255
                )

                i = y - tile_bounds.y1
                j = x - tile_bounds.x1

                background[
                    i * OSM_TILE_SIZE : (i + 1) * OSM_TILE_SIZE,
                    j * OSM_TILE_SIZE : (j + 1) * OSM_TILE_SIZE,
                    :,
                ] = self._render_tile_image(
                    x, y, tile_bounds.zoom, kind_ids, date_start, date_end
                )

        f = io.BytesIO()
        pl.imsave(f, background, format="png")
        return bytes(f.getbuffer())
