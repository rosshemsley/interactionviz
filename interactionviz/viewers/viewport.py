from dataclasses import dataclass
import numpy as np
from typing import List, Optional

from interactionviz.maps import Map


@dataclass
class Viewport:
    screen_width: Optional[float]
    screen_height: Optional[float]
    viewport_x_range: np.ndarray
    viewport_y_range: np.ndarray

    def project(self, points: List[np.ndarray]) -> List[np.ndarray]:
        result = []

        width = self.viewport_x_range[1] - self.viewport_x_range[0]
        height = self.viewport_y_range[1] - self.viewport_y_range[0]

        if self.screen_width is None or self.screen_height is None:
            offset = np.array(
                [
                    self.viewport_x_range[0] + width / 2,
                    self.viewport_y_range[0] + height / 2,
                ]
            )
            return [p - offset for p in points]

        for p in points:
            # v moves to a unit box centered at 0.
            v = p - np.array(
                [
                    self.viewport_x_range[0] + width / 2,
                    self.viewport_y_range[0] + height / 2,
                ]
            )
            v = v / max(width, height)
            # now move to the viewport
            v = v * min(self.screen_height, self.screen_width)
            v = v + np.array([self.screen_width / 2, self.screen_height / 2])
            result.append(v)

        # rescale = min(self.screen_height, self.screen_width) / max(x_range, y_range)
        # midpoint = np.array([self.screen_width / 2, self.screen_height / 2])
        # result = []
        # for p in points:
        #     normalized_frame = (
        #         p
        #         - np.array(
        #             [
        #                 self.viewport_x_range[0] + x_range / 2,
        #                 self.viewport_y_range[0] + y_range / 2,
        #             ]
        #         )
        #     ) / max(x_range / 2, y_range / 2)
        #     normalized_frame *= min(self.screen_height, self.screen_width)
        #     normalized_frame += np.array(
        #         [self.screen_width / 2, self.screen_height / 2]
        #     )

        #     result.append(normalized_frame)

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
        screen_width=None,
        screen_height=None,
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
