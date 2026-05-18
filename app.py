import streamlit as st
import pandas as pd
import os

# Set up page config for mobile viewing
st.set_page_config(page_title="Indy 500 Pool", layout="centered")
st.title("🏎️ Indy 500 Live Pool Tracker")

# 1. Load Drivers Grid
@st.cache_data(ttl=10) # Refreshes rapidly for live updates
def load_drivers():
    return pd.read_csv("drivers.csv")

df = load_drivers()
driver_list = sorted(df['Driver'].tolist())

# 2. Setup/Load Dynamic Participant Picks
PICKS_FILE = "picks.csv"

def load_picks():
    if os.path.exists(PICKS_FILE):
        return pd.read_csv(PICKS_FILE)
    else:
        # Create an empty template if file doesn't exist yet
        return pd.DataFrame(columns=["Participant", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"])

picks_df = load_picks()

# 3. Main Navigation Layout
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Standings", "📝 Join Draft", "🏁 Live Field", "📋 Roster View"])

# --- TAB 1: LIVE LEADERBOARD ---
with tab1:
    st.header("Overall Standings")
    if picks_df.empty:
        st.info("No entries yet! Be the first to join the draft tab above.")
    else:
        leaderboard_data = []
        for _, row in picks_df.iterrows():
            user_picks = [row['P1'], row['P2'], row['P3'], row['P4'], row['P5'], row['P6'], row['P7'], row['P8']]
            user_drivers = df[df['Driver'].isin(user_picks)]
            
            # Calculations
            total_score = user_drivers['Current_Pos'].sum()
            tier_count = user_drivers[user_drivers['Tier_1_3'] == 'Yes'].shape[0]
            status = "✅ Valid" if tier_count <= 3 else "❌ DQ (>3 Top-Tier)"
            
            leaderboard_data.append({
                "Participant": row['Participant'],
                "Live Score": int(total_score) if not pd.isna(total_score) else 0,
                "Top Rows (Max 3)": f"{tier_count}/3",
                "Status": status
            })
        
        lbl_df = pd.DataFrame(leaderboard_data).sort_values(by="Live Score", ascending=True)
        st.dataframe(lbl_df, use_container_width=True, hide_index=True)

# --- TAB 2: INTERACTIVE DRAFT FORM ---
with tab2:
    st.header("Submit Your 8-Driver Roster")
    st.markdown("⚠️ *Rule: You can only select a maximum of 3 drivers from Rows 1-3 (Alex Palou, Alexander Rossi, David Malukas, Felix Rosenqvist, Santino Ferrucci, Pato O'Ward, Kyffin Simpson, Conor Daly, Scott McLaughlin).*")
    
    with st.form("draft_form", clear_on_submit=True):
        name = st.text_input("Your Name / Entry Name:").strip()
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.selectbox("Driver Pick 1", driver_list, index=0)
            p2 = st.selectbox("Driver Pick 2", driver_list, index=1)
            p3 = st.selectbox("Driver Pick 3", driver_list, index=2)
            p4 = st.selectbox("Driver Pick 4", driver_list, index=3)
        with col2:
            p5 = st.selectbox("Driver Pick 5", driver_list, index=4)
            p6 = st.selectbox("Driver Pick 6", driver_list, index=5)
            p7 = st.selectbox("Driver Pick 7", driver_list, index=6)
            p8 = st.selectbox("Driver Pick 8", driver_list, index=7)
            
        submitted = st.form_submit_button("Submit Roster Lineup")
        
        if submitted:
            all_picks = [p1, p2, p3, p4, p5, p6, p7, p8]
            
            if not name:
                st.error("Please enter your name before submitting.")
            elif len(set(all_picks)) < 8:
                st.error("Error: You cannot select the same driver more than once!")
            elif name in picks_df['Participant'].values:
                st.error(f"An entry named '{name}' already exists!")
            else:
                # Validation checks before appending data
                selected_drivers = df[df['Driver'].isin(all_picks)]
                tier_count = selected_drivers[selected_drivers['Tier_1_3'] == 'Yes'].shape[0]
                
                # Append new row data
                new_row = pd.DataFrame([{
                    "Participant": name, "P1": p1, "P2": p2, "P3": p3, "P4": p4, 
                    "P5": p5, "P6": p6, "P7": p7, "P8": p8
                }])
                
                updated_picks = pd.concat([picks_df, new_row], ignore_index=True)
                updated_picks.to_csv(PICKS_FILE, index=False)
                
                if tier_count > 3:
                    st.warning(f"Roster saved, but flags a WARNING! You chose {tier_count} drivers from Rows 1-3. Max limit is 3.")
                else:
                    st.success(f"Success! {name}'s roster is officially locked in.")
                st.rerun()

# --- TAB 3: LIVE TRACK RUNNING ORDER ---
with tab3:
    st.header("Actual Indy 500 Running Order")
    sorted_field = df.sort_values(by="Current_Pos")
    
    for _, row in sorted_field.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                st.metric(label="Pos", value=int(row['Current_Pos']))
            with col2:
                st.subheader(row['Driver'])
                st.caption(f"Car #{row['Car_Num']} | {row['Team']}")
            with col3:
                st.image(row['Driver_Pic'], width=90)

# --- TAB 4: INDIVIDUAL ROSTER PROFILE ---
with tab4:
    st.header("Roster Inspection")
    if picks_df.empty:
        st.info("No participants submitted yet.")
    else:
        selected_user = st.selectbox("Select Participant Profile:", picks_df['Participant'].tolist())
        user_row = picks_df[picks_df['Participant'] == selected_user].iloc[0]
        user_picks = [user_row['P1'], user_row['P2'], user_row['P3'], user_row['P4'], user_row['P5'], user_row['P6'], user_row['P7'], user_row['P8']]
        
        user_filtered_df = df[df['Driver'].isin(user_picks)].sort_values(by="Current_Pos")
        st.metric(label="Roster Score", value=int(user_filtered_df['Current_Pos'].sum()))
        
        for _, row in user_filtered_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Position {int(row['Current_Pos'])}**: {row['Driver']}")
                    st.caption(f"Car #{row['Car_Num']} | Tier 1-3: {row['Tier_1_3']}")
                with col2:
                    st.image(row['Car_Pic'], width=75)
