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
from sys import argv


@dataclass
class DataHighlight:
    fore: str = None
    back: str = None
    regex: str = None


@dataclass
class DataGame:
    """
    Used to generate the game configuration attributes.
    creates DataHighlight from the highlighting list given
    """
    name: str
    notes: list[str]
    highlighting: list[DataHighlight]

    def __post_init__(self):
        holder = list.copy(self.highlighting)
        self.highlighting.clear()
        for highlight in holder:
            self.highlighting.append(DataHighlight(**dict(highlight)))


@dataclass
class DataConf:
    """
    Used to generate the configuration attributes.
    """

    games: list[DataGame]

    def __post_init__(self):
        holder = list.copy(self.games)
        self.games.clear()
        for game in holder:
            self.games.append(DataGame(**dict(game)))


@dataclass
class JsonSettings:
    """
    Contains the and manages the configuration and the configuration files

    __defaultjson: Its declaration it's mainly for visual representation, since the value will be overwritten on __init__

    conf: Will be transformed into a dataclass object.
    conf.game: list[DataGame]
    conf.game[x]: DataGame
    conf.game[x].notes: list[list]
    conf.game[x].notes[x]: str
    conf.game[x].highlight: list
    conf.game[x].highlight[x]: list[DataHighlight]
    conf.game[x].highlight[x].fore: str       hex color used to highlight the color of the text
    conf.game[x].highlight[x].back: str       hex color used to highlight the background of the text
    conf.game[x].highlight[x].regex: str      regex_rule used to highlight the text


    """
    __defaultjson = {'games': [
        {
            'name': str,
            'notes': [str],
            'highlight': [{'fore': str, 'back': str, 'regex': str}],
        },
    ]}
    conf: DataConf = None

    def __init__(self, json: {} = None, path: str = None) -> None:
        """
        __defaultson json: will be used as an empty configuration.

        :param json: Receives a json that will be used as a configuration instead of using a file
        :param path: Receives the path to a file that contains the configuration file that contains a JSON configuration
        """

        self.__defaultjson = {
            'games': []
        }
        if path:
            self.load_json_from_file(path=path)
        elif json:
            self.load_json_from_dic(json=json)
        else:
            self.load_json_from_dic(json=self.__defaultjson)

    def load_json_from_dic(self, json: {}) -> None:
        """
        :param json: Pass the content received to build_conf, which will build the configuration
        """
        self.build_conf(json=json)

    def load_json_from_file(self, path: str) -> None:
        """
        :param path: Opens the content of the given file and pass it's content to build_conf, which will build the
        configuration.
        """
        with open(path) as json_file:
            json = jload(json_file)
        # Validation/Checking
        self.build_conf(json=json)

    def export_json_to_file(self, path: str) -> None:
        """
        Exports the current configuration to file
        :param path: File path to overwrite/create.
        """
        with open(path, 'w') as outfile:
            jwrite(self.json, outfile)

    def build_conf(self, json: dict):
        """
        Converts a json/dictionary object into a dataclass configuration, and overwrites the current configuration.
        """
        self.conf = DataConf(**dict(json))

    @property
    def json(self) -> dict:
        """
        Transforms current dataclass configuration into a dictionary
        It's main usage is being able to export the current configuration into a json file

        DONT USE THIS TO OVERWRITE THE CURRENT CONFIGURATION

        :return dict: Returns a dictionary/JSON.
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


class zombie_window(tk.Toplevel, tk.Tk):
    """
    Floating window used to store text and highlight it.

    on_save_note_callback: Callback used when clicking add_note_button, as a single argument sends the text_box content
    text: tk.Text object where the label is stored for future usages
    add_note_bt: tk.Button object created to add notes
    destroyed: Bool to keep track about if the window been destroyed or not.
    """

    on_save_note_callback = lambda txt: print(f'Executed the add note command, but by default doesnt store it '
                                              f'anywhere.\n\t:: {txt}')
    text: tk.Text
    add_note_bt: tk.Button
    destroyed: bool

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
        """
        Creates and packs the text wd
        :return:
        """
        self.text = tk.Text(self)
        self.text.insert(tk.INSERT, "Select a note first")
        self.text.pack(fill=tk.X, side=tk.RIGHT, expand=True, anchor=tk.E)

    def update_text(self, text='', highlight: list = None) -> None:
        """
        Updates the content that it's displaying right now.
        :param text: Text to display
        :param highlight: List of rules used to highlight the text
        """
        self.destroy_content()
        self.create_text_wd()
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.INSERT, text)
        self.highlight_text(*highlight or [])

    def highlight_text(self, *rules: Union[list[DataHighlight], None]) -> None:
        """
        Highlights the text.

        For each line in the txt widged, search words that match the regex rules
            For every entry found will create a rule with the configuration given

        x: Is used to keep track of the number of generated rules
           Every time you create a rule you need a different name for the rule and updating the text removes them all.
        :param rules: List of rules used to highlight the text
        """
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
        """In case that the text widged or the add_note_button is created, it destroys them"""
        if hasattr(self, 'text') and callable(getattr(self.text, 'destroy')):
            self.text.destroy()
        if hasattr(self, 'add_note_bt') and callable(getattr(self.add_note_bt, 'destroy')):
            self.add_note_bt.destroy()

    def new_note_mode(self, callback: typing.Callable = None):
        """
        Updating the size of the window it's a workaround to the button not displaying
        Once updated removes the text
        Finally creates the button with the given callback

        :arg callback: pass the content to create_addnote_button

        """
        self.geometry("650x60")
        self.update_text()
        self.create_addnote_button(callback)

    def create_addnote_button(self, callback: typing.Callable = None):
        """
        Creates the button widget.

        :arg callback: function used as a callback to receive the current text of the text widget

            def callback(text):
                pass
        """
        self.on_save_note_callback = callback or self.on_save_note_callback
        self.add_note_bt = tk.Button(
            self,
            text='Add note',
            height=20,
            width=20,
            command=self.__on_save_note)
        self.add_note_bt.pack(expand=False, side=tk.LEFT, anchor=tk.W)

    def __on_save_note(self):
        """
        Executed when the add_note_button is pressed.

        Will execute the stored callback sending the text content currently being displayed.

        If set up a master window:
            Update the list of notes from the manager in order to display the new note.
        """
        self.on_save_note_callback(txt=self.current_txt())
        if hasattr(self, 'master') and callable(getattr(self.master, 'update_notelist')):
            self.master.update_notelist()

    def destroy(self):
        """
        Destroys the window

        destroyed: bool: Stores if the window been destroyed or not
        """
        super().destroy()
        self.destroyed = True

    def current_txt(self):
        """
        :return: Current text stored in the labbel, and replaces the ending newline
        """
        txt = self.text.get("1.0", tk.END)
        if txt[-1] == '\n':
            txt = txt[:-1]
        return txt


class Manager:
    """
    Manager used to contain the configuration and the windows displayed

    tk_menu: tk.Tk: Stores the main tk menu
    wd_title: str: Window name that be used when creating the main tk menu
    """
    tk_menu: tk.Tk
    wd_title: str

    def __init__(self, title="tk picker", jsonpath=None):
        """

        :param title: Window name that be used when creating the main tk menu
        :param jsonpath: Path to the JSON configuration file, used in case want to be loaded from the start
        """
        self.json_conf: JsonSettings = JsonSettings(path=jsonpath)
        self.wd_title = title

    def __load_tk(self):
        """Dump conf into tk manager obj"""
        self.tk_menu: tk = tk_menu(manager=self, title=self.wd_title)

    def start_tk(self):
        """Starts the main tk window"""
        self.__load_tk()
        self.tk_menu.start()


class tk_menu(tk.Tk):
    """
    Main tk window used to manage the lists and the zombie window, created as a tkinter object


    game_dic: dict[str:DataGame]: Dictionary that will store (only for display) the game configurations, using the game name as a key
    load_bt: tk.Button : Button used to load the configuration
    save_bt: tk.Button : Button used to export the configuration
    game_list_var: tk.StringVar : Variable used to store the selected game
    game_list_wd: tk.OptionMenu : Widget used to display the available games
    note_list_var: tk.StringVar : Variable used to store the selected note
    note_list_wd: tk.OptionMenu : Widget used to display the available notes
    zombie_window: tk.Tk : Window used to display the desired text and highlight with the given rules
    addnotemsg: str : Text displayed as en element in the note list to add a new note
    conf_dir: str : Last directory used to load/save a configuration, by default it points to the user home folder

    """
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

    def __init__(self, *args, title="tk", manager: Manager = None):
        """
        :param args: Arguments passed to the tk.__init__ default function
        :param title: Title used to display in the window
        :param manager: Manager object stored for later usage/load the json configuration
        """
        super().__init__(*args)
        self.conf_dir = str(Path.home())
        self.game_dic: dict[str:DataGame] = {}
        self.manager = manager
        self.title(title)
        self.update()
        self.create_menu()

    def update_game_dic(self):
        """
        Updates the content of the game_dic
        """
        self.game_dic.clear()
        for game in self.manager.json_conf.conf.games:
            self.game_dic[game.name] = game

    def create_menu(self):
        """
        Calls the function that creates the widget to manage the configuration, aka, load/save buttons
        """
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
        """Creates the load conf button"""
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=self.conf_dir or str(Path.home()),
            filetypes=filetypes)
        self.conf_dir = dirname(filename)
        self.manager.json_conf.load_json_from_file(filename)
        self.update_lists_wd()

    def __save_conf(self):
        """Creates the save conf button"""
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = fd.asksaveasfilename(
            title='Save to file',
            initialdir=self.conf_dir or str(Path.home()),
            filetypes=filetypes)
        self.conf_dir = dirname(filename)
        # Check stuff
        self.manager.json_conf.export_json_to_file(filename)

    def create_game_list_wd(self):
        """
        Creates the widget that displays the list of games
        """
        self.game_list_var = tk.StringVar(self)
        self.game_list_var.set(("Select one" if len(self.game_dic.keys()) != 0 else "Any game detected"))
        self.game_list_var.trace('w', self.__once_selected_game)
        self.game_list_wd = tk.OptionMenu(self, self.game_list_var, *[key for key in self.game_dic])
        self.game_list_wd.pack(fill=tk.Y, expand=False)

    def create_notes_list_wd(self, game_name):
        """
        Creates the widget that displays the list of notes based on the currently selected game
        """
        self.note_list_var = tk.StringVar(self)
        self.note_list_var.set(("Select one" if len(self.game_dic.keys()) != 0 else "Any note"))
        self.note_list_var.trace('w', self.__once_selected_note)
        self.note_list_wd = tk.OptionMenu(self, self.note_list_var,
                                          *self.game_dic.get(game_name).notes, self.addnotemsg)
        self.note_list_wd.pack(fill=tk.Y, expand=False)
        self.update()

    def start(self):
        """
        Starts the mainloop function
        """
        self.mainloop()

    def update_lists_wd(self):
        """
        Destroy the current lists/buttons widgeds in order to update all the contents
        """
        self.update_game_dic()
        self.destroy_notelist_wd()
        self.destroy_gamelist_wd()
        self.create_game_list_wd()

    def destroy_gamelist_wd(self):
        """Destroys game_list widget"""
        if type(self.game_list_wd) is tk.OptionMenu:
            self.game_list_wd.destroy()

    def update_notelist(self):
        """Destroys and calls the function to recreate the list of notes"""
        self.destroy_notelist_wd()
        self.create_notes_list_wd(self.game_list_var.get())
        pass

    def destroy_notelist_wd(self):
        """Destroys notelist widged"""
        if type(self.note_list_wd) is tk.OptionMenu:
            self.note_list_wd.destroy()

    def __once_selected_game(self, *args):
        """
        Callback from selecting an element from the game list widget
        :param args: Not used, receive arguments from the callback
        """
        print(f"game selected: <<<{self.current_game}>>>")
        self.update_notelist()
        pass

    def __once_selected_note(self, *args):
        """
        Callback from selecting an element from the note list widget
        :param args: Not used, receive arguments from the callback
        """
        if type(self.zombie_window) is not zombie_window or self.zombie_window.destroyed:
            self.zombie_window = zombie_window(master=self)
        if self.current_note == self.addnotemsg:
            self.zombie_window.new_note_mode(self.store_new_note)
        else:
            self.zombie_window.update_text(self.current_note,
                                           highlight=self.game_dic[self.current_game].highlighting)

    def store_new_note(self, txt):
        """
        Prints a message once adding a note, also displays the content from added note.
        :param txt: Adds the received content as a new note in the current game list
        """
        print(f"Added new note to storage: \n::: {txt}")
        next(game.notes for game in self.manager.json_conf.conf.games
             if game.name == self.current_game).append(txt)

    @property
    def current_game(self):
        """
        Returns the content from the current game selected
        """
        return self.game_list_var.get()

    @property
    def current_note(self):
        """
        Returns the content from the current note selected

        If the note list widget not been created yet, prints a message (which should be replaced by a warning message
        or something)
        """
        if type(self.note_list_wd) is tk.OptionMenu:
            return self.note_list_var.get()
        else:
            print("Select a game first")

if __name__ == '__main__':
    """
    Takes the first argument and use it as a path to the JSON configuration
    If no argument is passed will start without a configuration.
    """
    default_file: str or None = None
    if len(argv) > 1:
        default_file = argv[1]
    x = Manager(title="tk menu", jsonpath=default_file)
    x.start_tk()