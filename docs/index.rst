Rainbow Stream
--------------

.. image:: http://img.shields.io/pypi/dm/rainbowstream.svg?style=flat
   :target: https://pypi.python.org/pypi/rainbowstream

.. image:: http://img.shields.io/pypi/v/rainbowstream.svg?style=flat
   :target: https://pypi.python.org/pypi/rainbowstream

Terminal-based Twitter Client. Realtime tweetstream, compose, search ,
favorite … and much more fun directly from terminal.

This package is built on the top of `Python Twitter Tool`_ and `Twitter API`_,
can run on Python 2.7.x and 3.x .

Install
-------

The quick way
^^^^^^^^^^^^^

You will need Python and pip (2.7.x or 3.x).

.. code:: bash

    sudo pip install rainbowstream
    # Python 3 users: sudo pip3 install rainbowstream

The recommended way
^^^^^^^^^^^^^^^^^^^

Use `virtualenv`_

.. code:: bash

    virtualenv venv
    # Python 3 users : use -p to specify your Python 3 localtion as below
    # virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install rainbowstream

Troubleshooting
^^^^^^^^^^^^^^^

If you use Linux, you might need to install some packages if you haven't already.
For debian-based distros, these can be installed with

.. code:: bash

    sudo apt-get install python-dev libjpeg libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

Besides, Mac OSX Maverick with Xcode 5.1 has a well-known `clang unknown argument`_ problem with
the ``Pillow`` package installation - a dependency of this app.
If you are in this case, I recommend taking a look at `Issue #10`_ and let me know if this workaround doesn't work for you.

.. code:: bash

    export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

If installation in *the quick way* doesn't work:

-  ``sudo pip uninstall rainbowstream``
-  use the *virtualenv way* above
-  `create an issue`_ and provide:

  + Your OS
  + Your Python version

Usage
-----

The stream
^^^^^^^^^^

Just type

.. code:: bash

    rainbowstream

and see your stream.

I shipped a feature which can display **tweet's images directly on terminal**.
You can try it with:

.. code:: bash

    rainbowstream -iot # Or rainbowstream --image-on-term

You also can change the config key ``IMAGE_ON_TERM`` to ``True`` inside the app
to enable above feature,
change ``IMAGE_SHIFT`` to set image's margin (relative to your terminal's width)
or ``IMAGE_MAX_HEIGHT`` to control max height of every image.
(see `config management`_ section).

In the first time you will be asked for authorization of Rainbow Stream
app at Twitter. Just click the “Authorize access” button and paste PIN
number to the terminal, the rainbow will start.

The interactive mode
^^^^^^^^^^^^^^^^^^^^

While your personal stream is continued, you are also ready to tweet,
search, reply, retweet… directly from console. Simply type “h” and hit
the Enter key to see the help.

Input is in interactive mode. It means that you can use arrow key to
move up and down history, tab-autocomplete or 2 tab to view available
suggestion. Input history from previous run is available as well.

Here is full list of supported command:

**Explore Commands**

-  ``trend`` will show global trending topics. ``trend US`` will show trends in United States while ``trend JP Tokyo`` will show trends in Tokyo/Japan.

-  ``home`` will show your timeline. ``home 10`` will print exactly 10 tweets.

-  ``notification`` will show your notification from the time you started RainbowStream.

-  ``mentions`` will show mentions timeline. ``mentions 7`` will show 7 mention tweets.

-  ``whois @dtvd88`` will show profile of @dtvd88.

-  ``view @mdo`` will show @mdo ’s timeline. ``view @dmo 9`` will print exactly 9 tweets.

-  ``s noah`` will search the word *‘noah’*. Result will come back with highlight. Search can be performed with or without hashtag.

**Tweet Commands**

-  ``t the rainbow is god's promise to noah`` will tweet exactly *‘the rainbow is god’s promise to noah’*.

-  ``rt 12`` will retweet the tweet with *[id=12]*. You can see id of each tweet beside the time.

-  ``quote 12`` will quote the tweet with *[id=12]*. If no extra text is added, the quote will be cancelled.

-  ``allrt 12 20`` will list 20 newest retweets of the tweet with *[id=12]*. If the number of retweets is not specified, 5 newest retweets will be listed instead.

-  ``conversation 12`` will show the chain of replies prior to the tweet with *[id=12]*.

-  ``rep 12 Really`` will reply *‘Really’* to the tweet with *[id=12]*.

-  ``fav 12`` will favorite the tweet with *[id=12]*.

-  ``ufav 12`` will unfavorite tweet with *[id=12]*.

-  ``del 12`` will delete tweet with *[id=12]*.

-  ``show image 12`` will show the image in tweet with *[id=12]* in your OS’s image viewer.

