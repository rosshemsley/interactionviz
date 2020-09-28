from dataclasses import dataclass
import numpy as np
from typing import List

from interactionviz.maps import Map


@dataclass
class Viewport:
    screen_width: float
    screen_height: float
    viewport_x_range: np.ndarray
    viewport_y_range: np.ndarray

    def project(self, points: List[np.ndarray]) -> List[np.ndarray]:
        x_range = self.viewport_x_range[1] - self.viewport_x_range[0]
        y_range = self.viewport_y_range[1] - self.viewport_y_range[0]

        rescale = min(self.screen_height, self.screen_width) / max(x_range, y_range)
        midpoint = np.array([self.screen_width / 2, self.screen_height / 2])
        result = []
        for p in points:
            normalized_frame = (
                p
                - np.array(
                    [
                        self.viewport_x_range[0] + x_range / 2,
                        self.viewport_y_range[0] + y_range / 2,
                    ]
                )
            ) / max(x_range / 2, y_range / 2)
            normalized_frame *= min(self.screen_height, self.screen_width)
            normalized_frame += np.array(
                [self.screen_width / 2, self.screen_height / 2]
            )

            result.append(normalized_frame)

        return result


def viewport_for_map_no_scaling(interaction_map):
    """
    Returns a viewport where the screen width and height are the same as the map width and height.

    This is useful for rendering on a 3D canvas where we want the units to be equal to meters.
    """
    min_x, min_y, max_x, max_y = None, None, None, None

    for n in interaction_map.nodes.values():
        x, y = n.position[0], n.position[1]
        if min_x is None:
            min_x = max_x = x
            min_y = max_y = y
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    return Viewport(
        screen_width=max_x - min_x ,
        screen_height=min_y - max_y,
        viewport_x_range=np.array([min_x, max_x]),
        viewport_y_range=np.array([min_y, max_y]),
    )


def viewport_for_map(
    screen_width: float, screen_height: float, interaction_map: Map
) -> Viewport:
    min_x, min_y, max_x, max_y = None, None, None, None

    for n in interaction_map.nodes.values():
        x, y = n.position[0], n.position[1]
        if min_x is None:
            min_x = max_x = x
            min_y = max_y = y
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    return Viewport(
        screen_width=screen_width,
        screen_height=screen_height,
        viewport_x_range=np.array([min_x, max_x]),
        viewport_y_range=np.array([min_y, max_y]),
    )
