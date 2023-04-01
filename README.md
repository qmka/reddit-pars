[![Maintainability](https://api.codeclimate.com/v1/badges/92d18413fdc52546576d/maintainability)](https://codeclimate.com/github/qmka/reddit-pars/maintainability)
[![flake8](https://github.com/qmka/reddit-pars/actions/workflows/flake8.yml/badge.svg)](https://github.com/qmka/reddit-pars/actions/workflows/flake8.yml)

Console utility to parse images from Reddit

Usage:
```
reddit-img-parser name  [-h] [-a] [-b] [-s] [-u]
                        [-c {hot,new,rising,top}]
                        [-t {hour,day,week,month,year,all}] 
                        [-l LIMIT]
```

positional arguments:
```
  name - name of redditor or subreddit
```

options:
```
  -h, --help
  -s, --statistics - use this option if you want to get the list of redditors that posts to subreddit
  -b, --batch  - download data from all redditors or subreddits that written in file
  (use filename for 'name' positional argument)
  -r, --subreddit - indicates to the program that you are working with a subreddit
  -u, --user - indicates to the program that you are working with a redditor
  -c {hot,new,rising,top}, --category {hot,new,rising,top} - set category of posts
  -t {hour,day,week,month,year,all}, --time {hour,day,week,month,year,all} - set time filter of posts
  -l LIMIT, --limit LIMIT - indicates to the program how many media posts to download
```

If you don't specify category, time filter and/or limit, then the download will be performed with default values similar to: -c new -t day -l 10

Known issues:
- unable to process names starting with "-"