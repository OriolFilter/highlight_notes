#!/bin/python3

#  DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                      Version 2, December 2004
#
#   Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
#   Everyone is permitted to copy and distribute verbatim or modified
#   copies of this license document, and changing it is allowed as long
#   as the name is changed.
#
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#     TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#    0. You just DO WHAT THE FUCK YOU WANT TO.

import tkinter as tk
import re
import typing
from typing import TypedDict, Union
from dataclasses import dataclass
from tkinter import filedialog as fd
from json import load as jload, dump as jwrite
from os.path import dirname
from pathlib import Path


@dataclass
class DataHighlight:
    fore: str = None
    back: str = None
    regex: str = None


@dataclass
class DataGame:
    name: str
    notes: list[str]
    highlighting: list[DataHighlight]

    def __post_init__(self):
        # Replaces highlighting as a dictionary, to DataHighlight dataclass
        holder = list.copy(self.highlighting)
        self.highlighting.clear()
        for highlight in holder:
            self.highlighting.append(DataHighlight(**dict(highlight)))


@dataclass
class DataConf:
    games: list[DataGame]

    def __post_init__(self):
        holder = list.copy(self.games)
        self.games.clear()
        for game in holder:
            self.games.append(DataGame(**dict(game)))


@dataclass
class JsonSettings:
    def __init__(self, json: {} = None, path: str = None):
        self.__defaultjson = {
            'games': []
        }
        if path:
            self.load_json_from_file(path=path)
        elif json:
            self.load_json_from_dic(json=json)
        else:
            self.load_json_from_dic(json=self.__defaultjson)


    def load_json_from_dic(self, json: {}):
        self.reload_conf(json=json)

    def load_json_from_file(self, path: str):
        with open(path) as json_file:
            json = jload(json_file)
        # Validation/Checking etc idc
        self.reload_conf(json=json)

    def export_json_to_file(self, path: str):

        # print(self.json)
        with open(path, 'w') as outfile:
            jwrite(self.json, outfile)

    def reload_conf(self, json: dict):
        """Recreate its configuration based on the dictionary converting it into a data class"""
        self.conf = DataConf(**dict(json))

    def add_note(self, game, txt: str):
        pass

    def del_note(self, game, index: int):
        pass

    @property
    def json(self) -> dict:
        """
        Transforms current dataclass into a dictionary, it's main usage is being able to export the current
        configuration into a json file

        DONT USE THIS TO MODIFY THE CURRENT CONFIGURATION
        """
        json: JsonSettings.__defaultjson = dict(self.__defaultjson)
        for game in self.conf.games:
            game: DataGame
            dictEntry: JsonSettings.__defaultjson = dict()
            dictEntry['name'] = str(game.name)
            dictEntry['notes'] = list.copy(game.notes)
            dictEntry['highlighting'] = [dict(fore=rule.fore, back=rule.back, regex=rule.regex) for rule in
                                         list.copy(game.highlighting)]

            json['games'].append(dictEntry)
        return json

    conf: DataConf = None
    __defaultjson = {'games': [
        {
            'name': str,
            'notes': [str],
            'highlight': [{'fore': str, 'back': str, 'char': str}],
        },
    ]}


