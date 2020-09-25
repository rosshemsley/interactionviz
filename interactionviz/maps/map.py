from scipy.spatial import Delaunay
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

import numpy as np


class WayKind(Enum):
    SolidLine = 1
    ThickLine = 2
    DashedLine = 3
    GuardRail = 4
    CurbStone = 5
    Virtual = 6
    PedestrianMarking = 7
    TrafficSign = 8
    StopLine = 9
    RoadBorder = 10


@dataclass
class Node:
    osm_id: str
    position: np.ndarray


@dataclass
class Way:
    osm_id: str
    nodes: List
    kind: WayKind


@dataclass
class Lane:
    osm_id: str
    left_way: Way
    right_way: Way

    def to_triangles(self):
        """
        triangulate the lane so it can easily be rendered.

        Note(Ross): We do this by computing the Delaunay triangulation,
        and then keeping all triangles that contain two points from one boundary,
        and one point from the other.
        """
        left_ps = [n.position for n in self.left_way.nodes]
        right_ps = [n.position for n in self.right_way.nodes]

        def is_left(idx):
            return idx < len(left_ps)

        ps = left_ps + right_ps
        tri = Delaunay(ps)

        result = []
        simplices = tri.simplices
        for i in range(simplices.shape[0]):
            num_left_points = sum(is_left(idx) for idx in simplices[i])
            if num_left_points == 1 or num_left_points == 2:
                triangle = [ps[idx] for idx in simplices[i]]
                result.append(triangle)

        return result


@dataclass
class Map:
    """
    Map represents the data loaded from a lanelets XML file,
    as represented in the interactions dataset.
    """

    ways: Dict[str, Way]
    nodes: Dict[str, Node]
    lanes: Dict[str, Lane]
