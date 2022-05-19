substitute `develop` with proper branch name (the one you're currently on)

```shell script
heroku login
heroku create --region eu angelareader-dev
heroku buildpacks:set heroku/python
git commit --allow-empty -m "set buildpacks for heroku"
git remote add heroku https://git.heroku.com/angelareader-dev.git
git push heroku develop:main
# heroku config:set token=<insert a valid token here>
heroku ps:scale bot=1
# heroku logs --tail
```

SSH to server:

```shell script
heroku ps:exec --status
heroku ps:exec --dyno=bot.1
```

Turn the bot off:

```shell script
heroku ps:scale bot=0
```

NB: there is a workflow to automatically deploy to Heroku
