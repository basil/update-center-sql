# Update Center SQL

An [SQLite](https://www.sqlite.org) interface to the [Jenkins Update Center](https://github.com/jenkins-infra/update-center2). This program:

* Downloads the update center JSON from `updates.jenkins.io`.
* Imports the result into an SQLite database.
* Drops you into an `sqlite3(1)` shell in that database.

<img width="600" src="docs/images/recording.svg">

## Usage

```sh
$ python3 update-center-sql.py -h
usage: update-center-sql.py [-h] [-o OUTPUT] [-u UPDATE_CENTER]

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The name of the SQLite database to create. (default: update-center.db)
  -u UPDATE_CENTER, --update-center UPDATE_CENTER
                        The Update Center URL to fetch plugins from. (default: https://updates.jenkins.io/update-center.json)
```

## Examples

```sql
$ python3 update-center-sql.py
SQLite version 3.37.2 2022-01-06 13:25:41
Enter ".help" for usage hints.
sqlite> .tables
core          deprecations  plugins       root          signature
sqlite> .mode column
sqlite> .header on
sqlite> select size,url,version from core;
size      url                                                        version
--------  ---------------------------------------------------------  -------
97886217  https://updates.jenkins.io/download/war/2.377/jenkins.war  2.377
sqlite> select name,popularity from plugins order by popularity desc limit 5;
name             popularity
---------------  ----------
script-security  294142
mailer           293797
scm-api          293204
credentials      292977
structs          292887
sqlite> select * from deprecations order by name limit 5;
name                 url
-------------------  ----------------------------------------------------
BlameSubversion      https://github.com/jenkinsci/jenkins/pull/5320
CFLint               https://issues.jenkins.io/browse/INFRA-2487
DotCi                https://www.jenkins.io/security/plugins/#suspensions
DotCi-DockerPublish  https://www.jenkins.io/security/plugins/#suspensions
DotCi-Fig-template   https://www.jenkins.io/security/plugins/#suspensions
sqlite> .quit
$ sqlite3 update-center.db "select name,popularity from plugins where name in ('timestamper', 'email-ext', 'swarm') order by popularity desc;"
timestamper|249292
email-ext|246868
swarm|8072
$
```

## License

Licensed under [the MIT License](LICENSE).
