import logging
import http
import json
import asyncio
import websockets
import os
import math
import numpy as np

from typing import Optional
from interactionviz.maps import WayKind, Map
from interactionviz.tracks import AgentKind, Tracks, Frame, Agent
from .viewport import Viewport, viewport_for_map_no_scaling

from typing import Dict, List, Union, Any

DEFAULT_PORT = 8000

STATIC_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")

JSON = Dict[str, Any]

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


class WebViewer:
    def __init__(
        self,
        interaction_map: Map,
        tracks: Optional[Tracks] = None,
    ):
        logging.warn("This feature is a very early preview, YMMV")
        self.map = interaction_map
        self.tracks = tracks
        self.viewport = viewport_for_map_no_scaling(
            interaction_map=interaction_map,
        )
        self._track_index = 0
        self._cached_background = None

    def run(self):
        start_server = websockets.serve(
            self._socket_server,
            "localhost",
            DEFAULT_PORT,
            process_request=self._serve_static,
        )
        logging.info(f"Starting server at localhost:{DEFAULT_PORT}...")
        print(
            f"Open http://localhost:{DEFAULT_PORT}/viewer in your browser to see the viewer"
        )
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def _serve_static(self, path, headers):
        if path == "/":
            return None
        if path == "/viewer" or path == "/viewer/":
            local_file = os.path.join(STATIC_DIR, "index.html")
        else:
            local_file = os.path.join(STATIC_DIR, path[1:])

        if os.path.exists(local_file):
            with open(local_file, "rb") as infile:
                import mimetypes

                content_type = mimetypes.guess_type(local_file)
                return (
                    http.HTTPStatus.OK,
                    {"Content-type": content_type[0]},
                    bytes(infile.read()),
                )

    async def _socket_server(self, websocket, path):
        map_data = _serialize_map(self.viewport, self.map)
        await websocket.send(json.dumps(map_data))

        while True:
            request = json.loads(await websocket.recv())

            if "action" in request and request["action"] == "request_frame":
                idx = request["index"]
                response = dict(
                    action="frame",
                    payload=dict(
                        current_index=idx,
                        max_index=len(self.tracks),
                        agents=_serialize_agents(self.viewport, self.tracks[idx]),
                    )
                )

                await websocket.send(json.dumps(response))


def _serialize_agents(viewport: Viewport, frame: Frame) -> JSON:
    return [
        _serialize_car_agent(viewport, a)
        for a in frame.agents
        if a.kind is AgentKind.CAR
    ]


def _serialize_car_agent(viewport: Viewport, agent: Agent):
    return dict(
        track_id=agent.track_id,
        position=viewport.project([agent.position])[0].tolist(),
        extent=agent.extent.tolist(),
        yaw=agent.yaw,
        color=AGENT_COLORS[hash(agent.track_id) % len(AGENT_COLORS)],
    )


def _serialize_map(viewport: Viewport, interaction_map: Map) -> JSON:
    triangulated_lanes = []

    for osm_id, lane in interaction_map.lanes.items():
        lane_triangles = []
        triangles = lane.to_triangles()
        for triangle in triangles:
            lane_triangles.append([p.tolist() for p in viewport.project(triangle)])
        triangulated_lanes.append(lane_triangles)

    return dict(
        action="map_data",
        payload=dict(
            triangulated_lanes=triangulated_lanes,
            ways=_serialize_ways(viewport, interaction_map),
        ),
    )


def _serialize_ways(viewport: Viewport, interaction_map: Map) -> JSON:
    return [
        dict(
            points=[
                p.tolist()
                for p in viewport.project([node.position for node in way.nodes])
            ],
            kind=way.kind.name,
        )
        for way in interaction_map.ways.values()
    ]
