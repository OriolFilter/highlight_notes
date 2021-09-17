## What do I do

This app takes a configuration form a JSON file that contains a list of notes and (optionally) a list of regex rules 
that will highlight the text.

Once the file is loaded, will display a list of the games that our configuration contains.

<img src="https://raw.githubusercontent.com/OriolFilter/highlight_notes/master/screenshots/game_list.png"/>

After selecting the desired game, will show a list of the current notes.

<img src="https://raw.githubusercontent.com/OriolFilter/highlight_notes/master/screenshots/note_list.png"/>

Finally, when a note is selected, will open a new window to display the content of the note and highlight the text based 
on the highlight list from that game (that way one can have multiple different highlighting rules for multiple games).

<img src="https://raw.githubusercontent.com/OriolFilter/highlight_notes/master/screenshots/note_example.png"/>

Keep in mind that one can replace the game for whichever topic they want, ie. instead of game you could have a list of
notes for each character you want to learn/play, but remember that the highlighting ISN'T shared, so you will need to 
manually duplicate the lines.

### Adding a new note

Additionally, in case of selecting the "**_Add new note_**" element from the list of notes, the note window will empty 
itself, and we will be able to write a new note, once we finished writing it, we can click the button "_**Add note**_" 
to add the note to the list.

<img src="https://raw.githubusercontent.com/OriolFilter/highlight_notes/master/screenshots/new_note_A.png"/>

<strong style="color: #e22727">It's probable that if the window it's not wide enough, the button might be hidden, keep 
it in mind if the button doesn't show up.</strong>

### Removing a note

One is able to add multiple notes in a row, but, if one want to <strong style="color: #e22727">delete</strong> a note, 
you will need to access the JSON configuration file, and remove the note manually (it's simply removing a line of text).


## But... why?

The purpose of this was being able to display some text in a floating window, allowing me to capture that window in OBS 
while recording the labbing sessions, so in a future I remember what was attempting to do that day/moment. 

### Executing the file from terminal

```bash
python3 (path_to_folder)/notes_app.py
```

In case you want to load a configuration file automatically, by default takes the first argument as the file desired to 
use as configuration. 

```bash
python3 (path_to_folder)/notes_app.py (path_to_folder)/custom_json.json
```

### To make the file self-executable (Linux)

This enables executing the file without specifying python path (yet might still be required in Windows, or if the 
python path differs from the current in testing environment).
First step is to give the executable permission.
```
chmod +x (path_to_folder)/notes_app.py
```
Once the permission is given, next step is to execute it from the terminal:
```
(path_to_folder)/notes_app.py
```
Or in case of being in the current folder, instead of using the global path, we can use the relative one, yet in case 
of using a shortcut the global path must be used:
```
./notes_app.py
```
Also, now, using the graphic interface, we can execute the file (if our system configuration allows us), to run the 
app with a double click.


#### Example of JSON configuration:

- To validate your JSON file, one can use this page: https://jsonlint.com/ .

- To validate/test your regex rules, one can use this page: https://regex101.com/ .

- Remember to scape the specials characters in the regex rule (aka, if you need to use the character '\', you should
replace it with a double '\', make it look like '\\').

```json
{
            "games": [
                {
                    "name": "game",
                    "notes": [
                        "note"
                    ],
                    "highlighting": [
                        {"fore": "#hexcolor", "regex": "regex_rule"}
                        ]
                },
                {
                    "name": "game2",
                    "notes": [
                        "note"
                    ],
                    "highlighting": [
                        {"fore": "#hexcolor", "regex": "regex_rule"}
                        ]
                }
            ]
}
```



##### TODO

- [ ] Comment the functions properly
- [x] Add being able to call the file from terminal specifying a file as an argument in order to automate it
- [ ] Do some sort of error checking / data validation / output message in case things go wrong
- [ ] Improve GUI (but idc since it suits the function it was designed to)


### In case someone want to share their configuration file (mainly for the highlighting), it can be added to the list of examples.

## Contact

- Discord: `OriolFilter#3716`
- GitHub: itself