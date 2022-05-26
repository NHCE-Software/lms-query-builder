import json
from flask import Flask, jsonify
import os
from flask_cors import CORS

from flask import Flask, flash, request, redirect, url_for
from sqlalchemy import JSON
from werkzeug.utils import secure_filename

from core import sanitize

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {"csv"}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/upload', methods=['POST'])
def upload_file():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("souceeeeee", request.form['source'])
            res, cols = sanitize(
                filename=filename, source=request.form['source'])

    return {'data': json.loads(res), 'cols': cols}


if __name__ == "__main__":
    app.debug = True
    app.run()
