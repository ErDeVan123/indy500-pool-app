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
        "Starting_Pos": list(range(1, 34)),
        "Car_Num": [10,20,12,60,14,5,8,23,3,9,76,75,33,6,21,66,28,7,26,6,45,31,2,18,27,11,47,15,19,51,77,4,24],
        "Driver": ["Alex Palou", "Alexander Rossi", "David Malukas", "Felix Rosenqvist", "Santino Ferrucci", "Pato O'Ward", "Kyffin Simpson", "Conor Daly", "Scott McLaughlin", "Scott Dixon", "Rinus VeeKay", "Takuma Sato", "Ed Carpenter", "Helio Castroneves", "Christian Rasmussen", "Marcus Armstrong", "Marcus Ericsson", "Christian Lundgaard", "Will Power", "Nolan Siegel", "Louis Foster", "Ryan Hunter-Reay", "Josef Newgarden", "Romain Grosjean", "Kyle Kirkwood", "Katherine Legge", "Mick Schumacher", "Graham Rahal", "Dennis Hauger", "Jacob Abel", "Sting Ray Robb", "Caio Collet", "Jack Harvey"],
        "Team": ["Chip Ganassi", "ECR", "Penske", "MSR", "Foyt", "McLaren", "Ganassi", "D&R", "Penske", "Ganassi", "Juncos", "RLL", "ECR", "MSR", "ECR", "MSR", "Andretti", "McLaren", "Andretti", "McLaren", "RLL", "McLaren", "Penske", "Coyne", "Andretti", "HMD", "RLL", "RLL", "Coyne", "Abel", "Juncos", "Foyt", "D&R"],
        "Qual_Speed": ["234.2 mph"]*33,
        "Tier_1_3": ["Yes"]*9 + ["No"]*24,
        "Car_Pic": ["https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/10-DHL-SS.png"]*33
    }
    return pd.DataFrame(data)

POSITIONS_FILE = "race_positions.csv"
PICK_FILE = "picks.csv"

df = get_base_drivers()
# Load positions if exist
if os.path.exists(POSITIONS_FILE):
    pos_df = pd.read_csv(POSITIONS_FILE)
    df = pd.merge(df, pos_df[["Driver", "Pos_100", "Pos_150", "Pos_Final"]], on="Driver", how="left")
else:
    df[["Pos_100", "Pos_150", "Pos_Final"]] = 0

picks_df = pd.read_csv(PICK_FILE) if os.path.exists(PICK_FILE) else pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

def calculate_master_standings():
    if picks_df.empty: return pd.DataFrame()
    leaderboard_data = []
    for _, row in picks_df.iterrows():
        user_drivers = df[df['Driver'].isin([row[f'P{i}'] for i in range(1, 9)])]
        leaderboard_data.append({"Name": row['Participant'], "Starting Pts": int(user_drivers['Starting_Pos'].sum()), "Final Pts": int(user_drivers['Pos_Final'].sum())})
    return pd.DataFrame(leaderboard_data).sort_values(by="Starting Pts")

t2, t4, t5, t3, t1 = st.tabs(["📝 Draft Drivers", "📋 View Rosters", "📊 Popular Picks", "🏁 Milestone Ranks", "🏆 Standings"])

# --- VIEW 2: DRAFT DRIVERS ---
with t2:
    st.markdown("Select exactly **8 drivers**. Maximum **3 from Rows 1-3**.")
    
    entry_name = st.text_input("Enter Roster Submission Name:", key="new_user_name", placeholder="e.g., Sarah - Lineup 1").strip()
    
    if "selected_pool" not in st.session_state:
        st.session_state["selected_pool"] = []
        
    current_picks = st.session_state["selected_pool"]
    count_picked = len(current_picks)
    count_tier = df[df['Driver'].isin(current_picks) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    # Metrics and Submit moved here
    c1, c2 = st.columns(2)
    c1.metric("Drivers Picked", f"{count_picked} / 8")
    c2.metric("Top-Tier Rows 1-3", f"{count_tier} / 3")
    
    can_submit = (count_picked == 8 and count_tier <= 3 and entry_name and entry_name not in picks_df['Participant'].values)
    
    if st.button("Submit Official Roster Lineup", type="primary", disabled=not can_submit):
        new_entry = pd.DataFrame([{
            "Participant": entry_name,
            "P1": current_picks[0], "P2": current_picks[1], "P3": current_picks[2], "P4": current_picks[3],
            "P5": current_picks[4], "P6": current_picks[5], "P7": current_picks[6], "P8": current_picks[7]
        }])
        pd.concat([picks_df, new_entry], ignore_index=True).to_csv(PICK_FILE, index=False)
        st.success(f"Success! '{entry_name}' lineup was successfully submitted.")
        st.session_state["selected_pool"] = []
        st.rerun()

    st.write("---")
    for idx, row in df.iterrows():
        is_selected = row['Driver'] in st.session_state["selected_pool"]
        with st.container(border=True):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.subheader(row['Driver'])
                if st.checkbox("Select", key=f"d_{idx}", value=is_selected):
                    if row['Driver'] not in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].append(row['Driver'])
                        st.rerun()
                else:
                    if row['Driver'] in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].remove(row['Driver'])
                        st.rerun()
            with col2:
                st.image(row['Car_Pic'])

# --- VIEW 1: STANDINGS ---
with t1:
    st.header("Standings")
    master_standings = calculate_master_standings()
    if not master_standings.empty:
        total_participants = len(master_standings)
        chart_data = [{"Milestone": "Start", "Pos": total_participants - i, "Name": name} 
                      for i, name in enumerate(master_standings['Name'])]
        
        base = alt.Chart(pd.DataFrame(chart_data)).encode(
            x='Milestone:N', y=alt.Y('Pos:Q', axis=None), color='Name:N'
        )
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.altair_chart(base.mark_line() + base.mark_circle(), use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)
