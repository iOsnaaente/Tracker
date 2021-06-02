# Simple plots take in a list and plot y-axis data against the number of items in the list. These can be line 
# graphs or histograms and are demonstrated below

from dearpygui.core import *
from dearpygui.simple import *

with window("Tutorial"):
    add_simple_plot("Simpleplot1", value=[0.3, 0.9, 0.5, 0.3], height=300)
    add_simple_plot("Simpleplot2", value=[0.3, 0.9, 2.5, 8.9], overlay="Overlaying", height=180, histogram=True)

start_dearpygui()