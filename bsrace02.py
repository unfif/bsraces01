# In[]
from flask import Flask, render_template
import os, requests, copy
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

def unwraptags(obj, taglist):
    for tag in taglist:
        tags = obj.find_all(tag)
        for each in tags:
            each.unwrap()

def delattrs(obj, attrlist):
    for attr in attrlist:
        attrs = obj.select('[' + attr + ']')
        for each in attrs:
            del each[attr]

baseurl = 'http://race.netkeiba.com'
racelistid = 'p0527'
racelisturl = baseurl + '/?pid=race_list_sub&id=' + racelistid
racelistreq = requests.get(racelisturl)
# racelistreq.status_code

bsracepage = BeautifulSoup(racelistreq.text, 'lxml')
with open('C:/Users/pathz/Documents/web/netkeiba/fapp/racelist/racelist' + racelistid + '.html', mode='w', encoding='utf-8') as fw:
    fw.write(str(bsracepage))

# In[]
bsplacelist = bsracepage.select('.RaceList_Box .race_top_hold_list')
# bsplacelist = [bsplacelist[0]]###
titles = []
races = []
detaillist = []
for i, place in enumerate(bsplacelist):
    titles.append(place.select('.kaisaidata')[0].text)
    races.append(place.ul('li'))

    urls = []
    for race in races[i]:
        urls.append(baseurl + race.a['href'])

    # urls = [urls[0], urls[1]]###
    detaillist.append({})
    detaillist[i]['title'] = titles[i]
    detaillist[i]['urls'] = urls
    detaillist[i]['bsraces'] = []
    detaillist[i]['tagracetbls'] = []
    detaillist[i]['bsracetbls'] = []
    for j, detailurl in enumerate(detaillist[i]['urls']):
        bslist = detaillist[i]['bsraces']
        reqdetailurl = requests.get(detailurl) # commentouted posibelity
        bslist.append(BeautifulSoup(reqdetailurl.content, 'lxml'))
        unwraptags(bslist[j], ['br', 'diary_snap', 'diary_snap_cut'])
        delattrs(bslist[j], ['style', 'cellpadding', 'cellspacing'])
        for table in bslist[j]('table'):
            table['class'].extend(['table', 'table-striped', 'table-hover'])

        for th in bslist[j]('th'):
            contents = th.contents[:]
            th.string = ''
            for content in contents:
                th.string += content

        tagracetbls = detaillist[i]['tagracetbls']
        tagracetbls.append(bslist[j].select('.race_table_01')[0])

        tmptbl = BeautifulSoup('<table class="table table-striped table-hover"></table>', 'lxml')

        for k, tr in enumerate(tagracetbls[j]('tr')):
            if k == 0:
                tmptbl.table.append(tmptbl.new_tag('thead'))
                tmptbl.thead['class'] = ['thead-dark']
                tmptbl.thead.append(tr)
                tmptbl.table.append(tmptbl.new_tag('tbody'))
            else:
                tmptbl.tbody.append(tr)

        detaillist[i]['bsracetbls'].append(tmptbl)

# In[]
defaultlayout = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>test</title>
    <link rel="stylesheet" href="../static/css/bootstrap.min.css">
    <script src="../static/js/jquery-3.3.1.min.js"></script>
    <script src="../static/js/popper.min.js"></script>
    <script src="../static/js/bootstrap.min.js"></script>
</head>
<body>
    <div class="container-fluid">
        <div class="table-responsive">
        </div>
    </div>
</body>
<style>
    html{
        font-size: 12px;
    }

    body{
        margin: 0;
        padding: 0;
        /*background: #eee;*/
    }

    /*table{
        border-collapse: collapse;
    }*/

    .table th, .table td{
        padding: 0.25rem;
        /*border: 1px solid #000;*/
        white-space: nowrap;
    }

    th{
        /*background: #666;*/
        /*color: #eee;*/
        text-align: center;
    }

    /*td {
        background: #eee;
    }*/
</style>
</html>'''

bshtml = BeautifulSoup(defaultlayout, 'lxml')
for detail in detaillist:
    for bsracetbl in detail['bsracetbls']:
        bshtml.find('div', attrs={'class': 'table-responsive'}).append(bsracetbl.table)

with open('C:/Users/pathz/Documents/heroku/testflask01/templates/index.html', mode='w', encoding='utf-8') as fw:
    fw.write(str(bshtml))

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
