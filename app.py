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
        leaderboard_data.append({
            "Name": row['Participant'], 
            "Starting Pts": int(user_drivers['Starting_Pos'].sum()), 
            "100L Pts": int(user_drivers['Pos_100'].sum()), 
            "150L Pts": int(user_drivers['Pos_150'].sum()), 
            "Final Pts": int(user_drivers['Pos_Final'].sum())
        })
    master_df = pd.DataFrame(leaderboard_data).sort_values(by="Starting Pts")
    master_df["Start Place"] = range(1, len(master_df) + 1)
    return master_df

# App Navigation Layout
t2, t4, t5, t3, t1 = st.tabs(["📝 Draft Drivers", "📋 View Rosters", "📊 Popular Picks", "🏁 Milestone Ranks", "🏆 Standings"])

# --- VIEW 2: HARD-VALIDATED DRAFT BOARD ---
with t2:
    st.markdown("Select exactly **8 drivers**. Maximum **3 from Rows 1-3**.")
    
    entry_name = st.text_input("Enter Roster Submission Name:", key="new_user_name", placeholder="e.g., Sarah - Lineup 1").strip()
    
    if "selected_pool" not in st.session_state:
        st.session_state["selected_pool"] = []
        
    current_picks = st.session_state["selected_pool"]
    count_picked = len(current_picks)
    count_tier = df[df['Driver'].isin(current_picks) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    c1, c2 = st.columns(2)
    c1.metric("Drivers Picked", f"{count_picked} / 8", delta=None if count_picked <= 8 else "Too Many!", delta_color="inverse")
    c2.metric("Top-Tier Rows 1-3", f"{count_tier} / 3", delta=None if count_tier <= 3 else "Limit Exceeded!", delta_color="inverse")
    
    can_submit = (count_picked == 8 and count_tier <= 3 and entry_name and entry_name not in picks_df['Participant'].values)
    
    if st.button("Submit Official Roster Lineup", type="primary", disabled=not can_submit):
        new_entry = pd.DataFrame([{
            "Participant": entry_name,
            "P1": current_picks[0], "P2": current_picks[1], "P3": current_picks[2], "P4": current_picks[3],
            "P5": current_picks[4], "P6": current_picks[5], "P7": current_picks[6], "P8": current_picks[7]
        }])
        updated_df = pd.concat([picks_df, new_entry], ignore_index=True)
        updated_df.to_csv(PICK_FILE, index=False)
        
        st.success(f"Success! '{entry_name}' lineup was successfully submitted.")
        st.session_state["selected_pool"] = []
        st.rerun()

    st.write("---")
    
    if count_picked != 8 and count_picked > 0:
        st.warning(f"Lineup must contain exactly 8 choices. You currently have {count_picked}.")
    if count_tier > 3:
        st.error(f"Limit Exceeded: You have {count_tier} top-tier drivers (Max 3).")
    
    for idx, row in df.iterrows():
        d_name = row['Driver']
        is_selected = d_name in st.session_state["selected_pool"]
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader(d_name)
                st.caption(f"#{row['Car_Num']} | {row['Team']} | Pos: {row['Starting_Pos']}")
                if row['Tier_1_3'] == "Yes": st.markdown("⭐ *Row 1-3 Premium*")
                
                if st.checkbox("Select Driver", key=f"draft_check_{idx}", value=is_selected):
                    if d_name not in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].append(d_name)
                        st.rerun()
                else:
                    if d_name in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].remove(d_name)
                        st.rerun()
            with col2:
                st.image(row['Car_Pic'])

# --- VIEW 4: VIEW ROSTERS ---
with t4:
    st.header("Submitted Rosters")
    if picks_df.empty:
        st.info("No rosters submitted yet.")
    else:
        for _, row in picks_df.iterrows():
            with st.expander(f"📋 {row['Participant']}"):
                roster_drivers = [row[f'P{i}'] for i in range(1, 9)]
                roster_details = df[df['Driver'].isin(roster_drivers)]
                st.dataframe(roster_details[["Starting_Pos", "Car_Num", "Driver", "Team"]], use_container_width=True, hide_index=True)

