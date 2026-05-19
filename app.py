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
        background-position: 0 0, 0 20px, 20px -20px, -20px 0px;
        background-color: #ffffff !important;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp small, .stMarkdown p {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

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

# 1. Base Data with Updated Alex Palou Headshot Link
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
            "Meyer Shank Racing", "Andretti Global", "Arrow McLaren", "Andretti Global", "Arrow McLaren", 
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
        "Driver_Pic": [
            "https://www.indycar.com/-/media/IndyCar/Drivers/Headshots/2025/Alex-Palou.png",  # Updated with official image file path
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150"
        ],
        "Car_Pic": [
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100",  
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100", 
            "https://via.placeholder.com/300x100",
            "https://via.placeholder.com/300x100"
        ]
    }
    return pd.DataFrame(data)

POSITIONS_FILE = "race_positions.csv"
def load_race_positions():
    base_df = get_base_drivers()
    if os.path.exists(POSITIONS_FILE):
        pos_df = pd.read_csv(POSITIONS_FILE)
        if all(col in pos_df.columns for col in ["Driver", "Pos_100", "Pos_150", "Pos_Final"]):
            return pd.merge(base_df, pos_df[["Driver", "Pos_100", "Pos_150", "Pos_Final"]], on="Driver", how="left")
    
    base_df["Pos_100"] = 0
    base_df["Pos_150"] = 0
    base_df["Pos_Final"] = 0
    return base_df

df = load_race_positions()

PICK_FILE = "picks.csv"
def load_picks():
    if os.path.exists(PICK_FILE):
        return pd.read_csv(PICK_FILE)
    return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

def calculate_master_standings():
    if picks_df.empty:
        return pd.DataFrame()
    
    leaderboard_data = []
    for _, row in picks_df.iterrows():
        user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
        user_drivers = df[df['Driver'].isin(user_picks)]
        
        score_start = user_drivers['Starting_Pos'].sum()
        score_100 = user_drivers['Pos_100'].sum()
        score_150 = user_drivers['Pos_150'].sum()
        score_final = user_drivers['Pos_Final'].sum()

        leaderboard_data.append({
            "Name": row['Participant'],
            "Starting Pts": int(score_start),
            "100L Pts": int(score_100),
            "150L Pts": int(score_150),
            "Final Pts": int(score_final)
        })
        
    master_df = pd.DataFrame(leaderboard_data)
    master_df = master_df.sort_values(by="Starting Pts", ascending=True)
    master_df["Start Place"] = range(1, len(master_df) + 1)
    
    if not (df['Pos_100'] == 0).all():
        master_df = master_df.sort_values(by="100L Pts", ascending=True)
        master_df["100L Place"] = range(1, len(master_df) + 1)
    else:
        master_df["100L Place"] = 0

    if not (df['Pos_150'] == 0).all():
        master_df = master_df.sort_values(by="150L Pts", ascending=True)
        master_df["150L Place"] = range(1, len(master_df) + 1)
    else:
        master_df["150L Place"] = 0

    if not (df['Pos_Final'] == 0).all():
        master_df = master_df.sort_values(by="Final Pts", ascending=True)
        master_df["Final Place"] = range(1, len(master_df) + 1)
    else:
        master_df["Final Place"] = 0
        
    return master_df

tab_names = ["📝 Draft Drivers", "📋 View Rosters", "📊 Popular Picks", "🏁 Milestone Ranks", "🏆 Standings"]
t2, t4, t5, t3, t1 = st.tabs(tab_names)