-  ``open 12`` will open url in tweet with *[id=12]* in your OS’s default browser.

**Direct Messages Commands**

-  ``inbox`` will show inbox messages. ``inbox 7`` will show newest 7 messages.

-  ``thread 2`` will show full thread with [id=2].

-  ``mes @dtvd88 hi`` will send a ``hi`` message to @dtvd88.

-  ``trash 5`` will remove message with *[message\_id=5]*

**Friends and followers Commands**

-  ``ls fl`` will list all your followers (people who are following you).

-  ``ls fr`` will list all your friends (people who you are following).

-  ``fl @dtvd88`` will follow @dtvd88.

-  ``ufl @dtvd88`` will unfollow @dtvd88.

-  ``mute @dtvd88`` will mute @dtvd88.

-  ``unmute @dtvd88`` will unmute @dtvd88.

-  ``muting`` will list muting users.

-  ``block @dtvd88`` will block @dtvd88.

-  ``unblock @dtvd88`` will unblock @dtvd88.

-  ``report @dtvd88`` will report @dtvd88 as a spam account.

**Twitter list**

-  ``list`` will show all lists you are belong to.

-  ``list home`` will show timeline of list. You will be asked for list's name.

-  ``list all_mem`` will show list's all members.

-  ``list all_sub`` will show list's all subscribers.

-  ``list add`` will add specific person to a list owned by you.

-  ``list rm`` will remove specific person from a list owned by you.

-  ``list sub`` will subscribe you to a specific list.

-  ``list unsub`` will unsubscribe you from a specific list.

-  ``list own`` will show all list owned by you.

-  ``list new`` will create a new list.

-  ``list update`` will update a list owned by you.

-  ``list del`` will delete a list owned by you.

**Switching Stream Commands**

-  ``switch public #AKB48`` will switch current stream to public stream and track keyword ``AKB48``

-  ``switch public #AKB48 -f`` will do exactly as above but will ask you to provide 2 list:

   ``Only nicks`` decide what nicks will be include only.

   ``Ignore nicks``\ decide what nicks will be exclude.

-  ``switch public #AKB48 -d`` will apply filter to *ONLY\_LIST* and *IGNORE\_LIST*. You can setup 2 list above at ``config.py``

-  ``switch mine`` will switch current stream to personal stream. ``-f`` and ``-d`` will work as well.

**Smart shell**

- Put anything to terminal, the app will try to eval and display result as a python interactive shell.

  + ``142857*2`` or ``101**3`` like a calculator.
  + Even ``cal`` will show the calendar for current month.
  + Put ``order_rainbow('anything')`` or ``random_rainbow('wahahaha')`` will make more fun :)

**Config Management**

-  ``theme`` will list available themes.

  + ``theme monokai`` will apply *monokai* theme immediately.
  + Changed theme will be remember as the next time's default theme.

-  ``config`` will list all config key.

  + ``config ASCII_ART`` will output current value of *ASCII_ART* config key.
  + ``config TREND_MAX default`` will output default value of *TREND_MAX* config key.
  + ``config CUSTOM_CONFIG drop`` will drop *CUSTOM_CONFIG* config key.
  + ``config IMAGE_ON_TERM = true`` will set value of *IMAGE_ON_TERM* config key to *True*.

**Screening Commands**

-  ``h`` will show the help.

-  ``p`` will pause the stream.

-  ``r`` will unpause the stream.

-  ``c`` will clear the screen.

-  ``q`` will quit.

Theme customization
^^^^^^^^^^^^^^^^^^^

Rainbow Stream is shipped with some default themes.
You can either change theme by ``theme`` command or create your favorite one.

Theme’s screenshot:

- Monokai

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/themes/Monokai.png
   :alt: monokai

- Solarized

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/themes/Solarized.png
   :alt: solarized

- Tomorrow Night

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/themes/TomorrowNight.png
   :alt: tomorrownight

- Larapaste

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/themes/larapaste.png
   :alt: larapaste

For detaile information, see `theme usage and customization`_.

Config explanation
^^^^^^^^^^^^^^^^^^

Rainbow Stream has a custom config file located at ``~/.rainbow_config.json`` which will be loaded **after** its `default config`_. You are free to change anything on your custom config, but if you messed up with JSON format, the app would still works fine. Simply overwrite your custom config withe the `default config`_ to solve format problems.

You also can view or set a new value of every config key by ``config`` command (See **Interactive mode** section above).

-  ``HEARTBEAT_TIMEOUT``: after this timeout (count by minutes), the stream will automatically hangup.

-  ``IMAGE_ON_TERM``: display tweet's image directly on terminal.

-  ``THEME``: current theme.

