
from bokeh.plotting import figure, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import Slider, CustomJS, ImageURL, Circle, Range1d
from bokeh.colors import RGB
import datetime
from bokeh.layouts import layout, column
import numpy as np
import math

SLOPE_TYPE_LIN = "linear"
SLOPE_TYPE_QUAD = "quadratic"
SLOPE_TYPE_TRIG = "trigonometric"

GRAPH_TYPE_AREA = "area"
GRAPH_TYPE_SCATTER = "scatter"
GRAPH_TYPE_LINE = "line"


def generate_data(slope_type=SLOPE_TYPE_QUAD, n=100, slope=1.0, amplitude = 1.2, exponent = 2.5, plot_type=GRAPH_TYPE_AREA, mu = 1.0):
    xs = []
    ys = []
    q = 0.1
    # mu *= 0.5

    if plot_type == GRAPH_TYPE_AREA:
        if slope_type == SLOPE_TYPE_TRIG:
            xs.append(1.0)
            ys.append(0.0)
            xs.append(0.0)
            ys.append(0.0)
        else:
            xs.append(1.0)
            ys.append(-1.0)
            xs.append(0.0)
            ys.append(-1.0)

    if slope_type == "linear":
        for i in range(n):
            xs.append(i / n)
            ys.append(float((slope * (i / n)) + np.random.normal(0, mu, 1)))

        m = np.mean(ys)
        trend_line = ColumnDataSource(data=dict(x=[0.0, 1.0], y=[m, m], slope=[0, 0]), name="slope_ds")

    elif slope_type == "quadratic":
        trend_xs = []
        trend_ys = []
        for i in range(n):
            x = i / n
            e = np.random.normal(0, mu, 1) * np.sqrt(x)
            xs.append(x)
            ys.append(float(x ** exponent + e))
            trend_xs.append(x)
            trend_ys.append(x)
        trend_line = ColumnDataSource(data=dict(x=trend_xs, y=trend_ys, slope = [1.0] * len(trend_xs)), name="slope_ds")

    elif slope_type == "trigonometric":
        trend_xs = []
        trend_ys = []
        for i in range(n):
            xs.append(i / n)
            ys.append(float(np.sin(i * q) * (amplitude - 1.0) + np.random.normal(0, mu, 1)))
            trend_xs.append(i / n)
            trend_ys.append(0)
        trend_line = ColumnDataSource(data=dict(x=trend_xs, y=trend_ys, slope = [0] * len(trend_xs)), name="slope_ds")

    return ColumnDataSource(data=dict(xs=xs, ys=ys)), trend_line


def generate_plot(ds, trend_line, plot_type = GRAPH_TYPE_AREA, slope_type = SLOPE_TYPE_QUAD):
    # data =
    # tools = ['wheel_zoom', "save", " reset", "tap", "pan"]  # "pan",
    p = figure(tools="")
    if plot_type == GRAPH_TYPE_SCATTER:
        p.circle(x="xs", y="ys", source=ds)
    elif plot_type == GRAPH_TYPE_LINE:
        p.line(x="xs", y="ys", source=ds)
    elif plot_type == GRAPH_TYPE_AREA:
        p.patch(x="xs", y="ys", color="#99d8c9", source=ds)

    if slope_type == SLOPE_TYPE_LIN:
        p.x_range = Range1d(0.0, 1.0)
        p.y_range = Range1d(-0.5, 1.0)
        mean = np.mean(ds.data['ys'])
        p.line(x="x", y="y", line_color="red", source=trend_line)

        callback = CustomJS(args=dict(source=trend_line), code="""
            var data = source.data;
            var s = slope.value;
            data.slope[0] = s
            var x1 = 0
            var x2 = s * 1.0
           
            var m = mean - (x1 + x2) / 2
            data.y[0] = x1 + m;
            data.y[1] = x2 + m;
            source.change.emit();
        """)
        amp_slider = Slider(start=-2.0, end=2.0, value=0.0, step=.01,
                            title=None, callback=callback)
        callback.args["slope"] = amp_slider
        callback.args["mean"] = mean

    elif slope_type == SLOPE_TYPE_TRIG:
        p.line(x="x", y="y", line_color="red", source=trend_line)
        p.y_range = Range1d(-1.2, 1.2)

        callback = CustomJS(args=dict(source=trend_line), code="""
                    var data = source.data;
                    data.slope[0] = amplitude.value -1.0;
                    for (var i = 0; i < source.data['x'].length; i++){
                        data['y'][i] = Math.sin(i * 0.1) * amplitude.value;
                    }
                    source.change.emit();
                """)
        amp_slider = Slider(start=0, end=2.0, value=1.0, step=.01,
                            title=None, callback=callback)
        callback.args["amplitude"] = amp_slider

    elif slope_type == SLOPE_TYPE_QUAD:
        p.x_range = Range1d(0.0, 1.0)
        p.y_range = Range1d(-0.2, 1.2)
        p.line(x="x", y="y", line_color="red", source=trend_line)

        callback = CustomJS(args=dict(source=trend_line), code="""
                    var data = source.data;
                    data.slope[0] = slope.value - 1.0;
                    for (var i = 0; i < source.data['x'].length; i++){
                        x = source.data['x'][i]
                        data['y'][i] = Math.pow(x, slope.value);
                    }
                    source.change.emit();
                """)
        amp_slider = Slider(start=0, end=6, value=1.0, step=.01,
                            title=None, callback=callback)
        callback.args["slope"] = amp_slider

    return column(p, amp_slider, sizing_mode="scale_width")

if __name__ == '__main__':
    ds = generate_data("linear", n=100)
    show(generate_plot(ds))