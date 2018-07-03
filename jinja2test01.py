from jinja2 import Environment, FileSystemLoader
import os

os.chdir('C:/Users/pathz/Documents/heroku/bsraces01')
os.path.join(os.getcwd(), 'templates')
os.listdir(os.path.join(os.getcwd(), 'templates'))

tmpldir = os.path.join(os.getcwd(), 'templates')
tmplenv = Environment(loader = FileSystemLoader(tmpldir), trim_blocks = True)

tmplenv.get_template('default.html').render({'title': 'test jinja2'})
