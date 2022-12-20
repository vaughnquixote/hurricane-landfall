import os
import csv

from flask import Flask, render_template, request
from hurricane_report import process_cyclone_data

ALLOWED_GEOJSON_EXTENSIONS = {"geojson", "json"}
ALLOWED_HURDAT_EXTENSIONS = {"txt", "csv"}
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
REPORT_FOLDER = os.path.join(os.getcwd(), "reports")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def homepage():
    """
    Render the homepage.
    """
    return render_template("index.html")

# the following two functions are based on code available in the official flask
# documentation describing patterns for handling file uploads 
# source: https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
def allowed_file(filename, allowed_extensions):
    """
    Check that the given filename has one of the allowed extensions

    Params:
    filename (str): file name
    allowed_extensions (set{str}): the acceptable extensions

    Returns:
    bool: indicating whether or not the filename is allowed
    """
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in allowed_extensions

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    Upload two files to the service, a hurdat2 formatted file and a geojson 
    file. 
    """

    if request.method == "POST":
        # if either file is missing reload the same page
        if "hurdat2" not in request.files or "geojson" not in request.files:
            return render_template("upload_new.html")

        # get files from request params
        hurdat2_file = request.files["hurdat2"]
        geojson_file = request.files["geojson"]

        # if either is empty reload same page
        if hurdat2_file.filename == "" or geojson_file.filename == "":
            return render_template("upload.html")

        # get boolean indicating that both files are not null and that they 
        # have the correct file extensions
        allowed = hurdat2_file and geojson_file and\
            allowed_file(hurdat2_file.filename, ALLOWED_HURDAT_EXTENSIONS) and\
            allowed_file(geojson_file.filename, ALLOWED_GEOJSON_EXTENSIONS) 
        
        # save the files to the uploads dir
        if allowed:
            hurdat2_file.save(os.path.join(app.config["UPLOAD_FOLDER"], "hurdat2.csv"))
            geojson_file.save(os.path.join(app.config["UPLOAD_FOLDER"], "state.geojson"))
        return render_template("upload_success.html")
    return render_template("upload_new.html")

@app.route("/report")
def report():
    """
    Get both of the uploaded files, process them, generate a csv report 
    of those that made landfall, the date they made landfall and their
    maximum wind speed. 
    """
    
    # variable holding template to be rendered
    correct_template = "report_fail.html"
    
    # get the file paths
    hurdat2_file = os.path.join(app.config["UPLOAD_FOLDER"], "hurdat2.csv")
    geojson_file = os.path.join(app.config["UPLOAD_FOLDER"], "state.geojson")

    # check that the files exist and are readable
    if os.path.isfile(hurdat2_file) and os.path.isfile(geojson_file):
        # process the data and generate a report, saved in the report folder
        success = process_cyclone_data(hurdat2_file, geojson_file, \
            output_dir=REPORT_FOLDER)
        if success:
            correct_template = "report.html"
            with open(os.path.join(REPORT_FOLDER, "landfall_report.csv")) as report:
                reader = csv.reader(report)
                # dont pass header to template
                next(reader)
                data = list(reader)
                data.reverse()
        else:
            data = "Failed to process your data, sorry :("
    else:
        data = "One of the required files is missing or unreadable."
    
    return render_template(correct_template, data=data)