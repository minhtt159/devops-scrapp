import logging
import sys
import pandas as pd
import json
from flask import Flask, request, render_template, make_response
from address_to_price import get_price_from_location
from house_dataclass import HouseWOZ

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)

result_arr = {}


def get_df(list_of_houses):
    result = pd.DataFrame()
    for house in list_of_houses:
        assert isinstance(list_of_houses[house], HouseWOZ), "Data error"
        data = json.loads(list_of_houses[house].to_json())
        df = pd.json_normalize(data)
        result = pd.concat([result, df], ignore_index=True)
    return result


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    global result_arr
    
    house_id = request.form["text"] if len(request.form["text"]) != 0 else ""

    try:
        logging.info(f"====== Process {house_id} =====")
        result = get_price_from_location(house_id)
        logging.info(f"Got price for {result.house_name}: {result.WOZ}")
        if result.house_name in result_arr:
            logging.info(f"Overwrite {result.house_name}")
        result_arr[result.house_name] = result
        df = get_df(result_arr)
    except Exception as e:
        logging.error(e)
        return render_template("error.html")
    return df.to_html()

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