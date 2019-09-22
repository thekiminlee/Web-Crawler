from flask import Flask, render_template, request
from search_engine import retrieval

app = Flask(__name__)
engine = retrieval.Retrieval()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':
        result = request.form
        for key, value in result.items():
            engine.prompt_user(value)
            engine.refine_query()
            result = engine.display_web()
        return render_template("result.html", result = result)

if __name__ == '__main__':
    app.run()