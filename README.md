# Interaction Viz.

A no-nonsense, pure Python, renderer / visualizer and loader for the [INTERACTION](http://interaction-dataset.com/) dataset.

![Demo](https://raw.githubusercontent.com/rosshemsley/interactionviz/master/demo/output.gif)


## Quickstart
If you have Python >= 3.7.5, just use
```
$ pip install interactionviz
```
(probably it's best to run this inside of an activated `virtualenv` of some kind)

To view a scene, you can use
```
$ interactionviz --root-dir </root/of/interaction/dataset> --dataset DR_USA_Intersection_EP0 --session 1
```
This will open a native 2D top-down viewer.

If you have an older version of Python, you can use `pyenv` to install a more recent version.

### 🧪 Experimental Feature: 3D Web viewer
An experimental feature is provided to support rendering the tracks in a webviewer using THREE.js.
To try this out, run the following command and navigate to `http://localhost:8000/viewer`.
```
$ interactionviz --viewer-kind web --root-dir </root/of/interaction/dataset>
```

## Using this as a library
The code is modular and easy to extend. Beware this is an early version and the API
might change unexpectedly in future versions.

Here's an example of importing and using this viewer in your own code.

```python
from interactionviz.maps import load_map_xml
from interactionviz.tracks import load_tracks_files
from interactionviz.viewers import ArcadeViewer
# Note: You can use the following to render in 3D in a web browser,
#   from interactionviz.viewers import WebViewer

interaction_map = load_map_xml("<path/to/map.osm_xy>")
tracks = load_tracks_files("<path/to/vehicle_tracks_000.csv>")
viewer = ArcadeViewer(interaction_map, tracks)

viewer.run()
```
