import io
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import cross_origin
import pandas as pd
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import boto3
from base64 import encodebytes
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

def get_info(file):
    df = pd.read_csv(file)
    df = df.rename(columns={"Exercise" : "Exercise Name"})
    return df

def get_exercises(file, date_format, info):
    df = pd.read_csv(file, sep=';')
    df = df[['Date', 'Exercise Name', 'Weight', 'Reps']]
    # TODO: consider handling different weight units
    df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, date_format).date())
    df['Volume'] = df['Weight'] * df['Reps']

    result = pd.merge(df, info, how="left", on="Exercise Name")
    return result

def plot_volumes(data, filename):
    fig, ax = plt.subplots()
    ax = sns.lineplot(data=data, x="Date", y="Volume", label="Volume", marker="H", lw=2.5, ls="--")
    ax.set(ylabel="Volume (kg)", title=filename[:-4])
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
    ax.set(title=filename[:-4])
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

@app.route('/get_gainz', methods=['POST'])
@cross_origin()
def get_gainz():
    file = request.files.get('file')
    exercises_info = get_info("exercises.csv")
    exercises = get_exercises(file, '%Y-%m-%d %H:%M:%S', exercises_info)
    plot_all(exercises, "./plots")

    encoded_imges = []
    for _, _, files in os.walk("./plots"):
        for file_name in files:
            encoded_imges.append(get_response_image("./plots/" + file_name))
            os.remove("./plots/" + file_name)
    return jsonify(encoded_imges)

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img