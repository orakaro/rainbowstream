Rainbow Stream
--------------

.. image:: http://img.shields.io/pypi/dm/rainbowstream.svg?style=flat
   :target: https://pypi.python.org/pypi/rainbowstream

.. image:: http://img.shields.io/pypi/v/rainbowstream.svg?style=flat
   :target: https://pypi.python.org/pypi/rainbowstream

Terminal-based Twitter Client. Realtime tweetstream, compose, search ,
favorite … and much more fun directly from terminal.

This package is built on the top of `Python Twitter Tool`_ and `Twitter API`_.

Showcase
----------
Screencast: https://www.youtube.com/watch?v=tykCvPMJq8s

Screenshot:

.. figure:: https://raw.githubusercontent.com/DTVD/rainbowstream/master/screenshot/RainbowStreamAll.png
   :alt: rainbowstream

Install
-------

You will need Python 2.7+ and pip.

.. code:: bash

    sudo pip install rainbowstream

or try with a virtualenv

.. code:: bash

    sudo pip install virtualenv # skip if you already have virtualenv
    virtualenv venv
    source venv/bin/activate # use the brand new virtualenv.
    pip install rainbowstream

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

In the first time you will be asked for authorization of Rainbow Stream
app at Twitter. Just click the “Authorize access” button and paste PIN
number to the terminal, the rainbow will start.

The interactive mode
--------------------

While your personal stream is continued, you are also ready to tweet,
search, reply, retweet… directly from console. Simply type “h” and hit
the Enter key to see the help.

Input is in interactive mode. It means that you can use arrow key to
move up and down history, tab-autocomplete or 2 tab to view available
suggestion. Input history from previous run is available as well.

Available commands are listed in `Read The Docs`_.

Theme customization
------------------------

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

Bug and feature requests
------------------------

Found a bug or a feature request ?
Please `create an issue`_ or contact me at `@dtvd88`_

Contributing
------------
I appreciate any help and support. Feel free to `fork`_ and `create a pull request`_.
You will be listed as contributor.

License
-------

Rainbow Stream are released under an MIT License. See LICENSE.txt for
details


.. _Python Twitter Tool: http://mike.verdone.ca/twitter/
.. _Twitter API: https://dev.twitter.com/docs/api/1.1
.. _create an issue: https://github.com/DTVD/rainbowstream/issues/new
.. _@dtvd88: https://twitter.com/dtvd88
.. _fork: https://github.com/DTVD/rainbowstream/fork
.. _create a pull request: https://github.com/DTVD/rainbowstream/compare/
.. _Read The Docs: http://rainbowstream.readthedocs.org/en/latest/
.. _config guide: https://github.com/DTVD/rainbowstream/blob/master/theme.md
.. _theme usage and customization: https://github.com/DTVD/rainbowstream/blob/master/theme.md
