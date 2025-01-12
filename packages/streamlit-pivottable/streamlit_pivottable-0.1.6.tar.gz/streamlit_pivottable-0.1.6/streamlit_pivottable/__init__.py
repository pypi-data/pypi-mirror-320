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


def streamlit_pivottable(name="streamlit_pivottable", data=None, default_settings = {
      "rows": [],
      "cols": [],
      "aggregatorName": "Count",
      "vals": [],
      "rendererName": "streamlit_pivottable",
    }, height=100, use_container_width=False):

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
    3. "rows":

        Value: An empty list ([]).
        Purpose: Likely represents the rows in a pivot table. Defaulting to an empty list means no rows are initially configured.
        "cols":

        Value: An empty list ([]).
        Purpose: Represents the columns in a pivot table. Defaulting to an empty list means no columns are initially configured.
        "aggregatorName":

        Value: "Count".
        Purpose: Specifies the default aggregation function to be used in the pivot table. "Count" indicates that the data will be counted as the default aggregation.
        "vals":

        Value: An empty list ([]).
        Purpose: Represents the values to be aggregated. An empty list means no default values are provided.
        "rendererName":

        Value: "streamlit_pivottable".
        Purpose: Specifies the default renderer or display format for the pivot table. "streamlit_pivottable" could indicate a custom renderer designed for Streamlit integration.

    4. height (int): 
       - An integer representing the height of the pivot table in rem units.
       - Determines how much vertical space the pivot table occupies.
       - Default: 100 (which typically translates to 1600px if 1rem = 16px).

    5. use_container_width (bool): 
       - A boolean that specifies whether the pivot table should stretch to fit the full width of the container.
       - If `True`, the pivot table will take up the entire width of its parent container.
       - If `False`, it uses its default or explicitly set width.
       - Default: False.

    6. key (str or None): 
       - An optional string to uniquely identify this Streamlit component.
       - Useful for maintaining state across reruns of the Streamlit app, especially if you have multiple instances of the component.
       - Default: None.


    Here're the example of Code:   
    ############################################################################################################################################
    import streamlit as st
    from streamlit_pivottable import streamlit_pivottable
    import pandas as pd
    import numpy as np

    # Set page configuration    
    st.set_page_config(layout='wide')

    # Limit the number of rows
    num_rows = 1000000

    # Generate sample DataFrame for Pivot Table
    df = pd.DataFrame({
        "Category": np.random.choice(
            ["Category A", "Category B", "Category C", "Category D", 
            "Category E", "Category F", "Category G", "Category H", 
            "Category I", "Category J"], size=num_rows),
        "Region": np.random.choice(
            ["North", "South", "East", "West", "Central", "Northeast", 
            "Southeast", "Northwest", "Southwest", "International"], size=num_rows),
        "Priority": np.random.choice(
            ["Very Low", "Low", "Medium Low", "Medium", "Medium High", 
            "High", "Very High", "Critical", "Non-Critical", "Undefined"], size=num_rows),
        "Product Type": np.random.choice(
            ["Product A", "Product B", "Product C", "Product D", "Product E", 
            "Product F", "Product G", "Product H", "Product I", "Product J"], size=num_rows),
        "Quarter": np.random.choice(
            ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"], size=num_rows),
        "Source": np.random.choice(
            ["Online", "Offline", "In-Store", "Marketplace", "Subscription", 
            "Direct Sales", "Wholesale", "Retail", "Auction", "Flash Sale"], size=num_rows),
        "Gender": np.random.choice(
            ["Male", "Female", "Other", "Prefer Not to Say", "Non-Binary", 
            "Transgender", "Intersex", "Androgynous", "Genderqueer", "Agender"], size=num_rows),
        "Age Range": np.random.choice(
            ["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", 
            "75-84", "85-94", "95+", "Under 18"], size=num_rows),
        "Customer Type": np.random.choice(
            ["New Customer", "Returning Customer", "VIP", "Wholesale Buyer", 
            "Gift Buyer", "Seasonal Buyer", "Frequent Shopper", "Rare Shopper", 
            "Business Client", "Occasional Buyer"], size=num_rows),
        "Promotion": np.random.choice(
            ["Discounted", "Full Price", "Clearance", "Premium", "Subscription Plan", 
            "Limited Offer", "Flash Sale", "Bundle Deal", "Gift Pack", "Exclusive"], size=num_rows),
    })

    df["Value"] = np.random.uniform(1000000, 999999999, size=num_rows).round(2)


    sample_size = 100000  # Adjust this to improve performance
    df_sample = df.sample(n=sample_size, random_state=42)
    data_2d = [df_sample.columns.tolist()] + df_sample.values.tolist()


    default_settings = {
            "rows": [],
            "cols": [],
            "aggregatorName": "Average",
            "vals": [],
            "rendererName": "streamlit_pivottable",
        }

    # Display Streamlit component Pivot Table
    with st.spinner("Loading Pivot Table..."):
        with st.container():
            pivot_table_settings = streamlit_pivottable(
                data=data_2d, 
                default_settings=default_settings,
                height=50, 
                use_container_width=True, 
            )

    # Display pivot table configuration
    if pivot_table_settings:
        st.write("Pivot Table Configuration:")
        st.json(pivot_table_settings)

    ############################################################################################################################################
    """
    if data is None:
        data = []



    # Pass parameters to the Streamlit component
    component_value = _component_func(
        name=name,
        data=data,
        default_settings=default_settings,
        height=height,
        use_container_width=use_container_width,
        key=default_settings["rendererName"],
        default=0
    )

    return component_value
