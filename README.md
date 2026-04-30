# TGML Handicap Calculator

Streamlit app for the TGML 9-hole golf league. Log rounds, compute USGA-style handicap differentials, and see each player's index + course handicap by tee.

## Tee boxes

| Tee | Slope | Course Rating |
|---|---|---|
| White Front | 124 | 34.3 |
| White Back | 121 | 33.8 |
| Red/Gold Front | 124 | 34.4 |
| Red/Gold Back | 126 | 34.6 |

## Math

- **Differential** = `(Adj Gross − Course Rating) × 113 / Slope`
- **Handicap Index** = best-N-of-last-20 differentials × 0.96 (USGA table; needs 3+ rounds)
- **Course Handicap** = `Index × (Slope / 113) + (CR − Par)`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io and connect the repo.
3. Set the entrypoint to `app.py`.

Note: Streamlit Cloud has an ephemeral filesystem, so `rounds.csv` resets on each redeploy. For persistent multi-player data, swap the CSV layer in `app.py` for a hosted store (Google Sheet, Supabase, etc.).
