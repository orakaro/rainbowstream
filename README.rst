Rainbow Stream
--------------

.. image:: http://img.shields.io/pypi/l/rainbowstream.svg?style=flat-square
   :target: https://github.com/DTVD/rainbowstream/blob/master/LICENSE.txt

.. image:: http://img.shields.io/pypi/v/rainbowstream.svg?style=flat-square
   :target: https://pypi.python.org/pypi/rainbowstream

Terminal-based full-fledged Twitter client, built upon `Python Twitter Tools`.

Showcase
--------

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/rs.gif
   :alt: gif

Installation
------------

Direct installation
^^^^^^^^^^^^^^^^^^^

.. code:: bash

    sudo pip3 install rainbowstream

Virtualenv (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install rainbowstream

Installation Troubleshooting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you run into dependency issues, you may want to install additional libraries

Debian-based distros:

.. code:: bash

    sudo apt-get install python-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

CentOS:

.. code:: bash

    sudo yum install python-devel libjpeg-devel

Mac OSX 
Mac has a `clang unknown argument`_
problem with the ``Pillow`` package—a dependency of this
app.  Please see the workaround in `Issue #10`_

.. code:: bash

    export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

If you still experience issues:

-  ``sudo pip uninstall rainbowstream``
-  Use the *virtualenv installation*
-  `Create an issue`_ and provide:
    - Your OS
    - Your Python version

Usage
-----

The Stream
^^^^^^^^^^

Simply run ``rainbowstream`` to start the application, or enjoy its ASCII images with ``rainbowstream -iot`` or set ``IMAGE_ON_TERM`` to ``True`` in your config.

If your terminal supports 24-bit colors, run ``rainbowstream -p24`` instead to utilize 24 bit ASCII images.

If your terminal supports sixel, ie. wezterm or MLTerm, change the ``IMAGE_ON_TERM`` config to ``sixel`` and enjoy high-quality images.

You might want to change ``IMAGE_SHIFT`` to set the image's margin (relative to your terminal's
width), and ``IMAGE_MAX_HEIGHT`` to control the max height of every image (see
`Config Management`_).

You will be asked for Twitter authorization the first time you run Rainbow
Stream.  Just click the "Authorize access" button, paste the PIN to the
terminal, and the application will start.

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

While your stream is continued, you are also ready to tweet, search,
reply, retweet, etc. directly from your console.  Simply type ``h`` and hit the
Enter key to see the help.

Input is in interactive mode.  It means that you can use the arrow keys to move
up and down through the history, tab-autocomplete, or double-tab to view
available suggestions.  Input history from the previous run is also available.

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

A Note about Twitter API Change
-------------------------------

Since Twitter discontinued supporting Stream API, RainbowStream is now using a [Polling Strategy](https://github.com/orakaro/rainbowstream/issues/271) that utilizes the `home` command to poll for your tweets every 90 seconds. This `home` command is rate limited by 15 times per 15 minutes, so don't run it too frequently to leave space for the polling stream.

Bug and Feature Requests
------------------------

Found a bug or a feature request?  Please `create an issue`_ or contact me at
`@orakaro`_.

Development
-----------

If you want to build a runnable version yourself, follow these simple steps:

- `Create your Twitter Application`_
-  Get your Twitter application’s API key and secret
- `Create your own Pocket Application`_ (platform: Web)
-  Get your Pocket application’s key
-  Fork this repo and ``git clone`` it
-  Create a ``consumer.py`` file in the `rainbowstream` directory containing:

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
request`_. 

License
-------

Rainbow Stream is released under an MIT License.  See LICENSE.txt for details.


.. _Python Twitter Tools: http://mike.verdone.ca/twitter/
.. _Twitter API: https://dev.twitter.com/docs/api/1.1
.. _Create an issue: https://github.com/DTVD/rainbowstream/issues/new
.. _@orakaro: https://twitter.com/dtvd88
.. _fork: https://github.com/DTVD/rainbowstream/fork
.. _create a pull request: https://github.com/DTVD/rainbowstream/compare/
.. _Read the docs: http://rainbowstream.readthedocs.org/en/latest/
.. _config guide: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _Theme Usage and Customization: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _Create your Twitter Application: https://apps.twitter.com/app/new
.. _Create your own Pocket Application: https://getpocket.com/developer/apps/new
.. _Config Management: http://rainbowstream.readthedocs.org/en/latest/#config-explanation
.. _clang unknown argument: http://kaspermunck.github.io/2014/03/fixing-clang-error/
.. _Issue #10: https://github.com/DTVD/rainbowstream/issues/10
