import streamlit as st
import pandas as pd
import altair as alt
import os

# Page layout setup
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")

# Custom Styling: Overriding native mobile dark-mode layers for absolute contrast
st.markdown("""
    <style>
    /* 1. FORCE THE APP ROOT VARIABLES TO LIGHT STATE FOR MOBILE SYSTEM OVERRIDES */
    :root, [data-theme="light"], [data-theme="dark"] {
        --text-color: #000000 !important;
        --background-color: #ffffff !important;
        --primary-color: #ff0000 !important;
    }

    /* Set a clean, responsive checkered flag background pattern */
    .stApp {
        background-image: linear-gradient(45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(-45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(45deg, transparent 75%, rgba(200,200,200,0.15) 75%), 
                          linear-gradient(-45deg, transparent 75%, rgba(200,200,200,0.15) 75%);
        background-size: 40px 40px;
        background-position: 0 0, 0 20px, 20px -20px, -20px 0px;
        background-color: #ffffff !important;
    }
    
    /* Target regular body text safely across mobile webkit engines */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp small, .stMarkdown p {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* --- NATIVE ST.TABS STYLING OVERRIDES --- */
    div[data-testid="stTabs"] {
        background-color: #f1f1f1 !important;
        padding: 4px 4px 0px 4px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #ff0000 !important;
    }

    div[data-testid="stTabs"] button {
        background-color: #e0e0e0 !important;
        color: #333333 !important;
        border: 1px solid #d3d3d3 !important;
        border-bottom: none !important;
        margin-right: 4px;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] button span {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #ff0000 !important;
        background: #ff0000 !important;
        color: #ffffff !important;
        border: 1px solid #cc0000 !important;
        border-bottom: none !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: bold !important;
    }
    
    [data-testid="stImage"] img {
        height: 100px !important;
        object-fit: contain !important;
        border-radius: 4px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    
    .scroll-container {
        width: 100%;
        overflow-x: auto;
        white-space: nowrap;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    [data-testid="stDataFrame"] {
        width: 100% !important;
        overflow-x: auto;
        background-color: #ffffff !important;
    }
    [data-testid="stDataFrame"] div[data-testid="stTable"] {
        background-color: #ffffff !important;
    }
    [data-testid="stDataFrame"] div[data-testid="stTable"] th,
    [data-testid="stDataFrame"] div[data-testid="stTable"] td {
        color: #000000 !important;   
        background-color: #ffffff !important;
        text-align: center !important;
        white-space: normal !important; 
        font-size: 13px !important;     
        padding: 4px 6px !important;    
    }
    [data-testid="stDataFrame"] div[data-testid="stTable"] td:nth-child(2),
    [data-testid="stDataFrame"] div[data-testid="stTable"] th:nth-child(2) {
        text-align: left !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ Indy 500: VanGutz Style")

# 1. Base Starting Grid Data
@st.cache_data
def get_base_drivers():
    data = {
        "Starting_Pos": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
        "Car_Num": [10,20,12,60,14,5,8,23,3,9,76,75,33,6,21,66,28,7,26,6,45,31,2,18,27,11,47,15,19,51,77,4,24],
        "Driver": [
            "Alex Palou", "Alexander Rossi", "David Malukas", "Felix Rosenqvist", "Santino Ferrucci", 
            "Pato O'Ward", "Kyffin Simpson", "Conor Daly", "Scott McLaughlin", "Scott Dixon", 
            "Rinus VeeKay", "Takuma Sato", "Ed Carpenter", "Helio Castroneves", "Christian Rasmussen", 
            "Marcus Armstrong", "Marcus Ericsson", "Christian Lundgaard", "Will Power", "Nolan Siegel", 
            "Louis Foster", "Ryan Hunter-Reay", "Josef Newgarden", "Romain Grosjean", "Kyle Kirkwood", 
            "Katherine Legge", "Mick Schumacher", "Graham Rahal", "Dennis Hauger", "Jacob Abel", 
            "Sting Ray Robb", "Caio Collet", "Jack Harvey"
        ],
        "Team": [
            "Chip Ganassi Racing", "Ed Carpenter Racing", "Team Penske", "Meyer Shank Racing", "A.J. Foyt Racing", 
            "Arrow McLaren", "Chip Ganassi Racing", "Dreyer & Reinbold", "Team Penske", "Chip Ganassi Racing", 
            "Juncos Hollinger", "Rahal Letterman", "Ed Carpenter Racing", "Meyer Shank Racing", "Ed Carpenter Racing", 
            "Marcus Armstrong", "Andretti Global", "Arrow McLaren", "Andretti Global", "Arrow McLaren", 
            "Rahal Letterman", "Arrow McLaren", "Team Penske", "Dale Coyne Racing", "Andretti Global", 
            "HMD Motorsports", "Rahal Letterman", "Rahal Letterman", "Dale Coyne Racing", "Abel Motorsports", 
            "Juncos Hollinger", "A.F. Foyt Racing", "Dreyer & Reinbold"
        ],
        "Qual_Speed": [
            "234.214 mph", "233.811 mph", "233.504 mph", "233.210 mph", "233.114 mph", 
            "232.998 mph", "232.845 mph", "232.612 mph", "232.401 mph", "232.214 mph", 
            "232.105 mph", "231.994 mph", "231.785 mph", "231.654 mph", "231.411 mph", 
            "231.202 mph", "231.004 mph", "230.985 mph", "230.841 mph", "230.652 mph", 
            "230.414 mph", "230.201 mph", "230.114 mph", "229.984 mph", "229.814 mph", 
            "229.654 mph", "229.412 mph", "229.412 mph", "229.214 mph", "229.004 mph", 
            "228.841 mph", "228.651 mph", "228.411 mph"
        ],
        "Tier_1_3": [
            "Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No"
        ],
        "Car_Pic":