class zombie_window(tk.Toplevel, tk.Tk):
    """
    Floating window used to store text and highlight it.
    """

    def __init__(self, *args, title="tk zombie", master=None):
        """
        If receive a tk.root it will be a Toplevel object,
        otherwise will create itself as a tk.Tk object
        """
        self.on_save_note_callback = lambda txt: print(f'Executed the add note command, but by default doesnt store it '
                                                       f'anywhere.\n\t:: {txt}')
        if master:
            tk.Toplevel.__init__(self, master, *args)
        else:
            tk.Tk.__init__(self, *args)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.geometry("400x20")
        self.title(title)
        self.update()
        self.destroyed = False

    #     https://www.pythontutorial.net/tkinter/tkinter-text/

    def create_text_wd(self):
        # Create text widged
        self.text = tk.Text(self)
        self.text.insert(tk.INSERT, "Select a note first")
        self.text.pack(fill=tk.X, side=tk.RIGHT, expand=True, anchor=tk.E)

    def update_text(self, text='', highlight: list = None) -> None:
        self.destroy_content()
        self.create_text_wd()
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.INSERT, text)
        self.highlight_text(*highlight or [])

    def highlight_text(self, *rules: Union[list[DataHighlight], None]):
        x = 0
        for rule in rules:
            rule: DataHighlight
            for l, line in enumerate(str(self.current_txt()).split("\n"), start=1):
                if len(line) > 0:
                    for result in re.finditer(pattern=f'{rule.regex}', string=line, flags=re.I):
                        self.text.tag_add(f"{x}",
                                          f'{l}.{result.start()}',
                                          f'{l}.{result.end()}')
                        self.text.tag_config(f"{x}", background=rule.back, foreground=rule.fore)
                        x += 1
        pass

    def destroy_content(self):
        if hasattr(self, 'text') and callable(getattr(self.text, 'destroy')):
            self.text.destroy()
        if hasattr(self, 'add_note_bt') and callable(getattr(self.add_note_bt, 'destroy')):
            self.add_note_bt.destroy()

    def new_note_mode(self, callback: typing.Callable = None):
        self.geometry("650x60")
        self.update_text()
        self.create_addnote_button(callback)

    def create_addnote_button(self, callback: typing.Callable = None):
        """ On adding a note will execute the callback command, by default will print a message but will not be
        stored anywhere """
        self.on_save_note_callback = callback or self.on_save_note_callback
        self.add_note_bt = tk.Button(
            self,
            text='Add note',
            height=20,
            width=20,
            command=self.__on_save_note)
        self.add_note_bt.pack(expand=False, side=tk.LEFT, anchor=tk.W)

    on_save_note_callback = lambda txt: print(f'Executed the add note command, but by default doesnt store it '
                                              f'anywhere.\n\t:: {txt}')

    def __on_save_note(self):
        self.on_save_note_callback(txt=self.current_txt())
        self.master.update_notelist()

    def destroy(self):
        super().destroy()
        self.destroyed = True

    def current_txt(self):
        txt = self.text.get("1.0", tk.END)
        if txt[-1] == '\n':
            txt = txt[:-1]
        return txt

    # text_wd: tk.Text
    label: tk.Label
    text: tk.StringVar or tk.Text
    add_note_bt: tk.Button
    destroyed: bool
    pass


class Manager:
    def __init__(self, title="tk picker", jsonpath=None):
        self.json_conf: JsonSettings = JsonSettings(path=jsonpath)
        self.wd_title = title

    def __load_tk(self):
        """Dump conf into tk manager obj"""
        self.tk_menu: tk = tk_menu(manager=self, title=self.wd_title)

    def start_tk(self):
        self.__load_tk()
        self.tk_menu.start()

    def kill_tk(self):
        pass

    tk_menu: object
    wd_title: str


