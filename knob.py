from dearpygui.dearpygui import * 


with window( autosize = True ) as main_window: 
    add_knob_float( width= 500, height=500, pos=[500,500])
    add_tab_bar()
    add_progress_bar()
    add_slider_float(id=1, pos=[100,100], width=500, height=50, min_value=0, max_value=1000, indent=0.5, format='%3.4')
    add_slider_float(id=2, pos=[100,200], width=25, height=500, min_value=0, max_value=1000, indent=0.5, format='%3.4', vertical=True)
setup_viewport()

set_primary_window( main_window, True )


while is_dearpygui_running():
    render_dearpygui_frame()
