import io
from logging.handlers import TimedRotatingFileHandler
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from base64 import encodebytes
from PIL import Image
import pandas as pd
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import logging

load_dotenv()

logger = logging.getLogger(__name__)
handler = TimedRotatingFileHandler(filename='runtime.log', when='D', interval=1, backupCount=90, encoding='utf-8', delay=False)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

root = os.path.dirname(__file__)

@app.route('/', methods=["GET", "POST", "OPTION"])
def default():
    return jsonify('OK'), 200

@app.route('/get_gainz', methods=["POST"])
def get_gainz():
    app.logger.info(f"Got request from {request.remote_addr}")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files.get('file')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if len(file.read()) > MAX_FILE_SIZE_BYTES:
        return jsonify({'error': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes'}), 400
    file.seek(0)
    app.logger.info(f"Request from {request.remote_addr} file OK.")
    exercises_info = get_info(os.path.join(root, "exercises.csv"))
    try:
        exercises = get_exercises(file, '%Y-%m-%d %H:%M:%S', exercises_info)
    except ValueError as e:
        app.logger.error(f"Request from {request.remote_addr} file in wrong format.")
        return jsonify({'error': e.args[0]}), 400
    
    plot_all(exercises, os.path.join(root, "./plots/"))

    encoded_images = []
    for _, _, files in os.walk(os.path.join(root, "./plots")):
        for file_name in files:
            encoded_images.append(_get_response_image(os.path.join(root, "./plots/" + file_name)))
            os.remove(os.path.join(root, "./plots/" + file_name))
    response = jsonify(encoded_images)
    response.headers.add('Access-Control-Allow-Origin', '*')
    app.logger.info(f"Request from {request.remote_addr} sending response with plots.")
    return response

def _get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img

def verify_dataframe_format(df):
    expected_columns = ['Date', 'Workout Name', 'Exercise Name', 'Set Order', 'Weight', 
                        'Reps', 'RPE', 'Distance', 'Distance Unit', 'Seconds', 'Notes', 
                        'Workout Notes', 'Workout Duration']    
    try:
        for col in expected_columns:
            df[col]
    except KeyError:
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
        