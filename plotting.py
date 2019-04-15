
from bokeh.plotting import figure, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import Slider, CustomJS, ImageURL, Circle
from bokeh.colors import RGB
import datetime
from bokeh.layouts import layout, column
import numpy as np
import math


def generate_data(trend_type="linear", n=100, slope=1.0):
    xs = range(n)
    ys = np.random.uniform(0, 100, n)

    if trend_type == "linear":
        for i in range(n):
            ys[i] += (slope * i)

    return ColumnDataSource(data=dict(xs=xs, ys=ys)), ColumnDataSource(data=dict(x=[0.0, 100.0], y=[0, 100], slope=[0, 0]), name="slope_ds")

def generate_plot(ds, trend_line):
    # data =
    tools = ['wheel_zoom', "save", " reset", "tap", "pan"]  # "pan",
    p = figure(tools=tools)

    p.circle(x="xs", y="ys", fill_alpha=0, source=ds)
    p.line(x="x", y="y", source=trend_line)

    mean = np.mean(ds.data['ys'])
    callback = CustomJS(args=dict(source=trend_line), code="""
        var data = source.data;
        var s = slope.value;
        data.slope = s
        k = 100
        x1 = s
        x2 = s * k
       
        m = mean - (x1 + x2) / 2
        data.y[0] = x1 + m;
        data.y[1] = x2 + m;
        source.change.emit();
    """)
    amp_slider = Slider(start=-10.0, end=10, value=0.0, step=.1,
                        title="Slope", callback=callback)
    callback.args["slope"] = amp_slider
    callback.args["mean"] = mean


    return column(p, amp_slider, sizing_mode="scale_width")

if __name__ == '__main__':
    ds = generate_data("linear", n=100)
    show(generate_plot(ds))