# --- VIEW 5: POPULAR PICKS ---
with t5:
    st.header("Pick Popularity")
    if picks_df.empty:
        st.info("No selection insights available yet.")
    else:
        all_picks = []
        for i in range(1, 9):
            all_picks.extend(picks_df[f'P{i}'].tolist())
        pick_counts = pd.DataFrame(all_picks, columns=['Driver']).value_counts().reset_index(name='Total Picks')
        
        pop_chart = alt.Chart(pick_counts).mark_bar(color='#ff0000').encode(
            x=alt.X('Total Picks:Q', title="Times Selected"),
            y=alt.Y('Driver:N', sort='-x', title="Driver Name")
        ).properties(height=400)
        st.altair_chart(pop_chart, use_container_width=True)

# --- VIEW 3: LIVE FIELD RUNNING ORDER (Milestone Ranks) ---
with t3:
    st.header("Milestone Ranks")
    sort_basis_label = st.selectbox(
        "Milestone to display:",
        options=["Starting Order", "Running Order @ Lap 100", "Running Order @ Lap 150", "Finishing Order"]
    )
    
    if sort_basis_label == "Running Order @ Lap 100":
        sort_by_col = "Pos_100"
        display_title = "Running Order @ Lap 100"
    elif sort_basis_label == "Running Order @ Lap 150":
        sort_by_col = "Pos_150"
        display_title = "Running Order @ Lap 150"
    elif sort_basis_label == "Finishing Order":
        sort_by_col = "Pos_Final"
        display_title = "Finishing Order"
    else:
        sort_by_col = "Starting_Pos"
        display_title = "Starting Order"

    st.write("---")
    st.subheader(display_title)
    
    sorted_df = df.copy()
    if sort_by_col != "Starting_Pos":
        sorted_df["sort_key"] = sorted_df[sort_by_col].apply(lambda x: 99 if x == 0 else x)
        sorted_df = sorted_df.sort_values(by=["sort_key", "Starting_Pos"], ascending=True)
    else:
        sorted_df = sorted_df.sort_values(by="Starting_Pos", ascending=True)
    
    for _, row in sorted_df.iterrows():
        with st.container(border=True):
            current_val = row[sort_by_col]
            metric_label = f"P{current_val}" if current_val != 0 else "--"
            st.metric(f"{sort_basis_label} Position", metric_label)
            st.subheader(row['Driver'])
            st.caption(f"#{row['Car_Num']} | {row['Team']}")
            
            st.image(row['Car_Pic'])
            
            if sort_basis_label == "Starting Order":
                st.markdown(f"🏁 Starting from **P{row['Starting_Pos']}**")
            else:
                pos_differential = int(row['Starting_Pos']) - int(row[sort_by_col])
                
                if sort_basis_label in ["Running Order @ Lap 100", "Running Order @ Lap 150"]:
                    status_text = f"(Start Position: **P{row['Starting_Pos']}** ➡️ Current Position: **P{row[sort_by_col]}**)"
                else: 
                    status_text = f"(Start Position: **P{row['Starting_Pos']}** ➡️ Finished: **P{row[sort_by_col]}**)"
                
                if current_val == 0:
                    st.markdown(f"📋 Started from **P{row['Starting_Pos']}**, telemetry data pending.")
                elif pos_differential > 0:
                    st.markdown(f"📈 **Gained {pos_differential} places** {status_text}.")
                elif pos_differential < 0:
                    st.markdown(f"📉 **Lost {abs(pos_differential)} places** {status_text}.")
                else:
                    st.markdown(f"↔️ **Held position** exactly {status_text}.")

# --- VIEW 1: STANDINGS ---
with t1:
    st.header("Standings")
    master_standings = calculate_master_standings()
    if not master_standings.empty:
        total_participants = len(master_standings)
        standings_chart_records = []
        for _, row in master_standings.iterrows():
            standings_chart_records.append({
                "Milestone": "Start", 
                "GraphPosition": (total_participants + 1) - row['Start Place'], 
                "Pool Participant": row['Name']
            })
        
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
