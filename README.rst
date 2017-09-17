Rainbow Stream
--------------

.. image:: http://img.shields.io/pypi/l/rainbowstream.svg?style=flat-square
   :target: https://github.com/DTVD/rainbowstream/blob/master/LICENSE.txt

.. image:: http://img.shields.io/pypi/v/rainbowstream.svg?style=flat-square
   :target: https://pypi.python.org/pypi/rainbowstream

Terminal-based Twitter Client.  Real-time tweetstream, compose, search, favorite,
and much more fun directly from terminal.

This package is built on the `Python Twitter Tools`_ and the `Twitter API`_, and runs
on Python (2.7.x and 3.x).

Home page: https://github.com/orakaro/rainbowstream

Source code: https://github.com/DTVD/rainbowstream

Showcase
--------

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/rs.gif
   :alt: gif

Installation
------------

The Quick Way
^^^^^^^^^^^^^

System Python (2.7.x or 3.x)

.. code:: bash

    sudo pip install rainbowstream
    # Python 3 users: sudo pip3 install rainbowstream

The Recommended Way
^^^^^^^^^^^^^^^^^^^

`virtualenv`_

.. code:: bash

    virtualenv venv
    # Python 3 users : use -p to specify your Python 3 location:
    # virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install rainbowstream

Troubleshooting
^^^^^^^^^^^^^^^

Some additional libraries may need to be installed on linux.

For Debian-based distros:

.. code:: bash

    sudo apt-get install python-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

For CentOS:

.. code:: bash

    sudo yum install python-devel libjpeg-devel

Mac OSX Maverick with Xcode 5.1 has a well-known `clang unknown argument`_
problem with the installation of the ``Pillow`` package—a dependency of this
app.  Take a look at `Issue #10`_ and let me know if the workaround doesn't work
for you.

.. code:: bash

    export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

If *The Quick Way* doesn't work, then:

-  ``sudo pip uninstall rainbowstream``
-  Use the *The Recommended Way*
-  `Create an issue`_ and provide:
    - Your OS
    - Your Python version

Usage
-----

The Stream
^^^^^^^^^^

Just type ``rainbowstream`` to see your stream.

You can now **display tweeted images directly on the terminal**!  Try it with:

.. code:: bash

    rainbowstream -iot # Or rainbowstream --image-on-term

Set ``IMAGE_ON_TERM`` to ``True`` in your config to to enable above feature,
change ``IMAGE_SHIFT`` to set image's margin (relative to your terminal's
width), and ``IMAGE_MAX_HEIGHT`` to control max height of every image (see
`Config Management`_).

You will be asked for authorization on Twitter the first time you run Rainbow
Stream.  Just click the "Authorize access" button, paste PIN number to the
terminal, and the rainbow will start.

You might want to use Rainbow Stream with an **HTTP/SOCKS proxy**.  Proxy
settings are specified as follows:

.. code:: bash

    rainbowstream --proxy-host localhost --proxy-port 1337 --proxy-type HTTP
    # or the short form:
    rainbowstream -ph localhost -pp 1337 -pt HTTP

Both ``--proxy-port`` and ``--proxy-type`` are optional.  The default proxy port
is ``8080`` and the default proxy type is ``SOCKS5``.

Interactive Mode
^^^^^^^^^^^^^^^^

While your personal stream is continued, you are also ready to tweet, search,
reply, retweet, etc. directly from your console.  Simply type ``h`` and hit the
Enter key to see the help.

Input is in interactive mode.  It means that you can use the arrow keys to move
up and down through the history, tab-autocomplete or double-tab to view
available suggestions.  Input history from previous run is also available.

`Read the docs`_ for available commands.

Theme Customization
^^^^^^^^^^^^^^^^^^^

Rainbow Stream is shipped with some default themes.  You can switch themes with
the ``theme`` command.  You can also customize themes as you please.

Theme screenshots:

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

See `Theme Usage and Customization`_ for detailed information.


Bug and Feature Requests
------------------------

Found a bug or a feature request?  Please `create an issue`_ or contact me at
`@dtvd88`_.

Development
-----------

If you want to build a runnable version yourself, follow these simple steps:

- `Create your own Twitter Application`_
-  Get your Twitter application’s API key and secret
- `Create your own Pocket Application`_ (platform: Web)
-  Get your Pocket application’s key
-  Fork this repo and ``git clone`` it
-  Create a ``consumer.py`` file in the `rainbowstream`_ directory containing:

   .. code:: python

       # Consumer information
       CONSUMER_KEY = 'APIKey' # Your Twitter application's API key
       CONSUMER_SECRET = 'APISecret' # Your Twitter application's API secret
       PCKT_CONSUMER_KEY = 'PocketAPIKey' # Your Pocket application's API key

-  Use pip to install it locally

   .. code:: bash

       # cd to directory which contains setup.py (cloned directory)
       virtualenv venv # Python3 users: use -p to specify python3
       source venv/bin/activate
       pip install -e .
       which rainbowstream # /this-directory/venv/bin/rainbowstream
       # Remove ~/.rainbow_oauth if it exists
       rainbowstream # local version of rainbowstream


Contributing
------------

I appreciate any help and support.  Feel free to `fork`_ and `create a pull
request`_.  You will be listed as a contributor.

License
-------

Rainbow Stream is released under an MIT License.  See LICENSE.txt for details.


.. _Python Twitter Tools: http://mike.verdone.ca/twitter/
.. _Twitter API: https://dev.twitter.com/docs/api/1.1
.. _Create an issue: https://github.com/DTVD/rainbowstream/issues/new
.. _@dtvd88: https://twitter.com/dtvd88
.. _fork: https://github.com/DTVD/rainbowstream/fork
.. _create a pull request: https://github.com/DTVD/rainbowstream/compare/
.. _Read the docs: http://rainbowstream.readthedocs.org/en/latest/
.. _config guide: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _Theme Usage and Customization: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _Create your own Twitter Application: https://apps.twitter.com/app/new
.. _Create your own Pocket Application: https://getpocket.com/developer/apps/new
.. _rainbowstream: https://github.com/DTVD/rainbowstream/tree/master/rainbowstream
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Config Management: http://rainbowstream.readthedocs.org/en/latest/#config-explanation
.. _clang unknown argument: http://kaspermunck.github.io/2014/03/fixing-clang-error/
.. _Issue #10: https://github.com/DTVD/rainbowstream/issues/10
