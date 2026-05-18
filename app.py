import streamlit as st
import pandas as pd
import os

# Page configurations for a highly visual layout
st.set_page_config(page_title="Indy 500 Pool Engine", layout="centered")
st.title("🏎️ Indy 500 Live Pool Tracker")

# 1. Official 2026 Indy 500 Starting Grid
@st.cache_data(ttl=5)
def load_drivers():
    data = {
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
        "Tier_1_3": ["Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","Yes","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No","No"],
        "Car_Pic": ["https://picsum.photos/id/102/100/60"] * 33 # Standard image placeholder for vehicle livery
    }
    return pd.DataFrame(data)

df = load_drivers()

# 2. Sync Active Draft Database
PICKS_FILE = "picks.csv"
if os.path.exists(PICKS_FILE):
    picks_df = pd.read_csv(PICKS_FILE)
else:
    picks_df = pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

# 3. Dynamic App Interface Tabs
tabs = st.tabs(["🏆 Standings", "📝 Visual Draft Board", "🏁 Live Field", "📋 Roster View", "📊 Popular Picks"])
tab1, tab2, tab3, tab4, tab5 = tabs

# --- TAB 1: OVERALL STANDINGS ---
with tab1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No pool sheets logged. Head to the 'Visual Draft Board' to make selections!")
    else:
        leaderboard_data = []
        for _, row in picks_df.iterrows():
            user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
            user_drivers = df[df['Driver'].isin(user_picks)]
            total_score = user_drivers['Current_Pos'].sum()
            tier_count = user_drivers[user_drivers['Tier_1_3'] == 'Yes'].shape[0]
            status = "✅ Valid" if tier_count <= 3 else "❌ DQ (>3 Top-Tier)"
            
            leaderboard_data.append({
                "Participant": row['Participant'],
                "Live Score": int(total_score),
                "Top Rows (Max 3)": f"{tier_count}/3",
                "Status": status
            })
        lbl_df = pd.DataFrame(leaderboard_data).sort_values(by="Live Score", ascending=True)
        st.dataframe(lbl_df, use_container_width=True, hide_index=True)

# --- TAB 2: VISUAL DRAFT BOARD ---
with tab2:
    st.header("Interactive Draft Field")
    st.markdown("Select exactly **8 drivers**. Your choices will highlight in green.")
    
    entry_name = st.text_input("Enter Your Name:", key="new_user_name").strip()
    
    if "selected_pool" not in st.session_state:
        st.session_state["selected_pool"] = []
        
    st.write("---")
    
    # Loop across all 33 drivers matching the Live Grid template
    for idx, row in df.iterrows():
        d_name = row['Driver']
        is_selected = d_name in st.session_state["selected_pool"]
        
        # Container presentation matches live feed card layout
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                st.write(f"**Grid**\n#{row['Car_Num']}")
                if row['Tier_1_3'] == "Yes":
                    st.caption("⭐ Row 1-3")
            
            with col2:
                st.subheader(d_name)
                st.caption(row['Team'])
                
                # Checkbox inside card to handle highlighting toggle
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
    st.subheader("Roster Overview")
    
    current_picks = st.session_state["selected_pool"]
    count_picked = len(current_picks)
    count_tier = df[df['Driver'].isin(current_picks) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    c1, c2 = st.columns(2)
    c1.metric("Drivers Locked", f"{count_picked} / 8")
    c2.metric("Top Row Drivers", f"{count_tier} / 3")
    
    if st.button("Submit Official Roster Lineup", type="primary"):
        if not entry_name:
            st.error("Error: Please enter an Entry Name at the top.")
        elif count_picked != 8:
            st.error(f"Error: Lineups must have exactly 8 choices. You currently have selected {count_picked}.")
        elif entry_name in picks_df['Participant'].values:
            st.error(f"Error: The name '{entry_name}' is already registered.")
        else:
            new_entry = pd.DataFrame([{
                "Participant": entry_name,
                "P1": current_picks[0], "P2": current_picks[1], "P3": current_picks[2], "P4": current_picks[3],
                "P5": current_picks[4], "P6": current_picks[5], "P7": current_picks[6], "P8": current_picks[7]
            }])
            updated_df = pd.concat([picks_df, new_entry], ignore_index=True)
            updated_df.to_csv(PICKS_FILE, index=False)
            
            st.success(f"Success! {entry_name}'s line-up is officially live.")
            st.session_state["selected_pool"] = []
            st.rerun()

# --- TAB 3: LIVE FIELD ---
with tab3:
    st.header("Actual Indy 500 Running Field")
    for _, row in df.sort_values(by="Current_Pos").iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 3, 2])
            col1.metric("Pos", int(row['Current_Pos']))
            col2.subheader(row['Driver'])
            col2.caption(f"Car #{row['Car_Num']} | {row['Team']}")
            col3.image(row['Car_Pic'], use_container_width=True)

# --- TAB 4: ROSTER VIEW ---
with tab4:
    st.header("Roster Inspection Profiles")
    if picks_df.empty:
        st.info("No active rosters to inspect.")
    else:
        user = st.selectbox("Choose Profile:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by="Current_Pos")
        st.metric("Roster Score Total", int(u_df['Current_Pos'].sum()))
        
        for _, row in u_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 2])
                col1.markdown(f"**Track Position {int(row['Current_Pos'])}**: {row['Driver']} *(#{row['Car_Num']})*")
                col2.image(row['Car_Pic'], use_container_width=True)

# --- TAB 5: POPULAR PICKS METRICS ---
with tab5:
    st.header("Participant Pick Summary")
    st.markdown("See which participants drafted each driver.")
    
    if picks_df.empty:
        st.info("No calculations available until picks are drafted.")
    else:
        # Create a dictionary mapping driver name to list of participants who selected them
        driver_pick_map = {driver: [] for driver in df['Driver'].tolist()}
        
        for _, row in picks_df.iterrows():
            participant = row['Participant']
            user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
            for pick in user_picks:
                if pick in driver_pick_map:
                    driver_pick_map[pick].append(participant)
                    
        # Display each driver alongside the roster list of people who picked them
        for _, row in df.iterrows():
            d_name = row['Driver']
            choosing_participants = driver_pick_map[d_name]
            
            with st.container(border=True):
                col1, col2 = st.columns([4, 2])
                with col1:
                    st.subheader(d_name)
                    st.caption(f"Car #{row['Car_Num']} | {row['Team']}")
                    
                    if choosing_participants:
                        # Renders participant names cleanly separated by commas
                        st.markdown(f"**Drafted By:** {', '.join(choosing_participants)}")
                    else:
                        st.markdown("*Nobody has drafted this driver yet.*")
                        
                with col2:
                    st.image(row['Car_Pic'], use_container_width=True)
