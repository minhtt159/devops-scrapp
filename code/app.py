import re
import os
import logging
import sys
import pandas as pd
import json
from flask import Flask, request, render_template, make_response
from werkzeug.utils import secure_filename
# from geopy.geocoders import Nominatim
from address_to_price import get_price_from_location
from house_dataclass import HouseWOZ

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)
uploads_dir = os.path.join(app.instance_path, "uploads")
try:
    os.makedirs(uploads_dir)
except FileExistsError:
    # directory already exists
    pass

# geolocator = Nominatim(user_agent="scrapp")

result_arr = {}


def get_df(list_of_houses):
    result = pd.DataFrame()
    for house in list_of_houses:
        assert isinstance(list_of_houses[house], HouseWOZ), "Data error"
        data = json.loads(list_of_houses[house].to_json())
        df = pd.json_normalize(data)
        result = pd.concat([result, df], ignore_index=True)
    return result


# def reverse_address(row):
#     try:
#         coord_arr = [float(i) for i in row.split(",")]
#         logging.info(f"Coordinate: {coord_arr}")
#         location = geolocator.reverse(",".join(str(i) for i in coord_arr))
#         logging.info(f"Location: {location.address}")
#     except Exception as e:
#         location = row
#         logging.info(f"Location: {location}")
#     return location


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    global result_arr, uploads_dir

    # Get the uploaded CSV file
    file = request.files["csv"]
    # Get the text input from the user
    column_name = (
        request.form["text"] if len(request.form["text"]) != 0 else "house_name"
    )

    try:
        # Log file to server
        out_file = os.path.join(uploads_dir, secure_filename(file.filename))
        file.save(out_file)
        # Load the CSV data into a pandas dataframe
        df = pd.read_csv(out_file, delimiter=";")
        # logging.info(df)
        # logging.info(column_name)

        # Get house list from csv file
        house_list = df[column_name]
        for house in house_list:
            logging.info(f"====== Process {house} =====")
            result = get_price_from_location(house)
            logging.info(f"Got price for {result.house_name}: {result.WOZ}")
            if result.house_name in result_arr:
                logging.info(f"Overwrite {result.house_name}")
            result_arr[result.house_name] = result
        df = get_df(result_arr)
    except Exception as e:
        logging.error(e)
        return render_template("error.html")
    return render_template("results.html", df=df)

@app.route("/download_csv", methods=["GET"])
def download_csv():
    global result_arr

    # Parse result_arr to pandas dataframe
    df = get_df(result_arr)
    # convert the dataframe to a csv string
    csv = df.to_csv(index=False)

    # create a response object with the csv data
    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=results.csv"
    response.headers["Content-Type"] = "text/csv"

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)