import streamlit as st
import pandas as pd
import altair as alt
import os

# --- APP CONFIG & CUSTOM CSS (Mobile High-Contrast Optimization) ---
st.set_page_config(page_title="Indy 500 Pool Engine", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* High-contrast styles for mobile visibility outdoor/at racetrack */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    h1, h2, h3, h4, p, span, label, th, td {
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem;
        font-weight: 700;
        background-color: #1E293B;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        margin-right: 4px;
        color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF;
    }
    .scroll-container {
        overflow-x: auto;
        white-space: nowrap;
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 3px solid #EF4444;
    }
    div[data-testid="stTable"] table {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 2px solid #475569 !important;
        font-size: 1.1rem;
    }
    div[data-testid="stTable"] th {
        background-color: #334155 !important;
        color: #00FFCC !important;
        font-weight: bold;
        text-transform: uppercase;
    }
    div[data-testid="stTable"] td {
        border-bottom: 1px solid #475569 !important;
    }
    .driver-card {
        background-color: #1E293B;
        padding: 12px;
        border-radius: 6px;
        border-left: 5px solid #EF4444;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOCAL FILE PATH STORAGE PERSISTENCE ---
DRIVERS_FILE = "drivers.csv"
PARTICIPANTS_FILE = "participants.csv"
POSITIONS_FILE = "positions_overwrite.csv"

# --- DEFAULT IMMUTABLE DATA INITIALIZATION ---
# Base 33 Car Grid Entry Configurations
DEFAULT_DRIVERS = [
    {"Starting_Pos": 1, "Car_Num": "3", "Driver": "Scott McLaughlin", "Team": "Team Penske"},
    {"Starting_Pos": 2, "Car_Num": "12", "Driver": "Will Power", "Team": "Team Penske"},
    {"Starting_Pos": 3, "Car_Num": "2", "Driver": "Josef Newgarden", "Team": "Team Penske"},
    {"Starting_Pos": 4, "Car_Num": "5", "Driver": "Pato O'Ward", "Team": "Arrow McLaren"},
    {"Starting_Pos": 5, "Car_Num": "6", "Driver": "Nolan Siegel", "Team": "Arrow McLaren"},
    {"Starting_Pos": 6, "Car_Num": "7", "Driver": "Alexander Rossi", "Team": "Arrow McLaren"},
    {"Starting_Pos": 7, "Car_Num": "10", "Driver": "Alex Palou", "Team": "Chip Ganassi Racing"},
    {"Starting_Pos": 8, "Car_Num": "11", "Driver": "Marcus Armstrong", "Team": "Chip Ganassi Racing"},
    {"Starting_Pos": 9, "Car_Num": "9", "Driver": "Scott Dixon", "Team": "Chip Ganassi Racing"},
    {"Starting_Pos": 10, "Car_Num": "8", "Driver": "Linus Lundqvist", "Team": "Chip Ganassi Racing"},
    {"Starting_Pos": 11, "Car_Num": "28", "Driver": "Marcus Ericsson", "Team": "Andretti Global"},
    {"Starting_Pos": 12, "Car_Num": "27", "Driver": "Kyle Kirkwood", "Team": "Andretti Global"},
    {"Starting_Pos": 13, "Car_Num": "26", "Driver": "Colton Herta", "Team": "Andretti Global"},
    {"Starting_Pos": 14, "Car_Num": "60", "Driver": "Felix Rosenqvist", "Team": "Meyer Shank Racing"},
    {"Starting_Pos": 15, "Car_Num": "66", "Driver": "David Malukas", "Team": "Meyer Shank Racing"},
    {"Starting_Pos": 16, "Car_Num": "14", "Driver": "Santino Ferrucci", "Team": "A.J. Foyt Enterprises"},
    {"Starting_Pos": 17, "Car_Num": "41", "Driver": "Sting Ray Robb", "Team": "A.J. Foyt Enterprises"},
    {"Starting_Pos": 18, "Car_Num": "15", "Driver": "Graham Rahal", "Team": "Rahal Letterman Lanigan"},
    {"Starting_Pos": 19, "Car_Num": "30", "Driver": "Pietro Fittipaldi", "Team": "Rahal Letterman Lanigan"},
    {"Starting_Pos": 20, "Car_Num": "45", "Driver": "Christian Lundgaard", "Team": "Rahal Letterman Lanigan"},
    {"Starting_Pos": 21, "Car_Num": "20", "Driver": "Christian Rasmussen", "Team": "Ed Carpenter Racing"},
    {"Starting_Pos": 22, "Car_Num": "21", "Driver": "Rinus VeeKay", "Team": "Ed Carpenter Racing"},
    {"Starting_Pos": 23, "Car_Num": "33", "Driver": "Ed Carpenter", "Team": "Ed Carpenter Racing"},
    {"Starting_Pos": 24, "Car_Num": "18", "Driver": "Jack Harvey", "Team": "Dale Coyne Racing"},
    {"Starting_Pos": 25, "Car_Num": "51", "Driver": "Katherine Legge", "Team": "Dale Coyne Racing"},
    {"Starting_Pos": 26, "Car_Num": "4", "Driver": "Kyffin Simpson", "Team": "Chip Ganassi Racing"},
    {"Starting_Pos": 27, "Car_Num": "77", "Driver": "Romain Grosjean", "Team": "Juncos Hollinger Racing"},
    {"Starting_Pos": 28, "Car_Num": "78", "Driver": "Conor Daly", "Team": "Juncos Hollinger Racing"},
    {"Starting_Pos": 29, "Car_Num": "24", "Driver": "Pippa Mann", "Team": "Dreyer & Reinbold Racing"},
    {"Starting_Pos": 30, "Car_Num": "23", "Driver": "Ryan Hunter-Reay", "Team": "Dreyer & Reinbold Racing"},
    {"Starting_Pos": 31, "Car_Num": "50", "Driver": "Abel Speedway", "Team": "Abel Motorsports"},
    {"Starting_Pos": 32, "Car_Num": "98", "Driver": "Marco Andretti", "Team": "Andretti Herta"},
    {"Starting_Pos": 33, "Car_Num": "17", "Driver": "Callum Ilott", "Team": "Arrow McLaren"}
]

# Base Pool Entries (Pre-draft selection arrays)
DEFAULT_PARTICIPANTS = [
    {"Name": "Uncle Al", "D1": "Scott McLaughlin", "D2": "Scott Dixon", "D3": "Graham Rahal"},
    {"Name": "Speedway Steve", "D1": "Will Power", "D2": "Kyle Kirkwood", "D3": "Rinus VeeKay"},
    {"Name": "RaceDay Rick", "D1": "Josef Newgarden", "D2": "Alexander Rossi", "D3": "Santino Ferrucci"},
    {"Name": "Paddock Pete", "D1": "Pato O'Ward", "D2": "Colton Herta", "D3": "Christian Rasmussen"},
    {"Name": "PitRoad Patty", "D1": "Alex Palou", "D2": "Marcus Ericsson", "D3": "Felix Rosenqvist"}
]

# --- SYSTEM ENGINE DATA SEED LOADER FUNCTIONS ---
def load_drivers_data():
    if not os.path.exists(DRIVERS_FILE):
        pd.DataFrame(DEFAULT_DRIVERS).to_csv(DRIVERS_FILE, index=False)
    return pd.read_csv(DRIVERS_FILE)

def load_participants_data():
    if not os.path.exists(PARTICIPANTS_FILE):
        pd.DataFrame(DEFAULT_PARTICIPANTS).to_csv(PARTICIPANTS_FILE, index=False)
    return pd.read_csv(PARTICIPANTS_FILE)

def load_positions_overwrite_data(drivers_df):
    if not os.path.exists(POSITIONS_FILE):
        overwrites = []
        for _, r in drivers_df.iterrows():
            overwrites.append({
                "Driver": r['Driver'],
                "Pos_100": 0,
                "Pos_150": 0,
                "Pos_Final": 0
            })
        pd.DataFrame(overwrites).to_csv(POSITIONS_FILE, index=False)
    return pd.read_csv(POSITIONS_FILE)

# --- CORE AGGREGATION & PIPELINE ENGINE CALCULATIONS ---
def get_compiled_race_dataframe():
    d_df = load_drivers_data()
    p_df = load_positions_overwrite_data(d_df)
    merged = pd.merge(d_df, p_df, on="Driver", how="left")
    merged["Pos_100"] = merged["Pos_100"].fillna(0).astype(int)
    merged["Pos_150"] = merged["Pos_150"].fillna(0).astype(int)
    merged["Pos_Final"] = merged["Pos_Final"].fillna(0).astype(int)
    return merged

def calculate_master_standings():
    df_race = get_compiled_race_dataframe()
    df_pool = load_participants_data()
    
    if df_pool.empty:
        return pd.DataFrame()
        
    # Build fast dictionary map lookups for driver metrics
    map_start = dict(zip(df_race['Driver'], df_race['Starting_Pos']))
    map_100 = dict(zip(df_race['Driver'], df_race['Pos_100']))
    map_150 = dict(zip(df_race['Driver'], df_race['Pos_150']))
    map_final = dict(zip(df_race['Driver'], df_race['Pos_Final']))
    
    standings_records = []
    
    for _, part in df_pool.iterrows():
        drivers = [part['D1'], part['D2'], part['D3']]
        
        # Point Calculation: Cumulative sum of positions (0 treats unchecked indices as zero)
        pts_start = sum(map_start.get(d, 0) for d in drivers)
        pts_100 = sum(map_100.get(d, 0) if map_100.get(d, 0) != 0 else map_start.get(d, 0) for d in drivers)
        pts_150 = sum(map_150.get(d, 0) if map_150.get(d, 0) != 0 else (map_100.get(d, 0) if map_100.get(d, 0) != 0 else map_start.get(d, 0)) for d in drivers)
        pts_final = sum(map_final.get(d, 0) if map_final.get(d, 0) != 0 else (map_150.get(d, 0) if map_150.get(d, 0) != 0 else map_100.get(d, 0)) for d in drivers)
        
        standings_records.append({
            "Name": part['Name'],
            "Starting Pts": pts_start,
            "100L Pts": pts_100,
            "150L Pts": pts_150,
            "Final Pts": pts_final
        })
        
    st_df = pd.DataFrame(standings_records)
    
    # Generate positional rankings dynamically across historical nodes (Dense min ranking sorting strategy)
    st_df["Start Place"] = st_df["Starting Pts"].rank(method="min", ascending=True).astype(int)
    st_df["100L Place"] = st_df["100L Pts"].rank(method="min", ascending=True).astype(int)
    st_df["150L Place"] = st_df["150L Pts"].rank(method="min", ascending=True).astype(int)
    st_df["Final Place"] = st_df["Final Pts"].rank(method="min", ascending=True).astype(int)
    
    return st_df

# --- RUN ARCHITECTURE COMPILATION LAYER ---
st.title("🏁 Indy 500 Live Pool Tracking Engine")

df = get_compiled_race_dataframe()
t1, t2, t3, t4 = st.tabs(["🏆 Pool Standings", "🏎️ Driver Field Mat", "📋 Participant Rosters", "🎛️ Control Tower Overwrites"])

# --- VIEW 4: CONTROL TOWER DATA OVERWRITES ---
with t4:
    st.header("Control Tower Processing Console")
    st.write("Overriding track positions below pushes real-time telemetry array telemetry into leaderboard charts.")
    
    with st.expander("⚠️ Track Position Direct Entry Console", expanded=False):
        position_dropdown_choices = list(range(34))
        
        updated_rows = []
        for idx, row in df.sort_values(by="Starting_Pos").iterrows():
            st.markdown(f"**#{row['Car_Num']} — {row['Driver']}**")
            cc1, cc2, cc3 = st.columns(3)
            
            with cc1:
                val_100 = st.selectbox(f"Lap 100 Rank", options=position_dropdown_choices, index=int(row['Pos_100']), key=f"t100_{idx}")
            with cc2:
                val_150 = st.selectbox(f"Lap 150 Rank", options=position_dropdown_choices, index=int(row['Pos_150']), key=f"t150_{idx}")
            with cc3:
                val_final = st.selectbox(f"Finish Rank", options=position_dropdown_choices, index=int(row['Pos_Final']), key=f"tfin_{idx}")
                
            updated_rows.append({
                "Driver": row['Driver'],
                "Pos_100": val_100,
                "Pos_150": val_150,
                "Pos_Final": val_final
            })
            st.write("---")
            
        if st.button("Save Control Tower Data Overwrites", type="primary"):
            save_df = pd.DataFrame(updated_rows)
            save_df.to_csv(POSITIONS_FILE, index=False)
            st.success("Race placement logs updated globally!")
            st.rerun()

# --- VIEW 1: MASTER SCOREBOARD STANDINGS (Restored Version) ---
with t1:
    st.header("Standings")
    master_standings = calculate_master_standings()
    
    if master_standings.empty:
        st.info("No pool participant entries available to calculate score metrics.")
    else:
        # Determine current active tracking tier based on data entries
        if not (df['Pos_Final'] == 0).all():
            active_sort = "Final Pts"
            rank_col = "Final Place"
        elif not (df['Pos_150'] == 0).all():
            active_sort = "150L Pts"
            rank_col = "150L Place"
        elif not (df['Pos_100'] == 0).all():
            active_sort = "100L Pts"
            rank_col = "100L Place"
        else:
            active_sort = "Starting Pts"
            rank_col = "Start Place"
            
        total_participants = len(master_standings)
        
        # Build comprehensive multi-line progression grid tracking for the pool standings
        standings_milestones = ["Start", "Lap 100", "Lap 150", "Finish"]
        standings_chart_records = []
        
        for _, row in master_standings.iterrows():
            places = [row['Start Place'], row['100L Place'], row['150L Place'], row['Final Place']]
            for m_lbl, place_val in zip(standings_milestones, places):
                if m_lbl == "Start" or place_val != 0:
                    graph_coord = (total_participants + 1) - place_val
                    standings_chart_records.append({
                        "Milestone": m_lbl,
                        "GraphPosition": graph_coord,
                        "RawDisplay": f"#{place_val}",
                        "Pool Participant": row['Name']
                    })
                    
        if standings_chart_records:
            standings_chart_df = pd.DataFrame(standings_chart_records)
            
            base_standings = alt.Chart(standings_chart_df).encode(
                x=alt.X('Milestone:N', sort=standings_milestones, title="Race Milestone", axis=alt.Axis(grid=True, domain=True)),
                y=alt.Y(
                    'GraphPosition:Q', 
                    scale=alt.Scale(domain=[1, total_participants]), 
                    title=None, 
                    axis=alt.Axis(grid=True, domain=True, labels=False, ticks=False)
                ),
                color=alt.Color('Pool Participant:N', legend=alt.Legend(orient='left', title=None, labelColor='black'))
            )
            
            lines_st = base_standings.mark_line(strokeWidth=3).encode()
            points_st = base_standings.mark_circle(size=65)
            labels_st = base_standings.mark_text(align='left', dx=7, dy=-7, fontStyle='bold', fontSize=11, color='black').encode(text='RawDisplay:N')
            
            chart_render_st = (lines_st + points_st + labels_st).properties(width=1200, height=350, background='white').configure_axis(
                labelColor='black', titleColor='black'
            )
            
            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
            st.altair_chart(chart_render_st, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("ℹ️ Swipe right to scroll the timeline. Upward trending lines mean you are climbing towards 1st place.")
            st.write("---")
            
        display_scoreboard = master_standings.sort_values(by=active_sort, ascending=True).copy()
        
        display_scoreboard = display_scoreboard.rename(columns={
            "Name": "Participant Name",
            "Starting Pts": "Start Pts",
            "100L Pts": "Lap 100 Pts",
            "150L Pts": "Lap 150 Pts",
            "Final Pts": "Finish Pts"
        })
        
        render_columns = ["Participant Name", "Start Pts", "Lap 100 Pts", "Lap 150 Pts", "Finish Pts"]
        
        st.write("🏆 *Lower score is better! Points equal sum of team driver ranks.*")
        st.table(display_scoreboard[render_columns].set_index("Participant Name"))

# --- VIEW 2: CAR FIELD MAT DATA VIEW ---
with t2:
    st.header("Field Entry Tracking Array")
    st.write("Full grid metadata with live overwritten standings.")
    
    grid_view = df.copy().sort_values(by="Starting_Pos")
    grid_view.columns = ["Starting Box", "Car #", "Driver Engine Name", "Racing Entrant", "Lap 100", "Lap 150", "Final Rank"]
    st.dataframe(grid_view.set_index("Starting Box"), use_container_width=True)

# --- VIEW 3: ROSTER OVERVIEW MATRIX ---
with t3:
    st.header("Drafted Pool Rosters")
    df_pool = load_participants_data()
    
    if df_pool.empty:
        st.info("No pool roster configurations deployed.")
    else:
        for _, roster in df_pool.iterrows():
            with st.container():
                st.markdown(f'<div class="driver-card"><h4>👤 Roster Name: {roster["Name"]}</h4></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric(label="Primary Tier Driver (D1)", value=roster["D1"])
                c2.metric(label="Secondary Tier Driver (D2)", value=roster["D2"])
                c3.metric(label="Valuation Split Driver (D3)", value=roster["D3"])
                st.write("---")
