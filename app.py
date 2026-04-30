"""TGML Golf Handicap Calculator — Streamlit app.

Run with:  streamlit run app.py
"""

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from handicap import course_handicap, differential, handicap_index
from tees import PAR, TEES

DATA_FILE = Path(__file__).parent / "rounds.csv"
COLUMNS = ["date", "player", "tee", "adj_gross", "differential"]


def load_rounds() -> pd.DataFrame:
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE, parse_dates=["date"])
    return pd.DataFrame(columns=COLUMNS)


def save_rounds(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


st.set_page_config(page_title="TGML Handicap", page_icon="⛳", layout="wide")
st.title("⛳ TGML Handicap Calculator")
st.caption("9-hole daily rounds · USGA-style index (best of last 20 × 0.96)")

rounds = load_rounds()

tab_log, tab_index, tab_history, tab_admin = st.tabs(
    ["Log a round", "Handicap index", "History", "Admin"]
)

# ---------- Tab: Log a round ----------
with tab_log:
    col_a, col_b = st.columns(2)
    with col_a:
        existing_players = sorted(rounds["player"].dropna().unique().tolist())
        player = st.selectbox(
            "Player",
            options=["<new player>"] + existing_players,
            index=0 if not existing_players else 1,
        )
        if player == "<new player>":
            player = st.text_input("New player name").strip()
        round_date = st.date_input("Date", value=date.today())
    with col_b:
        tee_name = st.selectbox("Tee box", list(TEES.keys()))
        adj_gross = st.number_input(
            "Adjusted gross score (9 holes)",
            min_value=20.0,
            max_value=80.0,
            value=45.0,
            step=1.0,
        )

    tee = TEES[tee_name]
    diff = differential(adj_gross, tee["rating"], tee["slope"])
    st.metric("Round differential", f"{diff:+.2f}")
    st.caption(
        f"Formula: ({adj_gross} − {tee['rating']}) × 113 / {tee['slope']} = {diff:.2f}"
    )

    if st.button("Save round", type="primary", disabled=not player):
        new_row = pd.DataFrame(
            [
                {
                    "date": pd.Timestamp(round_date),
                    "player": player,
                    "tee": tee_name,
                    "adj_gross": adj_gross,
                    "differential": round(diff, 2),
                }
            ]
        )
        rounds = pd.concat([rounds, new_row], ignore_index=True)
        save_rounds(rounds)
        st.success(f"Saved round for {player}: {adj_gross} ({diff:+.2f})")
        st.rerun()

# ---------- Tab: Handicap index ----------
with tab_index:
    if rounds.empty:
        st.info("No rounds logged yet. Log a round to get started.")
    else:
        provisional = st.toggle(
            "Provisional index for new players (1–2 rounds)",
            value=True,
            help="When on, new players get an index from their first round (mean × 0.96). "
                 "Switches to USGA best-of-N after 3+ rounds.",
        )
        rows = []
        for name, grp in rounds.sort_values("date").groupby("player"):
            diffs = grp["differential"].astype(float).tolist()
            idx = handicap_index(diffs, provisional=provisional)
            n = len(diffs)
            status = "—" if idx is None else ("Provisional" if n < 3 else "Established")
            row = {
                "Player": name,
                "Rounds": n,
                "Status": status,
                "Index": idx if idx is not None else "—",
            }
            if idx is not None:
                for tee_name, tee in TEES.items():
                    row[tee_name] = course_handicap(
                        idx, tee["slope"], tee["rating"], PAR
                    )
            rows.append(row)
        out = pd.DataFrame(rows).sort_values(
            "Index",
            key=lambda s: pd.to_numeric(s, errors="coerce").fillna(99),
        )
        st.dataframe(out, use_container_width=True, hide_index=True)
        st.caption(
            "Course handicap = Index × (Slope / 113) + (CR − Par). "
            "Provisional = mean of logged diffs × 0.96. "
            "Established (3+ rounds) = USGA best-of-N × 0.96."
        )

# ---------- Tab: History ----------
with tab_history:
    if rounds.empty:
        st.info("No rounds yet.")
    else:
        players = ["All"] + sorted(rounds["player"].unique().tolist())
        pick = st.selectbox("Filter by player", players)
        view = rounds if pick == "All" else rounds[rounds["player"] == pick]
        view = view.sort_values("date", ascending=False)
        st.dataframe(view, use_container_width=True, hide_index=True)

        if pick != "All" and not view.empty:
            chart = view.sort_values("date").set_index("date")["differential"]
            st.line_chart(chart, height=240)

# ---------- Tab: Admin ----------
with tab_admin:
    st.subheader("Edit / delete rounds")
    if rounds.empty:
        st.info("Nothing to edit.")
    else:
        edited = st.data_editor(
            rounds.sort_values("date", ascending=False).reset_index(drop=True),
            num_rows="dynamic",
            use_container_width=True,
            key="editor",
        )
        if st.button("Save changes"):
            edited["differential"] = edited.apply(
                lambda r: round(
                    differential(
                        float(r["adj_gross"]),
                        TEES[r["tee"]]["rating"],
                        TEES[r["tee"]]["slope"],
                    ),
                    2,
                )
                if r["tee"] in TEES and pd.notna(r["adj_gross"])
                else r["differential"],
                axis=1,
            )
            save_rounds(edited)
            st.success("Saved.")
            st.rerun()

    st.divider()
    st.subheader("Tee boxes (from Daily_Round_Excel.numbers)")
    st.dataframe(
        pd.DataFrame(
            [
                {"Tee": k, "Slope": v["slope"], "Course Rating": v["rating"], "Par": PAR}
                for k, v in TEES.items()
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
