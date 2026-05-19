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
    /* Target the overall tab container bar */
    div[data-testid="stTabs"] {
        background-color: #f1f1f1 !important;
        padding: 4px 4px 0px 4px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #ff0000 !important;
    }

    /* Base styling for ALL tabs (unselected state) */
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

    /* High-intensity override to guarantee unselected text color visibility */
    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] button span {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }

    /* Active/Selected Tab styling (Stays Red background with White text) */
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
    
    /* Target images inside columns to center vertically and fit horizontally */
    [data-testid="stImage"] img {
        height: 100px !important;
        object-fit: contain !important;
        border-radius: 4px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    /* Ensure the column layout visually balances the text height and centers content */
    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    
    /* HORIZONTAL SCROLL FOR WIDE GRAPHS */
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
    
    /* MOBILE TEXT & WHITE BACKGROUND FIX FOR DATAFRAMES */
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
    /* Force left alignment specifically for the Participant Name column cells */
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
        "Car_Pic": [
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/10-DHL-SS.png?dp=05-11-2026T06:02PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/20-JavaHouse-SS.png?dp=05-11-2026T06:03PM",
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/12-Verizon-SS.png?dp=05-11-2026T06:02PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/60-SiriusXM-MorganWallen-SS.png?dp=05-11-2026T06:05PM",
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/14-HFOT-SS.png?dp=05-11-2026T06:03PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/5-Arrow-SS.png?dp=05-15-2026T08:23PM",
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/8-Sunoco-SS.png?dp=05-11-2026T06:02PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/23-Kingspan-SS.png?dp=05-11-2026T06:03PM",
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/3-Pennzoil-SS.png?dp=05-11-2026T06:01PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/9-PNCBank-SS.png?dp=05-11-2026T06:02PM",
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/76-Wedbush-SS.png?dp=05-11-2026T06:05PM", 
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/75-Amada-SS.png?dp=05-11-2026T06:05PM",
            "https://your-hosting-site.com/car-33.jpg", "https://your-hosting-site.com/car-6.jpg",
            "https://your-running-site.com/car-21.jpg", "https://your-hosting-site.com/car-66.jpg",
            "https://your-running-site.com/car-28.jpg", "https://your-hosting-site.com/car-7.jpg",
            "https://your-hosting-site.com/car-26.jpg", "https://your-hosting-site.com/car-6b.jpg",
            "https://your-running-site.com/car-45.jpg", "https://your-hosting-site.com/car-31.jpg",
            "https://your-running-site.com/car-2.jpg",  "https://your-hosting-site.com/car-18.jpg",
            "https://your-hosting-site.com/car-27.jpg", "https://your-hosting-site.com/car-11.jpg",
            "https://your-hosting-site.com/car-47.jpg", "https://your-hosting-site.com/car-15.jpg",
            "https://your-hosting-site.com/car-19.jpg", "https://your-hosting-site.com/car-51.jpg",
            "https://your-running-site.com/car-77.jpg", "https://your-hosting-site.com/car-4.jpg",
            "https://your-hosting-site.com/car-24.jpg"
        ]
    }
    return pd.DataFrame(data)

# 2. Sync Race Positions Database
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

# 3. Synchronize Participant CSV Database
PICK_FILE = "picks.csv"
def load_picks():
    if os.path.exists(PICK_FILE):
        return pd.read_csv(PICK_FILE)
    return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

# Helper function to generate current standings calculations
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

# 4. Navigation Layout using native st.tabs
tab_names = ["🏆 Standings", "📝 Draft Drivers", "🏁 Milestone Ranks", "📋 View Rosters", "📊 Popular Picks"]
t1, t2, t3, t4, t5 = st.tabs(tab_names)

