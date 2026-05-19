import streamlit as st
import pandas as pd
import altair as alt
import os

# Page layout setup
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")

# Custom Styling: Checkered background pattern and clean table alignments
st.markdown("""
    <style>
    /* Set a clean, responsive checkered flag background pattern */
    .stApp {
        background-image: linear-gradient(45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(-45deg, rgba(200,200,200,0.15) 25%, transparent 25%), 
                          linear-gradient(45deg, transparent 75%, rgba(200,200,200,0.15) 75%), 
                          linear-gradient(-45deg, transparent 75%, rgba(200,200,200,0.15) 75%);
        background-size: 40px 40px;
        background-position: 0 0, 0 20px, 20px -20px, -20px 0px;
        background-color: #ffffff;
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
    
    /* MOBILE TEXT FIX: Force table container cells to display completely on narrow viewports */
    [data-testid="stDataFrame"] {
        width: 100% !important;
        overflow-x: auto;
    }
    [data-testid="stDataFrame"] div[data-testid="stTable"] th,
    [data-testid="stDataFrame"] div[data-testid="stTable"] td {
        text-align: center !important;
        white-space: normal !important; /* Forces text to wrap instead of cutting off */
        font-size: 13px !important;     /* Marginally smaller text for phone layouts */
        padding: 4px 6px !important;    /* Tighter padding to save real estate */
    }
    /* Force left alignment specifically for the Participant Name column cells */
    [data-testid="stDataFrame"] div[data-testid="stTable"] td:nth-child(2),
    [data-testid="stDataFrame"] div[data-testid="stTable"] th:nth-child(2) {
        text-align: left !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ Indy 500: VanGutz Style")

# 1. Base Starting Grid Data (All arrays carefully aligned to exactly 33 rows)
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
            "Juncos Hollinger", "A.J. Foyt Racing", "Dreyer & Reinbold"
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
            "https://your-hosting-site.com/car-10.jpg", "https://your-hosting-site.com/car-20.jpg",
            "https://your-hosting-site.com/car-12.jpg", "https://your-hosting-site.com/car-60.jpg",
            "https://your-hosting-site.com/car-14.jpg", "https://your-hosting-site.com/car-5.jpg",
            "https://your-hosting-site.com/car-8.jpg", "https://your-hosting-site.com/car-23.jpg",
            "https://your-hosting-site.com/car-3.jpg", "https://your-hosting-site.com/car-9.jpg",
            "https://your-hosting-site.com/car-76.jpg", "https://your-hosting-site.com/car-75.jpg",
            "https://your-hosting-site.com/car-33.jpg", "https://your-hosting-site.com/car-6.jpg",
            "https://your-hosting-site.com/car-21.jpg", "https://your-hosting-site.com/car-66.jpg",
            "https://your-hosting-site.com/car-28.jpg", "https://your-hosting-site.com/car-7.jpg",
            "https://your-hosting-site.com/car-26.jpg", "https://your-hosting-site.com/car-6b.jpg",
            "https://your-hosting-site.com/car-45.jpg", "https://your-hosting-site.com/car-31.jpg",
            "https://your-running-site.com/car-2.jpg",  "https://your-hosting-site.com/car-18.jpg",
            "https://your-hosting-site.com/car-27.jpg", "https://your-hosting-site.com/car-11.jpg",
            "https://your-hosting-site.com/car-47.jpg", "https://your-hosting-site.com/car-15.jpg",
            "https://your-hosting-site.com/car-19.jpg", "https://your-hosting-site.com/car-51.jpg",
            "https://your-hosting-site.com/car-77.jpg", "https://your-hosting-site.com/car-4.jpg",
            "https://your-hosting-site.com/car-24.jpg"
        ]
    }
    return pd.DataFrame(data)

# 2. Sync Race Positions Database (Tracks milestones across reloads)
POSITIONS_FILE = "race_positions.csv"
def load_race_positions():
    base_df = get_base_drivers()
    if os.path.exists(POSITIONS_FILE):
        pos_df = pd.read_csv(POSITIONS_FILE)
        if all(col in pos_df.columns for col in ["Driver", "Pos_100", "Pos_150", "Pos_Final"]):
            return pd.merge(base_df, pos_df[["Driver", "Pos_100", "Pos_150", "Pos_Final"]], on="Driver", how="left")
    
    # Starting conditions: Milestones default to 0
    base_df["Pos_100"] = 0
    base_df["Pos_150"] = 0
    base_df["Pos_Final"] = 0
    return base_df

df = load_race_positions()

# 3. Synchronize Participant CSV Database
PICKS_FILE = "picks.csv"
def load_picks():
    if os.path.exists(PICKS_FILE):
        return pd.read_csv(PICKS_FILE)
    return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

# Helper function to generate current standings calculations for historical mapping
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
    
    # Explicitly calculate placing sequences dynamically across intervals
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

# 4. Clear One-Click Navigation Layout
tab_options = ["🏆 Standings", "📝 Visual Draft Board", "🏁 Live Field", "📋 Roster View", "📊 Popular Picks"]

selected_tab = st.segmented_control(
    "Navigation Menu", 
    options=tab_options, 
    default="🏆 Standings",
    label_visibility="collapsed"
)

st.write("---")

# --- VIEW 1: OVERALL STANDINGS ---
if selected_tab == "🏆 Standings":
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged yet. Select the 'Visual Draft Board' menu above to add yours!")
    else:
        master_df = calculate_master_standings()
        
        # --- COMBINED PARTICIPANTS STANDINGS TRACKING CHART ---
        st.subheader("Pool Field Performance Tracker")
        total_participants = len(master_df)
        standings_milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        
        field_chart_records = []
        for _, p_row in master_df.iterrows():
            places = [p_row['Start Place'], p_row['100L Place'], p_row['150L Place'], p_row['Final Place']]
            for m_lbl, place_val in zip(standings_milestones, places):
                # Clean skip data markers if a given segment timeline hasn't finished yet
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
                x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True)),
                y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Pool Standing Rank (Top is 1st)", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True)),
                color='Participant:N'
            )
            
            lines_field = base_field.mark_line(strokeWidth=3).encode()
            points_field = base_field.mark_circle(size=60)
            labels_field = base_field.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11).encode(text='RawDisplay:N')
            
            st.altair_chart((lines_field + points_field + labels_field).properties(height=300), use_container_width=True)
            st.caption("ℹ️ Higher lines indicate superior pool standings. Ranks update live as milestone track coordinates change.")
            st.write("---")

        # Format layout ordering and sorting optimized for small mobile phone viewports
        column_order = [
            "Final Place", "Name", "Final Pts", "100L Pts", "150L Pts"
        ]
        master_df = master_df[column_order].sort_values(by=["Final Place", "Name"])

        st.dataframe(
            master_df, 
            column_config={
                "Final Place": st.column_config.NumberColumn("Rank", format="%d"),
                "Name": st.column_config.TextColumn("Participant"),
                "Final Pts": "Fin Pts",
                "100L Pts": "100L",
                "150L Pts": "150L"
            },
            use_container_width=True, 
            hide_index=True
        )

# --- VIEW 2: HARD-VALIDATED DRAFT BOARD ---
elif selected_tab == "📝 Visual Draft Board":
    st.header("Interactive Draft Field")
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
    st.subheader("Roster Validation Dashboard")
    
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
        updated_df.to_csv(PICKS_FILE, index=False)
        
        st.session_state["selected_pool"] = []
        st.rerun()

# --- VIEW 3: LIVE FIELD RUNNING ORDER ---
elif selected_tab == "🏁 Live Field":
    st.header("Actual Indy 500 Running Order")
    
    milestone_options = ["Start", "Lap 100", "Lap 150", "Finish"]
    selected_milestone = st.segmented_control(
        "Display Sort Metric:",
        options=milestone_options,
        default="Start"
    )
    
    if selected_milestone == "Lap 100":
        sort_by_col = "Pos_100"
        display_title = "Running Order @ Lap 100"
    elif selected_milestone == "Lap 150":
        sort_by_col = "Pos_150"
        display_title = "Running Order @ Lap 150"
    elif selected_milestone == "Finish":
        sort_by_col = "Pos_Final"
        display_title = "Final Track Finishing Order"
    else:
        sort_by_col = "Starting_Pos"
        display_title = "Official Initial Grid Ranks"

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
                st.markdown(f"🏁 **P{row['Pos_100']}** (100L) | **P{row['Pos_150']}** (150L) | **P{row['Pos_Final']}** (Fin)")
                
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
                        y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Track Position (Top is Lead)", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                    )
                    
                    lines = base.mark_line(color="#ff4b4b").encode()
                    points = base.mark_circle(size=60, color="#ff4b4b")
                    labels = base.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11).encode(text='RawDisplay:N')
                    
                    st.altair_chart((lines + points + labels).properties(height=175), use_container_width=True)
            with col2:
                st.image(row['Car_Pic'])

# --- VIEW 4: ROSTER VIEW ---
elif selected_tab == "📋 Roster View":
    st.header("Roster Inspection Profiles")
    if picks_df.empty:
        st.info("No active rosters submitted.")
    else:
        user = st.selectbox("Choose Entry Profile:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        sort_basis = "Pos_Final" if df["Pos_Final"].sum() == 561 else ("Pos_150" if df["Pos_150"].sum() == 561 else ("Pos_100" if df["Pos_100"].sum() == 561 else "Starting_Pos"))
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by=sort_basis)
        
        # --- PARTICIPANT OVERALL STANDINGS PLACE GRAPH ---
        st.subheader("Your Pool Standings Progress Tracker")
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
                    y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, total_participants]), title="Pool Standing Rank (Top is 1st)", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                )
                
                lines_pool = base_pool.mark_line(color="#1f77b4", strokeWidth=3).encode()
                points_pool = base_pool.mark_circle(size=70, color="#1f77b4")
                labels_pool = base_pool.mark_text(align='left', dx=8, dy=-8, fontStyle='bold', fontSize=12).encode(text='RawDisplay:N')
                
                st.altair_chart((lines_pool + points_pool + labels_pool).properties(height=160), use_container_width=True)
                st.caption("ℹ️ Charts track overall pool placement. Higher curves mean you are leading the standings ladder.")
        
        st.write("---")
        
        # --- ROSTER WIDE MULTI-DRIVER LINE GRAPH ---
        st.subheader("Lineup Milestone Progression Tracker")
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
                        "Driver": f"{row['Driver']} (#{row['Car_Num']})"
                    })
                    
        if chart_records:
            chart_df = pd.DataFrame(chart_records)
            
            base_multi = alt.Chart(chart_df).encode(
                x=alt.X('Milestone:N', sort=milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True)),
                y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Track Position Rank (Top is Lead)", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True)),
                color='Driver:N'
            )
            
            lines_multi = base_multi.mark_line().encode()
            points_multi = base_multi.mark_circle(size=50)
            labels_multi = base_multi.mark_text(align='left', dx=6, dy=-6, fontStyle='bold', fontSize=10).encode(text='RawDisplay:N')
            
            st.altair_chart((lines_multi + points_multi + labels_multi).properties(height=380), use_container_width=True)
            
        st.write("---")
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4.0, 4.0])
                col1.markdown(f"**{row['Driver']}** *(#{row['Car_Num']})*")
                col1.caption(f"Grid Start: P{row['Starting_Pos']} | 100L: P{row['Pos_100']} | 150L: P{row['Pos_150']} | Final: P{row['Pos_Final']}")
                with col2:
                    st.image(row['Car_Pic'])

# --- VIEW 5: POPULAR PICKS METRICS ---
elif selected_tab == "📊 Popular Picks":
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
                            y=alt.Y('GraphPosition:Q', scale=alt.Scale(domain=[1, 33]), title="Track Position (Top is Lead)", axis=alt.Axis(labels=False, ticks=False, grid=True, domain=True))
                        )
                        
                        lines_pop = base_pop.mark_line(color="#ff4b4b").encode()
                        points_pop = base_pop.mark_circle(size=60, color="#ff4b4b")
                        labels_pop = base_pop.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11).encode(text='RawDisplay:N')
                        
                        st.altair_chart((lines_pop + points_pop + labels_pop).properties(height=175), use_container_width=True)
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
            updated_picks.to_csv(PICKS_FILE, index=False)
            st.success(f"Successfully erased profile data for: {delete_target}")
            st.rerun()
