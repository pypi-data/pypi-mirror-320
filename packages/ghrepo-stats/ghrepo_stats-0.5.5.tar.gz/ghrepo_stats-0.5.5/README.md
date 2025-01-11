# ghrepo-stats [![PyPI version](https://badge.fury.io/py/ghrepo-stats.svg)](https://badge.fury.io/py/ghrepo-stats)

Have you ever wondered how the number of stargazers or the number of open
issues has changed over time for your or any public GitHub repository? I did, 
so I wrote this small command line tool that will show this data.

*ghrepo-stats* uses [pygithub](https://github.com/PyGithub/PyGithub) to 
collect some statistics from a specific repository using a command line tool
and show it using [matplotlib](https://github.com/matplotlib/matplotlib) or
write it to a csv file. 

Features
--------
The following sub-commands are supported:
- stars: shows the number of stargazers over time (caveat: stargazers that
  have removed their star are not shown, as the info is not available)
- issues: shows the number of currently open issues over time
- prs: shows the number of currently open pull requests over time
- commits: shows the number of commits over the last year
- codesize: shows the change of the code size over time measured by the 
  number of added and deleted lines
- issue-life: shows the average life time in days of issues over time
  (sampled once a week) 
- pr-life: shows the average life time in days of issues over time 
  (sampled once a week) 
- dependents: show which repositories and packages depend on your repository
  as a list sorted by the number of stargazers

Runtime
-------
Using sub-commands related to issues and PRs on repositories with many
(open or close) issues may take a lot of time due to API access
limitations the first time they are used on a given repository. 
Each subsequent call shall be much faster, as the results are cached in the file system
(as json files in the subdirectory `.ghrepo-stats` in the home directory of the current 
user).
Commands not related to issues/prs usually shall not take a long time, except for 
dependents - these are currently not cached and take a sufficient time 
(up to several minutes) if there are many of them (e.g. several thousands).

Installation
------------
If you want to try it, you can install it from PyPi:
```
pip install ghrepo-stats
```
Or you can install the current main branch from GitHub:
```
pip install git+https://github.com/mrbean-bremen/ghrepo-stats
```

Usage
-----
To use this, you need a GitHub account and a
[personal access token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token)
able to read public repositories for your GitHub account. The user name and
token is expected to be found in the file `ghrepo-stats.ini`, either in the
repository root, or in your home path.

The contents should be in the form:
```
[auth]
username = my-github-username
token = 123456789abcdef0123456789abcdef012345678
```

To get usage information you can now type:
```
$ show-ghstats -h
usage: show-ghstats [-h] [--verbose] [--csv CSV] sub_command repo_name

Shows GitHub repo statistics

positional arguments:
  sub_command    The kind of statistics to show. Possible values: 'issues',
                 'prs', 'stars', 'commits', 'codesize', 'issue-life', 'pr-
                 life', 'dependents'.
  repo_name      Full repository name in the form <repo_owner>/<repo_name>.

optional arguments:
  -h, --help     show this help message and exit
  --verbose, -v  Outputs diagnostic information
  --csv CSV      Write the output into a csv file with the given file path
  --packages     Only for dependents: get dependent packages instead of repositories
  --min-stars MIN_STARS
                 Only for dependents: limits the output to dependents with at least 
                 the given number of stargazers.
```

So, for example, to get a star plot of a specific repository, you can write:
```
$ show-ghstats stars "my-github-username/my-repo"
```
If you want to have the numbers saved in a csv file instead to play around with
the numbers you can write: 
```
$ show-ghstats stars "my-github-username/my-repo" --csv=my_repo-issues
```
This will write a file `my_repo-issues.csv` with the numbers (date+time /
number of issues) in the current path.

Dependents
----------
Getting dependent repositories is a bit different from the other commands, as 
dependent repositories are not available via the GitHub API, and there is no 
statistics to show. Instead, the data is collected using web scraping, and output 
into a CSV file if given or as lines on the standard output.
There are also 2 specific parameters for this option (`--packages` and `--min-stars`)
as shown above. Sorting by the number of stargazers is done to show the most known 
repositories first.
No caching is done here (yet), so depending on the number of dependent repositories
the call may take a long time.

Examples
--------
Get some measure of popularity change by showing the number of stargazers over
time (note: stars that have been retracted are not counted):
```commandline
$ show-ghstats stars "pytest-dev/pyfakefs"
```
![stars](https://github.com/mrbean-bremen/ghrepo-stats/raw/main/doc/images/stars.png)

Check how issues are handled over time. There are two possibilities:
 - Show the number of open issues at any point in time:
```commandline
$ show-ghstats issues "svg-net/svg"
```
![issues](https://github.com/mrbean-bremen/ghrepo-stats/raw/main/doc/images/issues.png)

 - Show the average lifetime of an issue as it changes over time. An 
   increasing curve means ever more unresolved issues (also depends on the
   policies of the specific project - some projects leave issues open
   indefinitely, while others close outdated issues):
```commandline
$ show-ghstats issue-life "pytest-dev/pyfakefs"
```
![issue-lifetime](https://github.com/mrbean-bremen/ghrepo-stats/raw/main/doc/images/issuelife.png)

Get some measure of activity by checking how the code size changed over time 
(measured in code additions/deletions):
```commandline
$ show-ghstats codesize "pytest-dev/pyfakefs"
```
![codesize](https://github.com/mrbean-bremen/ghrepo-stats/raw/main/doc/images/codesize.png)

Check which well-known packages depend on your repository: 
```commandline
$ show-ghstats dependents pydicom/pydicom --packages --min-stars=1000
```
```
fastai/fastai   23163
activeloopai/deeplake   5120
pypa/sampleproject      4500
openvinotoolkit/openvino        3890
Project-MONAI/MONAI     3675
Project-MONAI/MONAI     3675
microsoft/presidio      1906
Image-Py/imagepy        1209
```