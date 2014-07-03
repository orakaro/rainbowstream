## Available themes
#### Default
![Default](./screenshot/themes/Default.png)
#### Monokai
![Monokai](./screenshot/themes/Monokai.png)
#### Solarized
![Solarized](./screenshot/themes/Solarized.png)

## Customize:
You are free to create your own themes.

Create a file `~/.rainbow_config.json` and follow next instruction.
Examples are available in 
[Monokai theme](https://github.com/DTVD/rainbowstream/blob/master/rainbowstream/colorset/monokai.json)
or
[Solarized theme](https://github.com/DTVD/rainbowstream/blob/master/rainbowstream/colorset/solarized.json)

### Custom config
 * Config file should be excatly named `.rainbow_config.json` and placed at home directory.
 * Config file's content should follow `Json` format.
 * Comment as `//` or `/*...*/` is accepted.
 * Here is an example

```json
 /* Color config
    There are 16 basic colors supported :
        * default
        * black
        * red
        * green
        * yellow
        * blue
        * magenta
        * cyan
        * grey
        * light_red
        * light_green
        * light_yellow
        * light_blue
        * light_magenta
        * light_cyan
        * white
    and 256 terminal's colors from term_0 to term_255
    */

    "DECORATED_NAME" : "term_198",
    "CYCLE_COLOR" :["term_198","term_57","term_166","term_50","term_179","term_74","term_112"],
    "TWEET" : {
        "nick"      : "term_112",
        "clock"     : "term_57",
        "id"        : "term_166",
        "favourite" : "term_50",
        "rt"        : "term_179",
        "link"      : "term_74",
        "keyword"   : "on_light_green"
    },

    "MESSAGE" : {
        "sender"    : "term_112",
        "recipient" : "term_112",
        "to"        : "term_50",
        "clock"     : "term_57",
        "id"        : "term_166"
    },

    "PROFILE" : {
        "statuses_count"    : "term_112",
        "friends_count"     : "term_198",
        "followers_count"   : "term_57",
        "nick"              : "term_198",
        "profile_image_url" : "term_74",
        "description"       : "term_166",
        "location"          : "term_112",
        "url"               : "term_74",
        "clock"             : "term_57"
    },

    "TREND" : {
        "url": "term_74"
    }
}
```

### Available Colors

There are 16 basic colors:
  * default
  * black
  * red
  * green
  * yellow
  * blue
  * magenta
  * cyan
  * grey
  * light_red
  * light_green
  * light_yellow
  * light_blue
  * light_magenta
  * light_cyan
  * white

These colors will be enough for almost terminals.
But if your terminals can support 256 colors (check your `$XTERM` variable!), 
you can even use `term_0` to `term_255` as sample above.

Color reference can be found at 
[bash color](http://misc.flogisoft.com/bash/tip_colors_and_formatting) or 
[256 xterm](http://www.calmar.ws/vim/256-xterm-24bit-rgb-color-chart.html)

### Available options
* DECORATED_NAME: color of your Twitter's _username_ which is placed at every line's begin.
* CYCLE_COLOR: is a list of colors from which Twitter _real name_ 's color is selected. 

⋅⋅* Color selection is cycle through this list but with a _memoization_. 
⋅⋅* It's means that same names will appear in same colors.



