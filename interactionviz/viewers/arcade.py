import os
import arcade
import math
import numpy as np

from typing import Optional
from interactionviz.maps import WayKind, Map
from interactionviz.tracks import AgentKind, Tracks, Frame
from .viewport import Viewport, viewport_for_map

AGENT_COLORS = [
    (161, 201, 244),
    (255, 180, 130),
    (141, 229, 161),
    (255, 159, 155),
    (208, 187, 255),
    (222, 187, 155),
    (250, 176, 228),
    (207, 207, 207),
    (255, 254, 163),
    (185, 242, 240),
]
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_FRAMERATE = 1 / 10


class ArcadeViewer:
    def __init__(
        self,
        interaction_map: Map,
        tracks: Optional[Tracks] = None,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
    ):
        self.map = interaction_map
        self.tracks = tracks
        self.width = width
        self.height = height
        self.viewport = viewport_for_map(
            screen_width=width,
            screen_height=height,
            interaction_map=interaction_map,
        )
        self._track_index = 0
        self._cached_background = None

    def run(self):
        arcade.open_window(self.width, self.height, "Interaction Viz")

        def closure(dt):
            self._draw()

        arcade.schedule(closure, DEFAULT_FRAMERATE)
        arcade.run()

    def _draw(self):
        arcade.start_render()
        if self._cached_background is None:
            _render_background(self.width, self.height)
            _render_map(self.viewport, self.map)

            self._cached_background = arcade.Texture(
                "bg", arcade.get_image(), hit_box_algorithm="None"
            )

        arcade.draw_lrwh_rectangle_textured(
            0, 0, self.width, self.height, self._cached_background
        )

        if self.tracks is not None and self._track_index < len(self.tracks):
            frame = self.tracks[self._track_index]
            _render_obstacles(self.viewport, frame)
            self._track_index += 1


def _render_map(viewport: Viewport, interaction_map: Map) -> None:
    to_draw = {
        WayKind.SolidLine,
        WayKind.ThickLine,
        WayKind.DashedLine,
        WayKind.GuardRail,
    }

    for osm_id, lane in interaction_map.lanes.items():
        triangles = lane.to_triangles()
        for triangle in triangles:
            triangle = viewport.project(triangle)
            arcade.draw_polygon_filled(triangle, (140, 140, 140))

    for osm_id, way in interaction_map.ways.items():
        if way.kind is WayKind.StopLine:
            ps = viewport.project(
                [interaction_map.nodes[n.osm_id].position for n in way.nodes]
            )
            arcade.draw_line_strip(ps, arcade.color.AMBER, 5)

    for osm_id, lane in interaction_map.lanes.items():
        left_ps = [n.position for n in lane.left_way.nodes]
        right_ps = [n.position for n in lane.right_way.nodes]

        left_ps = viewport.project(left_ps)
        right_ps = viewport.project(right_ps)

        if lane.left_way.kind is not WayKind.Virtual:
            thickness = 1.5
            if lane.left_way.kind is WayKind.ThickLine:
                thickness = 2
            arcade.draw_line_strip(left_ps, (240, 240, 240), thickness)

        if lane.right_way.kind is not WayKind.Virtual:
            thickness = 1.5
            if lane.right_way.kind is WayKind.ThickLine:
                thickness = 2
            elif lane.right_way.kind is WayKind.DashedLine:
                thickness = 2
            arcade.draw_line_strip(right_ps, (240, 240, 240), thickness)


def _render_background(width: int, height: int) -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    grass = os.path.join(dir_path, "static", "grass.png")
    background = arcade.load_texture(grass)

    for i in range(0, width, 32):
        for j in range(0, height, 32):
            arcade.draw_lrwh_rectangle_textured(i, j, 32, 32, background)


def _render_obstacles(viewport: Viewport, frame: Frame) -> None:
    for agent in frame.agents:
        # color = AGENT_COLORS[agent.track_id % len(AGENT_COLORS)]
        color = AGENT_COLORS[hash(agent.track_id) % len(AGENT_COLORS)]
        position = agent.position

        if agent.extent is not None and agent.yaw is not None:
            half_extent = 0.5 * agent.extent
            sin_theta = math.sin(agent.yaw)
            cos_theta = math.cos(agent.yaw)
            rot = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
            offsets = [
                half_extent * np.array([1, 1]),
                half_extent * np.array([1.2, 0]),
                half_extent * np.array([1, 1]),
                half_extent * np.array([1, -1]),
                half_extent * np.array([-1, -1]),
                half_extent * np.array([-1, 1]),
            ]
            ps = [position + rot.dot(o) for o in offsets]
            ps = viewport.project(ps)
            arcade.draw_polygon_filled(ps, color)
        else:
            position = viewport.project([position])[0]
            arcade.draw_circle_filled(*position, 5, color=color)
