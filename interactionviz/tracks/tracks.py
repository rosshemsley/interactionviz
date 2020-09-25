from csv import DictReader
from collections import defaultdict
import os
from typing import List, IO
from dataclasses import dataclass

import numpy as np


@dataclass
class Agent:
    track_id: int
    position: np.ndarray  # x, y
    extent: np.ndarray  # length, width
    yaw: float


@dataclass
class Frame:
    agents: List[Agent]


class Tracks:
    def __init__(self, trackfile_dir):
        self.trackfile_dir = trackfile_dir

        first_vehicles_file = os.path.join(self.trackfile_dir, "vehicle_tracks_000.csv")
        with open(first_vehicles_file) as f:
            self.tracks = _load_tracks_csv(f)

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, idx):
        return self.tracks[idx]


def _load_tracks_csv(csvfile: IO):
    agents_by_frame = defaultdict(list)

    r = DictReader(csvfile)
    for dct in r:
        frame_id = int(dct["frame_id"])

        agents_by_frame[frame_id].append(
            Agent(
                track_id=int(dct["track_id"]),
                position=np.array([float(dct["x"]), float(dct["y"])]),
                yaw=float(dct["psi_rad"]),
                extent=np.array([float(dct["length"]), float(dct["width"])]),
            )
        )

    sorted_keys = sorted(agents_by_frame.keys())
    return [Frame(agents=agents_by_frame[k]) for k in sorted_keys]
