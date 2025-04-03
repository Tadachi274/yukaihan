from flask import Flask, render_template
import os
from flask import render_template_string
app = Flask(__name__, template_folder="templates")

@app.route('/')
def hello():
    name = "who"
    #return name
    print("Rendering template...")
    print()
    return render_template('hello.html', title='hello2', name=name)

@app.route('/test')
def test():
    print(render_template("layout.html", title="Test Layout"))
    return "aa"

@app.route('/check_template')
def check_template():
    template_path = os.path.join(app.root_path, "templates", "layout.html")
    exists = os.path.exists(template_path)
    return f"Template found: {exists} (Path: {template_path})"

@app.route('/test_string')
def test_string():
    return render_template_string("<h1>This is a test</h1>")



if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)  
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    