class tk_menu(tk.Tk):
    def __init__(self, *args, title="tk", manager: Manager = None):
        super().__init__(*args)
        self.conf_dir = str(Path.home())
        self.game_dic: dict[str:DataGame] = {}
        self.manager = manager
        self.title(title)
        self.update()
        self.create_menu()

    def update_game_dic(self):
        self.game_dic.clear()
        for game in self.manager.json_conf.conf.games:
            self.game_dic[game.name] = game

    def create_menu(self):
        self.create_manage_conf_wd()
        if self.manager.json_conf.conf and len(self.manager.json_conf.conf.games) > 0:
            self.update_lists_wd()

    def create_manage_conf_wd(self):
        """Creates the load and save conf buttons"""
        self.load_bt = tk.Button(
            self,
            text='Load conf',
            command=self.__load_conf)
        self.save_bt = tk.Button(
            self,
            text='Save conf',
            command=self.__save_conf)
        self.load_bt.pack(expand=True)
        self.save_bt.pack(expand=True)
        # https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/

    def __load_conf(self):
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=self.conf_dir or '/',
            filetypes=filetypes)
        self.conf_dir = dirname(filename)
        self.manager.json_conf.load_json_from_file(filename)
        self.update_lists_wd()

    def __save_conf(self):
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = fd.asksaveasfilename(
            title='Save to file',
            initialdir=self.conf_dir or '/',
            filetypes=filetypes)
        self.conf_dir = dirname(filename)
        # Check stuff
        self.manager.json_conf.export_json_to_file(filename)


    def create_game_list_wd(self):
        # Drop Box
        self.game_list_var = tk.StringVar(self)
        self.game_list_var.set(("Select one" if len(self.game_dic.keys()) != 0 else "Any game detected"))
        self.game_list_var.trace('w', self.__once_selected_game)
        self.game_list_wd = tk.OptionMenu(self, self.game_list_var, *[key for key in self.game_dic])
        self.game_list_wd.pack(fill=tk.Y, expand=False)

    def create_notes_list_wd(self, game_name):
        self.note_list_var = tk.StringVar(self)
        self.note_list_var.set(("Select one" if len(self.game_dic.keys()) != 0 else "Any note"))
        self.note_list_var.trace('w', self.__once_selected_note)
        self.note_list_wd = tk.OptionMenu(self, self.note_list_var,
                                          *self.game_dic.get(game_name).notes, self.addnotemsg)
        self.note_list_wd.pack(fill=tk.Y, expand=False)
        self.update()

    def start(self):
        self.mainloop()

    def update_lists_wd(self, *args):
        self.update_game_dic()
        self.destroy_notelist_wd()
        self.destroy_gamelist_wd()
        self.create_game_list_wd()

    def destroy_gamelist_wd(self):
        """Destroys game_list widged"""
        if type(self.game_list_wd) is tk.OptionMenu:
            self.game_list_wd.destroy()

    def update_notelist(self, *args):
        self.destroy_notelist_wd()
        self.create_notes_list_wd(self.game_list_var.get())
        pass

    def destroy_notelist_wd(self):
        """Destroys notelist widged"""
        if type(self.note_list_wd) is tk.OptionMenu:
            self.note_list_wd.destroy()

    def __once_selected_game(self, *args):
        print(f"game selected: <<<{self.current_game}>>>")
        self.update_notelist()
        pass

    def __once_selected_note(self, *args):
        """Raised when a note is selected from the dropbox"""
        if type(self.zombie_window) is not zombie_window or self.zombie_window.destroyed:
            self.zombie_window = zombie_window(master=self)
        if self.current_note == self.addnotemsg:
            self.zombie_window.new_note_mode(self.store_new_note)
        else:
            self.zombie_window.update_text(self.current_note,
                                           highlight=self.game_dic[self.current_game].highlighting)

    def store_new_note(self, txt):
        print(f"Added new note to storage: \n::: {txt}")
        next(game.notes for game in self.manager.json_conf.conf.games
             if game.name == self.current_game).append(txt)

    @property
    def current_game(self):
        return self.game_list_var.get()

    @property
    def current_note(self):
        if type(self.note_list_wd) is tk.OptionMenu:
            return self.note_list_var.get()
        else:
            print("Select a game first")

    tk: tk.Tk

    game_dic: dict[str:DataGame] = {}
    load_bt: tk.Button = None
    save_bt: tk.Button = None
    game_list_var: tk.StringVar = None
    game_list_wd: tk.OptionMenu = None
    note_list_var: tk.StringVar = None
    note_list_wd: tk.OptionMenu = None
    zombie_window: tk.Tk = None
    addnotemsg: str = "Add new note..."
    conf_dir: str = ''


if __name__ == '__main__':
    x = Manager(title="tk menu")
    x.start_tk()


