import os
from datetime import datetime, timedelta
import shutil
import subprocess


def get_files_in_directory(directory_path, file_ending=None, content_filter=None):
    
    files_in_dir = []
    
    if(os.path.isdir(directory_path)):
        for file in os.listdir(directory_path):
                filename = os.fsdecode(file)
                filepath = os.getcwd() + '/' + directory_path + '/' + filename
                
                if file_ending == None:
                    if content_filter == None:
                        files_in_dir.append(filename)
                    else:
                        with open(filepath) as f:
                            if(content_filter in f.read()):
                                files_in_dir.append(filename)
                                
                elif filename.endswith(file_ending):
                    if content_filter == None:
                        files_in_dir.append(filename)
                    else:
                        with open(filepath) as f:
                            if(content_filter in f.read()):
                                files_in_dir.append(filename)
        return files_in_dir
    return None



def copy_from_card():
    pass


def cull_raws(CFG_module_cull, CFG_path_fastrawviewer, DIR_Unculled):
    
    cull_command = []
    if CFG_module_cull == 'FastRawViewer': cull_command.append(CFG_path_fastrawviewer)
    
    cull_command.append(os.getcwd() + '/' + DIR_Unculled)

    p = subprocess.Popen(cull_command)
    #print('Cull complete')

# Processes the raw files in _Selected using the defined denoising strategy
# Archives the original raw files into 4_Raw_Archive
def process_selected(CFG_module_denoise, CFG_path_dxopureraw, CFG_denoise_on_process, CFG_RAW_filetype, DIR_Unculled_Selected):
    
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
                
                if filename.endswith(CFG_RAW_filetype):
                    denoise_command.append(os.getcwd() + '/' + DIR_Unculled_Selected + '/' + filename)
                    
        p = subprocess.Popen(denoise_command)
                    
    # Denoise single images
    # Only explicitly marked photos are imported to DxO PureRaw
    # All others are copied as is
    if(CFG_denoise_on_process == 'False'):
        pass
    
    
def archive_raws(CFG_archive_on_process, CFG_RAW_filetype, CFG_metadata_filetype, DIR_Unculled_Selected, DIR_Unedited, DIR_Raw_Archive):
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
                if filename.endswith(CFG_RAW_filetype) or filename.endswith(CFG_metadata_filetype):
                    
                    # Check if file with same name exists in the editing layer -> proceed with archiving; else skip as the photo has not been processed yet!
                    if filename.split('.')[0] not in filenames_in_edit:
                        continue
                    
                    # Determine source
                    source = DIR_Unculled_Selected + '/' + filename
                    
                    # Determine destination
                    destination_year = filename[0:4]
                    destination_month = filename[4:6]
                    destination_day = filename[6:8]
                    destination = DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day
                    
                    # Create destination directory if missing
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year)): os.mkdir(DIR_Raw_Archive + '/' + destination_year)
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month)): os.mkdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month)
                    if(not os.path.isdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day)): os.mkdir(DIR_Raw_Archive + '/' + destination_year + '/' + destination_month + '/' + destination_day)
                    
                    # Move file
                    shutil.move(source, destination)            
      
def edit(CFG_module_edit, CFG_path_darktable, DIR_Unedited):
    edit_command = []
    if CFG_module_edit == 'darktable': edit_command.append(CFG_path_darktable)
    # add other options?
    
    #edit_command.append('-d')
    #edit_command.append('all')
    #edit_command.append(os.getcwd() + '\\' + DIR_Unedited)
             
    #edit_command.append(os.getcwd() + '/' + DIR_Unedited + '/20250705_00006.dng')
    #print(edit_command)    
    p = subprocess.Popen(edit_command)
    
    
def export(CFG_metadata_filetype, DIR_Unedited):
    
    xmps_for_archival = []
    files_for_export = []
    
    if(os.path.isdir(DIR_Unedited)):
        for file in os.listdir(DIR_Unedited):
            filename = os.fsdecode(file)
            filepath = os.getcwd() + '/' + DIR_Unedited + '/' + filename
            
            # read tags from xmp
            # reading as a text file is enough!
            if filename.endswith(CFG_metadata_filetype): 
                with open(filepath) as f:
                    if('READYFOREXPORT' in f.read()):
                        xmps_for_archival.append(filepath)
                        files_for_export.append(filepath[:-4])
                        
    #print(xmps_for_archival)
    #print(files_for_export)
                

# Deletes rejected RAWs over CFG_keep_rejected_days old       
async def cleanup_rejected(CFG_delete_raws_with_missing_timestamp, CFG_keep_rejected_days, DIR_Unculled_Rejected, show, ui):
    current_date = datetime.now().date()
    
    files_to_be_removed = []
    
    if(os.path.isdir(DIR_Unculled_Rejected)):
        for file in os.listdir(DIR_Unculled_Rejected):
                filename = os.fsdecode(file)
                
                try: 
                    file_date = datetime.strptime(filename[0:8], '%Y%m%d').date()
                except:
                    if(CFG_delete_raws_with_missing_timestamp == 'True'):
                        files_to_be_removed.append(DIR_Unculled_Rejected + '/' + file)
                    else:
                        print(f'Invalid filename {filename}, skipping...')
                    continue
                
                if current_date > file_date + timedelta(days=int(CFG_keep_rejected_days)):
                    files_to_be_removed.append(DIR_Unculled_Rejected + '/' + file)
                    
    result = await show()
    if(result == 'Yes'):
        ui.notify('Rejected RAWs cleared!')
        for file in files_to_be_removed:
            os.remove(file)