Changelog
*********
..
   All enhancements and patches to Fedinesia will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   The format is trending towards that described at `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
   and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
==========

See the fragment files in the `changelog.d directory`_.

.. _changelog.d directory: https://codeberg.org/MarvinsMastodonTools/fedibooster/src/branch/main/changelog.d


.. scriv-insert-here

.. _changelog-1.2.0:

1.2.0 — 2025-01-10
==================

Changed
-------

- Now checking usernames against `no_reblog_users` list entries using regex search. This allows regex
  to be added to the `no_reblog_users` list and for example exclude all users from a particular server
  For example any user from Threads by adding `@threads.net` to the `no_reblog_users` list.

- Updated CI

.. _changelog-1.1.2:

1.1.2 — 2024-12-31
==================

Changed
--------

- Updated dependencies versions...we now support Python 3.13

.. _changelog-1.1.1:

1.1.1 — 2024-12-15
==================

Fixed
-----

- Checking of no_reblog_users when username of status does not contain host.

.. _changelog-1.1.0:

1.1.0 — 2024-11-18
==================

Added
-----

- Added config setting `reblog_sensitive` taking `true` or `false` to indicate if fedibooster should boost statuses marked sensitive (potentially NSFW). If not specified, this setting defaults to `false`, i.e. fedibooster will NOT boost sensitive statuses.

.. _changelog-1.0.1:

1.0.1 — 2024-11-17
==================

Initial release
