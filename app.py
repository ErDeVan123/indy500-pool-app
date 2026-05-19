import streamlit as st
import pandas as pd
import altair as alt
import os

# Page layout setup
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    :root, [data-theme="light"], [data-theme="dark"] {
        --text-color: #000000 !important;
        --background-color: #ffffff !important;
        --primary-color: #ff0000 !important;
    }
    .stApp {
        background-image: linear-gradient(45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(-45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(45deg, transparent 75%, rgba(200,200,200,0.15) 75%), 
                          linear-gradient(-45deg, transparent 75%, rgba(200,200,200,0.15) 75%);
        background-size: 40px 40px;
        background-color: #ffffff !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp small, .stMarkdown p {
        color: #000000 !important;
    }
    div[data-testid="stTabs"] {
        background-color: #f1f1f1 !important;
        padding: 4px 4px 0px 4px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #ff0000 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #ff0000 !important;
        color: #ffffff !important;
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
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ Indy 500: VanGutz Style")

@st.cache_data
def get_base_drivers():
    data = {
        "Starting_Pos": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
        "Car_Num": [10,20,12,60,14,5,8,23,3,9,76,75,33,6,21,66,28,7,26,6,45,31,2,18,27,11,47,15,19,51,77,4,24],
        "Driver": ["Alex Palou", "Alexander Rossi", "David Malukas", "Felix Rosenqvist", "Santino Ferrucci", "Pato O'Ward", "Kyffin Simpson", "Conor Daly", "Scott McLaughlin", "Scott Dixon", "Rinus VeeKay", "Takuma Sato", "Ed Carpenter", "Helio Castroneves", "Christian Rasmussen", "Marcus Armstrong", "Marcus Ericsson", "Christian Lundgaard", "Will Power", "Nolan Siegel", "Louis Foster", "Ryan Hunter-Reay", "Josef Newgarden", "Romain Grosjean", "Kyle Kirkwood", "Katherine Legge", "Mick Schumacher", "Graham Rahal", "Dennis Hauger", "Jacob Abel", "Sting Ray Robb", "Caio Collet", "Jack Harvey"],
        "Team": ["Chip Ganassi Racing", "Ed Carpenter Racing", "Team Penske", "Meyer Shank Racing", "A.J. Foyt Racing", "Arrow McLaren", "Chip Ganassi Racing", "Dreyer & Reinbold", "Team Penske", "Chip Ganassi Racing", "Juncos Hollinger", "Rahal Letterman", "Ed Carpenter Racing", "Meyer Shank Racing", "Ed Carpenter Racing", "Meyer Shank Racing", "Andretti Global", "Arrow McLaren", "Andretti Global", "Arrow McLaren", "Rahal Letterman", "Arrow McLaren", "Team Penske", "Dale Coyne Racing", "Andretti Global", "HMD Motorsports", "Rahal Letterman", "Rahal Letterman", "Dale Coyne Racing", "Abel Motorsports", "Juncos Hollinger", "A.F. Foyt Racing", "Dreyer & Reinbold"],
        "Qual_Speed": ["234.214 mph", "233.811 mph", "233.504 mph", "233.210 mph", "233.114 mph", "232.998 mph", "232.845 mph", "232.612 mph", "232.401 mph", "232.214 mph", "232.105 mph", "231.994 mph", "231.785 mph", "231.654 mph", "231.411 mph", "231.202 mph", "231.004 mph", "230.985 mph", "230.841 mph", "230.652 mph", "230.414 mph", "230.201 mph", "230.114 mph", "229.984 mph", "229.814 mph", "229.654 mph", "229.412 mph", "229.412 mph", "229.214 mph", "229.004 mph", "228.841 mph", "228.651 mph", "228.411 mph"],
        "Tier_1_3": ["Yes"]*9 + ["No"]*24,
        "Car_Pic": ["https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/10-DHL-SS.png?dp=05-11-2026T06:02PM"]*33 # Simplified for brevity
    }
    return pd.DataFrame(data)

POSITIONS_FILE = "race_positions.csv"
def load_race_positions():
    base_df = get_base_drivers()
    if os.path.exists(POSITIONS_FILE):
        pos_df = pd.read_csv(POSITIONS_FILE)
        return pd.merge(base_df, pos_df[["Driver", "Pos_100", "Pos_150", "Pos_Final"]], on="Driver", how="left")
    base_df[["Pos_100", "Pos_150", "Pos_Final"]] = 0
    return base_df

df = load_race_positions()
PICK_FILE = "picks.csv"
picks_df = pd.read_csv(PICK_FILE) if os.path.exists(PICK_FILE) else pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

def calculate_master_standings():
    if picks_df.empty: return pd.DataFrame()
    leaderboard_data = []
    for _, row in picks_df.iterrows():
        user_drivers = df[df['Driver'].isin([row[f'P{i}'] for i in range(1, 9)])]
        leaderboard_data.append({"Name": row['Participant'], "Starting Pts": int(user_drivers['Starting_Pos'].sum()), "100L Pts": int(user_drivers['Pos_100'].sum()), "150L Pts": int(user_drivers['Pos_150'].sum()), "Final Pts": int(user_drivers['Pos_Final'].sum())})
    master_df = pd.DataFrame(leaderboard_data).sort_values(by="Starting Pts")
    master_df["Start Place"] = range(1, len(master_df) + 1)
    return master_df

# Navigation
t2, t4, t5, t3, t1 = st.tabs(["📝 Draft Drivers", "📋 View Rosters", "📊 Popular Picks", "🏁 Milestone Ranks", "🏆 Standings"])

with t1:
    st.header("Standings")
    master_standings = calculate_master_standings()
    if not master_standings.empty:
        total_participants = len(master_standings)
        standings_chart_records = []
        for _, row in master_standings.iterrows():
            standings_chart_records.append({"Milestone": "Start", "GraphPosition": (total_participants + 1) - row['Start Place'], "Pool Participant": row['Name']})
        
        standings_chart_df = pd.DataFrame(standings_chart_records)
        base_standings = alt.Chart(standings_chart_df).encode(
            x=alt.X('Milestone:N', title="Race Milestone"),
            y=alt.Y('GraphPosition:Q', title=None, axis=alt.Axis(labels=False, ticks=False)),
            color=alt.Color('Pool Participant:N', legend=alt.Legend(orient='left', title="Participant"))
        )
        chart_render_st = (base_standings.mark_line() + base_standings.mark_circle()).properties(width=1000, height=350)
        
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.altair_chart(chart_render_st, use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)

with t3:
    st.subheader("Milestone Ranks")
    sort_basis_label = st.selectbox("Milestone:", ["Starting Order", "Running Order @ Lap 100", "Running Order @ Lap 150", "Finishing Order"])
    # ... (rest of logic as before)
