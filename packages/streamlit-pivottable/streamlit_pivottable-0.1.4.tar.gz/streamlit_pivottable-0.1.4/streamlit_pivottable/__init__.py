import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_pivottable",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    if not os.path.exists(build_dir):
        raise FileNotFoundError(f"Frontend build directory not found: {build_dir}")
    _component_func = components.declare_component("Streamlit_pivottable", path=build_dir)


def streamlit_pivottable(name="streamlit_pivottable", data=None, height=100, use_container_width=False, key=None):
    """
    Parameters:
    1. name (str): 
       - A string representing the name or title of the pivot table. 
       - Used to identify the component, often displayed as a header or label.
       - Default: "streamlit_pivottable".

    2. data (list): 
       - A list containing the dataset for the pivot table. 
       - Each item in the list represents a row, where the first sublist defines the headers (columns).
       - Example:
         [
             ["Name", "Age", "City"],
             ["Alice", 30, "New York"],
             ["Bob", 25, "Los Angeles"]
         ]
       - Default: None (initializes to an empty list).

    3. height (int): 
       - An integer representing the height of the pivot table in rem units.
       - Determines how much vertical space the pivot table occupies.
       - Default: 100 (which typically translates to 1600px if 1rem = 16px).

    4. use_container_width (bool): 
       - A boolean that specifies whether the pivot table should stretch to fit the full width of the container.
       - If `True`, the pivot table will take up the entire width of its parent container.
       - If `False`, it uses its default or explicitly set width.
       - Default: False.

    5. key (str or None): 
       - An optional string to uniquely identify this Streamlit component.
       - Useful for maintaining state across reruns of the Streamlit app, especially if you have multiple instances of the component.
       - Default: None.
    """
    if data is None:
        data = []

    # Pass parameters to the Streamlit component
    component_value = _component_func(
        name=name,
        data=data,
        height=height,
        use_container_width=use_container_width,
        key=key,
        default=0
    )

    return component_value
