import streamlit as st
import pandas as pd
import os

# Page layout setup
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")
st.title("🏎️ Indy 500 Live Pool Tracker")

# 1. Official 2026 Starting Grid with Qualifying Metrics
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
            "Juncos Hollinger", "A.Y. Foyt Racing", "Dreyer & Reinbold"
        ],
        "Qual_Speed": [
            "234.214 mph", "233.811 mph", "233.504 mph", "233.210 mph", "233.114 mph", 
            "232.998 mph", "232.845 mph", "232.612 mph", "232.401 mph", "232.214 mph", 
            "232.105 mph", "231.994 mph", "231.785 mph", "231.654 mph", "231.411 mph", 
            "231.202 mph", "231.004 mph", "230.985 mph", "230.841 mph", "230.652 mph", 
            "230.414 mph", "230.201 mph", "230.114 mph", "229.984 mph", "229.814 mph", 
            "229.654 mph", "229.412 mph", "229.214 mph", "229.004 mph", "228.841 mph", 
            "228.651 mph", "228.411 mph", "228.104 mph"
        ],
        "Tier_1_3": ["Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No"],
        "Car_Pic": ["https://picsum.photos/id/102/100/60"] * 33
    }
    return pd.DataFrame(data)

df = load_drivers()

# 2. Synchronize CSV Database Local State
PICKS_FILE = "picks.csv"
def load_picks():
    if os.path.exists(PICKS_FILE):
        return pd.read_csv(PICKS_FILE)
    return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

# 3. Dynamic Application Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Standings", "📝 Visual Draft Board", "🏁 Live Field", "📋 Roster View", "📊 Popular Picks"])

# --- TAB 1: OVERALL STANDINGS ---
with tab1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged yet.")
    else:
        leaderboard_data = []
        for _, row in picks_df.iterrows():
            user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
            user_drivers = df[df['Driver'].isin(user_picks)]
            total_score = user_drivers['Current_Pos'].sum()
            tier_count = user_drivers[user_drivers['Tier_1_3'] == 'Yes'].shape[0]
            
            leaderboard_data.append({
                "Participant": row['Participant'],
                "Live Score": int(total_score),
                "Top Rows (Max 3)": f"{tier_count}/3"
            })
        lbl_df = pd.DataFrame(leaderboard_data).sort_values(by="Live Score", ascending=True)
        st.dataframe(lbl_df, use_container_width=True, hide_index=True)

# --- TAB 2: HARD-VALIDATED DRAFT BOARD ---
with tab2:
    st.header("Interactive Draft Field")
    st.markdown("Select exactly **8 drivers**. Maximum **3 from Rows 1-3**.")
    
    entry_name = st.text_input("Enter Your Name:", key="new_user_name").strip()
    
    if "selected_pool" not in st.session_state:
        st.session_state["selected_pool"] = []
        
    st.write("---")
    
    for idx, row in df.iterrows():
        d_name = row['Driver']
        is_selected = d_name in st.session_state["selected_pool"]
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([1.5, 3, 2])
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
                st.image(row['Car_Pic'], use_container_width=True)

    st.write("---")
    st.subheader("Roster Validation Dashboard")
    
    current_picks = st.session_state["selected_pool"]
    count_picked = len(current_picks)
    count_tier = df[df['Driver'].isin(current_picks) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    c1, c2 = st.columns(2)
    c1.metric("Drivers Picked (Must be 8)", f"{count_picked} / 8", delta=None if count_picked <= 8 else "Too Many!", delta_color="inverse")
    c2.metric("Top-Tier Rows 1-3 (Max 3)", f"{count_tier} / 3", delta=None if count_tier <= 3 else "Limit Exceeded!", delta_color="inverse")
    
    # STRICT HARD RULES SUBMISSION BLOCKER
    can_submit = True
    if count_picked != 8:
        st.error(f"⚠️ Blocked: You must select exactly 8 drivers. You currently have {count_picked}.")
        can_submit = False
    if count_tier > 3:
        st.error(f"⚠️ Blocked: You have selected {count_tier} drivers from Rows 1-3. The absolute limit is 3.")
        can_submit = False
    if not entry_name:
        st.warning("Please enter your name above to activate the submission button.")
        can_submit = False
    elif entry_name in picks_df['Participant'].values:
        st.error(f"⚠️ Blocked: An entry named '{entry_name}' already exists.")
        can_submit = False

    if st.button("Submit Official Roster Lineup", type="primary", disabled=not can_submit):
        new_entry = pd.DataFrame([{
            "Participant": entry_name,
            "P1": current_picks[0], "P2": current_picks[1], "P3": current_picks[2], "P4": current_picks[3],
            "P5": current_picks[4], "P6": current_picks[5], "P7": current_picks[6], "P8": current_picks[7]
        }])
        updated_df = pd.concat([picks_df, new_entry], ignore_index=True)
        updated_df.to_csv(PICKS_FILE, index=False)
        st.success("Roster locked and loaded successfully!")
        st.session_state["selected_pool"] = []
        st.rerun()

# --- TAB 3: LIVE FIELD RUNNING ORDER ---
with tab3:
    st.header("Actual Indy 500 Field")
    for _, row in df.sort_values(by="Current_Pos").iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1.5, 3, 2])
            col1.metric("Live Pos", int(row['Current_Pos']))
            col1.caption(f"Started: P{row['Starting_Pos']}")
            col2.subheader(row['Driver'])
            col2.caption(f"#{row['Car_Num']} | {row['Team']}\nQual Speed: {row['Qual_Speed']}")
            col3.image(row['Car_Pic'], use_container_width=True)

# --- TAB 4: ROSTER VIEW ---
with tab4:
    st.header("Roster Inspection Profiles")
    if picks_df.empty:
        st.info("No active rosters submitted.")
    else:
        user = st.selectbox("Choose Profile:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by="Current_Pos")
        st.metric("Roster Live Score", int(u_df['Current_Pos'].sum()))
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 2])
                col1.markdown(f"**Live Pos {int(row['Current_Pos'])}**: {row['Driver']} *(#{row['Car_Num']})*")
                col1.caption(f"Grid Start: P{row['Starting_Pos']} | Speed: {row['Qual_Speed']}")
                col2.image(row['Car_Pic'], use_container_width=True)

# --- TAB 5: POPULAR PICKS METRICS ---
with tab5:
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
                col1, col2 = st.columns([4, 2])
                with col1:
                    st.subheader(d_name)
                    st.caption(f"Car #{row['Car_Num']} | Start: P{row['Starting_Pos']} ({row['Qual_Speed']})")
                    if choosing_p:
                        st.markdown(f"**Drafted By:** {', '.join(choosing_p)}")
                    else:
                        st.markdown("*Nobody has drafted this driver yet.*")
                with col2:
                    st.image(row['Car_Pic'], use_container_width=True)

# --- SYSTEM ADMIN COMMAND DECK (HIDDEN FOOTER EDITOR) ---
st.write("---")
with st.expander("🛠️ Admin Command Deck (Edit / Delete Entry Controls)"):
    if picks_df.empty:
        st.info("No participant records currently stored to edit.")
    else:
        st.subheader("Delete a Participant Profile")
        delete_target = st.selectbox("Select Entry to Permanently Delete:", picks_df['Participant'].tolist(), key="admin_del_select")
        
        if st.button("Permanently Delete Roster", type="primary"):
            updated_picks = picks_df[picks_df['Participant'] != delete_target]
            updated_picks.to_csv(PICKS_FILE, index=False)
            st.success(f"Successfully erased profile data for: {delete_target}")
            st.rerun()
