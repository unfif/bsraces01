# In[]
from flask import Flask, render_template, request
import os, requests
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
title = 'Test Heroku'

# In[]
@app.route('/')
def index():
    data = {}
    return render_template('index.html', data=data)

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        print(request.form)
    if request.method == 'GET':
        print(request.args)

    return render_template('form.html')

@app.route('/env')
def env():
    data = {
        'ctime': datetime.now().ctime(),
        'cwd': os.getcwd(),
        'env': os.environ
    }
    return render_template('env.html', data=data)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
