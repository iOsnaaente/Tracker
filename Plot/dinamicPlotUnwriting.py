#  Plots also can be dynamic. Dynamic function can be applied as easy as clearing the plot and 
#  adding new data using a callback such as render or item's callback. set_value. This is shown 
#  below.

from dearpygui.core import *
from dearpygui.simple import *
from math import cos

def plot_callback(sender, data):
    # keeping track of frames
    frame_count = get_data("frame_count")
    frame_count += 1
    add_data("frame_count", frame_count)

    # updating plot data
    plot_datax = get_data("plot_datax")
    plot_datay = get_data("plot_datay")
    if len(plot_datax) > 2000:
        frame_count = 0
        plot_datax.clear()
        plot_datay.clear()
    plot_datax.append(3.14 * frame_count / 180)
    plot_datay.append(cos(3 * 3.14 * frame_count / 180))
    add_data("plot_datax", plot_datax)
    add_data("plot_datay", plot_datay)

    # plotting new data
    clear_plot("Plot")
    add_line_series("Plot", "Cos", plot_datax, plot_datay, weight=2)

with window("Tutorial"):
    add_plot("Plot", height=-1)
    add_data("plot_datax", [])
    add_data("plot_datay", [])
    add_data("frame_count", 0)
    set_render_callback(plot_callback)

start_dearpygui()