# Streamlit Pivot Table

This Project is created at 2025 Jan 6th

```sh
import streamlit as st
from streamlit_pivottable import streamlit_pivottable

st.set_page_config(layout='wide')

data = [
    {
        "Name": "Name_1",
        "Age": 58,
        "City": "Phoenix",
        "Salary": 87052,
        "Department": "IT",
        "Joining Date": "2020-01-31",
    },
    {
        "Name": "Name_2",
        "Age": 25,
        "City": "Los Angeles",
        "Salary": 85082,
        "Department": "HR",
        "Joining Date": "2020-02-29",
    },
    {
        "Name": "Name_3",
        "Age": 19,
        "City": "Phoenix",
        "Salary": 119131,
        "Department": "Marketing",
        "Joining Date": "2020-03-31",
    },
    {
        "Name": "Name_4",
        "Age": 35,
        "City": "Houston",
        "Salary": 74671,
        "Department": "Finance",
        "Joining Date": "2020-04-30",
    },
    {
        "Name": "Name_5",
        "Age": 33,
        "City": "Los Angeles",
        "Salary": 45695,
        "Department": "Marketing",
        "Joining Date": "2020-05-31",
    },

]

streamlit_pivottable(data=data,height=50, use_container_width=True, key="streamlit_pivottable")

```
