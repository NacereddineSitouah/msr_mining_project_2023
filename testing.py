import numpy as np
import pandas as pd
import chartify

ch = chartify.Chart(blank_labels=True, y_axis_type='categorical')
ch.set_title("Pokemon EDA using Chartify")
ch.set_subtitle("Number of Pokemon of Each Type in Each Generation using a Lollipop chart")
ch.plot.lollipop(
        data_frame=[111,111,1,1,1,1,1,11,1,5],
        categorical_columns=['generation','type'],
        numeric_column='count',
        color_column='generation')
ch.axes.set_xaxis_tick_orientation('horizontal')
ch.show()