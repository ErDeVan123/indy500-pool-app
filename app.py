import streamlit as st
import pandas as pd

# Set up page config for mobile viewing
st.set_page_config(page_title="Indy 500 Pool", layout="centered")
st.title("🏎️ Indy 500 Pool Tracker")

# 1. Load Data
@st.cache_data(ttl=60) # Refreshes every minute
def load_data():
    return pd.read_csv("drivers.csv")

df = load_data()

# 2. Hardcoded Participant Rosters
# (You can easily edit these names and picks right here in GitHub!)
participants = {
    "Sarah": ["Alex Palou", "Pato O'Ward", "Scott Dixon", "Felix Rosenqvist", "Santino Ferrucci", "Kyffin Simpson", "Conor Daly", "Scott McLaughlin"],
    "Mark": ["Alex Palou", "Alexander Rossi", "David Malukas", "Felix Rosenqvist", "Scott Dixon", "Kyffin Simpson", "Conor Daly", "Scott McLaughlin"]
}

# 3. Calculate Scores and Validate Tiers
leaderboard_data = []
for name, picks in participants.items():
    user_drivers = df[df['Driver'].isin(picks)]
    
    # Calculate score (Sum of current positions)
    total_score = user_drivers['Current_Pos'].sum()
    
    # Check row 1-3 restriction (Max 3 Allowed)
    tier_count = user_drivers[user_drivers['Tier_1_3'] == 'Yes'].shape[0]
    status = "✅ Valid Roster" if tier_count <= 3 else "❌ DQ: >3 Top-Tier Drivers"
    
    leaderboard_data.append({
        "Participant": name,
        "Live Score": total_score,
        "Tier Count": f"{tier_count}/3",
        "Status": status
    })

leaderboard_df = pd.DataFrame(leaderboard_data).sort_values(by="Live Score", ascending=True)

# 4. App Navigation Tabs (Toggles)
tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard", "🏁 Live Race Field", "📋 My Roster View"])

with tab1:
    st.header("Overall Standings")
    st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)

with tab2:
    st.header("Actual Indy 500 Running Order")
    sorted_field = df.sort_values(by="Current_Pos")
    
    for _, row in sorted_field.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                st.metric(label="Pos", value=int(row['Current_Pos']))
            with col2:
                st.subheader(row['Driver'])
                st.text(f"Car #{row['Car_Num']} | {row['Team']}")
            with col3:
                # Displays driver image seamlessly
                st.image(row['Driver_Pic'], width=100)

with tab3:
    st.header("Check Your Roster Status")
    selected_user = st.selectbox("Select Participant:", list(participants.keys()))
    
    user_picks = participants[selected_user]
    user_filtered_df = df[df['Driver'].isin(user_picks)].sort_values(by="Current_Pos")
    
    st.metric(label="Your Total Score", value=int(user_filtered_df['Current_Pos'].sum()))
    
    for _, row in user_filtered_df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Position {int(row['Current_Pos'])}**: {row['Driver']}")
                st.caption(f"Car #{row['Car_Num']} | Tier 1-3: {row['Tier_1_3']}")
            with col2:
                st.image(row['Car_Pic'], width=80)
