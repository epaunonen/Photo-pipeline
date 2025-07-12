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
        self.DIR_Raw_Archive = '4_Raw_Archive'
        
        # Helpers
        self.HELPER_n_of_files_to_be_deleted = 0
    
    
    def reload_config(self, refresh=False):
        self.config.read('config.ini')
        
        # Program paths
        self.CFG_path_fastrawviewer = self.config['Program paths']['path_fastrawviewer']
        self.CFG_path_dxopureraw = self.config['Program paths']['path_dxopureraw']
        self.CFG_path_darktable = self.config['Program paths']['path_darktable']

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
        
        if refresh: os.utime('process.py')
        

    def start_process(self):
        
        # load initial configuration
        self.reload_config()
        
        # Create UI
        dark = ui.dark_mode()
        dark.enable()

        # Dialog for cleanup rejected
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Really clear rejected raws')
            ui.label(f'over {self.CFG_keep_rejected_days} day(s) old?')
            with ui.row():
                ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
                ui.button('No', on_click=lambda: dialog.submit('No'))
                
        async def show():
            result = await dialog
            return result
        
        # Actual UI
        #with ui.grid(rows=20, columns=1).classes('items-start').style('row-gap: 0.1rem'):
        with ui.column().classes('w-full no-wrap').style('row-gap: 1rem'):
            
            # Labels
            ui.markdown('####Photos')#.classes('col-span-2')
            # Actions
            ui.button('0. Get Files', on_click=lambda: copy_from_card()).classes('w-1/6')#.classes('col-span-2')
            ui.separator().classes('w-1/6')
            
            ui.label(f'Unculled files: {len(get_files_in_directory(self.DIR_Unculled, file_ending=self.CFG_RAW_filetype))}')
            ui.button('1. Cull', on_click=lambda: cull_raws(self.CFG_module_cull, self.CFG_path_fastrawviewer, self.DIR_Unculled)).classes('w-1/6')#.classes('col-span-2')
            ui.separator().classes('w-1/6')

            ui.label(f'Selected files: {len(get_files_in_directory(self.DIR_Unculled_Selected, file_ending=self.CFG_RAW_filetype))}')
            ui.button('2. Process', on_click=lambda: process_selected(self.CFG_module_denoise, self.CFG_path_dxopureraw, self.CFG_denoise_on_process, self.CFG_RAW_filetype, self.DIR_Unculled_Selected)).classes('w-1/6')
            ui.button('3. Archive RAWs', on_click=lambda: archive_raws(self.CFG_archive_on_process, self.CFG_RAW_filetype, self.CFG_metadata_filetype, self.DIR_Unculled_Selected, self.DIR_Unedited, self.DIR_Raw_Archive)).classes('w-1/6')
            ui.separator().classes('w-1/6')

            ui.label(f'Files waiting for editing: {len(get_files_in_directory(self.DIR_Unedited, file_ending=".dng"))}')    
            ui.button('4. Edit', on_click=lambda: edit(self.CFG_module_edit, self.CFG_path_darktable)).classes('w-1/6')
            ui.separator().classes('w-1/6')

            ui.label(f'Files ready for export: {len(get_files_in_directory(self.DIR_Unedited, file_ending=self.CFG_metadata_filetype, content_filter="READYFOREXPORT"))}')    
            ui.button('5. Export', on_click=lambda: export(self.CFG_metadata_filetype, self.DIR_Unedited)).classes('w-1/6')
            ui.separator().classes('w-1/6')

            
            with ui.row().classes('w-1/6 no-wrap'):#('col-span-2 no-wrap'):
                ui.button(icon='delete_sweep', on_click=lambda: cleanup_rejected(self.CFG_delete_raws_with_missing_timestamp, self.CFG_keep_rejected_days, self.DIR_Unculled_Rejected, show, ui)).classes('w-1/2')
                ui.button(icon='refresh', on_click=lambda: self.reload_config(refresh=True)).classes('w-1/2')

        ui.run(favicon="icon.png", title="Photo-pipeline")


pipeline_process = Pipelineprocess()
pipeline_process.start_process()