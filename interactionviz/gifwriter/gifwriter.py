import logging
import numpy as np
import math
from interactionviz.tracks import Tracks
from interactionviz.maps import WayKind, Map
from interactionviz.tracks import AgentKind, Tracks, Frame
from interactionviz.viewers import Viewport, viewport_for_map
from typing import IO

from PIL import Image, ImageDraw

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
BACKGROUND_COLOR = (15, 125, 45)
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600


def write_gif(
    tracks: Tracks,
    interaction_map: Map,
    fileobj: IO,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    step: int = 1):

    viewport = viewport_for_map(width, height, interaction_map)

    map_img = _render_map(viewport, interaction_map)
    imgs = [
        draw_frame(viewport, map_img, f, width, height)
        for i, f in enumerate(tracks) if i % step == 0
    ]

    imgs[0].save(fp=fileobj, format="GIF", append_images=imgs, save_all=True, duration=len(imgs), loop=1)


def draw_frame(viewport: Viewport, map_img: Image, frame: Frame, width: int, height: int) -> Image:
    img = map_img.copy()
    ctx = ImageDraw.Draw(img)
    _render_obstacles(ctx, viewport, frame)
    return img



def _render_map(viewport: Viewport, interaction_map: Map) -> Image:
    img = Image.new("RGB", (viewport.screen_width, viewport.screen_height), BACKGROUND_COLOR)
    ctx = ImageDraw.Draw(img)

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
            ctx.polygon(to_tuples(triangle), (140, 140, 140))

    for osm_id, way in interaction_map.ways.items():
        if way.kind is WayKind.StopLine:
            ps = viewport.project(
                [interaction_map.nodes[n.osm_id].position for n in way.nodes]
            )
            ctx.line(to_tuples(ps), (252, 186, 3), width=5)

    for osm_id, lane in interaction_map.lanes.items():
        left_ps = [n.position for n in lane.left_way.nodes]
        right_ps = [n.position for n in lane.right_way.nodes]

        left_ps = viewport.project(left_ps)
        right_ps = viewport.project(right_ps)

        if lane.left_way.kind is not WayKind.Virtual:
            thickness = 1.5
            if lane.left_way.kind is WayKind.ThickLine:
                thickness = 2
            ctx.line(to_tuples(left_ps), (240, 240, 240), width=int(thickness))

        if lane.right_way.kind is not WayKind.Virtual:
            thickness = 1.5
            if lane.right_way.kind is WayKind.ThickLine:
                thickness = 2
            elif lane.right_way.kind is WayKind.DashedLine:
                thickness = 2
            ctx.line(to_tuples(right_ps), (240, 240, 240), width=int(thickness))
    
    return img


def _render_obstacles(ctx, viewport: Viewport, frame: Frame) -> None:
    for agent in frame.agents:
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
            ctx.polygon(to_tuples(ps), color)
        else:
            position = viewport.project([position])[0]
            logging.warn("not implemented: rendering pedestrians to gif")


def to_tuples(ps):
    return [tuple(int(x) for x in p) for p in ps]
