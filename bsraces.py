# In[]
from flask import Flask, render_template
from jinja2 import Environment
import os, requests, lxml, copy, pickle
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

def jrender(html, dict):
    return Environment().from_string(html).render(dict)

defaultlayout = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="../static/css/bootstrap.min.css">
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#resultsModal01">詳細情報</button>
    <div class="container-fluid text-dark">
    </div>
    <script src="../static/js/jquery-3.3.1.min.js"></script>
    <script src="../static/js/popper.min.js"></script>
    <script src="../static/js/bootstrap.min.js"></script>
    <script src="../static/js/main.js"></script>
</body>
</html>'''.replace('    ', '').replace('\n', '')

# defaultlayout = Environment().from_string(defaultlayout).render(title = 'race details')
defaultlayout = jrender(defaultlayout, {'title': 'Race Details'})
baseurl = 'http://race.netkeiba.com'
racelistid = 'p0617'
racelisturl = baseurl + '/?pid=race_list_sub&id=' + racelistid

# In[]
try:
    reqracelist = requests.get(racelisturl) # commentouted posibelity
    with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req01.dat', 'wb') as fw:
        pickle.dump(reqracelist, fw)
except requests.exceptions.RequestException as err:
    with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req01.dat', 'rb') as f:
        reqracelist = pickle.load(f)
        # print(req01.status_code, req01.text)

bsracepage = BeautifulSoup(reqracelist.content, 'lxml')
with open('C:/Users/pathz/Documents/web/netkeiba/fapp/racelist/racelist' + racelistid + '.html', 'w', encoding='utf-8') as fw:
    fw.write(str(bsracepage).replace('\n', ''))

# In[]
tagplacelist = copy.copy(bsracepage).select('.RaceList_Box .race_top_hold_list')
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

    # urls = [urls[0], urls[1], urls[2]]###
    detaillist.append({})
    detaillist[i]['title'] = titles[i]
    detaillist[i]['urls'] = urls
    detaillist[i]['bsraces'] = []
    detaillist[i]['bsracesorig'] = []
    for j, detailurl in enumerate(detaillist[i]['urls']):
        bsraces = detaillist[i]['bsraces']
        try:
            reqdetailurl = requests.get(detailurl) # commentouted posibelity
            with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req02.dat', 'wb') as fw:
                pickle.dump(copy.copy(reqracelist), fw)
        except requests.exceptions.RequestException as err:
            with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req02.dat', 'rb') as f:
                reqdetailurl = pickle.load(f)

        bsrace = BeautifulSoup(reqdetailurl.content, 'lxml')
        detaillist[i]['bsracesorig'].append(bsrace)
        bsraces.append(copy.copy(bsrace))
        unwraptags(bsraces[j], ['br', 'diary_snap', 'diary_snap_cut'])
        delattrs(bsraces[j], ['style', 'cellpadding', 'cellspacing'])
        for table in bsraces[j]('table'):
            table['class'].extend(['table', 'table-striped', 'table-hover'])

        for th in bsraces[j]('th'):
            contents = th.contents[:]
            th.string = ''
            for content in contents:
                th.string += content

        bsraces[j].select('.race_table_01')[0].wrap(bsraces[j].new_tag('div', **{'class': ['table-responsive']}))
        bsraces[j].select('.table-responsive')[0].wrap(bsraces[j].new_tag('div', **{'class': ['tblwrap']}))
        bsraces[j].select('.tblwrap')[0].insert(0, bsraces[j].new_tag('div', **{'class': ['tbltitle', 'bg-light', 'text-dark']}))
        # bsraces[j].select('.tblwrap > .tbltitle')[0].insert(0, bsraces[j].new_tag('h2'))
        # bsraces[j].select('.tblwrap > .tbltitle > h2')[0].string = '{:02}'.format(j + 1) + 'R'
        bsraces[j].select('.race_table_01')[0].append(bsraces[j].new_tag('thead', **{'class': ['thead-dark']}))

        for k, tr in enumerate(bsraces[j].select('.race_table_01 > tr')):
            if k == 0:
                bsraces[j].select('.race_table_01 > thead')[0].append(tr)
                bsraces[j].select('.race_table_01')[0].append(bsraces[j].new_tag('tbody'))
            elif 1 <= k <= 5:
                tr['class'] = ['disp']
                bsraces[j].select('.race_table_01 > tbody')[0].append(tr)
            else:
                tr['class'] = ['disptgl', 'hidden']
                bsraces[j].select('.race_table_01 > tbody')[0].append(tr)

        racename = bsraces[j].select('.mainrace_data .racedata h1')[0].text
        bsraces[j].select('.mainrace_data .racedata h1')[0].replace_with(bsraces[j].new_tag('h5'))
        bsraces[j].select('.mainrace_data .racedata h5')[0].append(racename)
        racenum = bsraces[j].select('.mainrace_data .racedata dt')[0].string.strip().zfill(3)
        bsraces[j].select('.mainrace_data .racedata dt')[0].string = racenum

        tbltitle = bsraces[j].select('.tblwrap > .tbltitle')[0]
        tbltitle.append(bsraces[j].select('.DateList_Box .active')[0])
        tbltitle.append(bsraces[j].select('.race_place ul.fc')[0])
        tbltitle.append(bsraces[j].select('.mainrace_data .racedata')[0])
        tbltitle.append(bsraces[j].select('.mainrace_data .race_otherdata')[0])

bshtml = BeautifulSoup(defaultlayout, 'lxml')
for detail in detaillist:
    for bsrace in detail['bsraces']:
        bshtml.select('.container-fluid')[0].append(bsrace.select('.tblwrap')[0])

# In[]
modalclass = bsraces[0].select('.race_result')[0]['class']
modalclass.extend(['modal', 'fade'])
bsraces[0].select('.race_result')[0].attrs = {
    'id': 'resultsModal01',
    'class': modalclass,
    'tabindex': '-1',
    'role': 'dialog',
    'aria-labelledby': 'resultsModal01Label',
    'aria-hidden': 'true'}
modalbody = bsraces[0].select('.pay_block')[0].find_parent()
modalbody['class'] = ['modal-body']
modalbody.wrap(bsraces[0].new_tag('div', **{'class': ['modal-content']}))
modalbody.find_parent().wrap(bsraces[0].new_tag('div', roll='document', **{'class': ['modal-dialog']}))

bsraces[0].select('#resultsModal01 > dl')[0]['class'] = ['raptime']
bsraces[0].select('#resultsModal01 .modal-body')[0].append(bsraces[0].select('#resultsModal01 > dl')[0])

bshtml.select('.container-fluid')[0].append(bsraces[0].select('#resultsModal01')[0])
# bshtml.select('#resultsModal01')[0]

with open('C:/Users/pathz/Documents/heroku/bsraces01/templates/index.html', 'w', encoding='utf-8') as fw:
    fw.write(str(bshtml).replace('\n', ''))

# In[]
