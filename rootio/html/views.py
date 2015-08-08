from flask import Blueprint, render_template

#the web login api
html = Blueprint('html', __name__, url_prefix='/html')


@html.route('/', methods=['GET', 'POST'])
def index():
    print "entrou index html"
#    print "recebeu name: %s e favourite food: %s" % (request.form['name'], request.form['food']) 
    return render_template('html/index.php')

@html.route('/index.php', methods=['POST'])
def index_php():
    print "entrou index html with PHP "
   # print "request = %s" % request
    return render_template('html/index.php')
