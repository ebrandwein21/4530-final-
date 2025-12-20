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

    # Added for the Players
    df["two_pt_made"] = df["flag_made_shot"] & ~df["flag_three_point"] & ~df["flag_free_throw"]
    df["two_pt_attempt"] = df["two_pt_made"] | (
        df["flag_missed_shot"] &
        ~df["flag_three_point"] &
        ~df["flag_free_throw"]
    )

    df["three_pt_made"] = df["flag_three_point"] & df["flag_made_shot"]
    df["three_pt_attempt"] = df["flag_three_point"]

    df["ft_made"] = df["flag_free_throw"] & df["flag_made_shot"]
    df["ft_attempt"] = df["flag_free_throw"]

    df["points"] = (
        2 * df["two_pt_made"].astype(int) +
        3 * df["three_pt_made"].astype(int) +
        1 * df["ft_made"].astype(int)
    )

    # grouping
    df = df[~df["player1_id"].isna()].copy()

    group_cols = ["player1_id", "player1_name", "player1_team_abbreviation", "game_id"]

    grouped = df.groupby(group_cols).agg(
        events=("eventnum", "count"),
        points=("points", "sum"),
        two_pt_made=("two_pt_made", "sum"),
        two_pt_attempt=("two_pt_attempt", "sum"),
        three_pt_made=("three_pt_made", "sum"),
        three_pt_attempt=("three_pt_attempt", "sum"),
        ft_made=("ft_made", "sum"),
        ft_attempt=("ft_attempt", "sum"),
        rebounds=("flag_rebound", "sum"),
        turnovers=("flag_turnover", "sum"),
        fouls=("flag_foul", "sum"),
    ).reset_index()

    # shooting percentages
    total_fgm = grouped["two_pt_made"] + grouped["three_pt_made"]
    total_fga = grouped["two_pt_attempt"] + grouped["three_pt_attempt"]

    grouped["fg_pct"] = np.where(total_fga > 0, total_fgm / total_fga, np.nan)
    grouped["three_pt_pct"] = np.where(
        grouped["three_pt_attempt"] > 0,
        grouped["three_pt_made"] / grouped["three_pt_attempt"],
        np.nan,
    )
    grouped["ft_pct"] = np.where(
        grouped["ft_attempt"] > 0,
        grouped["ft_made"] / grouped["ft_attempt"],
        np.nan,
    )


    return grouped


def main():

    first = True
    total = 0

    for chunk in pd.read_csv("preview_play_by_play.csv", chunksize=500000, low_memory=False):
        grouped = process_chunk(chunk)
        total += len(grouped)

        grouped.to_csv("cleaned_player.csv", mode="a", index=False, header=first)
        first = False

        print("Processed rows:", total)

    print("Done cleaning.")

if __name__ == "__main__":
    main()
