# foxgrowth
foxgrowth

## Re-sizing dynos on heroku
This will resize both the web and worker server's

`heroku ps:resize web=standard-1x worker=standard-1x`

## Deploying a new application on Heroku
Pushing new code to this github repo will automatically push the new code to the heroku application and force it to re-start with the new code.

## Logs on heroku
`heroku logs --tail`

`heroku logs --dyno web`