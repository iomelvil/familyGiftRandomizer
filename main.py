import os
import pandas as pd

year = 2026

# People no longer in the exchange. Their rows stay in the CSV so past years
# are kept; they just get "-" for this year and every year after.
INACTIVE = {"Wendy J."}


def import_gift_history():
    """Reads in previously unformatted gift history (one-time conversion)."""
    history_raw = pd.read_csv("Clarke Xmas Gift Giving 2023.csv", header=0)
    history = history_raw.dropna(axis=1, how="all").dropna(how="all")
    names = pd.read_csv("names.csv", header=0)
    history_renamed = history.rename(columns={'2023 Gift Giver': 'Giver', '2023 Gift Recipient': '2023'})
    merged_df = pd.merge(history_renamed, names, left_on='Giver', right_on='name', how='left')
    new_cols = ['Giver', 'age', 'family', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016']
    merged_df[new_cols].to_csv("ClarkeXmasList.csv", index=False)


def import_last_list(year):
    """Read in last year's xmas list from csv."""
    filename = "ClarkeXmasList" + str(year - 1) + ".csv"
    return pd.read_csv(os.path.join(filename), header=0)


def import_rel_grid(name, inactive=INACTIVE):
    """Load a giver x recipient exclusion grid, minus anyone inactive."""
    grid = pd.read_csv(os.path.join(str(name) + ".csv"), index_col=0)
    return grid.drop(index=inactive, columns=inactive, errors="ignore")


def overlay_excl(grid, df, year):
    """Mark last years' pairings as excluded.

    Only marks pairs where both people are in the grid. Without this check,
    grid.at[...] would silently ADD a row/column for anyone missing (e.g. an
    inactive person), putting them back into the draw.
    """
    col = str(year)
    if col not in df.columns:
        return
    for giver, recipient in zip(df["Giver"], df[col]):
        if giver in grid.index and recipient in grid.columns:
            grid.at[giver, recipient] = "x"


def find_match_with_grid(df, grid, year, max_tries=500):
    """Randomly assign a giver to every recipient, retrying on dead ends."""
    base = grid.copy()
    overlay_excl(base, df, year - 1)
    overlay_excl(base, df, year - 2)

    for attempt in range(1, max_tries + 1):
        cng_grid = base.copy()
        pairs = {}
        for col in base.columns:
            eligible = cng_grid[cng_grid[col] != "x"]
            if eligible.empty:
                break  # dead end: nobody left who can give to this person
            giver = eligible.sample().index[0]
            pairs[giver] = col
            cng_grid = cng_grid.drop(index=giver, columns=col)
        else:
            # Every recipient got a giver
            df = df.copy()
            for i, (giver, recipient) in enumerate(pairs.items(), 1):
                print(f"#{i},{giver}:{recipient}")
                df.loc[df['Giver'] == giver, str(year)] = recipient
            print(f"Matched on attempt {attempt}")
            return df

    raise RuntimeError(f"No valid matching found for {year} after {max_tries} attempts - "
                       "check the exclusion grid; it may be too restrictive.")


if __name__ == '__main__':
    df = import_last_list(year)
    # Add column for current year, deleting if it already exists
    if str(year) in df.columns:
        df = df.drop(columns=[str(year)])
    df.insert(2, str(year), '-')

    adults_df = df[df['age'] == 'a'].reset_index(drop=True)
    kids_df = df[df['age'] == 'k'].reset_index(drop=True)
    grid = import_rel_grid('familyExclusions')
    kidgrid = import_rel_grid('kidgrid')

    new_adults_df = find_match_with_grid(adults_df, grid, year)
    print("start kids")
    new_kids_df = find_match_with_grid(kids_df, kidgrid, year)
    new_combined = pd.concat([new_adults_df, new_kids_df], ignore_index=True)
    print(new_combined)

    new_combined.to_csv("ClarkeXmasList" + str(year) + ".csv", index=False)