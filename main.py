# This is a sample Python script.
import os
import random

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings
# .
import pandas as pd

year = 2024
def print_hi(year):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Ho ho ho, its {year}')  # Press Ctrl+F8 to toggle the breakpoint.

class MyClass:
    def __init__(self, name, age, family, past_giftee, past_past_giftee):
        self.name = name
        self.age = age
        self.family = family
        self.past_giftee =past_giftee
        self.past_past_giftee = past_past_giftee
    def display_info(self):
        print(f"First Name: {self.name}")
        print(f"Age Group:{self.age}")
        print(f"Family: {self.family}")
        print(f"Past Giftee: {self.past_giftee}")
        print(f"Second Past Giftee: {self.past_past_giftee}")

def import_gift_history():
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

def import_last_list():
    history = pd.read_csv(os.path.join("ClarkeXmasList.csv"),header=0)
    return (history)

def import_rel_grid(name):
    grid = pd.read_csv(os.path.join(str(name)+".csv"),index_col=0)
    # print(grid)
    return grid

# TODO: change family matching behaivor to be a network map of relationships that is checked each time a match is made,
#  aka bonnie match wendy j, matrix result = sibling, sibling in list=[disallowed relationships] therefore rematch.
#  need to make relationship df then list of unallowed relationships and add it into rematch condition
# Press the green button in the gutter to run the script.
def find_match(df, year):
    error_code=0
    adults = df['Giver'].tolist()
    for giver in df['Giver']:
        rematch_count=0
        match = False
        while match == False:
            giftee = random.choice(adults)
            print(f"---------------")
            print(f"Giver: {giver} -> {giftee}")
            # print(f"Random Giftee: {giftee}")
            print(f"giftees remaining: {len(adults)}")
            past_giftee = df.loc[df['Giver'] == giver, str(year - 1)].values[0]
            print(f"Past Giftee {year - 1}: {past_giftee}")
            past_past_giftee = df.loc[df['Giver'] == giver, str(year - 2)].values[0]
            giver_family = df.loc[df['Giver'] == giver, 'family'].values[0]
            giftee_family = df.loc[df['Giver'] == giftee, 'family'].values[0]
            if giver_family == giftee_family:
                same_family = True
            else:
                same_family = False

            print(f"Past Past Giftee {year - 2}: {past_past_giftee}")
            if giftee == giver:
                match = False
                print("illegal match")
                print("self gift")
                rematch_count +=1
            elif giftee == past_giftee or giftee == past_giftee:
                match = False
                print("illegal match")
                print("repeat giftee")
                rematch_count +=1
            elif same_family:
                match = False
                print("illegal match")
                print("same family")
                rematch_count +=1
            else:
                match = True
                adults.remove(giftee)
                df.loc[df['Giver'] == giver, str(year)] = giftee
            if rematch_count>= 3:
                error_code = -1
            return df, error_code

    print(df.iloc[:, 0:6])  # Columns + current year and past two
    return df


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

    # print(chosen_rows)



if __name__ == '__main__':
    print_hi(year)

# Example of creating an instance of the class
    example = MyClass(name="Kelsey",age="a",family="Dave", past_giftee="John", past_past_giftee="Jane")
    # example.display_info()
    df = import_last_list()

    # Add column for current year, deleting if already exists
    if str(year) in df.columns:
        df = df.drop(columns=[str(year)])
    df.insert(3,str(year),'-')
    df = df.drop(columns=['family'])

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