Rainbow Stream
--------------

.. image:: http://img.shields.io/pypi/l/rainbowstream.svg?style=flat-square
   :target: https://github.com/DTVD/rainbowstream/blob/master/LICENSE.txt

.. image:: http://img.shields.io/pypi/v/rainbowstream.svg?style=flat-square
   :target: https://pypi.python.org/pypi/rainbowstream

Terminal-based Twitter Client. Realtime tweetstream, compose, search,
favorite … and much more fun directly from terminal.

This package is built on the top of `Python Twitter Tool`_ and `Twitter API`_,
can run on Python 2.7.x and 3.x .

Home page : http://www.rainbowstream.org/

Source code : https://github.com/DTVD/rainbowstream

Showcase
--------

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/rs.gif
   :alt: gif

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
    # Python 3 users : use -p to specify your Python 3 location as below
    # virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install rainbowstream

Troubleshooting
^^^^^^^^^^^^^^^

If you use Linux, you might need to install some packages if you haven't already.
For debian-based distros, these can be installed with

.. code:: bash

    sudo apt-get install python-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

For CentOS:

.. code:: bash

    sudo yum install python-devel libjpeg-devel

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

You might want to use rainbowstream via an **HTTP/SOCKS proxy**. Proxy settings are
provided as follows:

.. code:: bash

    rainbowstream --proxy-host localhost --proxy-port 1337 --proxy-type HTTP
    # or using the short form:
    rainbowstream -ph localhost -pp 1337 -pt HTTP

Both ``--proxy-port`` and ``--proxy-type`` can be omitted. In this case default
proxy port ``8080`` and default proxy type ``SOCKS5`` are used.

The interactive mode
^^^^^^^^^^^^^^^^^^^^

While your personal stream is continued, you are also ready to tweet,
search, reply, retweet… directly from console. Simply type “h” and hit
the Enter key to see the help.

Input is in interactive mode. It means that you can use arrow key to
move up and down history, tab-autocomplete or 2 tab to view available
suggestion. Input history from previous run is available as well.

Available commands are listed in `Read The Docs`_.

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

For detail information, see `theme usage and customization`_.


Bug and feature requests
------------------------

Found a bug or a feature request ?
Please `create an issue`_ or contact me at `@dtvd88`_

Development
-----------

If you want to build a runnable version yourself, follow these simple
steps

- `Create your own Twitter Application`_
-  Get your Twitter application’s API key and secret
- `Create your own Pocket Application`_ (platform: Web)
-  Get your Pocket application’s key
-  Fork this repo and clone in your system.
-  Create a file ``consumer.py`` in `rainbowstream`_ folder with
   following content

   .. code:: python

       # Consumer information
       CONSUMER_KEY = 'APIKey' # Your Twitter application's API key
       CONSUMER_SECRET = 'APISecret' # Your Twitter application's API secret
       PCKT_CONSUMER_KEY = 'PocketAPIKey' # Your Pocket application's API key

-  Use pip to install in local

   .. code:: bash

       # cd to directory which contains setup.py (cloned directory)
       virtualenv venv # Python3 users: use -p to specify python3
       source venv/bin/activate
       pip install -e .
       which rainbowstream # /this-directory/venv/bin/rainbowstream
       # Remove ~/.rainbow_oauth if exists
       rainbowstream # local version of rainbowstream


Contributing
------------
I appreciate any help and support. Feel free to `fork`_ and `create a pull request`_.
You will be listed as contributor.

License
-------

Rainbow Stream are released under an MIT License. See LICENSE.txt for
details


.. _python twitter tool: http://mike.verdone.ca/twitter/
.. _Twitter API: https://dev.twitter.com/docs/api/1.1
.. _create an issue: https://github.com/DTVD/rainbowstream/issues/new
.. _@dtvd88: https://twitter.com/dtvd88
.. _fork: https://github.com/DTVD/rainbowstream/fork
.. _create a pull request: https://github.com/DTVD/rainbowstream/compare/
.. _Read The Docs: http://rainbowstream.readthedocs.org/en/latest/
.. _config guide: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _theme usage and customization: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _Create your own Twitter Application: https://apps.twitter.com/app/new
.. _Create your own Pocket Application: https://getpocket.com/developer/apps/new
.. _rainbowstream: https://github.com/DTVD/rainbowstream/tree/master/rainbowstream
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _config management: http://rainbowstream.readthedocs.org/en/latest/#config-explanation
.. _clang unknown argument: http://kaspermunck.github.io/2014/03/fixing-clang-error/
.. _Issue #10: https://github.com/DTVD/rainbowstream/issues/10
