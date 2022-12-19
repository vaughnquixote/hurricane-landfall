from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return "<p>Use this page to upload your files</p>"

@app.route("/report")
def report():
    return "<p>Here is a report based on your data</p>"