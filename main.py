import os
import pandas as pd

# Define the year and run file
year = 2025
def import_gift_history():
    """Reads in previoulsly unformatted gift history"""
    history_raw = pd.read_csv("Clarke Xmas Gift Giving 2023.csv", header=0)
    history1 = history_raw.dropna(axis=1,how="all")
    history = history1.dropna(how="all")
    names = pd.read_csv("names.csv", header=0)
    history_renamed = history.rename(columns={'2023 Gift Giver':'Giver','2023 Gift Recipient':'2023'})
    print(names)
    print(history)
    print(history_renamed)
    # Merge df1 to df2 based on 'name' from df1 and 'Giver' from df2
    merged_df = pd.merge(history_renamed, names, left_on='Giver', right_on='name', how='left')
    print(merged_df)
    new_cols = ['Giver','age','family','2023','2022','2021','2020','2019','2018','2017','2016']
    merged_sorted_df = merged_df[new_cols]
    print(merged_sorted_df)
    merged_sorted_df.to_csv("ClarkeXmasList.csv", index=False)

def import_last_list(year):
    """ Read in last years xmas list list from csv"""
    prefix= "ClarkeXmasList"
    last_year = year-1
    filename = prefix + str(last_year) + ".csv"
    history = pd.read_csv(os.path.join(filename),header=0)
    return (history)

def import_rel_grid(name):
    grid = pd.read_csv(os.path.join(str(name)+".csv"),index_col=0)
    # print(grid)
    return grid
def overlay_excl(grid,df,year):
    for i in range(df.shape[0]):
        grid.at[df.loc[i, 'Giver'],df.loc[i,str(year)]] = 'x'
    # grid.to_csv('overlay_excl.csv',index=True)

def find_match_with_grid(df, grid,year):
    # print(df)
    # print(grid)
    cng_grid = grid.copy()
    lastyear = year -1
    lastlastyear = year -2
    overlay_excl(cng_grid,df,lastyear)
    overlay_excl(cng_grid,df,lastlastyear)

    chosen_rows = {}
    i=0
    for col in cng_grid.columns:
        if cng_grid.empty:
            break
        excluded_df= cng_grid[cng_grid[col]!= 'x']
        chosen_row = excluded_df.sample()
        i+=1
        print(f"#{i},{chosen_row.index[0]}:{col}")
        df.loc[df['Giver']==chosen_row.index[0],str(year)] = str(col)
        chosen_row[col]=chosen_row.index[0] # save row
        cng_grid = cng_grid.drop(chosen_row.index[0]) # drop chosen row
        cng_grid = cng_grid.drop(columns=[col])
    # print(df)
    return df


if __name__ == '__main__':

    df = import_last_list(year)
    # Add column for current year, deleting if already exists
    if str(year) in df.columns:
        df = df.drop(columns=[str(year)])
    df.insert(2,str(year),'-')
    #df = df.drop(columns=['family']) # WHy is this here? Relic from old formatting?

    adults_df = df[df['age'] == 'a']
    kids_df = df[df['age'] == 'k']
    kids_df = kids_df.reset_index(drop=True)
    grid = import_rel_grid('familyExclusions')
    kidgrid = import_rel_grid('kidgrid')

    new_adults_df= find_match_with_grid(adults_df,grid,year)
    print("start kids")
    # print(kids_df)
    # print(kidgrid)
    new_kids_df = find_match_with_grid(kids_df,kidgrid,year)
    new_combined = pd.concat([new_adults_df,new_kids_df],ignore_index=True)
    print(new_combined)

    new_combined.to_csv("ClarkeXmasList"+str(year)+".csv", index=False)
# See PyCharm help at https://www.jetbrains.com/help/pych