from flask import Flask, render_template, jsonify, request
from plotting import generate_plot, generate_data
from bokeh.embed import components

app = Flask(__name__)

@app.route('/')
def entry_point():
    return render_template("index.html")

@app.route('/get_plot/')
def get_plot():
    ds, trendline = generate_data()
    script, div = components(generate_plot(ds, trendline))
    return jsonify(dict(plot=script+div))

@app.route('/done')
def done():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)