# interactionviz

A no-nonsense, pure Python, renderer and loader for the [INTERACTION](http://interaction-dataset.com/) dataset.

![Demo](demo/output.gif)


### Quickstart
If you have a recent pip, and Python > 3.7.5, then you can dive straight in with
```
$ pip install git+https://github.com/rosshemsley/interactionviz
```
Probably it's best to run this inside of an activated `virtualenv` of some kind.

To view one of the scenes use
```
$ interactionviz --root-dir </root/of/interaction/dataset> --dataset DR_USA_Intersection_EP0
```
This will open a window and render the tracks in realtime.

### Using this as a library
The code is modular and easy to extend. Take a look at `__main__.py` inside the cli package
for an example of using the basic tools. Beware this is an early version and the API
might change unexpectedly in future versions.
