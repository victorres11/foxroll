# foxroll
https://foxroll.herokuapp.com/

## Re-sizing dynos on heroku
This will resize both the web and worker server's

`heroku ps:resize web=standard-1x worker=standard-1x`

## Deploying a new application on Heroku
Pushing new code to this github repo will automatically deploy it on heroku application plus force it to re-start.

## Logs on heroku
`heroku logs --tail`

`heroku logs --dyno web`
