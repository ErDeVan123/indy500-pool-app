import streamlit as st
import pandas as pd
import os

# Page layout setup
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")
st.title("🏎️ Indy 500 Live Pool Tracker")

# Custom CSS: "contain" ensures the full car is visible; flex centering keeps them perfectly vertical
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# 1. Official Starting Grid Data (Full 33-Driver Field)
@st.cache_data(ttl=5)
def load_drivers():
    data = {
        "Starting_Pos": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
        "Current_Pos": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
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
            "https://www.indycar.com/-/media/IndyCar/Cars/2026/IndyCar-Series/Liveries/Indy500/10-DHL-SS.png?dp=05-11-2026T06:02PM",  # 1. Alex Palou
            "https://your-hosting-site.com/car-20.jpg",  # 2. Alexander Rossi
            "https://your-hosting-site.com/car-12.jpg",  # 3. David Malukas
            "https://your-hosting-site.com/car-60.jpg",  # 4. Felix Rosenqvist
            "https://your-hosting-site.com/car-14.jpg",  # 5. Santino Ferrucci
            "https://your-hosting-site.com/car-5.jpg",   # 6. Pato O'Ward
            "https://your-hosting-site.com/car-8.jpg",   # 7. Kyffin Simpson
            "https://your-hosting-site.com/car-23.jpg",  # 8. Conor Daly
            "https://your-hosting-site.com/car-3.jpg",   # 9. Scott McLaughlin
            "https://your-hosting-site.com/car-9.jpg",   # 10. Scott Dixon
            "https://your-hosting-site.com/car-76.jpg",  # 11. Rinus VeeKay
            "https://your-hosting-site.com/car-75.jpg",  # 12. Takuma Sato
            "https://your-hosting-site.com/car-33.jpg",  # 13. Ed Carpenter
            "https://your-hosting-site.com/car-6.jpg",   # 14. Helio Castroneves
            "https://your-hosting-site.com/car-21.jpg",  # 15. Christian Rasmussen
            "https://your-hosting-site.com/car-66.jpg",  # 16. Marcus Armstrong
            "https://your-hosting-site.com/car-28.jpg",  # 17. Marcus Ericsson
            "https://your-hosting-site.com/car-7.jpg",   # 18. Christian Lundgaard
            "https://your-hosting-site.com/car-26.jpg",  # 19. Will Power
            "https://your-hosting-site.com/car-6b.jpg",  # 20. Nolan Siegel
            "https://your-hosting-site.com/car-45.jpg",  # 21. Louis Foster
            "https://your-hosting-site.com/car-31.jpg",  # 22. Ryan Hunter-Reay
            "https://your-hosting-site.com/car-2.jpg",   # 23. Josef Newgarden
            "https://your-hosting-site.com/car-18.jpg",  # 24. Romain Grosjean
            "https://your-hosting-site.com/car-27.jpg",  # 25. Kyle Kirkwood
            "https://your-hosting-site.com/car-11.jpg",  # 26. Katherine Legge
            "https://your-hosting-site.com/car-47.jpg",  # 27. Mick Schumacher
            "https://your-hosting-site.com/car-15.jpg",  # 28. Graham Rahal
            "https://your-hosting-site.com/car-19.jpg",  # 29. Dennis Hauger
            "https://your-hosting-site.com/car-51.jpg",  # 30. Jacob Abel
            "https://your-hosting-site.com/car-77.jpg",  # 31. Sting Ray Robb
            "https://your-hosting-site.com/car-4.jpg",   # 32. Caio Collet
            "https://your-hosting-site.com/car-24.jpg"   # 33. Jack Harvey
        ]
    }
    return pd.DataFrame(data)

df = load_drivers()

# 2. Synchronize CSV Database
PICKS_FILE = "picks.csv"
def load_picks():
    if os.path.exists(PICKS_FILE):
        return pd.read_csv(PICKS_FILE)
    return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

# Initialize dynamic navigation pointer cleanly in state
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "🏆 Standings"

# 3. Streamlined One-Click Navigation Menu
tab_options = ["🏆 Standings", "📝 Visual Draft Board", "🏁 Live Field", "📋 Roster View", "📊 Popular Picks"]
selected_tab = st.segmented_control(
    "Navigation Menu", 
    options=tab_options, 
    key="active_tab", 
    label_visibility="collapsed"
)

