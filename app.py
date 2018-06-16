# In[]
from flask import Flask, render_template, request
import os, requests
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

# In[]
@app.route('/')
def index():
    data = {}

    return render_template('index.html', data=data)

@app.route('/env')
def env():
    data = {
        'ctime': datetime.now().ctime(),
        'cwd': os.getcwd(),
        'env': os.environ
    }
    # html = '<header style="padding: 20px; background: #000; color: #fff;"><h1>Test app 01</h1></header>'
    # html += '<div class="section">' + datetime.now().ctime() + '</div>'
    # html += '<div class="section">' + os.getcwd() + '</div>'
    # for each in os.environ:
    #     html += '<div class="section">' + each + '</div>'
    #
    # html += '<style>body, h1, h2, h3, h4, h5, h6{margin: 0; padding: 0;} .section{padding: 5px 20px; background: #eee; border-bottom: 2px solid #000;}</style>'
    # return html

    return render_template('env.html', data=data)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
