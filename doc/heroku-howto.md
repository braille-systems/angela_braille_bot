substitute `develop` with proper branch name (the one you're currently on)

```{bash}
# heroku login
# heroku create --region eu angelareader
# heroku buildpacks:set heroku/python
git push heroku develop:main
heroku ps:scale bot=1
# heroku logs --tail
```
