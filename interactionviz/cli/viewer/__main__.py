import os

import click

from interactionviz.maps import load_map_xml
from interactionviz.viewers import ArcadeViewer
from interactionviz.tracks import Tracks


@click.command()
@click.option(
    "--root-dir",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Root directory of the interaction dataset.",
)
@click.option("--dataset", default="DR_CHN_Merging_ZS")
def main(root_dir, dataset):
    map_path = os.path.join(root_dir, "maps", f"{dataset}.osm_xy")
    trackfile_dir = os.path.join(root_dir, "recorded_trackfiles", dataset)

    with open(map_path, "rt") as map_file:
        interaction_map = load_map_xml(map_file)

    tracks = Tracks(trackfile_dir)
    viewer = ArcadeViewer(interaction_map, tracks=tracks)
    viewer.run()


if __name__ == "__main__":
    main()