# --- VIEW 2: DRAFT BOARD ---
with t2:
    st.markdown("Select exactly **8 drivers**. Maximum **3 from Rows 1-3**.")
    entry_name = st.text_input("Enter Roster Submission Name:", key="new_user_name", placeholder="e.g., Sarah - Lineup 1").strip()
    
    if "selected_pool" not in st.session_state:
        st.session_state["selected_pool"] = []
        
    st.write("---")
    
    for idx, row in df.iterrows():
        d_name = row['Driver']
        is_selected = d_name in st.session_state["selected_pool"]
        
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1.2, 2.5, 1.2, 3.5])
            with col1:
                st.write(f"**Start Pos: {row['Starting_Pos']}**")
                st.caption(f"⏱️ {row['Qual_Speed']}")
                if row['Tier_1_3'] == "Yes":
                    st.markdown("⭐ *Row 1-3*")
            with col2:
                st.subheader(d_name)
                st.caption(f"#{row['Car_Num']} | {row['Team']}")
                
                box_label = "🟢 Selected" if is_selected else "Select Driver"
                if st.checkbox(box_label, key=f"draft_check_{idx}", value=is_selected):
                    if d_name not in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].append(d_name)
                        st.rerun()
                else:
                    if d_name in st.session_state["selected_pool"]:
                        st.session_state["selected_pool"].remove(d_name)
                        st.rerun()
            with col3:
                st.image(row['Driver_Pic'], width=85)
            with col4:
                st.image(row['Car_Pic'])

    st.write("---")
    current_picks = st.session_state["selected_pool"]
    count_picked = len(current_picks)
    count_tier = df[df['Driver'].isin(current_picks) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    c1, c2 = st.columns(2)
    c1.metric("Drivers Picked (Must be 8)", f"{count_picked} / 8", delta=None if count_picked <= 8 else "Too Many!", delta_color="inverse")
    c2.metric("Top-Tier Rows 1-3 (Max 3)", f"{count_tier} / 3", delta=None if count_tier <= 3 else "Limit Exceeded!", delta_color="inverse")
    
    can_submit = True
    if count_picked != 8:
        st.error(f"⚠️ Blocked: Lineup must contain exactly 8 choices.")
        can_submit = False
    if count_tier > 3:
        st.error(f"⚠️ Blocked: Maximum tier allowance exceeded.")
        can_submit = False
    if not entry_name:
        st.warning("Please input a distinct Submission Name above to activate the lock-in button.")
        can_submit = False
    elif entry_name in picks_df['Participant'].values:
        st.error(f"⚠️ Blocked: A lineup entry named '{entry_name}' has already been submitted.")
        can_submit = False

    if st.button("Submit Official Roster Lineup", type="primary", disabled=not can_submit):
        new_entry = pd.DataFrame([{
            "Participant": entry_name,
            "P1": current_picks[0], "P2": current_picks[1], "P3": current_picks[2], "P4": current_picks[3],
            "P5": current_picks[4], "P6": current_picks[5], "P7": current_picks[6], "P8": current_picks[7]
        }])
        updated_df = pd.concat([picks_df, new_entry], ignore_index=True)
        updated_df.to_csv(PICK_FILE, index=False)
        st.session_state["selected_pool"] = []
        st.rerun()

# --- VIEW 4: ROSTER VIEW ---
with t4:
    if picks_df.empty:
        st.info("No active rosters submitted.")
    else:
        user = st.selectbox("Whose roster would you like to see:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        race_is_finished = df["Pos_Final"].sum() == 561
        sort_basis = "Pos_Final" if race_is_finished else ("Pos_150" if df["Pos_150"].sum() == 561 else ("Pos_100" if df["Pos_100"].sum() == 561 else "Starting_Pos"))
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by=sort_basis)
        
        st.subheader(f"{user}'s Quest for Milk Drinking Immortality")
        master_standings = calculate_master_standings()
        
        if not master_standings.empty:
            p_history = master_standings[master_standings['Name'] == user].iloc[0]
            total_participants = len(master_standings)
            standings_milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
            standings_places = [p_history['Start Place'], p_history['100L Place'], p_history['150L Place'], p_history['Final Place']]
            
            pool_chart_records = []
            for m_lbl, place_val in zip(standings_milestones, standings_places):
                if m_lbl == "Start" or place_val != 0:
                    pool_chart_records.append({"Milestone": m_lbl, "GraphPosition": (total_participants + 1) - place_val, "RawDisplay": f"#{place_val}"})
            
            if len(pool_chart_records) > 1:
                chart_render_pool = alt.Chart(pd.DataFrame(pool_chart_records)).encode(
                    x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone"),
                    y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Rank", axis=alt.Axis(labels=False, ticks=False))
                ).mark_line(color="#1f77b4", strokeWidth=3) + alt.Chart(pd.DataFrame(pool_chart_records)).encode(
                    x=alt.X('Milestone:N', sort=standings_milestones), y=alt.Y('GraphPosition:Q')
                ).mark_circle(size=70, color="#1f77b4") + alt.Chart(pd.DataFrame(pool_chart_records)).encode(
                    x=alt.X('Milestone:N', sort=standings_milestones), y=alt.Y('GraphPosition:Q'), text='RawDisplay:N'
                ).mark_text(align='left', dx=8, dy=-8, fontStyle='bold', fontSize=12, color='black')
                st.altair_chart(chart_render_pool.properties(height=160, background='white'), use_container_width=True)
        
        st.write("---")
        st.subheader("Driver lineup progression")
        chart_records = []
        milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        
        for _, row in u_df.iterrows():
            points = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
            for m_label, pt in zip(milestones, points):
                if m_label == "Start" or pt != 0:
                    chart_records.append({"Milestone": m_label, "GraphPosition": 34 - pt, "RawDisplay": f"P{pt}", "Driver": f"{row['Driver']} (# {row['Car_Num']})"})
                    
        if chart_records:
            chart_render_multi = alt.Chart(pd.DataFrame(chart_records)).encode(
                x=alt.X('Milestone:N', sort=milestones, title="Race Milestone"),
                y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Rank", axis=alt.Axis(labels=False, ticks=False)),
                color=alt.Color('Driver:N', legend=alt.Legend(orient='bottom', direction='vertical'))
            ).mark_line(strokeWidth=2.5) + alt.Chart(pd.DataFrame(chart_records)).encode(
                x=alt.X('Milestone:N', sort=milestones), y=alt.Y('GraphPosition:Q'), color='Driver:N'
            ).mark_circle(size=55) + alt.Chart(pd.DataFrame(chart_records)).encode(
                x=alt.X('Milestone:N', sort=milestones), y=alt.Y('GraphPosition:Q'), color='Driver:N', text='RawDisplay:N'
            ).mark_text(align='left', dx=6, dy=-6, fontStyle='bold', fontSize=10, color='black')
            st.altair_chart(chart_render_multi.properties(height=520, background='white'), use_container_width=True)
            
        st.write("---")
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3.5, 1.2, 3.3])
                with col1:
                    st.subheader(row['Driver'])
                    st.caption(f"#{row['Car_Num']} | {row['Team']}")
                    st.caption(f"Start: P{row['Starting_Pos']} | Lap 100: P{row['Pos_100']} | Lap 150: P{row['Pos_150']} | Finish: P{row['Pos_Final']}")
                    if race_is_finished:
                        pos_differential = int(row['Starting_Pos']) - int(row['Pos_Final'])
                        st.markdown(f"📈 **Gained {pos_differential} places**" if pos_differential > 0 else (f"📉 **Lost {abs(pos_differential)} places**" if pos_differential < 0 else "↔️ **Held position**"))
                with col2:
                    st.image(row['Driver_Pic'], width=85)
                with col3:
                    st.image(row['Car_Pic'])