-  ``ASCII_ART``: diplay your twitter name by ascii art at stream begin or not.

-  ``HIDE_PROMPT``: hide prompt after receiving a tweet or not.

-  ``PREFIX``: display string of prompt.

-  ``SEARCH_TYPE``: search type in 'search' command ('mixed','recent','popular').

-  ``SEARCH_MAX_RECORD``: max tweets can display on 'search' command.

-  ``HOME_TWEET_NUM``: default tweets to display on 'home' command.

-  ``RETWEETS_SHOW_NUM``: default tweets to display on 'allrt' command.

-  ``CONVERSATION_MAX``: max tweet in a 'conversation' thread.

-  ``QUOTE_FORMAT``: format when quote a tweet

    + ``#comment``: Your own comment about the tweet
    + ``#owner``: owner's username with '@'
    + ``#tweet``: original tweet

-  ``THREAD_META_LEFT``: format for meta information of messages from partner which is display in the left of screen.

-  ``THREAD_META_RIGHT``: format for meta information of messages from you which is display in the right of screen.

-  ``THREAD_MIN_WIDTH``: minimum width of a message frame.

-  ``NOTIFY_FORMAT``: format of a notification.

-  ``MESSAGES_DISPLAY``: default messages to display on 'inbox' or 'sent' command.

-  ``TREND_MAX``: default trends to display on 'trend' command.

-  ``LIST_MAX``: default tweets to display on 'list home' command.

-  ``ONLY_LIST``: filter list on 'switch' command.

-  ``IGNORE_LIST``: ignore list on 'switch' command.

-  ``HISTORY_FILENAME``: name of file which stores input history.

-  ``IMAGE_SHIFT``: left and right margin of image in '-iot'/'--image-on-term' mode.

-  ``IMAGE_MAX_HEIGHT``: max height of image in '-iot'/'--image-on-term' mode.

-  ``USER_DOMAIN``: user URL of Twitter Streaming API.

-  ``PUBLIC_DOMAIN``: public URL of Twitter Streaming API.

-  ``SITE_DOMAIN``: site URL of Twitter Streaming API.

-  ``FORMAT``: display format for tweet and message.

  + ``CLOCK_FORMAT``: time format, see `Python's strftime format`_.
  + ``DISPLAY``: decide how tweet will be printed.

    + ``#name``: Twitter's name
    + ``#nick``: Twitter's screen name
    + ``#clock``: Datetime
    + ``#rt_count``: retweets count
    + ``#fa_count``: favorites count
    + ``#id``: ID
    + ``#fav``: favorited symbol
    + ``#fav``: favorited symbol
    + ``#tweet``: Tweet's content
    + ``#sender_name``: Message's sender name
    + ``#sender_nick``: Message's sender screen name
    + ``#to``: '>>>' symbol
    + ``#recipient_name``: Message's recipient name
    + ``#recipient_nick``: Message's recipient screen name


Development
-----------

If you want to build a runnable version yourself, follow these simple
steps

-  `Create your own Twitter Application`_
-  Get your Twitter application’s API key and secret
-  Fork github's repo and clone in your system.
-  Create a file ``consumer.py`` in ```rainbowstream```_ folder with
   following content

   .. code:: python

       # Consumer information
       CONSUMER_KEY = 'APIKey' # Your Twitter application's API key
       CONSUMER_SECRET = 'APISecret' # Your Twitter application's API secret

-  Use pip to install in local

   .. code:: bash

       # cd to directory which contains setup.py (cloned directory)
       virtualenv venv # Python3 users: use -p to specify python3
       source venv/bin/activate
       pip install -e .
       which rainbowstream # /this-directory/venv/bin/rainbowstream
       pip list | grep rainbowstream # rainbowstream (0.x.x, /this-directory)
       # Remove ~/.rainbow_oauth if exists
       rainbowstream # local version of rainbowstream

.. _Create your own Twitter Application: https://apps.twitter.com/app/new
.. _``rainbowstream``: https://github.com/DTVD/rainbowstream/tree/master/rainbowstream
.. _Python Twitter Tool: http://mike.verdone.ca/twitter/
.. _Twitter API: https://dev.twitter.com/docs/api/1.1
.. _theme usage and customization: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _config management: http://rainbowstream.readthedocs.org/en/latest/#config-explanation
.. _Python's strftime format: https://docs.python.org/2/library/time.html#time.strftime
.. _clang unknown argument: http://kaspermunck.github.io/2014/03/fixing-clang-error/
.. _Issue #10: https://github.com/DTVD/rainbowstream/issues/10
.. _default config: https://github.com/DTVD/rainbowstream/blob/master/rainbowstream/colorset/config