st.write("---")

# --- VIEW 1: OVERALL STANDINGS ---
if selected_tab == "🏆 Standings":
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged yet. Select the 'Visual Draft Board' menu above to add yours!")
    else:
        leaderboard_data = []
        for _, row in picks_df.iterrows():
            user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
            user_drivers = df[df['Driver'].isin(user_picks)]
            
            # Calculations
            total_score = user_drivers['Current_Pos'].sum()
            total_starting_positions = user_drivers['Starting_Pos'].sum()
            
            leaderboard_data.append({
                "Participant Name": row['Participant'],
                "Final Points": int(total_score),
                "Total Starting Positions": int(total_starting_positions)
            })
            
        # Convert to DataFrame and sort by Final Points ascending (lowest score wins)
        lbl_df = pd.DataFrame(leaderboard_data).sort_values(by="Final Points", ascending=True).reset_index(drop=True)
        
        # Inject Column 1: Participant's Place in the standings (1, 2, 3...)
        lbl_df.insert(0, "Place", lbl_df.index + 1)
        
        # Display table with requested columns
        st.dataframe(
            lbl_df, 
            column_config={
                "Place": st.column_config.NumberColumn("Place", format="%d"),
                "Participant Name": "Participant's Name",
                "Final Points": "Final Points",
                "Total Starting Positions": "Total Starting Positions"
            },
            use_container_width=True, 
            hide_index=True
        )

# --- VIEW 2: HARD-VALIDATED DRAFT BOARD ---
elif selected_tab == "📝 Visual Draft Board":
    st.header("Interactive Draft Field")
    st.markdown("Select exactly **8 drivers**. Maximum **3 from Rows 1-3**.")
    st.caption("💡 Tip: You can enter multiple times! Just give each submission a distinct Entry Name (e.g., 'Mark - Team A', 'Mark - Team B').")
    
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
        # Update session state key directly to skip the tab bug on forward auto-routing
        st.session_state["active_tab"] = "🏆 Standings"
        st.success("Lineup successfully validated and deployed!")
        st.rerun()

# --- VIEW 3: LIVE FIELD RUNNING ORDER ---
elif selected_tab == "🏁 Live Field":
    st.header("Actual Indy 500 Field")
    for _, row in df.sort_values(by="Current_Pos").iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1.2, 2.8, 4.0])
            col1.metric("Live Pos", int(row['Current_Pos']))
            col1.caption(f"Started: P{row['Starting_Pos']}")
            col2.subheader(row['Driver'])
            col2.caption(f"#{row['Car_Num']} | {row['Team']}\nQual Speed: {row['Qual_Speed']}")
            col3.image(row['Car_Pic'])

# --- VIEW 4: ROSTER VIEW ---
elif selected_tab == "📋 Roster View":
    st.header("Roster Inspection Profiles")
    if picks_df.empty:
        st.info("No active rosters submitted.")
    else:
        user = st.selectbox("Choose Entry Profile:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by="Current_Pos")
        st.metric("Roster Live Score", int(u_df['Current_Pos'].sum()))
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4.0, 4.0])
                col1.markdown(f"**Live Pos {int(row['Current_Pos'])}**: {row['Driver']} *(#{row['Car_Num']})*")
                col1.caption(f"Grid Start: P{row['Starting_Pos']} | Speed: {row['Qual_Speed']}")
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
                    
        for _, row in df.iterrows():
            d_name = row['Driver']
            choosing_p = driver_pick_map[d_name]
            with st.container(border=True):
                col1, col2 = st.columns([4.0, 4.0])
                with col1:
                    st.subheader(d_name)
                    st.caption(f"Car #{row['Car_Num']} | Start: P{row['Starting_Pos']} ({row['Qual_Speed']})")
                    if choosing_p:
                        st.markdown(f"**Drafted By:** {', '.join(choosing_p)}")
                    else:
                        st.markdown("*Nobody has drafted this driver yet.*")
                with col2:
                    st.image(row['Car_Pic'])

# --- SYSTEM ADMIN COMMAND DECK ---
st.write("---")
with st.expander("🛠️ Admin Command Deck (Edit / Delete Entry Controls)"):
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
