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

To be honest, this project is currently in rough shape (no tests)
but when I get around to it I might put some more work into it as I find
it useful for monitoring the pull requests for the projects I work on at
work.

+++ Install Dependencies +++
sudo easy_install PyGithub

+++ Install/Run +++
sudo ./setup.py install
prspy

+++ Authorization +++
PRSpy requires an OAuth token to communicate with github on your behalf. An
OAuth token can be created via the Option dialog's Authorization tab. Enter
your github credentials and click the create button.

+++ Adding Repositories +++
You can add repositories to track via the Option dialog's Repositories tab.
Here you can add a single repository at a time or all of the repositories
within an organization.

NOTE: Repositories should be entered in the following format:
[owner]/[repo_name]

For example: mstead/prspy

+++ Dependancies +++
Listing required dependencies here for now until I get around to packaging.

1. PyGithub (https://github.com/jacquev6/PyGithub)

