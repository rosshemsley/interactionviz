from enum import Enum
from csv import DictReader
from collections import defaultdict
import os
from pathlib import Path
from typing import Dict, List, IO, Optional, Sequence
from dataclasses import dataclass

import numpy as np


class AgentKind(Enum):
    CAR = 0
    TRUCK = 1
    MOTORBIKE = 1
    BICYCLE = 2
    PEDESTRIAN = 3


@dataclass
class Agent:
    """
    Note: Pedestrians and bicycles do not have yaw or extnt.
    """

    track_id: str
    kind: AgentKind
    position: np.ndarray  # x, y
    extent: Optional[np.ndarray]  # length, width
    yaw: Optional[float]


@dataclass
class Frame:
    frame_id: int
    agents: List[Agent]


# Tracks are simply ordered lists of frames with increasing frame_ids
Tracks = Sequence[Frame]


def load_tracks_files(*trackfiles: List[Path]) -> Tracks:
    """
    Load and merge several trackfiles together.
    It is assumed that the input files share the same id space for frames.
    """
    tracks = []
    all_frame_ids = set()

    for p in trackfiles:
        with p.open() as f:
            tracks_by_frame_id = _load_tracks_csv(f)
            tracks.append(tracks_by_frame_id)
            all_frame_ids |= set(tracks_by_frame_id.keys())

    result = []
    for frame_id in sorted(all_frame_ids):
        agents = []

        for t in tracks:
            if frame_id in t:
                agents.extend(t[frame_id])

        result.append(Frame(frame_id=frame_id, agents=agents))

    return result


def _load_tracks_csv(csvfile: IO) -> Dict[int, List[Agent]]:
    agents_by_frame = defaultdict(list)

    r = DictReader(csvfile)
    for dct in r:
        frame_id = int(dct["frame_id"])

        if "length" in dct:
            extent = np.array([float(dct["length"]), float(dct["width"])])
        else:
            extent = None

        agents_by_frame[frame_id].append(
            Agent(
                kind=_kind_from_str(dct["agent_type"]),
                track_id=str(dct["track_id"]),
                position=np.array([float(dct["x"]), float(dct["y"])]),
                yaw=float(dct["psi_rad"]) if "psi_rad" in dct else None,
                extent=extent,
            )
        )

    return dict(agents_by_frame)


def _kind_from_str(agent_type: str) -> AgentKind:
    if agent_type == "car":
        return AgentKind.CAR
    elif agent_type == "pedestrian":
        return AgentKind.PEDESTRIAN
    elif agent_type == "pedestrian/bicycle":
        return AgentKind.BICYCLE
    else:
        raise ValueError(f"unknown agent type: {agent_type}")
