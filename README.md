Will do more later

### Example of JSON configuration:

- To validate your JSON file, one can use this page: https://jsonlint.com/

- To validate/test your regex rules, one can use this page: https://regex101.com/

- Remember to scape the specials characters in the regex rule (aka, if you need to use the character '\', you should replace it with a double '\', make it look like '\\')

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

- Comment the functions properly
- Do some sort of error checking / data validation / output message in case things go wrong
- Improve GUI (but idc since it suits the function it was designed to)