# --- VIEW 5: POPULAR PICKS ---
with t5:
    st.header("Who drafted who?")
    if picks_df.empty:
        st.info("No picks drafted yet.")
    else:
        driver_pick_map = {driver: [] for driver in df['Driver'].tolist()}
        for _, row in picks_df.iterrows():
            p_name = row['Participant']
            for p in [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]:
                if p in driver_pick_map:
                    driver_pick_map[p].append(p_name)
                    
        df_sorted = df.copy()
        df_sorted['Pick_Count'] = df_sorted['Driver'].map(lambda x: len(driver_pick_map[x]))
        df_sorted = df_sorted.sort_values(by=["Pick_Count", "Starting_Pos"], ascending=[False, True])
                        
        for _, row in df_sorted.iterrows():
            d_name = row['Driver']
            choosing_p = driver_pick_map[d_name]
            
            with st.container(border=True):
                head_col1, head_col2 = st.columns([4.0, 1.0])
                with head_col1:
                    st.subheader(d_name)
                    st.caption(f"Car #{row['Car_Num']} | Start: P{row['Starting_Pos']} | Total Drafts: {len(choosing_p)}")
                with head_col2:
                    st.image(row['Driver_Pic'], width=75)
                
                st.image(row['Car_Pic'])
                
                if choosing_p:
                    st.markdown(f"**Drafted By:** {', '.join(choosing_p)}")
                else:
                    st.markdown("*Nobody has drafted this driver yet.*")
                    
                m_labels = ["Start", "Lap 100", "Lap 150", "Finish"]
                m_vals = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
                
                driver_history = []
                for lbl, val in zip(m_labels, m_vals):
                    if lbl == "Start" or val != 0:
                        driver_history.append({"Milestone": lbl, "GraphPosition": 34 - val, "RawDisplay": f"P{val}"})
                        
                if len(driver_history) > 1:
                    chart_render_pop = alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels, title="Milestone"),
                        y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Rank", axis=alt.Axis(labels=False, ticks=False))
                    ).mark_line(color="#ff4b4b") + alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels), y=alt.Y('GraphPosition:Q')
                    ).mark_circle(size=60, color="#ff4b4b") + alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels), y=alt.Y('GraphPosition:Q'), text='RawDisplay:N'
                    ).mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black')
                    st.altair_chart(chart_render_pop.properties(height=140, background='white'), use_container_width=True)

