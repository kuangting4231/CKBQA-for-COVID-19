from flask import Flask, render_template, request, jsonify
from knowledge_search import query
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html')


@app.route('/search_name', methods=['GET', 'POST'])
def search_name():
    name = request.args.get('name')
    json_data=query(str(name))
    return jsonify(json_data)


if __name__ == '__main__':
    app.debug=True
    app.run()