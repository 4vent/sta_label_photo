# -*- coding: utf-8 -*-

import ui
import dialogs
import console

from tableview_demo import tvDelegate

path = ''

class myTVDelegate(tvDelegate):
    def tableview_delete(self, tableview, section, row):
        
        # Called when the user confirms deletion of the given row.
        self.currentNumLines -=1 # see above regarding hte "syncing"
        tableview.delete_rows((row,)) # this animates the deletion  could also 'tableview.reload_data()'
        del self.items[row]
        
        save_items()

def create_main_view():
    v = ui.View(frame=(0,0,240,240))
    v.background_color = 'white'
    return v

tv = ui.TableView(frame=(0,0,240,240), name='table_main', flex='WH')

def on_button_add(sender):
    global tv
    items = tv.data_source.items
    title = 'New Class'
    new_item = console.input_alert(title=title)
    items.append({
        'title': new_item,
        'accessory_type': 'none'
    })
    tv.data_source.currentNumLines = len(tv.data_source.items)
    tv.insert_rows((len(tv.data_source.items)-1,))
    save_items()

def on_button_edit(sender):
    global tv
    row = tv.data_source.currentRow
    if row == None:
        console.alert('先に行を選択', button1='OK', hide_cancel_button = True)
        return
    items = tv.data_source.items
    input = tv.data_source.currentTitle
    title = 'Rename from "' + input + '"'
    new_item = console.input_alert(title, '', input , hide_cancel_button=True)
    items[row] = {
        'title': new_item,
        'accessory_type': 'none'
    }
    tv.reload_data()
    
    save_items()

def init_title_bar_button():
    global v
    add_button = ui.ButtonItem(image=ui.Image.named('iob:ios7_plus_empty_32'))
    edit_button = ui.ButtonItem(image=ui.Image.named('iob:ios7_compose_outline_32'))
    add_button.action = on_button_add
    edit_button.action = on_button_edit
    v.right_button_items = [add_button, edit_button]

def get_label_list():
    global path
    with open(path, 'r') as f:
        labelTitles = f.read().split()
    return labelTitles

def load_items():
    global tv
    items = []
    for l in get_label_list():
        items.append({
            'title': l,
            'accessory_type': 'none'
        })
    tv.delegate = tv.data_source = myTVDelegate(items=items)

def init_table_view():
    global v
    global tv
    tv.width = 240
    tv.height = 240
    load_items()
    v.add_subview(tv)

def on_select_table_main(sender):
    rename_item(sender, sender.data_source.currentRow)

def awake():
    global v
    init_title_bar_button()
    init_table_view()

def start():
    global v
    pass

def save_items():
    global tv
    global path
    items = tv.data_source.items
    with open(path, 'w') as f:
        f.write('\n'.join([i['title'] for i in items]))

def choose_class_dialog(classes_path):
    global v
    global path
    path = classes_path
    v = create_main_view()
    awake()
    v.present('fullscreen')
    start()
    v.wait_modal()
    return

if __name__ == '__main__':
    choose_class_dialog()

