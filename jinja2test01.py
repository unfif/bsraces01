from jinja2 import Environment, FileSystemLoader
import os

cwd = os.chdir('C:/Users/pathz/Documents/heroku/bsraces01')
tpldir = os.path.join(os.getcwd(), 'templates')
os.listdir(tpldir)
env = Environment(
    loader = FileSystemLoader(tpldir),
    trim_blocks = True,
    lstrip_blocks = True
)

tpls = {}
for file in os.listdir(tpldir):
    tpls[os.path.splitext(file)[0]] = env.get_template(file)

# tpl = env.get_template('default.html')
# html = tpl.render({'title': 'test jinja2'})
data = {
    'title': 'test jinja2',
    'container_fluid': True
}
render = tpls['form'].render(data).replace('\n', '')

with open(os.path.join(tpldir, 'testjinja01.html'), 'w', encoding='utf-8') as fw:
    fw.write(render)

from bs4 import BeautifulSoup
import lxml

markup = '<a href="http://example.com/">I linked to <i>example.com</i></a>'
soup = BeautifulSoup(markup, 'lxml')
a_tag = soup

a_tag
a_tag.body.unwrap()
a_tag.html.unwrap()
a_tag.body.extract()
a_tag
soup.extract()
