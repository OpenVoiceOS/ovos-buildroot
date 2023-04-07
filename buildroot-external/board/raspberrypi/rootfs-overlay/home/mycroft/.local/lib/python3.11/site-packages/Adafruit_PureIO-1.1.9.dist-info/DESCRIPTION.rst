
Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-pureio/badge/?version=latest
    :target: https://adafruit-pureio.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_Python_PureIO/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_Python_PureIO/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Pure python (i.e. no native extensions) access to Linux IO including I2C and SPI. Drop in replacement for smbus and spidev modules.


Dependencies
=============
This driver depends on:

* Python 3.5 or higher

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/Adafruit-PureIO/>`_. To install for current user:

.. code-block:: shell

    pip3 install Adafruit-PureIO

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install Adafruit-PureIO

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install Adafruit-PureIO

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_Python_PureIO/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.


