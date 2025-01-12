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
