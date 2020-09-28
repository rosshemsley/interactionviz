import os
import pathlib

import click
from interactionviz.maps import load_map_xml
from interactionviz.viewers import ArcadeViewer, WebViewer
from interactionviz.tracks import Tracks, load_tracks_files


@click.command()
@click.option(
    "--root-dir",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Root directory of the interaction dataset.",
)
@click.option("--dataset", default="DR_CHN_Merging_ZS")
@click.option("--viewer-kind", default="native", type=click.Choice(['web', 'native'], case_sensitive=False))
@click.option("--session", type=int, default=0, help="session to load for tracks")
def main(viewer_kind: str, root_dir: str, dataset: str, session: int):
    root = pathlib.Path(root_dir)
    map_path = root.joinpath("maps", f"{dataset}.osm_xy")

    interaction_map = load_map_xml(map_path)

    tracks = _load_tracks(root, dataset, session)
    if viewer_kind == "web":
        viewer = WebViewer(interaction_map, tracks=tracks)
    else:
        viewer = ArcadeViewer(interaction_map, tracks=tracks)
    viewer.run()


def _load_tracks(root: pathlib.Path, dataset: str, session: int) -> Tracks:
    paths = []
    tracks_dir = root.joinpath("recorded_trackfiles", dataset)

    vehicles = tracks_dir.joinpath(f"pedestrian_tracks_{session:03d}.csv")
    pedestrians = tracks_dir.joinpath(f"vehicle_tracks_{session:03d}.csv")

    if vehicles.exists():
        paths.append(vehicles)

    if pedestrians.exists():
        paths.append(pedestrians)

    if len(paths) == 0:
        raise ValueError(f"no tracks found at {vehicles} or {pedestrians}")

    return load_tracks_files(*paths)


if __name__ == "__main__":
    main()