# --- VIEW 1: OVERALL STANDINGS ---
with t1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged yet. Select the 'Draft Drivers' tab above to add yours!")
    else:
        master_df = calculate_master_standings()
        
        # --- SCROLLABLE PERFORMANCE TRACKER ---
        total_participants = len(master_df)
        standings_milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        
        field_chart_records = []
        for _, p_row in master_df.iterrows():
            places = [p_row['Start Place'], p_row['100L Place'], p_row['150L Place'], p_row['Final Place']]
            for m_lbl, place_val in zip(standings_milestones, places):
                if m_lbl == "Start" or place_val != 0:
                    graph_coord = (total_participants + 1) - place_val
                    field_chart_records.append({
                        "Milestone": m_lbl,
                        "GraphPosition": graph_coord,
                        "RawDisplay": f"#{place_val}",
                        "Participant": p_row['Name']
                    })
                    
        if field_chart_records:
            field_chart_df = pd.DataFrame(field_chart_records)
            
            base_field = alt.Chart(field_chart_df).encode(
                x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True, labelAngle=0)),
                y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Rank", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True)),
                color=alt.Color('Participant:N', legend=alt.Legend(orient='bottom', direction='vertical', titleColor='black', labelColor='black'))
            )
            
            lines_field = base_field.mark_line(strokeWidth=3).encode()
            points_field = base_field.mark_circle(size=60)
            labels_field = base_field.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black').encode(text='RawDisplay:N')
            
            chart_obj = (lines_field + points_field + labels_field).properties(width=800, height=320, background='white').configure_axis(
                labelColor='black', titleColor='black'
            )
            
            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
            st.altair_chart(chart_obj, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("ℹ️ Swipe right on the graph above to track later race milestones.")
            st.write("---")

        column_order = ["Final Place", "Name", "Final Pts", "100L Pts", "150L Pts"]
        master_df = master_df[column_order].sort_values(by=["Final Place", "Name"])

        st.dataframe(
            master_df, 
            column_config={
                "Final Place": st.column_config.NumberColumn("Rank", format="%d"),
                "Name": st.column_config.TextColumn("Participant"),
                "Final Pts": "Fin Pts",
                "100L Pts": "Lap 100",
                "150L Pts": "Lap 150"
            },
            use_container_width=True, 
            hide_index=True
        )

# --- VIEW 2: HARD-VALIDATED DRAFT BOARD ---
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
            col1, col2, col3 = st.columns([1.2, 2.8, 4.0])
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
        st.error(f"⚠️ Blocked: Lineup must contain exactly 8 choices. You currently have {count_picked} selected.")
        can_submit = False
    if count_tier > 3:
        st.error(f"⚠️ Blocked: You have selected {count_tier} drivers from Rows 1-3. The absolute tier limit is 3.")
        can_submit = False
    if not entry_name:
        st.warning("Please input a distinct Submission Name above to activate the lock-in button.")
        can_submit = False
    elif entry_name in picks_df['Participant'].values:
        st.error(f"⚠️ Blocked: A lineup entry named '{entry_name}' has already been submitted. Use a new modifier label.")
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

# --- VIEW 3: LIVE FIELD RUNNING ORDER ---
with t3:
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
            col1, col2 = st.columns([4.0, 4.0])
            with col1:
                current_val = row[sort_by_col]
                metric_label = f"P{current_val}" if current_val != 0 else "--"
                st.metric("Current Order", metric_label)
                st.subheader(row['Driver'])
                st.caption(f"#{row['Car_Num']} | {row['Team']}")
                
                # --- INDIVIDUAL FIELD DRIVER PROFILE CHART ---
                m_labels = ["Start", "Lap 100", "Lap 150", "Finish"]
                m_vals = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
                
                driver_history = []
                for lbl, val in zip(m_labels, m_vals):
                    if lbl == "Start" or val != 0:
                        driver_history.append({"Milestone": lbl, "GraphPosition": 34 - val, "RawDisplay": f"P{val}"})
                        
                if len(driver_history) > 1:
                    single_driver_df = pd.DataFrame(driver_history)
                    
                    base = alt.Chart(single_driver_df).encode(
                        x=alt.X('Milestone:N', sort=m_labels, title="Milestone", axis=alt.Axis(grid=True, domain=True)),
                        y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Rank", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                    )
                    
                    lines = base.mark_line(color="#ff4b4b").encode()
                    points = base.mark_circle(size=60, color="#ff4b4b")
                    labels = base.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black').encode(text='RawDisplay:N')
                    
                    chart_render = (lines + points + labels).properties(height=175, background='white').configure_axis(
                        labelColor='black', titleColor='black'
                    )
                    st.altair_chart(chart_render, use_container_width=True)
            with col2:
                st.image(row['Car_Pic'])

    # --- MOVING TIMING TOWER MANAGEMENT SECTION TO BOTTOM ---
    st.write("---")
    with st.expander("🛠️ Live Race Timing Tower Management (Input Milestone Positions Here)"):
        st.markdown("Select placement ranks via the dropdown boxes. Uncompleted points map safely to `0`.")
        
        position_dropdown_choices = list(range(34))
        
        updated_rows = []
        for idx, row in df.sort_values(by="Starting_Pos").iterrows():
            st.markdown(f"**#{row['Car_Num']} - {row['Driver']}**")
            box1, box2, box3, box4 = st.columns(4)
            
            with box1:
                st.selectbox("Grid Start", options=[int(row['Starting_Pos'])], disabled=True, key=f"start_drop_{idx}")
            with box2:
                p100_val = st.selectbox("Pos @ 100 Laps", options=position_dropdown_choices, index=int(row['Pos_100']), key=f"p100_drop_{idx}")
            with box3:
                p150_val = st.selectbox("Pos @ 150 Laps", options=position_dropdown_choices, index=int(row['Pos_150']), key=f"p150_drop_{idx}")
            with box4:
                pfin_val = st.selectbox("Finish Position", options=position_dropdown_choices, index=int(row['Pos_Final']), key=f"pfin_drop_{idx}")
                
            updated_rows.append({
                "Driver": row['Driver'],
                "Pos_100": p100_val,
                "Pos_150": p150_val,
                "Pos_Final": pfin_val
            })
            st.write("---")
            
        if st.button("Save Race Positions", type="primary"):
            save_df = pd.DataFrame(updated_rows)
            save_df.to_csv(POSITIONS_FILE, index=False)
            st.success("Track intervals securely recorded!")
            st.rerun()

# --- VIEW 4: ROSTER VIEW ---
with t4:
    if picks_df.empty:
        st.info("No active rosters submitted.")
    else:
        user = st.selectbox("Whose roster would you like to see:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        # Check if the race is officially marked finished (sum of positions 1 to 33 equals 561)
        race_is_finished = df["Pos_Final"].sum() == 561
        
        # Sort by finishing placement if complete, else default down to earlier milestones or qualifying grid layout
        if race_is_finished:
            sort_basis = "Pos_Final"
        else:
            sort_basis = "Pos_150" if df["Pos_150"].sum() == 561 else ("Pos_100" if df["Pos_100"].sum() == 561 else "Starting_Pos")
            
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by=sort_basis)
        
        # --- PARTICIPANT OVERALL STANDINGS PLACE GRAPH ---
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
                    graph_coord = (total_participants + 1) - place_val
                    pool_chart_records.append({
                        "Milestone": m_lbl,
                        "GraphPosition": graph_coord,
                        "RawDisplay": f"#{place_val}"
                    })
            
            if len(pool_chart_records) > 1:
                pool_chart_df = pd.DataFrame(pool_chart_records)
                
                base_pool = alt.Chart(pool_chart_df).encode(
                    x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True)),
                    y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Rank", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                )
                
                lines_pool = base_pool.mark_line(color="#1f77b4", strokeWidth=3).encode()
                points_pool = base_pool.mark_circle(size=70, color="#1f77b4")
                labels_pool = base_pool.mark_text(align='left', dx=8, dy=-8, fontStyle='bold', fontSize=12, color='black').encode(text='RawDisplay:N')
                
                chart_render_pool = (lines_pool + points_pool + labels_pool).properties(height=160, background='white').configure_axis(
                    labelColor='black', titleColor='black'
                )
                st.altair_chart(chart_render_pool, use_container_width=True)
                st.caption("ℹ️ Upward trending lines mean you are climbing towards 1st place.")
        
        st.write("---")
        
        # --- ROSTER WIDE MULTI-DRIVER LINE GRAPH ---
        st.subheader("Driver lineup progression")
        chart_records = []
        milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        
        for _, row in u_df.iterrows():
            points = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
            for m_label, pt in zip(milestones, points):
                if m_label == "Start" or pt != 0:
                    chart_records.append({
                        "Milestone": m_label,
                        "GraphPosition": 34 - pt,
                        "RawDisplay": f"P{pt}",
                        "Driver": f"{row['Driver']} (# {row['Car_Num']})"
                    })
                    
        if chart_records:
            chart_df = pd.DataFrame(chart_records)
            
            base_multi = alt.Chart(chart_df).encode(
                x=alt.X('Milestone:N', sort=milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True)),
                y=alt.Y(
                    'GraphPosition:Q', 
                    scale=alt.Scale(domain=[1, 33]), 
                    title="Rank", 
                    axis=alt.Axis(
                        grid=True, 
                        domain=True, 
                        tickCount=7, 
                        labels=False, 
                        ticks=False
                    )
                ),
                color=alt.Color('Driver:N', legend=alt.Legend(orient='bottom', direction='vertical', titleColor='black', labelColor='black'))
            )
            
            lines_multi = base_multi.mark_line(strokeWidth=2.5).encode()
            points_multi = base_multi.mark_circle(size=55)
            labels_multi = base_multi.mark_text(align='left', dx=6, dy=-6, fontStyle='bold', fontSize=10, color='black').encode(text='RawDisplay:N')
            
            chart_render_multi = (lines_multi + points_multi + labels_multi).properties(
                height=520, 
                background='white'
            ).configure_axis(
                labelColor='black', titleColor='black'
            )
            st.altair_chart(chart_render_multi, use_container_width=True)
            
        st.write("---")
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4.0, 4.0])
                with col1:
                    # Using st.subheader() here enforces visual match with draft board profile sizes
                    st.subheader(row['Driver'])
                    st.caption(f"#{row['Car_Num']} | {row['Team']}")
                    st.caption(f"Start: P{row['Starting_Pos']} | Lap 100: P{row['Pos_100']} | Lap 150: P{row['Pos_150']} | Finish: P{row['Pos_Final']}")
                    
                    # Compute & render positional shift if the race is completed
                    if race_is_finished:
                        pos_differential = int(row['Starting_Pos']) - int(row['Pos_Final'])
                        if pos_differential > 0:
                            st.markdown(f"📈 **Gained {pos_differential} places** during the race.")
                        elif pos_differential < 0:
                            st.markdown(f"📉 **Lost {abs(pos_differential)} places** during the race.")
                        else:
                            st.markdown("↔️ **Held position** exactly from grid position to checkered flag.")
                            
                with col2:
                    st.image(row['Car_Pic'])

