from collections import defaultdict
from datetime import datetime
import logging
import pickle
import time

from flask import Flask
from flask import jsonify
from flask import request
import pandas as pd


app = Flask(__name__)

logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

with open("models/model_lama.pkl", "rb") as f:
    model = pickle.load(f)


@app.route("/predict", methods=["POST"])
def predict():
    start = time.time()
    timestamp = datetime.now().strftime("[%Y-%b-%d %H:%M]")

    request_data = request.get_json(force=True)
    non_required_columns = [
        "features_names",
        "batch_size",
        "n_jobs",
        "return_all_predictions",
    ]
    fields = defaultdict(lambda: None)

    if "data" not in request_data or request_data["data"] == "":
        return jsonify(error="Data is required!"), 400
    else:
        fields["data"] = request_data["data"]

    for col in non_required_columns:
        if col in request_data and request_data[col] != "":
            fields[col] = request_data[col]

    if not fields["n_jobs"]:
        fields["n_jobs"] = 1

    data = pd.read_json(fields["data"])
    output = model.predict(
        data=data,
        features_names=fields["features_names"],
        batch_size=fields["batch_size"],
        n_jobs=fields["n_jobs"],
        return_all_predictions=fields["return_all_predictions"],
    )

    elapsed = time.time() - start
    logger.info(
        "%s %s %s %s %s %s",
        timestamp,
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        elapsed,
    )
    return jsonify(prediction=output.data.tolist())


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
