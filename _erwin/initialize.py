from _erwin import helper

def run_init():
    folder_list = [{
        'from': '_erwin/init_data/assets',
        'to': 'assets'
    }, {
        'from': '_erwin/init_data/content',
        'to': 'content'
    }, {
        'from': '_erwin/init_data/templates',
        'to': 'templates'
    }]
    for folder in folder_list:
        try:
          helper.copy_folder(folder['from'], folder['to'])
        except:
          print("Folder /" + folder['to'] + "/ already exists, initializing aborted to prevent data loss")
    
    helper.copy_file('_erwin/init_data/site_config.ini', 'site_config.ini')