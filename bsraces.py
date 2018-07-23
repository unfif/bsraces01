# In[]
from flask import Flask, render_template
from jinja2 import Environment, FileSystemLoader
import os, requests, lxml, copy, pickle, re
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)
lightmode = False
# lightmode = True

cwd = os.chdir('C:/Users/pathz/Documents/heroku/bsraces01')
tpldir = os.path.join(os.getcwd(), 'templates')
env = Environment(
    loader = FileSystemLoader(tpldir),
    trim_blocks = True,
    lstrip_blocks = True
)
tpls = {}
for file in os.listdir(tpldir):
    tpls[os.path.splitext(file)[0]] = env.get_template(file)

data = {
    'title': 'Race Details',
    'container_fluid': True
}
defaultlayout = tpls['default'].render(data).replace('\n', '')

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

def strrender(html, dict):
    return Environment().from_string(html).render(dict)

baseurl = 'http://race.netkeiba.com'
racelistid = 'p0722'
racelisturl = baseurl + '/?pid=race_list_sub&id=' + racelistid

# In[]
try:
    reqracelist = requests.get(racelisturl) # commentouted posibelity
    with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req01.dat', 'wb') as fw:
        pickle.dump(reqracelist, fw)
except requests.exceptions.RequestException as err:
    with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req01.dat', 'rb') as f:
        reqracelist = pickle.load(f)

bsracepage = BeautifulSoup(reqracelist.text, 'lxml')
with open('C:/Users/pathz/Documents/web/netkeiba/fapp/racelist/racelist' + racelistid + '.html', 'w', encoding='utf-8') as fw:
    fw.write(str(bsracepage).replace('\n', ''))

