""""""""""""""""""""""""""
fedibooster
""""""""""""""""""""""""""

|Repo| |CI| |AGPL|

|Checked with| |Downloads|

|Code style| |Version| |Wheel|



fedibooster is a command line (CLI) tool / bot / robot to re-blog / boost statuses with hash tags in a given list.
It respects rate limits imposed by servers.

Install and run from `PyPi <https://pypi.org>`_
=================================================

It's ease to install fedibooster from Pypi using the following command::

    pip install fedibooster

Once installed fedibooster can be started by typing ``fedibooster`` into the command line.

Install and run from `Source <https://codeberg.org/marvinsmastodontools/fedibooster>`_
==============================================================================================

Alternatively you can run fedibooster from source by cloning the repository using the following command line::

    git clone https://codeberg.org/marvinsmastodontools/fedibooster.git

fedibooster uses `uv`_ for dependency control, please install UV before proceeding further.

Before running, make sure you have all required python modules installed. With uv this is as easy as::

    uv sync

Run fedibooster with the command `uv run fedibooster`

Configuration / First Run
=========================

fedibooster will ask for all necessary parameters when run for the first time and store them in ```config.toml``
file in the current directory.

Licensing
=========
fedibooster is licensed under the `GNU Affero General Public License v3.0 <http://www.gnu.org/licenses/agpl-3.0.html>`_

Supporting fedibooster
==========================

There are a number of ways you can support fedibooster:

- Create an issue with problems or ideas you have with/for fedibooster
- Create a pull request if you are more of a hands on person.
- You can `buy me a coffee <https://www.buymeacoffee.com/marvin8>`_.
- You can send me small change in Monero to the address below:

Monero donation address
-----------------------
``88xtj3hqQEpXrb5KLCigRF1azxDh8r9XvYZPuXwaGaX5fWtgub1gQsn8sZCmEGhReZMww6RRaq5HZ48HjrNqmeccUHcwABg``


.. _uv: https://docs.astral.sh/uv/

.. |AGPL| image:: https://www.gnu.org/graphics/agplv3-with-text-162x68.png
    :alt: AGLP 3 or later
    :target:  https://codeberg.org/marvinsmastodontools/fedibooster/src/branch/main/LICENSE.md

.. |Repo| image:: https://img.shields.io/badge/repo-Codeberg.org-blue
    :alt: Repo at Codeberg.org
    :target: https://codeberg.org/marvinsmastodontools/fedibooster

.. |Downloads| image:: https://pepy.tech/badge/fedibooster
    :alt: Download count
    :target: https://pepy.tech/project/fedibooster

.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style: Black
    :target: https://github.com/psf/black

.. |Checked with| image:: https://img.shields.io/badge/pip--audit-Checked-green
    :alt: Checked with pip-audit
    :target: https://pypi.org/project/pip-audit/

.. |Version| image:: https://img.shields.io/pypi/pyversions/fedibooster
    :alt: PyPI - Python Version

.. |Wheel| image:: https://img.shields.io/pypi/wheel/fedibooster
    :alt: PyPI - Wheel

.. |CI| image:: https://ci.codeberg.org/api/badges/13923/status.svg
    :alt: CI / Woodpecker
    :target: https://ci.codeberg.org/repos/13923
