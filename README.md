## Rainbow Stream

[![Download](http://img.shields.io/pypi/dm/rainbowstream.svg?style=flat)](https://pypi.python.org/pypi/rainbowstream)
[![Version](http://img.shields.io/pypi/v/rainbowstream.svg?style=flat)](https://pypi.python.org/pypi/rainbowstream)

Terminal-based Twitter Client.
Realtime tweetstream, compose, search , favorite ... and much more fun directly from terminal.

This package is built on top of [Python Twitter Tool](http://mike.verdone.ca/twitter/) and [Twitter API](https://dev.twitter.com/docs/api/1.1).

## Showcase
Screencast:
https://www.youtube.com/watch?v=tykCvPMJq8s
<br>

Screenshot: (Click to see)
![rainbowstream](https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/RainbowStreamAll.png)

## Install
You will need Python 2.7+ and pip.

```bash
sudo pip install rainbowstream
```

or try with a virtualenv
```bash
sudo pip install virtualenv # skip if you already have virtualenv
virtualenv venv
source venv/bin/activate # use the brand new virtualenv.
pip install rainbowstream
```


## Usage
#### The stream
Just type
```bash
rainbowstream
```
and see your stream.

I shipped a feature which can display **tweet's images directly on terminal**.
You can try it with:
```bash
rainbowstream -iot # Or rainbowstream --image-on-term
```

In the first time you will be asked for authorization of Rainbow Stream app at Twitter.
Just click the "Authorize access" button and paste PIN number to the terminal, the rainbow will start.

## Interactive mode

While your personal stream is continued, you are also ready to tweet, search, reply, retweet... directly from console.
Simply type "h" and hit the Enter key to see the help.

Input is in interactive mode. It means that you can use arrow key to move up and down history, tab-autocomplete or 2 tab to view available suggestion. Input history from previous run is available as well.

Available commands are listed in [Read The Docs](http://rainbowstream.readthedocs.org/en/latest/) .

## Theme customization
Rainbow Stream is shipped with some default themes.
You can either change theme by `theme` command or create your favorite one.

Theme's screenshot:
* Monokai
![Monokai](./screenshot/themes/Monokai.png)
* Solarized
![Solarized](./screenshot/themes/Solarized.png)
* Tomorrow Night
![Solarized](./screenshot/themes/TomorrowNight.png)
* Larapaste
![Solarized](./screenshot/themes/larapaste.png)

For detaile information, see [theme usage and customization](https://github.com/DTVD/rainbowstream/blob/master/theme.md)

## Bug and feature requests
Found a bug or a feature request ?
Please [create an issue](https://github.com/DTVD/rainbowstream/issues/new)
or contact me at [@dtvd88](https://twitter.com/dtvd88)

## Development
If you want to build a runnable version yourself, follow these simple steps
* [Create your own Twitter Application](https://apps.twitter.com/app/new)
* Get your Twitter application's API key and secret
* Fork this repo
* Create a file `consumer.py` in [`rainbowstream`](https://github.com/DTVD/rainbowstream/tree/master/rainbowstream) folder with following content
```python
# Consumer information
CONSUMER_KEY = 'APIKey' # Your Twitter application's API key
CONSUMER_SECRET = 'APISecret' # Your Twitter application's API secret
```
* Use pip to install in local
```bash
# cd to directory which contains setup.py
pip install -e .
pip list # confirm installed version
rainbowstream # Local version of rainbowstream
```

## Contributing
I appreciate any help and support. Feel free to
[fork](https://github.com/DTVD/rainbowstream/fork)
and
[create a pull request](https://github.com/DTVD/rainbowstream/compare/).
You will be listed as contributor.

## License
Rainbow Stream are released under an MIT License. See LICENSE.txt for details