# In[]
tagplacelist = bsracepage.select('.RaceList_Box .race_top_hold_list')
# if lightmode: tagplacelist = [tagplacelist[0]]###
titles = []
races = []
detaillist = []
raceplacenos = []
raceinfos = []
for i, place in enumerate(tagplacelist):
    placedate = place.select('.kaisaidata')[0].text
    titles.append(placedate)
    races.append(place.ul('li'))
    raceinfos.append({})
    raceinfos[i]['placedate'] = placedate
    raceinfos[i]['raceorder'] = []

    urls = []
    for race in races[i]:
        urls.append(baseurl + race.a['href'])

    if lightmode: urls = [urls[0], urls[1], urls[2]]###
    detaillist.append({})
    detaillist[i]['title'] = titles[i]
    detaillist[i]['urls'] = urls
    detaillist[i]['bsraces'] = []
    detaillist[i]['bsracesorig'] = []
    for j, detailurl in enumerate(detaillist[i]['urls']):
        bsraces = detaillist[i]['bsraces']
        try:
            reqdetailurl = requests.get(detailurl) # commentouted posibelity
            with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req02_' + '{:04}'.format(i + 1) + '{:04}'.format(j + 1) + '.dat', 'wb') as fw:
                pickle.dump(reqdetailurl, fw)
        except requests.exceptions.RequestException as err:
            with open('C:/Users/pathz/Documents/heroku/bsraces01/_test/tmp/req02_' + '{:04}'.format(i + 1) + '{:04}'.format(j + 1) + '.dat', 'rb') as f:
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

        raceinfos[i]['raceorder'].append(pd.read_html(str(bsraces[j].select('.race_table_01')[0]), header = 0)[0])
        # df01.append(pd.read_html(str(bsraces[j].select('.race_table_01')[0]), header = 0)[0])

        # if j == 0: print(bsraces[j])
        bsraces[j].select('.race_table_01')[0].wrap(bsraces[j].new_tag('div', **{'class': ['table-responsive']}))
        bsraces[j].select('.table-responsive')[0].wrap(bsraces[j].new_tag('div', **{'class': ['tblwrap']}))
        bsraces[j].select('.tblwrap')[0].insert(0, bsraces[j].new_tag('div', **{'class': ['titlewrap', 'd-flex']}))
        bsraces[j].select('.titlewrap')[0].append(bsraces[j].new_tag('button', **{'class': ['btn', 'btn-primary', 'faa-parent', 'animated-hover'], 'data-toggle': ['modal'], 'data-target': ['#resultsModal' + '{:02}'.format(j)]}))
        # bsraces[j].select('.titlewrap > button')[0].string = '詳細'
        bsraces[j].select('.titlewrap > button')[0].append(bsraces[j].new_tag('i', **{'class': ['fas', 'fa-chevron-down', 'faa-pulse']}))
        bsraces[j].select('.titlewrap')[0].append(bsraces[j].new_tag('div', **{'class': ['tbltitle', 'bg-light', 'text-body', 'align-items-center']}))

        # modalの作成
        bsraces[j].select('.tblwrap')[0].append(bsraces[j].new_tag('div',  **{
            'id': 'resultsModal' + '{:02}'.format(j),
            'class': ['modal', 'fade'],
            'tabindex': '-1',
            'role': 'dialog',
            'aria-labelledby': 'resultsModal' + '{:02}'.format(j) + 'Label',
            'aria-hidden': 'true'}))

        # jinja2モーダル用定義リスト
        # modalcontent = bsraces[j].new_tag('modalcontent', **{'class': 'modalcontent'})
        # for dl in bsraces[j].select('.race_result dl'):
        #     if not dl.has_attr('class'): dl['class'] = ['raptime']
        #     modalcontent.append(dl)
        #
        # modalcontent.insert(0, "<modalbody>{%- md.modal(<contents></contents>) -%}{%- block contents -%}</modalbody>")
        # modalcontent.append("{%- endblock -%}")
        # modalcontent.unwrap()
        # print(modalcontent)

        modalbody = bsraces[j].select('.pay_block')[0].find_parent()
        modalbody['class'] = ['modal-body']
        bsraces[j].select('.race_result > dl')[0]['class'] = ['raptime']
        bsraces[j].select('.modal-body')[0].append(bsraces[j].select('.raptime')[0])
        modalbody.wrap(bsraces[j].new_tag('div', **{'class': ['modal-content']}))
        modalbody.find_parent().wrap(bsraces[j].new_tag('div', roll='document', **{'class': ['modal-dialog']}))
        bsraces[j].select('.tblwrap > .modal')[0].append(bsraces[j].select('.modal-dialog')[0])
        bsraces[j].select('.tblwrap')[0].append(bsraces[j].select('#resultsModal' + '{:02}'.format(j))[0])

        bsraces[j].select('.tbltitle')[0].append(bsraces[j].new_tag('table', **{'class': ['infotbl', 'hidden']}))
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

        # レース名h5とレースナンバーdtを新規格納
        racename = bsraces[j].select('.mainrace_data .racedata h1')[0].text
        bsraces[j].select('.mainrace_data .racedata h1')[0].replace_with(bsraces[j].new_tag('h5'))
        bsraces[j].select('.mainrace_data .racedata h5')[0].append(racename)
        racenum = bsraces[j].select('.mainrace_data .racedata dt')[0].string.strip().zfill(3)
        bsraces[j].select('.mainrace_data .racedata dt')[0].string = racenum
        # print(bsraces[j].select('.mainrace_data'))

        # テーブルタイトル部に各種要素を追加
        tbltitle = bsraces[j].select('.titlewrap > .tbltitle')[0]
        bsraces[j].select('.tbltitle > .infotbl')[0].append(bsraces[j].new_tag('tr'))
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('th', **{'class': ['hidden']}))
        bsraces[j].select('.tbltitle > .infotbl > tr > th')[0].string = '日程'
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('td'))
        bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1].string = bsraces[j].select('.DateList_Box .active')[0].text
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('td'))
        bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1].string = racenum

        tbltitle.append(bsraces[j].select('.DateList_Box .active')[0])
        bsraces[j].select('.tbltitle > .infotbl')[0].append(bsraces[j].new_tag('tr'))
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('th', **{'class': ['hidden']}))
        bsraces[j].select('.tbltitle > .infotbl > tr > th')[-1].string = '開催地'
        for place in bsraces[j].select('.race_place ul.fc')[0].select('li > a'):
            bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('td'))
            if place.has_attr('class'):
                bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1]['class'] = place['class'] + ['text-primary']
            else:
                bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1]['class'] = ['text-muted']
            bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1].string = place.text

        raceplace = bsraces[j].select('.race_place ul.fc a.active')[0].string
        raceplacenos.append(raceplace + racenum)

        tbltitle.append(bsraces[j].select('.race_place ul.fc')[0])
        bsraces[j].select('.tbltitle > .infotbl')[0].append(bsraces[j].new_tag('tr'))
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('th', **{'class': ['hidden']}))
        bsraces[j].select('.tbltitle > .infotbl > tr > th')[-1].string = '概要1'
        for raceinfo01 in bsraces[j].select('.mainrace_data .racedata')[0].dd.stripped_strings:
            bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('td'))
            bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1].string = raceinfo01

        tbltitle.append(bsraces[j].select('.mainrace_data .racedata')[0])
        bsraces[j].select('.tbltitle > .infotbl')[0].append(bsraces[j].new_tag('tr'))
        bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('th', **{'class': ['hidden']}))
        bsraces[j].select('.tbltitle > .infotbl > tr > th')[-1].string = '概要2'
        for raceinfo02 in bsraces[j].select('.mainrace_data .race_otherdata')[0].stripped_strings:
            bsraces[j].select('.tbltitle > .infotbl > tr')[-1].append(bsraces[j].new_tag('td'))
            bsraces[j].select('.tbltitle > .infotbl > tr > td')[-1].string = raceinfo02

        tbltitle.append(bsraces[j].select('.mainrace_data .race_otherdata')[0])

