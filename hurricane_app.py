import os
import csv

from flask import Flask, render_template, request
from hurricane_report import process_cyclone_data

ALLOWED_GEOJSON_EXTENSIONS = {"geojson", "json"}
ALLOWED_HURDAT_EXTENSIONS = {"txt", "csv"}
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def homepage():
    return render_template("index.html")

# the following two functions are based on code available in the official flask
# documentation describing patterns for handling file uploads 
# source: https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
def allowed_file(filename, allowed_extensions):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in allowed_extensions

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "hurdat2" not in request.files or "geojson" not in request.files:
            return render_template("upload_new.html")
        hurdat2_file = request.files["hurdat2"]
        geojson_file = request.files["geojson"]
        if hurdat2_file.filename == "" or geojson_file.filename == "":
            return render_template("upload.html")
        allowed = hurdat2_file and geojson_file and\
            allowed_file(hurdat2_file.filename, ALLOWED_HURDAT_EXTENSIONS) and\
            allowed_file(geojson_file.filename, ALLOWED_GEOJSON_EXTENSIONS) 
        if allowed:
            hurdat2_file.save(os.path.join(app.config["UPLOAD_FOLDER"], "hurdat2.csv"))
            geojson_file.save(os.path.join(app.config["UPLOAD_FOLDER"], "state.geojson"))
        return render_template("upload_success.html")
    return render_template("upload_new.html")

@app.route("/report")
def report():
    correct_template = "report_fail.html"
    hurdat2_file = os.path.join(app.config["UPLOAD_FOLDER"], "hurdat2.csv")
    geojson_file = os.path.join(app.config["UPLOAD_FOLDER"], "state.geojson")
    if os.path.isfile(hurdat2_file) and os.path.isfile(geojson_file):
        success = process_cyclone_data(hurdat2_file, geojson_file)
        if success:
            correct_template = "report.html"
            with open("./landfall_report.csv") as report:
                reader = csv.reader(report)
                next(reader)
                data = list(reader)
                data.reverse()
        else:
            data = "Failed to process your data, sorry :("
    else:
        data = "One of the required files is missing or unreadable."
    
    return render_template(correct_template, data=data)