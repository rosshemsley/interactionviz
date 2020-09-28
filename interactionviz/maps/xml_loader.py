import xml.etree
from typing import IO, Union
import pathlib

import numpy as np

from .map import Map, Way, WayKind, Node, Lane


def load_map_xml(infile: Union[pathlib.Path, IO]) -> Map:
    tree = xml.etree.ElementTree.parse(infile)
    root = tree.getroot()

    nodes = {}
    ways = {}
    lanes = {}

    for child in root:
        if child.tag == "relation":
            osm_id = child.attrib["id"]
            left_way_id, right_way_id = None, None
            tags = {}

            for e in child:
                if e.tag == "tag":
                    tags[e.attrib["k"]] = e.attrib["v"]

                if e.tag == "member" and e.attrib.get("role") == "left":
                    left_way_id = e.attrib.get("ref")
                if e.tag == "member" and e.attrib.get("role") == "right":
                    right_way_id = e.attrib.get("ref")

            if tags.get("type") == "lanelet":
                lanes[osm_id] = Lane(
                    osm_id=osm_id,
                    left_way=ways[left_way_id],
                    right_way=ways[right_way_id],
                )

        elif child.tag == "node":
            osm_id = child.attrib["id"]
            nodes[osm_id] = Node(
                osm_id=osm_id,
                position=np.array(
                    [
                        float(child.attrib["x"]),
                        float(child.attrib["y"]),
                    ]
                ),
            )
        elif child.tag == "way":
            way_id = child.attrib["id"]
            way_nodes = []
            tags = {}
            for n in child:
                if n.tag == "tag":
                    tags[n.attrib["k"]] = n.attrib["v"]
                elif n.tag == "nd":
                    way_nodes.append(nodes[n.attrib["ref"]])

            way_type = tags.get("type")
            way_sub_type = tags.get("subtype")

            way_kind = None
            if way_type == "road_border":
                way_kind = WayKind.RoadBorder
            elif way_type == "stop_line":
                way_kind = WayKind.StopLine
            elif way_type == "guard_rail":
                way_kind = WayKind.GuardRail
            elif way_type == "line_thin":
                if way_sub_type == "dashed":
                    way_kind = WayKind.DashedLine
                elif way_sub_type in {"solid", "solid_solid"}:
                    way_kind = WayKind.SolidLine
                else:
                    raise ValueError(f"unknown subkind {way_sub_type}")
            elif way_type == "curbstone":
                way_kind = WayKind.CurbStone
            elif way_type == "virtual":
                way_kind = WayKind.Virtual
            elif way_type == "pedestrian_marking":
                way_kind = WayKind.PedestrianMarking
            elif way_type == "traffic_sign":
                way_kind = WayKind.TrafficSign
            elif way_type == "line_thick":
                way_kind = WayKind.ThickLine
            else:
                raise ValueError(f"unknown way type {way_type}")

            ways[way_id] = Way(osm_id=way_id, nodes=way_nodes, kind=way_kind)

    return Map(
        ways=ways,
        nodes=nodes,
        lanes=lanes,
    )
