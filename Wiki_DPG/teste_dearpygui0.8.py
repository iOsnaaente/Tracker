import dearpygui.dearpygui as dpg
import array

texture_data = []
for i in range(0, 100*100):
    texture_data.append(255/255)
    texture_data.append(0)
    texture_data.append(255/255)
    texture_data.append(255/255)

raw_data = array.array('f', texture_data)

with dpg.texture_registry():
    texture_id = dpg.add_raw_texture(100, 100, raw_data, format=dpg.mvFormat_Float_rgba)

def update_dynamic_texture(sender, app_data, user_data):
    new_color = dpg.get_value(sender)
    new_color[0] = new_color[0]/255
    new_color[1] = new_color[1]/255
    new_color[2] = new_color[2]/255
    new_color[3] = new_color[3]/255

    for i in range(0, 100*100*4):
        raw_data[i] = new_color[i % 4]

with dpg.window(label="Tutorial"):
    dpg.add_image(texture_id)
    dpg.add_color_picker( (255, 0, 255, 255), label="Texture", no_side_preview=True, alpha_bar=True, width=200, callback=update_dynamic_texture )

dpg.start_dearpygui()