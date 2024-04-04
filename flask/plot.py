import pandas as pd
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def verify_dataframe_format(df):
    expected_columns = ['Date', 'Workout Name', 'Exercise Name', 'Set Order', 'Weight', 
                        'Reps', 'RPE', 'Distance', 'Distance Unit', 'Seconds', 'Notes', 
                        'Workout Notes', 'Workout Duration']    
    try:
        for col in expected_columns:
            df[col]
    except IndexError:
        raise ValueError(f"Missing columns: {col}")
    return True

def get_info(file):
    df = pd.read_csv(file)
    df = df.rename(columns={"Exercise" : "Exercise Name"})
    return df

def get_exercises(file, date_format, info):
    df = pd.read_csv(file, sep=';')
    if verify_dataframe_format(df):
        df = df[['Date', 'Exercise Name', 'Weight', 'Reps']]
        # TODO: consider handling different weight units
        df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, date_format).date())
        df['Volume'] = df['Weight'] * df['Reps']

        result = pd.merge(df, info, how="left", on="Exercise Name")
        return result

def plot_volumes(data, filename):
    fig, ax = plt.subplots()
    ax = sns.lineplot(data=data, x="Date", y="Volume", label="Volume", marker="H", lw=2.5, ls="--")
    title = filename.split("/")[-1]
    ax.set(ylabel="Volume (kg)", title=title)
    sns.move_legend(ax, "upper left") # set volume legend to upper left

    ax2 = ax.twinx()
    ax2= sns.lineplot(data=data, x="Date", y="Reps", ax=ax2, label="Reps", color="r", marker="*", lw=1, ls=":")
    ax2.set(ylabel="Reps")
    sns.move_legend(ax2, "upper right") # set reps legend to upper right
    
    fig.autofmt_xdate()
    plt.savefig(filename+".png")
    plt.close("all")

def plot_sets(primary, secondary, mrv, mev, filename):
    fig, ax = plt.subplots()
    sns.lineplot(ax=ax, data=primary, x="Date", y="Sets", label="Primary", marker="H")
    sns.lineplot(ax=ax, data=secondary, x="Date", y="Sets", label="Secondary", color="r", marker="p")
    title = filename.split("/")[-1]
    ax.set(title=title)
    ax.axhline(y=mrv, label="MRV", color="green",ls=":")
    ax.axhline(y=mev, label="MEV", color="green",ls=":")
    fig.autofmt_xdate()
    plt.savefig(filename+".png")
    plt.close("all")

def plot_all(data, directory):
    #TODO: filter based on limit
    
    exercises = data["Exercise Name"].unique()
    for ex in sorted(exercises):
        all_sets = data[data["Exercise Name"]==ex]
        all_sets = all_sets.groupby(["Date"]).agg({"Volume" : "sum", "Reps": "sum", "Date": "count"})
        all_sets = all_sets.rename(columns={"Date" : "Sets"})
        filename = directory + "/ex_" + ex
        plot_volumes(all_sets, filename)


    muscle_groups = list(data["Primary muscle group"].unique()) + list(data["Secondary muscle group"].unique()) + [np.nan]
    muscle_groups = set(muscle_groups)
    muscle_groups.remove(np.nan)
    for mg in muscle_groups:
        primary_sets = data[data["Primary muscle group"]==mg]
        secondary_sets = data[data["Secondary muscle group"]==mg]
        
        mrv = primary_sets.iloc[0]["MRV"] if not primary_sets.empty else np.nan
        mev = primary_sets.iloc[0]["MEV"] if not primary_sets.empty else np.nan

        primary_sets = primary_sets.groupby(["Date"]).agg({"Date": "count"})
        primary_sets = primary_sets.rename(columns={"Date" : "Sets"})
        secondary_sets = secondary_sets.groupby(["Date"]).agg({"Date": "count"})
        secondary_sets = secondary_sets.rename(columns={"Date" : "Sets"})

        plot_sets(primary_sets, secondary_sets, mrv, mev, directory + "/mg_"+mg)