# --- VIEW 5: POPULAR PICKS METRICS ---
with t5:
    st.header("Participant Pick Summary")
    if picks_df.empty:
        st.info("No picks drafted yet.")
    else:
        driver_pick_map = {driver: [] for driver in df['Driver'].tolist()}
        for _, row in picks_df.iterrows():
            p_name = row['Participant']
            for p in [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]:
                if p in driver_pick_map:
                    driver_pick_map[p].append(p_name)
                    
        for _, row in df.sort_values(by="Starting_Pos").iterrows():
            d_name = row['Driver']
            choosing_p = driver_pick_map[d_name]
            with st.container(border=True):
                col1, col2 = st.columns([4.0, 4.0])
                with col1:
                    st.subheader(d_name)
                    st.caption(f"Car #{row['Car_Num']} | Start: P{row['Starting_Pos']}")
                    if choosing_p:
                        st.markdown(f"**Drafted By:** {', '.join(choosing_p)}")
                    else:
                        st.markdown("*Nobody has drafted this driver yet.*")
                        
                    # --- POPULAR PICKS INDIVIDUAL DRIVER PROFILE CHART ---
                    m_labels = ["Start", "Lap 100", "Lap 150", "Finish"]
                    m_vals = [row['Starting_Pos'], row['Pos_100'], row['Pos_150'], row['Pos_Final']]
                    
                    driver_history = []
                    for lbl, val in zip(m_labels, m_vals):
                        if lbl == "Start" or val != 0:
                            driver_history.append({"Milestone": lbl, "GraphPosition": 34 - val, "RawDisplay": f"P{val}"})
                            
                    if len(driver_history) > 1:
                        single_driver_df = pd.DataFrame(driver_history)
                        
                        base_pop = alt.Chart(single_driver_df).encode(
                            x=alt.X('Milestone:N', sort=m_labels, title="Milestone", axis=alt.Axis(grid=True, domain=True)),
                            y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Rank", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                        )
                        
                        lines_pop = base_pop.mark_line(color="#ff4b4b").encode()
                        points_pop = base_pop.mark_circle(size=60, color="#ff4b4b")
                        labels_pop = base_pop.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black').encode(text='RawDisplay:N')
                        
                        chart_render_pop = (lines_pop + points_pop + labels_pop).properties(height=175, background='white').configure_axis(
                            labelColor='black', titleColor='black'
                        )
                        st.altair_chart(chart_render_pop, use_container_width=True)
                with col2:
                    st.image(row['Car_Pic'])

# --- SYSTEM ADMIN COMMAND DECK ---
st.write("---")
with st.expander("🛠️ Admin Command Deck (Edit / Delete Entry Controls)"):
    
    st.subheader("Reset Race Milestone Positions")
    st.markdown("Use this during testing to instantly clear all manual inputs for Lap 100, Lap 150, and Final standings, resetting fields clean to 0.")
    
    if st.button("Clear Milestone Data & Reset Field", type="secondary"):
        if os.path.exists(POSITIONS_FILE):
            os.remove(POSITIONS_FILE)
        st.success("All test milestones successfully cleared back to 0!")
        st.rerun()
        
    st.write("---")

    if picks_df.empty:
        st.info("No participant records currently stored to edit.")
    else:
        st.subheader("Delete an Entry Profile Lineup")
        delete_target = st.selectbox("Select Entry to Permanently Delete:", picks_df['Participant'].tolist(), key="admin_del_select")
        
        if st.button("Permanently Delete Roster", type="primary"):
            updated_picks = picks_df[picks_df['Participant'] != delete_target]
            updated_picks.to_csv(PICK_FILE, index=False)
            st.success(f"Successfully erased profile data for: {delete_target}")
            st.rerun()