# --- VIEW 3: LIVE FIELD RUNNING ORDER ---
with t3:
    sort_basis_label = st.selectbox("Milestone to display:", options=["Starting Order", "Running Order @ Lap 100", "Running Order @ Lap 150", "Finishing Order"])
    sort_by_col = "Pos_Final" if sort_basis_label == "Finishing Order" else ("Pos_150" if sort_basis_label == "Running Order @ Lap 150" else ("Pos_100" if sort_basis_label == "Running Order @ Lap 100" else "Starting_Pos"))

    st.write("---")
    st.subheader(sort_basis_label)
    
    sorted_df = df.copy()
    if sort_by_col != "Starting_Pos":
        sorted_df["sort_key"] = sorted_df[sort_by_col].apply(lambda x: 99 if x == 0 else x)
        sorted_df = sorted_df.sort_values(by=["sort_key", "Starting_Pos"], ascending=True)
    else:
        sorted_df = sorted_df.sort_values(by="Starting_Pos", ascending=True)
    
    for _, row in sorted_df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4.0, 4.0])
            with col1:
                st.metric("Current Order", f"P{row[sort_by_col]}" if row[sort_by_col] != 0 else "--")
                st.subheader(row['Driver'])
                st.caption(f"#{row['Car_Num']} | {row['Team']}")
                
                m_labels = ["Start", "Lap 100", "Lap 150", "Finish"]
                m_vals = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
                driver_history = [{"Milestone": lbl, "GraphPosition": 34 - val, "RawDisplay": f"P{val}"} for lbl, val in zip(m_labels, m_vals) if lbl == "Start" or val != 0]
                        
                if len(driver_history) > 1:
                    chart_render = alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels, title="Milestone"),
                        y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Rank", axis=alt.Axis(labels=False, ticks=False))
                    ).mark_line(color="#ff4b4b") + alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels), y=alt.Y('GraphPosition:Q')
                    ).mark_circle(size=60, color="#ff4b4b") + alt.Chart(pd.DataFrame(driver_history)).encode(
                        x=alt.X('Milestone:N', sort=m_labels), y=alt.Y('GraphPosition:Q'), text='RawDisplay:N'
                    ).mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black')
                    st.altair_chart(chart_render.properties(height=175, background='white'), use_container_width=True)
            with col2:
                st.image(row['Car_Pic'])

    st.write("---")
    with st.expander("🛠️ Live Race Timing Tower Management"):
        updated_rows = []
        for idx, row in df.sort_values(by="Starting_Pos").iterrows():
            st.markdown(f"**#{row['Car_Num']} - {row['Driver']}**")
            box1, box2, box3, box4 = st.columns(4)
            with box1: st.selectbox("Grid Start", options=[int(row['Starting_Pos'])], disabled=True, key=f"start_drop_{idx}")
            with box2: p100_val = st.selectbox("Pos @ 100 Laps", options=list(range(34)), index=int(row['Pos_100']), key=f"p100_drop_{idx}")
            with box3: p150_val = st.selectbox("Pos @ 150 Laps", options=list(range(34)), index=int(row['Pos_150']), key=f"p150_drop_{idx}")
            with box4: pfin_val = st.selectbox("Finish Position", options=list(range(34)), index=int(row['Pos_Final']), key=f"pfin_drop_{idx}")
            updated_rows.append({"Driver": row['Driver'], "Pos_100": p100_val, "Pos_150": p150_val, "Pos_Final": pfin_val})
            st.write("---")
            
        if st.button("Save Race Positions", type="primary"):
            pd.DataFrame(updated_rows).to_csv(POSITIONS_FILE, index=False)
            st.success("Track intervals securely recorded!")
            st.rerun()

