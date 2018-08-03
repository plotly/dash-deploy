# dash-deploy

In this repo lives the centralized `deploy.py` script, this helper is here to help dash app developers deploy to a Dash Deployment Server without going back and forth to copy and paste, or having to remember dokku/git commands to deploy their apps.

The command for any dash app to have the deploy helper in its root is:

`git submodule add https://git-scm.com/docs/git-submodule`

And every time the developer wants to get the latest version of the script locally, they would do:

`git submodule update --remote`