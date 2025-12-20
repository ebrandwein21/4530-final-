import os
import pandas as pd
import numpy as np

def process_chunk(df):
    #numeric columns
    for col in ["game_id", "eventnum", "eventmsgtype", "eventmsgactiontype",
                "period", "scoremargin"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # change string to numeric seconds remaining
    if "pctimestring" in df.columns:
        parts = df["pctimestring"].astype(str).str.split(":", n=1, expand=True)
        if parts.shape[1] == 2:
            mins = pd.to_numeric(parts[0], errors="coerce")
            secs = pd.to_numeric(parts[1], errors="coerce")
            df["seconds_remaining"] = mins * 60 + secs
        else:
            df["seconds_remaining"] = np.nan
    else:
        df["seconds_remaining"] = np.nan

    # time elapsed in game
    df["game_time_elapsed"] = (df["period"] - 1) * 720 + (720 - df["seconds_remaining"])

    # event name mapping
    map_types = {
        1: "made_shot", 2: "missed_shot", 3: "free_throw",
        4: "rebound", 5: "turnover", 6: "foul", 7: "violation",
        8: "substitution", 9: "timeout", 10: "jump_ball",
        12: "period_start", 13: "period_end"
    }
    df["event_name"] = df["eventmsgtype"].map(map_types).fillna("unknown")

    # score split
    if "score" in df.columns:
        parts = df["score"].astype(str).str.split("-", n=1, expand=True)
        df["home_score"] = pd.to_numeric(parts[0], errors="coerce")
        df["visitor_score"] = pd.to_numeric(parts[1], errors="coerce")
    else:
        df["home_score"] = np.nan
        df["visitor_score"] = np.nan

    # description flags
    desc = (
        df.get("homedescription", "").fillna("") + " " +
        df.get("visitordescription", "").fillna("") + " " +
        df.get("neutraldescription", "").fillna("")
    ).str.upper()

    df["flag_made_shot"]   = desc.str.contains("PTS", regex=False) & ~desc.str.contains("MISS", regex=False)
    df["flag_missed_shot"] = desc.str.contains("MISS", regex=False)
    df["flag_three_point"] = desc.str.contains("3PT", regex=False) | desc.str.contains("3-PT", regex=False)
    df["flag_free_throw"]  = desc.str.contains("FREE THROW", regex=False)
    df["flag_rebound"]     = desc.str.contains("REBOUND", regex=False)
    df["flag_turnover"]    = desc.str.contains("TURNOVER", regex=False)
    df["flag_foul"]        = desc.str.contains("FOUL", regex=False)
    df["flag_timeout"]     = desc.str.contains("TIMEOUT", regex=False)
    df["flag_jump_ball"]   = desc.str.contains("JUMP BALL", regex=False)

    #columns to keep
    keep = [
        "game_id", "eventnum", "eventmsgtype", "eventmsgactiontype", "event_name", "period", "wctimestring", "pctimestring", "seconds_remaining", "game_time_elapsed",
        "score", "home_score", "visitor_score", "scoremargin", "person1type", "player1_id", "player1_name", "player1_team_id", "player1_team_abbreviation", "person2type", "player2_id", "player2_name",
        "player2_team_id", "player2_team_abbreviation", "person3type", "player3_id", "player3_name", "player3_team_id", "player3_team_abbreviation", "flag_made_shot", "flag_missed_shot", 
        "flag_three_point", "flag_free_throw", "flag_rebound", "flag_turnover", "flag_foul", "flag_timeout", "flag_jump_ball",
    ]

    return df[[c for c in keep if c in df.columns]]

def main():

    first = True
    total = 0

    for chunk in pd.read_csv("archive/csv/play_by_play.csv", chunksize=500000, low_memory=False):

        cleaned = process_chunk(chunk)
        total += len(cleaned)

        cleaned.to_csv("cleaned_play_by_play.csv", mode="a", index=False, header=first)
        first = False

        print("Processed rows:", total)

    print("Done cleaning.")

if __name__ == "__main__":
    main()
