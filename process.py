import configparser
import shutil
import os
import subprocess

from nicegui import ui

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Obtain configuration values
# Program paths
CFG_path_fastrawviewer = config['Program paths']['path_fastrawviewer']
CFG_path_dxopureraw = config['Program paths']['path_dxopureraw']
CFG_path_darktable = config['Program paths']['path_darktable']

# Modules
CFG_module_cull = config['Modules']['module_cull']
CFG_module_denoise = config['Modules']['module_denoise']
CFG_module_edit = config['Modules']['module_edit']

# Process
CFG_denoise_on_process = config['Process']['denoise_on_process']
CFG_archive_on_process = config['Process']['archive_on_process']

# Labels
CGF_label_denoise_override = config['Labels']['label_denoise_override']
CFG_label_stack = config['Labels']['label_stack']


# Define directory paths
DIR_Unculled = '1_Unculled'
DIR_Unculled_Selected = '1_Unculled/_Selected'
DIR_Unculled_Rejected = '1_Unculled/_Rejected'
DIR_Unedited = '2_Unedited'
DIR_Exported = '3_Exported'
DIR_Raw_Archive = '4_Raw_Archive'


def cull_raws():
    
    cull_command = []
    if CFG_module_cull == 'FastRawViewer': cull_command.append(CFG_path_fastrawviewer)
    
    cull_command.append(os.getcwd() + '/' + DIR_Unculled)

    p = subprocess.Popen(cull_command)
    print('Cull complete')

# Processes the raw files in _Selected using the defined denoising strategy
# Archives the original raw files into 4_Raw_Archive
def process_selected():
    
    denoise_command = []
    if CFG_module_denoise == 'DxOPureRaw5': denoise_command.append(CFG_path_dxopureraw)
    # add other options?
    
    # Denoise all expected explicitly marked photos
    # This means that "all" photos are imported to DxO PureRaw
    # Only those that are actually processed into the next step are then archived
    # Explicitly marked photos are copied as is
    if(CFG_denoise_on_process == 'True'):
        
        # Get all files and append them to the denoise command
        if(os.path.isdir(DIR_Unculled_Selected)):
           
            for file in os.listdir(DIR_Unculled_Selected):
                filename = os.fsdecode(file)
                
                if filename.endswith('.ARW'):
                    denoise_command.append(os.getcwd() + '/' + DIR_Unculled_Selected + '/' + filename)
                    
        p = subprocess.Popen(denoise_command)
        p.wait()
                    
    # Denoise single images
    # Only explicitly marked photos are imported to DxO PureRaw
    # All others are copied as is
    if(CFG_denoise_on_process == 'False'):
        pass
    
    
def archive_raws():
    # Archive files that have been processed
    if(CFG_archive_on_process == 'True'):
        
        # Check if directory exists, TODO: consider if it should be created here?
        if(os.path.isdir(DIR_Unculled_Selected)):
           
            # Obtain filenames for all files in the editing layer
            files_in_edi = os.listdir(DIR_Unedited)
            files_in_edi.remove('.donotremove')
            filenames_in_edit = [item.split('.')[0] for item in files_in_edi]
           
            for file in os.listdir(DIR_Unculled_Selected):
                filename = os.fsdecode(file)
                
                # Archive RAWs and metadata
                if filename.endswith('.ARW') or filename.endswith('.xmp'):
                    
                    # Check if file with same name exists in the editing layer -> proceed with archiving; else skip as the photo has not been processed yet!
                    if filename.split('.')[0] not in filenames_in_edit:
                        continue
                    
                    # Determine source
                    source = DIR_Unculled_Selected + '/' + filename
                    
                    # Determine destination
                    destination_year = filename[0:4]
                    destination_month = filename[5:6]
                    destination_day = filename[7:8]
                    destination = DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day
                    
                    # Create destination directory if missing
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year)): os.mkdir(DIR_Raw_Archive + '/' + destination_year)
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month)): os.mkdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month)
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day)): os.mkdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day)
                    
                    # Move file
                    shutil.move(source, destination)            
      
def edit():
    pass
                  
def cleanup_rejected():
    pass


# Create UI
dark = ui.dark_mode()
dark.enable()

with ui.grid(rows=5).classes('items-start'):
    ui.button('1. Cull', on_click=lambda: cull_raws())
    ui.button('2. Process Selected', on_click=lambda: process_selected())
    ui.button('3. Archive RAWs', on_click=lambda: archive_raws())
    ui.button('4. Edit', on_click=lambda: edit())
    with ui.row().classes('w-full no-wrap'):
        ui.button(icon='delete_sweep', on_click=lambda: cleanup_rejected()).classes('w-1/2')
        ui.button('Exit', on_click=lambda: quit()).classes('w-1/2')

ui.run()