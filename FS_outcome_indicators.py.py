# Import the necessary modules
import os
import plotly as plt
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pyreadstat
import plotly.express as px
from datetime import datetime
import numpy as np
import datetime as dt
import time as tm
import pytz
import csv
from scipy.io import readsav

# Reading the mVAM data for use
cols = ['UserId', 'ObsDate', 'ADMIN1Name', 'ADM2', 'Location', 'Main_livelihood_zone', 'Year', 'Month', 'FCS',
        'FCSCat28','rCSI','rCSI_cat','HHS','HHS_IPC','Max_coping_behaviour']
mVAM = pd.read_spss('FS_indicators.sav', usecols=cols)
district = mVAM['ADM2'].unique()
region = mVAM['ADMIN1Name'].unique()
year = mVAM['Year'].unique()

# Streamlit app layout
st.set_page_config(layout="wide")  # Set the layout to wide mode


st.markdown("<h1 style='font-size: 24px; text-align: center;'>Food Security Outcome Indicators Trend</h1>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='font-size: 18px; text-align: center;'>For the years 2020 to 2023</h2>",
    unsafe_allow_html=True
)

# Sidebar for dropdowns
st.sidebar.title("Filters")

# Convert the years to integers to remove the decimal point
year = [int(y) for y in year]
year.sort()
# Dropdown for year selection
year_sel = st.sidebar.selectbox('Select year:', options=year, index=0)

# Update region options based on selected year
mVAM1 = mVAM[mVAM.Year == year_sel]
region_options = sorted(mVAM1.ADMIN1Name.unique())
region_sel = st.sidebar.selectbox('Select region:', options=region_options, index=0)

# Update district options based on selected region
mVAM1 = mVAM[mVAM.ADMIN1Name == region_sel]
district_options = sorted(mVAM1.ADM2.unique())
district_sel = st.sidebar.multiselect('Select District:', options=district_options, default=district_options)

# Placeholder for graphs
st.subheader('Graphs')
col1, col2 = st.columns(2)

def plot_graph(data, x, y, color, title, color_sequence, category_orders, labels):
    graph = px.bar(data, x=x, y=y, color=color, title=title, color_discrete_sequence=color_sequence,
                   category_orders=category_orders, hover_data=[y], labels=labels)
    graph.update_traces(textfont_size=12, textangle=0, cliponaxis=False, texttemplate='%{y:.1f}')
    graph.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="LightSteelBlue",
        plot_bgcolor="white",
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True)
    )
    return graph

if district_sel:
    mVAM1 = mVAM[(mVAM.ADMIN1Name == region_sel) & (mVAM.Year == year_sel) & (mVAM.ADM2.isin(district_sel))]

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("FCS Graph", expanded=True):
            mVAM2 = (mVAM1.groupby(["Month"])["FCSCat28"].value_counts(normalize=True) * 100).rename(
                'fcs_pro').reset_index()
            FCS_graph = plot_graph(mVAM2, 'Month', 'fcs_pro', 'FCSCat28', 'Food Consumption Score (FCS)',
                                   ["rgb(146,208,80)", "rgb(255,192,0)", "rgb(255,0,0)"],
                                   {"FCSCat28": ["Acceptable", "Borderline", "Poor"]},
                                   {'fcs_pro': '% of Households', 'FCSCat28': 'FCS'})
            st.plotly_chart(FCS_graph)

    with col2:
        with st.expander("rCSI Graph", expanded=True):
            mVAM3 = (mVAM1.groupby(["Month"])["rCSI_cat"].value_counts(normalize=True) * 100).rename(
                'rcsi_pro').reset_index()
            RCSI_graph = plot_graph(mVAM3, 'Month', 'rcsi_pro', 'rCSI_cat', 'Food Consumption-based Coping (rCSI)',
                                    ["rgb(146,208,80)", "rgb(255,255,0)", "rgb(255,0,0)"],
                                    {"rCSI_cat": ["None", "Stressed", "Crisis +"]},
                                    {'rcsi_pro': '% of Households', 'rCSI_cat': 'rCSI'})
            st.plotly_chart(RCSI_graph)

    col3, col4 = st.columns(2)

    with col3:
        with st.expander("HHS Graph", expanded=True):
            mVAM4 = (mVAM1.groupby(["Month"])["HHS_IPC"].value_counts(normalize=True) * 100).rename(
                'hhs_pro').reset_index()
            HHS_graph = plot_graph(mVAM4, 'Month', 'hhs_pro', 'HHS_IPC', 'Household Hunger Scale (HHS)',
                                   ["rgb(146,208,80)", "rgb(255,255,0)", "rgb(255,192,0)", "rgb(255,0,0)",
                                    "rgb(192,0,0)"],
                                   {"HHS_IPC": ["None", "Stressed", "Crisis", "Emergency", "Catastrophe"]},
                                   {'hhs_pro': '% of Households', 'HHS_IPC': 'HHS'})
            st.plotly_chart(HHS_graph)

    with col4:
        with st.expander("LVC Graph", expanded=True):
            mVAM5 = (mVAM1.groupby(["Month"])["Max_coping_behaviour"].value_counts(normalize=True) * 100).rename(
                'lvc_pro').reset_index()
            LVC_graph = plot_graph(mVAM5, 'Month', 'lvc_pro', 'Max_coping_behaviour', 'Livelihood-based coping',
                                   ["rgb(146,208,80)", "rgb(255,255,0)", "rgb(255,192,0)", "rgb(255,0,0)"],
                                   {"Max_coping_behaviour": ["None", "Stressed", "Crisis", "Emergency"]},
                                   {'lvc_pro': '% of Households', 'Max_coping_behaviour': 'Livelihood-coping'})
            st.plotly_chart(LVC_graph)
else:
    st.write("Please select at least one district to display the graphs.")
