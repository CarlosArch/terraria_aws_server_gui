import sys
import subprocess
import tkinter as tk
from tkinter import ttk
from functools import partial

sys.path.append('../../Python')
from my_tk_utils.core.forms import Form, TextInput, FormTextInput
from my_tk_utils.core.subprocesses import Subprocess
from my_tk_utils.core.applications import (Page, Window,
                                           XLARGE_FONT, LARGE_FONT,
                                           MEDIUM_FONT, SMALL_FONT,
                                           XSMALL_FONT)
from config import CONFIG, save_config


class HomePage(Page):
    title = 'AWS Terraria Utilites'

    def make_content(self, frame):
        ttk.Button(frame,
                   text='Open SSH to server',
                   command=self.ssh_to_server).pack()
        frame.config(padding=10)
        return frame

    def ssh_to_server(self):
        key_path = CONFIG.get('server', 'key_path')
        server_dns = CONFIG.get('server', 'server_dns')
        command = f'ssh -i "config\{key_path}" "{server_dns}"'
        subprocess.call(f'start cmd /k "{command}"', shell=True)


class WorldTransferPage(Page):
    title = 'World Transfer'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subprocess = Subprocess(self.update_textbox, delay_s=1)

    def make_content(self, frame):
        self.inp_world_name = TextInput(frame,
                                        label_text='World Name',
                                        default=CONFIG.get('world',
                                                           'world_name'))
        self.inp_world_name.grid(columnspan=2)
        ttk.Button(frame,
                   text='Send world',
                   command=self.send_world).grid(row=1, column=0,
                                                 sticky='ew')
        ttk.Button(frame,
                   text='Retrieve world',
                   command=self.retrieve_world).grid(row=1, column=1,
                                                     sticky='ew')

        self.txt_progress_box = tk.Text(frame,
                                        height=1,
                                        width=1,
                                        state='disabled')
        self.txt_progress_box.tag_configure('ERR', foreground='red')
        self.txt_progress_box.tag_configure('OUT', foreground='black')
        self.txt_progress_box.grid(row=3, columnspan=2, sticky='ew')

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.config(padding=10)
        return frame

    def update_textbox(self, queue):
        if not queue.empty():
            output, error, returncode = queue.get()
            output = output.strip()
            error = error.strip()

            self.txt_progress_box.configure(state='normal')
            self.txt_progress_box.delete('0.0', 'end')
            if error:
                text = (error, 'ERR')
            else:
                text = (output, 'ERR')
            self.txt_progress_box.insert('0.0', *text)
            while True:
                end_char = f'{self.txt_progress_box.index("end")} - 1 chars'
                end_visible = self.txt_progress_box.bbox(end_char) is not None
                current_height = self.txt_progress_box.cget('height')

                if not end_visible:
                    self.txt_progress_box.configure(height=current_height+1)
                    self.master.show_page(self.__class__)
                else:
                    break
            self.txt_progress_box.configure(state='disabled')
            queue.task_done()

    def send_world(self):
        server_dns, world_name = self.world_config()

        file_from = f'Worlds/{world_name}.wld'
        file_to = f'{server_dns}:~/.local/share/Terraria/Worlds/'

        self._secure_copy(file_from, file_to)

    def retrieve_world(self):
        server_dns, world_name = self.world_config()

        file_from = (f'{server_dns}:~/.local/share/Terraria/Worlds/'
                     f'{world_name}.wld')
        file_to = 'Worlds/'

        self._secure_copy(file_from, file_to)

    def world_config(self):
        server_dns = CONFIG.get('server', 'server_dns')
        world_name = self.inp_world_name.input.get()
        CONFIG.set('world', 'world_name', world_name)
        save_config()
        return server_dns, world_name

    def _secure_copy(self, file_from, file_to):
        key_path = CONFIG.get('server', 'key_path')
        command = ['scp',
                   f'-i config/{key_path}',
                   f'{file_from}',
                   f'{file_to}']
        # command = ['scp',
        #            f'scp_testerino/input/scp_test.txt',
        #            f'scp_testerino/output/']
        self.subprocess.communicate(command)


class ServerSettingsPage(Page):
    title = 'Server Settings'
    def make_content(self, frame):
        self.form = ServerSettingsForm(frame)
        self.form.pack(fill='both', expand=True, padx=10, pady=10)
        return frame


class ServerSettingsForm(Form):
    inputs = {
        'key_path': FormTextInput(label_text='Key Path',
                                  default=CONFIG.get('server',
                                                     'key_path')),
        'server_dns': FormTextInput(label_text='Server DNS',
                                    default=CONFIG.get('server',
                                                       'server_dns')),
    }

    def submit(self):
        CONFIG.set('server', 'key_path', self.key_path.get())
        CONFIG.set('server', 'server_dns', self.server_dns.get())
        save_config()


class MainWindow(Window):
    window_title = 'AWS Terraria Utilites'
    initial_page = HomePage

    def generate_menu(self, menu):
        main_menu = tk.Menu(menu, tearoff=False)
        main_menu.add_command(label="Home",
                              command=partial(self.show_page,
                                              HomePage))
        menu.add_cascade(label="Main", menu=main_menu)

        settings_menu = tk.Menu(menu, tearoff=False)
        settings_menu.add_command(label="Server",
                                  command=partial(self.show_page,
                                                  ServerSettingsPage))
        menu.add_cascade(label="Settings", menu=settings_menu)

        worlds_menu = tk.Menu(menu, tearoff=False)
        worlds_menu.add_command(label="World Transfer",
                                  command=partial(self.show_page,
                                                  WorldTransferPage))
        menu.add_cascade(label="Worlds", menu=worlds_menu)
        return menu
