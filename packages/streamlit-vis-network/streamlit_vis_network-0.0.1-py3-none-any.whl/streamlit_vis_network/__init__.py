from typing import (
    Any,
    Dict,
    List,
    Union
)
import os

import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "streamlit_vis_network",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "streamlit_vis_network", path=build_dir
    )


# Wrapper function for Streamlit use
def streamlit_vis_network(
    nodes:List[Dict[str, Any]],
    edges:List[Dict[str, Any]],
    options:Union[Dict[str, Any], None]=None,
    key:Union[str, int, None]=None
) -> Union[str, None]:
    """Create 

    Args:
        nodes: List of nodes to visualize.
        edges: List of edges to visualize.
        options: Configuration settings for the vis.js network visualization.
            See https://visjs.github.io/vis-network/docs/network/#options for more
            information. Defaults to None.
        key: An optional string or integer to use as the unique key for the widget.
            If this is omitted, a key will be generated for the widget based on its
            content. No two widgets may have the same key. Defaults to None.

    Returns:
        Returns the id of the currently selected node, if selected, otherwise returns
        None.
    
    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_vis_network import streamlit_vis_network
    >>>
    >>> nodes = [{'id': 1, "label": "node 1"}, {'id': 2, "label": "node 2"}]
    >>> edges = [{"from": 1, "to": 2, "label": "edge"}]
    >>>
    >>> selected_node = streamlit_vis_network(nodes=nodes, edges=edges)
    >>>
    >>> st.write(f"Selected node: {selected_node}")
    """
    return _component_func(nodes=nodes, edges=edges, key=key)