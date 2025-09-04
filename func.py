import glob
import os
from datetime import datetime, timedelta
import shutil
import subprocess
from exiftool import ExifToolHelper


def get_files_in_directory(directory_path, file_ending=None, content_filter=None):
    """_summary_

    Helper function for obtaining a list of all files in a folder that match a specified filetype, and optionally, content

    Args:
        directory_path (_type_): _description_
        file_ending (_type_, optional): _description_. Defaults to None.
        content_filter (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
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





def copy_from_card(CFG_path_memorycard_photo_root, CFG_path_exiftool, CFG_RAW_filetype, DIR_Unculled):
    """_summary_

    Args:
        CFG_path_exiftool (_type_): _description_
        CFG_RAW_filetype (_type_): _description_
        DIR_Unculled (_type_): _description_
    """
    
    # Recursively copy files only -> Unculled directory
    files = glob.glob(CFG_path_memorycard_photo_root + '/**/*', recursive=True)
    for p in files:
        if os.path.isfile(p):
            shutil.copy(p, DIR_Unculled)
    
    # Run rename for the copied files
    rename_raws(CFG_path_exiftool, CFG_RAW_filetype, DIR_Unculled)
    
    # TODO: should this also add additional metadata
    


# TODO: switch DIR_Unculled to any folder?
# Additionally stop hardcoding cfg-params

def rename_raws(CFG_path_exiftool, CFG_RAW_filetype, DIR_Unculled):
    """_summary_

    Renames all matching RAW-files in the specified Unculled-directory.
    
    New filename follows the schema of yyyyMMdd_nnnnnn
    
    where date is obtained from image EXIF-data, and nnnnn is an unique increasing id separately for each distinct date.
        
    Args:
        CFG_path_exiftool (_type_): _description_
        CFG_RAW_filetype (_type_): _description_
        DIR_Unculled (_type_): _description_
    """
    
    running_ids = {}
    
    # Start exiftool only once
    with ExifToolHelper(executable=CFG_path_exiftool) as et:

        # loop all files
        for file in os.listdir(DIR_Unculled):
                filename = os.fsdecode(file)
                
                # only process matching raws
                if filename.endswith(CFG_RAW_filetype):
                    
                    filepath = os.getcwd() + '/' + DIR_Unculled + '/'
                    
                    # Get only datetime
                    d = et.get_tags(filepath + filename, tags=["DateTimeOriginal"])
                    date = d[0]['EXIF:DateTimeOriginal'].split(' ')[0].replace(':', '')

                    # Add date as a key if it doesn't already exist
                    if date not in running_ids:
                        running_ids[date] = 0
                    
                    # Increase running id by one
                    running_ids[date] += 1
                    
                    # Generate new filename
                    new_filename = f'{date}_{running_ids[date]:05d}'
                    
                    # Rename the file
                    os.rename(filepath + filename, filepath + new_filename + CFG_RAW_filetype)
                    
                    # Rename matching .xmp as well, if one has already been generated
                    # This should be redundant under normal usage
                    if os.path.exists(filepath + filename[0:-4] + '.xmp'):
                        os.rename(filepath + filename[0:-4] + '.xmp', filepath + new_filename[0:-4] + '.xmp')





def cull_raws(CFG_module_cull, CFG_path_fastrawviewer, DIR_Unculled):
    """_summary_

    Opens FastRawViewer for culling raws

    Args:
        CFG_module_cull (_type_): _description_
        CFG_path_fastrawviewer (_type_): _description_
        DIR_Unculled (_type_): _description_
    """
    
    cull_command = []
    if CFG_module_cull == 'FastRawViewer': cull_command.append(CFG_path_fastrawviewer)
    
    cull_command.append(os.getcwd() + '/' + DIR_Unculled)

    p = subprocess.Popen(cull_command)





def process_selected(CFG_module_denoise, CFG_path_dxopureraw, CFG_denoise_on_process, CFG_RAW_filetype, DIR_Unculled_Selected):
    """_summary_

    Processes the raw files in _Selected using the defined denoising strategy
    
    Archives the original raw files into 4_Raw_Archive

    Args:
        CFG_module_denoise (_type_): _description_
        CFG_path_dxopureraw (_type_): _description_
        CFG_denoise_on_process (_type_): _description_
        CFG_RAW_filetype (_type_): _description_
        DIR_Unculled_Selected (_type_): _description_
    """
    
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
    """_summary_

    Args:
        CFG_archive_on_process (_type_): _description_
        CFG_RAW_filetype (_type_): _description_
        CFG_metadata_filetype (_type_): _description_
        DIR_Unculled_Selected (_type_): _description_
        DIR_Unedited (_type_): _description_
        DIR_Raw_Archive (_type_): _description_
    """
    
    # Archive files that have been processed
    if(CFG_archive_on_process == 'True'):
        
        # Check if directory exists, TODO: consider if it should be created here?
        if(os.path.isdir(DIR_Unculled_Selected)):
           
            # Obtain filenames for all files in the editing layer
            files_in_edit = os.listdir(DIR_Unedited)
            files_in_edit.remove('.donotremove')
            filenames_in_edit = [item.split('.')[0] for item in files_in_edit]
           
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
    """_summary_

    Args:
        CFG_module_edit (_type_): _description_
        CFG_path_darktable (_type_): _description_
        DIR_Unedited (_type_): _description_
    """
    
    edit_command = []
    if CFG_module_edit == 'darktable': edit_command.append(CFG_path_darktable)
    # add other options?
    
    #edit_command.append('-d')
    #edit_command.append('all')
    #edit_command.append(os.getcwd() + '\\' + DIR_Unedited)
             
    #edit_command.append(os.getcwd() + '/' + DIR_Unedited + '/20250705_00006.dng')
    #print(edit_command)    
    p = subprocess.Popen(edit_command)
    
    
    
    
    
async def export(CFG_metadata_filetype, DIR_Unedited, DIR_Exported, DIR_Edits_Archive, CFG_path_darktable_cli, CFG_path_darktable_purgetool, FLAG_archive_on_export, FLAG_clear_rejected, FLAG_run_dbpurge):
    """_summary_

    Args:
        CFG_metadata_filetype (_type_): _description_
        DIR_Unedited (_type_): _description_
    """
    
    #test_exif('D:\exiftool\exiftool.exe', "D:/Photo-pipeline/2_Unedited/20250704_00021.dng.xmp")
    
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
    
    # export photos
    for file in files_for_export:
        
        outputname = file.split('/')[-1].split('.')[0]
        
        # Determine destination
        destination_year = outputname[0:4]
        destination_month = outputname[4:6]
        destination_day = outputname[6:8]
        destination = DIR_Exported + '/' + destination_year + '/' + destination_month + '/' + destination_day
        
        # Create destination directory if missing
        if(not os.path.isdir(DIR_Exported + '/' + destination_year)): os.mkdir(DIR_Exported + '/' + destination_year)
        if(not os.path.isdir(DIR_Exported + '/' + destination_year + '/' + destination_month)): os.mkdir(DIR_Exported + '/' + destination_year + '/' + destination_month)
        if(not os.path.isdir(DIR_Exported + '/' + destination_year + '/' + destination_month + '/' + destination_day)): os.mkdir(DIR_Exported + '/' + destination_year + '/' + destination_month + '/' + destination_day)
        
        
        export_command = []
        export_command.append(CFG_path_darktable_cli)
        export_command.append(file)
        export_command.append(destination + '/' + outputname + '.jpg')
        
        #print(export_command)
        
        p = subprocess.Popen(export_command)
        p.wait()
                 
    # archive files
    if FLAG_archive_on_export:
        for file in files_for_export:
            shutil.move(file, DIR_Edits_Archive)
            
        for file in xmps_for_archival:
            shutil.move(file, DIR_Edits_Archive)
                
    # remove rejected images from darktable
    if FLAG_clear_rejected:
        sidecar_files = get_files_in_directory(DIR_Unedited, CFG_metadata_filetype, 'xmp:Rating="-1"')
        for file in sidecar_files:
            os.remove(os.getcwd() + '/' + DIR_Unedited + '/' + file)
        
        photo_files = [s.replace(CFG_metadata_filetype, '') for s in sidecar_files]
        for file in photo_files:
            os.remove(os.getcwd() + '/' + DIR_Unedited + '/' + file)
                        
    # run darktable db cleanup
    if FLAG_run_dbpurge:
        purge_command = []
        purge_command.append(CFG_path_darktable_purgetool)
        purge_command.append('--purge')
    
    p = subprocess.Popen(purge_command)
  
  
  
  
async def cleanup_rejected(CFG_delete_raws_with_missing_timestamp, CFG_keep_rejected_days, DIR_Unculled_Rejected, show, ui):
    """_summary_

    Deletes rejected RAWs over CFG_keep_rejected_days old
    
    ToDo: Currently bases detection on filename. EXIF-date should be used instead for more fool-proofness.

    Args:
        CFG_delete_raws_with_missing_timestamp (_type_): _description_
        CFG_keep_rejected_days (_type_): _description_
        DIR_Unculled_Rejected (_type_): _description_
        show (_type_): _description_
        ui (_type_): _description_
    """
    
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
            
           
           
           
            
def test_exif(CFG_path_exiftool, image):
    with ExifToolHelper(executable=CFG_path_exiftool) as et:
        # for d in et.get_metadata(image):
        #     for k, v in d.items():
        #         print(f'{k} = {v}')
        
        # Get only datetime
        #d = et.get_tags(image, tags=["DateTimeOriginal"])
        #print(d[0]['EXIF:DateTimeOriginal'])
        
        d = et.get_tags(image, tags=["Rating"])
        print(d[0]['XMP:Rating'])
