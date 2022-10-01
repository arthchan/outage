#!/usr/bin/env python3
"""Convert Excel data files to ttl data files."""

# Import libraries
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from rdflib import Graph, Namespace
import pandas as pd
import os

# Check if required folders exist
if not os.path.isdir("uploads"):
    os.makedirs("uploads")
if not os.path.isdir("data_ttl"):
    os.makedirs("data_ttl")

# Initialise fixed attributes
UPLOAD_FOLDER = os.getcwd() + '/uploads'
DATA_FOLDER = os.getcwd() + '/data_ttl'
ALLOWED_EXTENSIONS = {"xlsx"}

# Initialise dictionary
type_dict = {
    "Infeed Transformer": "ITX",
    "33kV Busbar": "33BUS",
    "33kV Circuit Breaker": "33CB",
    "33kV Position Switch": "33PS",
    "Distribution Transformer": "DTX",
    "11kV Busbar": "11BUS",
    "11kV Circuit Breaker": "11CB",
    "3.3kV Busbar": "3P3BUS",
    "Chiller": "CHIL",
    "11kV RMU Isolator": "RMUI",
    "11kV RMU Circuit Breaker": "RMUCB",
    "Service Transformer": "STX",
    "Rectifier Transformer": "RTX",
    "Rectifier": "REC",
    "1.5kV DC Busbar": "DCBUS",
    "1.5kV DC Circuit Breaker": "DCCB",
    "Overhead Line Isolator": "DCI",
    "Overhead Line": "OHL"
}


# Function for file extension verification in file upload
def allowed_file(filename):
    """Verify file extension in file upload."""
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Other initialisations
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Upload
@app.route("/", methods=["GET", "POST"])
def upload():
    """Upload Excel data file and transform to .ttl file."""
    if request.method == "POST":
        file = request.files["file"]

        if file.filename != '' and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Save Excel file in the "uploads" folder
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Read Excel data and form dataframe
            df = pd.read_excel("uploads/" + filename, sheet_name="INPUT")

            # Drop all rows with NaN in dataframe
            df.dropna(axis=0, how="all", inplace=True)

            # Reset dataframe index
            df.reset_index(drop=True, inplace=True)

            # Convert all data to string type
            df = df.astype(str)

            # Create an array to store all subject code
            loc = []
            input_asset = []
            error = False

            # Graph initialisations
            g = Graph()
            LNK = Namespace("http://corp.mtrc.com/imd/pd/lnk%")
            HVS = Namespace("http://corp.mtrc.com/imd/pd/hvs%")
            OHL = Namespace("http://corp.mtrc.com/imd/pd/ohl%")
            LOC = Namespace("http://corp.mtrc.com/imd/pd/loc%")
            g.bind("lnk", LNK)
            g.bind("hvs", HVS)
            g.bind("ohl", OHL)
            g.bind("loc", LOC)

            # Loop through all rows in dataframe
            for index, row in df.iterrows():

                # Check location
                if row[0].upper() not in loc:
                    loc.append(row[0].upper())
                    if len(loc) >= 2:
                        error_message = "Inconsistency in location! " \
                                        "Please check row " + str(index) + '!'
                        print(error_message)
                        return render_template("error.html", em=error_message)

                # HVS
                if '.' not in row[1]:

                    # Store HVS subject code to array input_asset if not exist
                    if row[0].upper() + row[1].upper() not in input_asset:
                        g.set((HVS[row[0].upper() + row[1].upper()], LNK[
                            "hasLocation"], LOC[row[0].upper()]))
                        input_asset.append(row[0].upper() + row[1].upper())

                    # HVS hasType
                    if row[2] == "hasType" and row[3] != "Overhead Line":
                        g.set((HVS[row[0].upper() + row[1].upper()], LNK[
                            "hasType"], HVS[type_dict[row[3].upper()]]))

                    # HVS hasStatus
                    elif row[2] == "hasStatus":
                        g.set((HVS[row[0].upper() + row[1].upper()], LNK[
                            "hasStatus"], HVS[row[3].upper()]))

                    # HVS isConnectedTo
                    elif row[2] == "isConnectedTo":

                        # Connected to HVS
                        if '.' not in row[4]:
                            g.add((HVS[row[0].upper() + row[1].upper()], LNK[
                                "isConnectedTo"], HVS[
                                row[3].upper() + row[4].upper()]))

                        # Connected to OHL
                        elif '.' in row[4]:
                            g.add((HVS[row[0].upper() + row[1].upper()], LNK[
                                "isConnectedTo"], OHL[row[4].upper()]))

                    # Error message
                    else:
                        error_message = "Error in processing row " + str(
                            index + 1) + ' in the Excel file!'
                        print(error_message)
                        return render_template("error.html", em=error_message)

                # OHL
                elif '.' in row[1]:
                    # Store OHL subject code to array input_asset if not exist
                    if row[1].upper() not in input_asset:
                        g.set((OHL[row[1].upper()], LNK["hasLocation"], LOC[
                            row[0].upper()]))
                        input_asset.append(row[1].upper())

                    # OHL hasType
                    if row[2] == "hasType" and row[3] == "Overhead Line":
                        g.set((OHL[row[1].upper()], LNK["hasType"], OHL[
                            type_dict[row[3].upper()]]))

                    # OHL hasStatus
                    elif row[2] == "hasStatus":
                        g.set((OHL[row[1].upper()], LNK["hasStatus"], OHL[
                            row[3].upper()]))

                    # OHL isConnectedTo
                    elif row[2] == "isConnectedTo":

                        # Connected to HVS
                        if '.' not in row[4]:
                            g.add((OHL[row[1].upper()], LNK[
                                "isConnectedTo"], HVS[
                                row[3].upper() + row[4].upper()]))

                        # Connected to OHL
                        elif '.' in row[4]:
                            g.add((OHL[row[1].upper()], LNK[
                                "isConnectedTo"], OHL[row[4].upper()]))

                    # Error message
                    else:
                        error_message = "Error in processing row " + str(
                            index + 1) + ' in the Excel file!'
                        print(error_message)
                        return render_template("error.html", em=error_message)

            # Graph serialisation
            if not error:
                try:
                    if '_' in filename:
                        g.serialize(DATA_FOLDER + '/' + filename.split(
                            '_')[0] + ".ttl", format="turtle")
                        return render_template(
                            "uploaded.html",
                            f=DATA_FOLDER + '/' + filename.split(
                                '_')[0] + ".ttl")
                    else:
                        g.serialize(DATA_FOLDER + '/' + filename.split(
                            '.')[0] + ".ttl", format="turtle")
                        return render_template(
                            "uploaded.html",
                            f=DATA_FOLDER + '/' + filename.split(
                                '.')[0] + ".ttl")
                except BaseException:
                    error_message = "Error in creating the turtle file!"
                    return render_template("error.html", em=error_message)

        else:
            error_message = "Error in uploading the Excel file! " \
                            "Please check the file again!"
            return render_template("error.html", em=error_message)

    return render_template("upload.html")


# Run application
if __name__ == "__main__":
    app.run(debug=True)
