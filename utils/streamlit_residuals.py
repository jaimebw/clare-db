#!/usr/bin/env python
# -*- coding: utf-8 -*-
#author: Jaime Bowen Varela
# How to run this dashboard
# 1. Install Streamlit and matplotlib: pip install streamlit matplotlib
# 2. Run it: streamlit run streamlit_residuals.py
# 3. Enjoy =D 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import random

def load_residuals(path_to_data):
    df = pd.read_csv(path_to_data,header = 1,sep = "\t",index_col =0)
    real_names = [i.strip() for i in df.columns]
    df.columns = real_names
    return df.dropna()

def residuals_plot(df):
    fig, ax = plt.subplots(figsize = (6,3))
    color = random.choice(["red","royalblue","darkorange","coral"]) 
    df.plot(ax = ax,color = color)
    ax.set_xlabel("Number of iterations")
    ax.set_ylim([0,df.mean()])
    ax.legend()
    
    

    return fig
st.title("Residual information")
residuals_path = Path("postProcessing/residuals/0/residuals.dat")
if not residuals_path.exists():
    st.write("Execute this file inside the folder of the simulation or choose the residuals.dat file")
    residuals_path = st.file_uploader("Choose a residual.dat file")
    if residuals_path== None:
        st.stop()

residuals_df = load_residuals(residuals_path)
st.metric(label = "Number of simulations",value = residuals_df.shape[0])
st.header("Values of the residuals")
#for i in residuals_df.columns:
#    st.metric(label = f"Minimum value of {i}",value = residuals_df[i].min())
col1, col2 = st.columns(2)
for index, i in enumerate(residuals_df.columns):
    if index %2 ==0:
        col1.metric(label = f"Minimum value of {i}",value = residuals_df[i].min())
        with col1:
            st.pyplot(residuals_plot(residuals_df[i]))
    else:
        col2.metric(label = f"Minimum value of {i}",value = residuals_df[i].min())
        with col2:
            st.pyplot(residuals_plot(residuals_df[i]))
#st.pyplot(residuals_plot(residuals_df))
