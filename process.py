import configparser
from datetime import datetime, timedelta, time
from nicegui import ui
import os

from func import get_files_in_directory, cull_raws, copy_from_card, process_selected, archive_raws, edit, export, cleanup_rejected

class Pipelineprocess():
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        
        # Program paths
        self.CFG_path_fastrawviewer = ''
        self.CFG_path_dxopureraw = ''
        
        self.CFG_path_darktable = ''
        self.CFG_path_darktable_cli = ''
        self.CFG_path_darktable_purgetool = ''
        
        self.CFG_path_exiftool = ''
        
        self.CFG_path_shutterencoder = '' 
        self.CFG_path_davinciresolve = ''
        
        self.CFG_path_memorycard_root = ''
        self.CFG_path_memorycard_photo_root = ''

        # Modules
        self.CFG_module_cull = ''
        self.CFG_module_denoise = ''
        self.CFG_module_edit = ''

        # Process
        self.CFG_denoise_on_process = ''
        self.CFG_archive_on_process = ''

        # Labels
        self.CGF_label_denoise_override = ''
        self.CFG_label_stack = ''
        # Misc
        self.CFG_keep_rejected_days = ''
        self.CFG_delete_raws_with_missing_timestamp = ''
        self.CFG_RAW_filetype = ''
        self.CFG_metadata_filetype = ''
        
        # Directories Todo: override from config
        self.DIR_Unculled = '1_Unculled'
        self.DIR_Unculled_Selected = '1_Unculled/_Selected'
        self.DIR_Unculled_Rejected = '1_Unculled/_Rejected'
        self.DIR_Unedited = '2_Unedited'
        self.DIR_Exported = '3_Exported'
        self.DIR_Raw_Archive = '4_Archive/Raws'
        self.DIR_Edits_Archive = '4_Archive/Edits'
        
        # Helpers
        self.HELPER_n_of_files_to_be_deleted = 0
    
    
    def reload_config(self, refresh=False):
        self.config.read('config.ini')
        
        # Program paths
        self.CFG_path_fastrawviewer = self.config['Program paths']['path_fastrawviewer']
        self.CFG_path_dxopureraw = self.config['Program paths']['path_dxopureraw']
        self.CFG_path_darktable = self.config['Program paths']['path_darktable']
        self.CFG_path_darktable_cli = self.config['Program paths']['path_darktable_cli']
        self.CFG_path_darktable_purgetool = self.config['Program paths']['path_darktable_purgetool']
        
        self.CFG_path_exiftool = self.config['Program paths']['path_exiftool']
        
        self.CFG_path_shutterencoder = self.config['Program paths']['path_shutterencoder'] 
        self.CFG_path_davinciresolve = self.config['Program paths']['path_davinciresolve']
        
        # Directoy paths
        self.CFG_path_memorycard_root = self.config['Directory paths']['path_memorycard_root']
        self.CFG_path_memorycard_photo_root = self.config['Directory paths']['path_memorycard_photo_root']

        # Modules
        self.CFG_module_cull = self.config['Modules']['module_cull']
        self.CFG_module_denoise = self.config['Modules']['module_denoise']
        self.CFG_module_edit = self.config['Modules']['module_edit']

        # Process
        self.CFG_denoise_on_process = self.config['Process']['denoise_on_process']
        self.CFG_archive_on_process = self.config['Process']['archive_on_process']

        # Labels
        self.CGF_label_denoise_override = self.config['Labels']['label_denoise_override']
        self.CFG_label_stack = self.config['Labels']['label_stack']

        # Misc
        self.CFG_keep_rejected_days = self.config['Misc']['keep_rejected_days']
        self.CFG_delete_raws_with_missing_timestamp = self.config['Misc']['delete_raws_with_missing_timestamp']
        self.CFG_RAW_filetype = self.config['Misc']['RAW_filetype']
        self.CFG_metadata_filetype = self.config['Misc']['metadata_filetype']
        
        if refresh: 
            os.utime('process.py')
            ui.notify('Configuration reloaded')
        

    def start_process(self):
        
        # load initial configuration
        self.reload_config()
            
        # Create labels and colors
        labels = {}
        colors = {}
        memory_card_found = {}
        
        def refresh_labels():
            
            labels['memorycard_status'] = f'Directory found at specified camera storage location {self.CFG_path_memorycard_root}' if os.path.isdir(self.CFG_path_memorycard_root) else f'No directory found at specified camera storage location {self.CFG_path_memorycard_root}'
            labels['unculled_filecount'] = f'Unculled files: {len(get_files_in_directory(self.DIR_Unculled, file_ending=self.CFG_RAW_filetype))}'
            labels['selected_filecount'] = f'Selected files: {len(get_files_in_directory(self.DIR_Unculled_Selected, file_ending=self.CFG_RAW_filetype))}'
            labels['unedited_filecount'] = f'Files waiting for editing: {len(get_files_in_directory(self.DIR_Unedited, file_ending=".dng"))}'
            labels['unexported_filecount'] = f"""Files ready for export: {len(get_files_in_directory(self.DIR_Unedited, file_ending=self.CFG_metadata_filetype, content_filter="READYFOREXPORT"))} | Rejected photos: {len(get_files_in_directory(self.DIR_Unedited, file_ending=self.CFG_metadata_filetype, content_filter='xmp:Rating="-1"'))}"""

            colors['button_color_photos'] = "#A55935"
            colors['button_color_delete'] = '#822831'
            colors['button_color_photos_getfiles'] = "#b7a22a"
            
            colors['button_color_video'] = "#7C2882"
            colors['button_color_video_getfiles'] = "#7a9645"
            
            memory_card_found['value'] = os.path.isdir(self.CFG_path_memorycard_root)

        refresh_labels()        
        
        # Create UI
        # ========================================================================================
        dark = ui.dark_mode()
        dark.enable()

        # Dialog for cleanup rejected
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Really clear rejected raws')
            ui.label(f'over {self.CFG_keep_rejected_days} day(s) old?')
            with ui.row():
                ui.button('Yes', on_click=lambda: dialog.submit('Yes'), color=colors['button_color_delete'])
                ui.button('No', on_click=lambda: dialog.submit('No'), color=colors['button_color_photos'])
                
        async def show():
            result = await dialog
            return result
        
        ui.image('banner.png').classes('w-1/5')
        
        with ui.tabs().classes('w-1/3') as tabs:
            photos = ui.tab('Photos', icon='camera').classes('w-1/3')
            video = ui.tab('Video', icon='theaters').classes('w-1/3')
            settings = ui.tab('Settings', icon='construction').classes('w-1/3')
        
        # Actual UI
        with ui.tab_panels(tabs, value=photos).classes('w-1/3'):
            
            # Photos
            with ui.tab_panel(photos):
 
                with ui.column().classes('w-full no-wrap').style('row-gap: 1rem'):
                    
                    label_getfiles = ui.label('')
                    button_getfiles = ui.button('0. Get Files', on_click=lambda: copy_from_card(self.CFG_path_memorycard_photo_root, self.CFG_path_exiftool, self.CFG_RAW_filetype, self.DIR_Unculled), color=colors['button_color_photos_getfiles']).classes('w-full')
                    ui.separator().classes('w-full')
                    
                    label_cull = ui.label('')
                    button_cull = ui.button('1. Cull', on_click=lambda: cull_raws(self.CFG_module_cull, self.CFG_path_fastrawviewer, self.DIR_Unculled), color=colors['button_color_photos']).classes('w-full')
                    ui.separator().classes('w-full')

                    label_process = ui.label('')
                    button_process = ui.button('2. Process', on_click=lambda: process_selected(self.CFG_module_denoise, self.CFG_path_dxopureraw, self.CFG_denoise_on_process, self.CFG_RAW_filetype, self.DIR_Unculled_Selected), color=colors['button_color_photos']).classes('w-full')
                    button_archiveraw = ui.button('3. Archive RAWs', on_click=lambda: archive_raws(self.CFG_archive_on_process, self.CFG_RAW_filetype, self.CFG_metadata_filetype, self.DIR_Unculled_Selected, self.DIR_Unedited, self.DIR_Raw_Archive), color=colors['button_color_photos']).classes('w-full')
                    ui.separator().classes('w-full')

                    label_edit = ui.label('')    
                    button_edit = ui.button('4. Edit', on_click=lambda: edit(self.CFG_module_edit, self.CFG_path_darktable, self.DIR_Unedited), color=colors['button_color_photos']).classes('w-full')
                    ui.separator().classes('w-full')

                    label_export = ui.label('')
                    checkbox_archive_on_export = ui.checkbox('On export: Archive photos and sidecars', value=True, on_change=None)
                    checkbox_clear_rejected = ui.checkbox('On export: Clean up rejected photos', value=True, on_change=None)
                    checkbox_run_dbpurge = ui.checkbox('On export: Purge darktable database', value=True, on_change=None)
                    button_export = ui.button('5. Export', on_click=lambda: export(self.CFG_metadata_filetype, self.DIR_Unedited, self.DIR_Exported, self.DIR_Edits_Archive, self.CFG_path_darktable_cli, self.CFG_path_darktable_purgetool, checkbox_archive_on_export.value, checkbox_clear_rejected.value, checkbox_run_dbpurge.value), color=colors['button_color_photos']).classes('w-full')
                    ui.separator().classes('w-full')

                    with ui.row().classes('w-full no-wrap'):
                        ui.button(icon='delete_sweep', on_click=lambda: cleanup_rejected(self.CFG_delete_raws_with_missing_timestamp, self.CFG_keep_rejected_days, self.DIR_Unculled_Rejected, show, ui), color=colors['button_color_delete']).classes('w-1/2')
                        ui.button(icon='refresh', on_click=lambda: self.reload_config(refresh=True), color=colors['button_color_photos']).classes('w-1/2')
                        
                        
                    def refresh_elements():
                        refresh_labels()
                        
                        label_getfiles.set_text(labels['memorycard_status'])
                        label_cull.set_text(labels['unculled_filecount'])
                        label_process.set_text(labels['selected_filecount'])
                        label_edit.set_text(labels['unedited_filecount'])
                        label_export.set_text(labels['unexported_filecount'])
                        
                        button_getfiles.enabled = memory_card_found['value']
                        
                        label_getfiles_video.set_text(labels['memorycard_status'])
                        button_getfiles_video.enabled = memory_card_found['value']
                        
                    # This timer does not seem to recover from a lengthy process, e.g. file transfer or export
                    ui.timer(1.0, lambda: refresh_elements())
                        
                        
            # Video
            with ui.tab_panel(video):
                
                label_getfiles_video = ui.label('')
                button_getfiles_video = ui.button('0. Get Files', on_click=lambda: None, color=colors['button_color_photos_getfiles']).classes('w-full')#.classes('col-span-2')
                ui.separator().classes('w-full')
                
                ui.button('1. Convert', on_click=lambda: None, color=colors['button_color_photos']).classes('w-full')
                ui.separator().classes('w-full')
                
                ui.button('2. Edit', on_click=lambda: None, color=colors['button_color_photos']).classes('w-full')
                ui.separator().classes('w-full')
                
                with ui.row().classes('w-full no-wrap'):#('col-span-2 no-wrap'):
                        #ui.button(icon='delete_sweep', on_click=lambda: cleanup_rejected(self.CFG_delete_raws_with_missing_timestamp, self.CFG_keep_rejected_days, self.DIR_Unculled_Rejected, show, ui), color=button_color_delete).classes('w-1/2')
                        ui.space().classes('w-1/2')
                        ui.button(icon='refresh', on_click=lambda: self.reload_config(refresh=True), color=colors['button_color_photos']).classes('w-1/2')
                        
                        
            # Settings
            with ui.tab_panel(settings):
                
                ui.separator().classes('w-full')
                
                with ui.row().classes('w-full no-wrap'):
                    ui.button('Reset', on_click=lambda: None, color=colors['button_color_photos']).classes('w-1/2')
                    ui.button('Save and reload', on_click=lambda: None, color=colors['button_color_photos_getfiles']).classes('w-1/2')

        ui.run(favicon="icon.png", title="Photo-pipeline")


pipeline_process = Pipelineprocess()
pipeline_process.start_process()