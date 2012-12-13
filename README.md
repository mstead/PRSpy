             ____________________  ________________________.___.
             \______   \______   \/   _____/\______   \__  |   |
             |     ___/|       _/\_____  \  |     ___//   |   |
             |    |    |    |   \/        \ |    |    \____   |
             |____|    |____|_  /_______  / |____|    / ______|
                              \/        \/            \/

PRSpy is a GNOME application that allows you to monitor GitHub pull requests
across multiple repositories.

This project started out when I decided to play with the github API one night.
After messing around with parsing JSON from responses and getting familiar
with the GH API a little more, I adapted PyGithub.

To be honest, this project is currently in rough shape (no tests/packaging)
but when I get around to it I might put some more work into it as I find
it useful for monitoring the pull requests for the projects I work on at
work.


+++ Running/Setup +++

For now, PRSpy must be run from the prspy (checkout) dir.

env PYTHONPATH=PYTHONPATH:src/ ./bin/prspy

It has a built-in configuration module that will be launched when PRSpy is
started. You will need to enter your github usename and password to create
an Oauth token so that PRSpy can access the API on your behalf.

Once created, it can be viewed via your github Settings --> Applications page.

Currently, PRSpy can only view the pull requests across multiple repositories
within a single organization. You will be asked to enter an organization ID
during the configuration process.

Alternatively, you can manually configure PRSpy by creating a configuration file
in ~/.prspy/prspy.conf (see the sample config file in the checkout dir). This is
useful if you already have an Oauth token created.


+++ Dependancies +++
Listing required dependencies here for now until I get around to packaging.

1. PyGithub (https://github.com/jacquev6/PyGithub)