# bshtml = BeautifulSoup(defaultlayout, 'lxml')
# for detail in detaillist:
#     for bsrace in detail['bsraces']:
#         bshtml.select('.container-fluid')[0].append(bsrace.select('.tblwrap')[0])
bshtml = BeautifulSoup('<container class="container-fluid"></container>', 'lxml')
for detail in detaillist:
    for bsrace in detail['bsraces']:
        bshtml.select('.container-fluid')[0].append(bsrace.select('.tblwrap')[0])

bshtml.container.insert(0, "{%- extends 'default.html' -%}{%- block contents -%}")
bshtml.container.append("{%- endblock -%}")
bshtml.container.unwrap()
bshtml.body.unwrap()
bshtml.html.unwrap()
# print(bshtml)
bshtml = env.from_string(str(bshtml)).render(data)
# print(bshtml)

with open('C:/Users/pathz/Documents/heroku/bsraces01/templates/index.html', 'w', encoding='utf-8') as fw:
    fw.write(str(bshtml).replace('\n', ''))

# In[]
raceinfos
len(raceinfos[0]['raceorder'])
raceinfos[0]['raceorder'][0]['騎手']

ptn = '☆|▲|△'
jockeyinfo = None
jockeyinfo2 = []
jockeyinfo3 = {}
for placeinfo in raceinfos:
    raceorders = []
    raceorders2 = {}
    for info in placeinfo['raceorder']:
        substr = []
        for jk in info['騎手']:
            sub = re.sub(ptn, '', jk)
            substr.append(sub)
        jockeyinfo = pd.concat([jockeyinfo, pd.Series(substr)], axis=1, ignore_index=True)
        raceorders.append(substr)
        raceorders2.update({'substr': substr})

    jockeyinfo2.append(raceorders)
    jockeyinfo3.update({'raceorder': raceorders})

len(jockeyinfo2[0])
jockeyinfo.columns = raceplacenos
jockeyinfo
jockeyinfo2
jockeyinfo3

jockeyinfo.iloc[0].value_counts()
jockeyinfo.iloc[0]
jockeyinfo.iloc[1]
pd.concat([jockeyinfo.iloc[0], jockeyinfo.iloc[1]])
pd.concat([jockeyinfo.iloc[0], jockeyinfo.iloc[1]]).value_counts()
pd.concat([jockeyinfo.iloc[0], jockeyinfo.iloc[1], jockeyinfo.iloc[2]]).value_counts()
jockeyinfo.nunique()


list(jockeyinfo.iterrows())[0]
cctrows = pd.Series([])
for row in jockeyinfo.iterrows():
    # print(row[1])
    # pd.concat([cctrows, row[1]], axis=1, ignore_index=True)
    cctrows.append(row[1])

cctrows.nunique()

# In[]
s1 = pd.Series([1,2,3,4])
s2 = pd.Series([5,6,7,8])
s3 = s1.append(s2)
s3 = pd.concat([s1,s2], axis=0)
s3

help(re)