# --- VIEW 1: OVERALL STANDINGS ---
with t1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged yet.")
    else:
        master_df = calculate_master_standings()
        total_participants = len(master_df)
        standings_milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        
        field_chart_records = []
        for _, p_row in master_df.iterrows():
            places = [p_row['Start Place'], p_row['100L Place'], p_row['150L Place'], p_row['Final Place']]
            for m_lbl, place_val in zip(standings_milestones, places):
                if m_lbl == "Start" or place_val != 0:
                    field_chart_records.append({"Milestone": m_lbl, "GraphPosition": (total_participants + 1) - place_val, "RawDisplay": f"#{place_val}", "Participant": p_row['Name']})
                    
        if field_chart_records:
            chart_obj = alt.Chart(pd.DataFrame(field_chart_records)).encode(
                x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone", axis=alt.Axis(labelAngle=0)),
                y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Rank", axis=alt.Axis(labels=False, ticks=False)),
                color=alt.Color('Participant:N', legend=alt.Legend(orient='bottom', direction='vertical'))
            ).mark_line(strokeWidth=3) + alt.Chart(pd.DataFrame(field_chart_records)).encode(
                x=alt.X('Milestone:N', sort=standings_milestones), y=alt.Y('GraphPosition:Q'), color='Participant:N'
            ).mark_circle(size=60) + alt.Chart(pd.DataFrame(field_chart_records)).encode(
                x=alt.X('Milestone:N', sort=standings_milestones), y=alt.Y('GraphPosition:Q'), color='Participant:N', text='RawDisplay:N'
            ).mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black')
            
            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
            st.altair_chart(chart_obj.properties(width=800, height=320, background='white'), use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("---")

        master_df = master_df[["Final Place", "Name", "Final Pts", "100L Pts", "150L Pts"]].sort_values(by=["Final Place", "Name"])
        st.dataframe(master_df, column_config={"Final Place": st.column_config.NumberColumn("Rank", format="%d"), "Name": st.column_config.TextColumn("Participant"), "Final Pts": "Fin Pts", "100L Pts": "Lap 100", "150L Pts": "Lap 150"}, use_container_width=True, hide_index=True)

# --- SYSTEM ADMIN COMMAND DECK ---
st.write("---")
with st.expander("🛠️ Admin Command Deck"):
    if st.button("Clear Milestone Data & Reset Field", type="secondary"):
        if os.path.exists(POSITIONS_FILE): os.remove(POSITIONS_FILE)
        st.success("All test milestones successfully cleared back to 0!")
        st.rerun()
    st.write("---")
    if not picks_df.empty:
        delete_target = st.selectbox("Select Entry to Permanently Delete:", picks_df['Participant'].tolist(), key="admin_del_select")
        if st.button("Permanently Delete Roster", type="primary"):
            picks_df[picks_df['Participant'] != delete_target].to_csv(PICK_FILE, index=False)
            st.success(f"Successfully erased profile data for: {delete_target}")
            st.rerun()
