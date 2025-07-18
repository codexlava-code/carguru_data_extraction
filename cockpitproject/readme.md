# BOBST Manchester LTD Machine Diagnosis and analytics tools
### Online diagnosis and data analysis tool of managing, analysing, visualising, and monitoring dataset from various sensors.

### Setup

Make sure you have the docker-compose V2

Both docker-compose and Dockerfile are in the root directory

The docker-compose.yml has the nginx and app configuration with the starting command present in Dockerfile.

To build the image and bring up the container.

```
docker-compose up -d --build
```

To bring up the container when is down run 

```
docker-compose up -d
```

### Dependency update

The application uses pipenv to manage package dependencies.

To install a new package use

```
pipenv install package_name
```

### Implementing task assigned on devops

Open assigned task

Change it to Active when you have started implementation 

create a branch locally for the task in this format

Always branch from the dev for new task

git checkout dev

```
git checkout -b feat/task_id
git checkout -b bug/task_id
git checkout -b task/task_id
```

When you are done with the task, your commit message should reference the ticket id

```
git commit -m "feat: #task_id"
git commit -m "bug: #task_id"
git commit -m "task: #task_id"
```

Then you can push to raise a merge request against the dev branch which should be protected by default.

A reviewer will review your code and put comment if required.


### Database Setup

To run all database migrations:

```
python manage.py --action migrate
```

To seed sample data:

```
python manage.py --action seed_sample
```

To rollback all database migrations:

```
python manage.py --action rollback
```


### Development

During the process you will do changes that won't be available straight away.
Investigate commands above and make sure you understand them, usually restart is 
enough to see local changes but sometimes you may need to do `docker compose down && docker compose up`.


### Coding style

Follow PEP8 coding style standard described [here](https://peps.python.org/pep-0008/). 
It's official Python coding styles developed by Guido van Rossum, creator of Python language.
We should make sure our code is consistent and readable as the most of our time a developer spends on reading
code not writing.

#### Most important style rules

Make sure you don't exceed 79 chars per line, it's described [here](https://peps.python.org/pep-0008/#maximum-line-length).
Also keep an eye on [imports](https://peps.python.org/pep-0008/#imports).

* Standard library imports. Check [here](https://docs.python.org/3/library/) if you are not sure if it's standard or not.
* Related third party imports.
* Local application/library specific imports.

You should put a blank line between each group of imports.

Here is an example:
```
import datetime

import peewee

from apps.common.db import db_config
```

where `uuid` is [in built](https://docs.python.org/3/library/uuid.html)(standard library and goes first),
`pymysql` goes after as it third party library defined in `Pipfile` and the last one is
`Timer` from `src.common.timer` which refers to repository codebase.

### Autoformatters

Jetbrains IDE has got a shortcut for auto formatting to make developer life easier which is `Ctrl + Alt + l`.
However you still need to keep an eye of line limit as the formatter doesn't do it really nicely unless you have a custom setup.

Another option is to use autopep8, see example:
