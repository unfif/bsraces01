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

defaultlayout = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>test</title>
    <link rel="stylesheet" href="../static/css/bootstrap.min.css">
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <div class="container-fluid">
    </div>
    <script src="../static/js/jquery-3.3.1.min.js"></script>
    <script src="../static/js/popper.min.js"></script>
    <script src="../static/js/bootstrap.min.js"></script>
    <script src="../static/js/main.js"></script>
</body>
</html>'''.replace('\n', '')

baseurl = 'http://race.netkeiba.com'
racelistid = 'p0603'
racelisturl = baseurl + '/?pid=race_list_sub&id=' + racelistid
racelistreq = requests.get(racelisturl) # commentouted posibelity
# racelistreq.status_code

bsracepage = BeautifulSoup(racelistreq.text, 'lxml')
with open('C:/Users/pathz/Documents/web/netkeiba/fapp/racelist/racelist' + racelistid + '.html', mode='w', encoding='utf-8') as fw:
    fw.write(str(bsracepage).replace('\n', ''))

# In[]
tagplacelist = bsracepage.select('.RaceList_Box .race_top_hold_list')
# tagplacelist = [tagplacelist[0]]###
titles = []
races = []
detaillist = []
for i, place in enumerate(tagplacelist):
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
    for j, detailurl in enumerate(detaillist[i]['urls']):
        bsraces = detaillist[i]['bsraces']
        reqdetailurl = requests.get(detailurl) # commentouted posibelity
        bsraces.append(BeautifulSoup(reqdetailurl.content, 'lxml'))
        unwraptags(bsraces[j], ['br', 'diary_snap', 'diary_snap_cut'])
        delattrs(bsraces[j], ['style', 'cellpadding', 'cellspacing'])
        for table in bsraces[j]('table'):
            table['class'].extend(['table', 'table-striped', 'table-hover'])

        for th in bsraces[j]('th'):
            contents = th.contents[:]
            th.string = ''
            for content in contents:
                th.string += content

        bsraces[j].select('.race_table_01')[0].wrap(bsraces[j].new_tag('div'))
        bsraces[j].select('.race_table_01')[0].find_parent()['class'] = ['table-responsive']
        bsraces[j].select('.table-responsive')[0].wrap(bsraces[j].new_tag('div'))
        bsraces[j].select('.table-responsive')[0].find_parent()['class'] = ['tblwrap']
        bsraces[j].select('.tblwrap')[0].insert(0, bsraces[j].new_tag('div'))
        bsraces[j].select('.tblwrap > div')[0]['class'] = ['tbltitle']
        bsraces[j].select('.tblwrap > .tbltitle')[0].insert(0, bsraces[j].new_tag('h2'))
        # bsraces[j].select('.tblwrap > .tbltitle > h2')[0].string = '{:02}'.format(j + 1) + 'R'

        bsraces[j].select('.race_table_01')[0].append(bsraces[j].new_tag('thead'))
        bsraces[j].select('.race_table_01 > thead')[0]['class'] = ['thead-dark']

        for k, tr in enumerate(bsraces[j].select('.race_table_01 > tr')):
            if k == 0:
                bsraces[j].select('.race_table_01 > thead')[0].append(tr)
                bsraces[j].select('.race_table_01')[0].append(bsraces[j].new_tag('tbody'))
            else:
                bsraces[j].select('.race_table_01 > tbody')[0].append(tr)

        # bsraces[j].select('.DateList_Box .active')[0]
        # bsraces[j].select('.race_place .active')[0].text
        # bsraces[j].select('.race_place ul.fc')[0]
        # bsraces[j].select('.mainrace_data .data_intro')[0]
        racenum = bsraces[j].select('.mainrace_data .racedata h1')[0].text.zfill(3)
        bsraces[j].select('.mainrace_data .racedata h1')[0].replace_with(bsraces[j].new_tag('h5'))
        bsraces[j].select('.mainrace_data .racedata h5')[0].append(racenum)
        bsraces[j].select('.mainrace_data .racedata')[0]
        bsraces[j].select('.mainrace_data .race_otherdata')[0]

        bsraces[j].select('.tblwrap > .tbltitle')[0].append(bsraces[j].select('.DateList_Box .active')[0])
        bsraces[j].select('.tblwrap > .tbltitle')[0].append(bsraces[j].select('.race_place ul.fc')[0])
        bsraces[j].select('.tblwrap > .tbltitle')[0].append(bsraces[j].select('.mainrace_data .racedata')[0])

bshtml = BeautifulSoup(defaultlayout, 'lxml')
for detail in detaillist:
    for bsrace in detail['bsraces']:
        bshtml.find('div', attrs={'class': 'container-fluid'}).append(copy.copy(bsrace.select('.tblwrap')[0]))

with open('C:/Users/pathz/Documents/heroku/testflask01/templates/index.html', mode='w', encoding='utf-8') as fw:
    fw.write(str(bshtml).replace('\n', ''))

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
