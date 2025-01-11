⚠ Project Archived - No Longer Maintained ⚠
===========================================

This project has been archived and is no longer maintained.

The main reason for this is that the website from which this software retrieved wallpapers is no longer operational. Without a reliable source for new content, the functionality of the tool is no longer viable.

As a result, this project will not receive any further updates or support. We thank everyone who has contributed to or used this project over time.

Thank you for your understanding!

Desktopography command line
===========================

see http://www.desktopography.net

Usage
-----

``` console
$ pip install desktopography
$ desktopography -h
```

TODO
----

- Add more verbose documentation and docstrings
- Add tests
- Setup CI
- Auto-detect screen size
- Fix XDG support
- Add changelog

Development
-----------

``` console
$ git clone https://gitlab.com/fbochu/desktopography.git
$ cd desktopography
$ poetry install
```

Tests
-----

``` console
$ poetry run prospector src/
$ poetry run black src/
$ poetry run isort src/
$ poetry run mypy src/
```

Publishing
----------

``` console
$ poetry version <patch|minor|major>
$ poetry build
$ poetry publish
```
