import streamlit as st
import pandas as pd
import os

# Page styling for a clean, visual mobile layout
st.set_page_config(page_title="Indy 500 Live Pool", layout="centered")
st.title("🏎️ Indy 500 Live Pool Tracker")

# 1. Official 2026 Indy 500 Starting Grid Data
@st.cache_data(ttl=5)
def load_drivers():
    # Complete, locked-in 33-driver field for the 110th Running
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
        "Driver_Pic": ["https://picsum.photos/id/101/100/100"] * 33,  # Replace with actual image URLs
        "Car_Pic": ["https://picsum.photos/id/102/100/100"] * 33     # Replace with actual image URLs
    }
    return pd.DataFrame(data)

df = load_drivers()

# 2. Manage Roster Picks
PICKS_FILE = "picks.csv"
if os.path.exists(PICKS_FILE):
    picks_df = pd.read_csv(PICKS_FILE)
else:
    picks_df = pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

# 3. Navigation
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Standings", "📝 Interactive Draft Board", "🏁 Live Field", "📋 Roster View"])

# --- TAB 1: STANDINGS ---
with tab1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No entries yet! Jump over to the 'Interactive Draft Board' tab to register your picks.")
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

# --- TAB 2: INTERACTIVE DRAFT BOARD ---
with tab2:
    st.header("Draft Your 8 Drivers")
    st.markdown("Tap or check the box next to **8 drivers** from the entire 33-car field below.")
    
    # Text input for participant name outside the main selection loop
    entry_name = st.text_input("Enter Your Name:", key="draft_entry_name").strip()
    
    st.write("---")
    
    # Dictionary to keep track of checkboxes
    selected_drivers = []
    
    # Create rows layout of 33 drivers
    for idx, row in df.iterrows():
        driver_name = row['Driver']
        is_top_tier = "⭐️ Top 3 Rows" if row['Tier_1_3'] == 'Yes' else "Field"
        label_text = f"Pos {row['Current_Pos']} | #{row['Car_Num']} {driver_name} ({is_top_tier})"
        
        # Unique styling wrapper if selected to highlight it
        if driver_name in st.session_state.get('temp_selections', []):
            # Simulated Highlight styling via Streamlit components
            with st.container(border=True):
                picked = st.checkbox(f"🟢 SELECTED: {label_text}", key=f"pick_{idx}", value=True)
        else:
            with st.container():
                picked = st.checkbox(label_text, key=f"pick_{idx}", value=False)
                
        if picked:
            selected_drivers.append(driver_name)
            
    # Save selection state dynamically
    st.session_state['temp_selections'] = selected_drivers
    
    # Real-time Roster Stats Counters
    num_selected = len(selected_drivers)
    selected_top_tier = df[df['Driver'].isin(selected_drivers) & (df['Tier_1_3'] == 'Yes')].shape[0]
    
    st.write("---")
    st.subheader("Your Roster Status Dashboard")
    
    # Visual metrics counters
    c1, c2 = st.columns(2)
    c1.metric("Drivers Picked (Need 8)", f"{num_selected} / 8")
    c2.metric("Top Tier Selected (Max 3)", f"{selected_top_tier} / 3")
    
    # Form submission validation button
    if st.button("Lock In & Submit Lineup", type="primary"):
        if not entry_name:
            st.error("Submission Denied: Please enter your name at the top of the board.")
        elif num_selected != 8:
            st.error(f"Submission Denied: You must select exactly 8 drivers. You currently have {num_selected} selected.")
        elif entry_name in picks_df['Participant'].values:
            st.error(f"Submission Denied: An entry under '{entry_name}' has already been drafted.")
        else:
            # Roster rule logic enforcement
            new_entry = pd.DataFrame([{
                "Participant": entry_name,
                "P1": selected_drivers[0], "P2": selected_drivers[1], "P3": selected_drivers[2], "P4": selected_drivers[3],
                "P5": selected_drivers[4], "P6": selected_drivers[5], "P7": selected_drivers[6], "P8": selected_drivers[7]
            }])
            
            updated_picks = pd.concat([picks_df, new_entry], ignore_index=True)
            updated_picks.to_csv(PICKS_FILE, index=False)
            
            if selected_top_tier > 3:
                st.warning(f"Roster saved, but you are marked DQ! You drafted {selected_top_tier} drivers from Rows 1-3 (Limit is 3).")
            else:
                st.success(f"Perfect! {entry_name}'s lineup is successfully logged and active!")
                
            # Clear data out for next participant
            st.session_state['temp_selections'] = []
            st.rerun()

# --- TAB 3: LIVE FIELD ---
with tab3:
    st.header("Actual Indy 500 Field")
    for _, row in df.sort_values(by="Current_Pos").iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            col1.metric("Pos", int(row['Current_Pos']))
            col2.subheader(row['Driver'])
            col2.caption(f"Car #{row['Car_Num']} | {row['Team']}")

# --- TAB 4: ROSTER VIEW ---
with tab4:
    st.header("Review Participant Choices")
    if picks_df.empty:
        st.info("No participants submitted yet.")
    else:
        user = st.selectbox("Select Roster:", picks_df['Participant'].tolist())
        u_row = picks_df[picks_df['Participant'] == user].iloc[0]
        u_picks = [u_row['P1'], u_row['P2'], u_row['P3'], u_row['P4'], u_row['P5'], u_row['P6'], u_row['P7'], u_row['P8']]
        
        u_df = df[df['Driver'].isin(u_picks)].sort_values(by="Current_Pos")
        st.metric("Total Points", int(u_df['Current_Pos'].sum()))
        
        for _, row in u_df.iterrows():
            st.markdown(f"**Position {int(row['Current_Pos'])}**: {row['Driver']} *(Car #{row['Car_Num']})*")
