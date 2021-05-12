substitute `develop` with proper branch name (the one you're currently on)

```{bash}
# heroku login
# heroku create --region eu angelareader
# heroku buildpacks:set heroku/python
# heroku buildpacks:add https://github.com/dmathieu/heroku-buildpack-submodules
# git commit --allow-empty -m "set buildpacks for heroku"
git push heroku develop:main
heroku ps:scale bot=1
# heroku logs --tail
```
SSH to server:
```shell script
heroku ps:exec --dyno=bot.1
```
Turn the bot off:
```shell script
heroku ps:scale bot=0
```

