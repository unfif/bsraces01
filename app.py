from flask import Flask
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    html = '<header style="padding: 20px; background: #000; color: #fff;"><h1>Test app 01</h1></header>'
    html += '<div class="section">' + datetime.now().ctime() + '</div>'
    html += '<div class="section">' + os.getcwd() + '</div>'
    for each in os.environ:
        html += '<div class="section">' + each + '</div>'
        
    html += '<style>body, h1, h2, h3, h4, h5, h6{margin: 0; padding: 0;} .section{padding: 20px; background: #eee; border-bottom: 2px solid #000;}</style>'
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=True)
