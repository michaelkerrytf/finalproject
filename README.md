# finalproject

A tool to enable tenants of Harvard Apigee to perform operations against artifacts therein, to better
facilitate CI/CD. The 'real' version of this tool actually runs against the Apigee Management API, 
but as doing so requires access to restricted environments and secrets, this version contains a 'mock' version
of that API, that mimics enough of the functionality in order to migrate a single artifact type, Shared Flows.

This tool logs all migration activity in a database, and displays it to the user. In the 'real' application the
user would need to authenticate against Harvard Key (as this is essentially a prototype, no authentication is required).
Use of this tool's API would also be restricted by the use of an API Key, managed by Apigee itself (I know, that 
is starting to sound a little "Inception-ish"). Again, as this is essentially a prototype, no API key is required.

I have included a suite of postman tests, and an environment that provides the base URL, in the `/postman_tests` directory. 
Once the application has been started via the instructions below, you may run any of those tests as many times as you 
wish to generate successful and failed migrations that will then appear in the appropriate logs. The default view
is for the adex logs, but there are links to take you to the others. Admittedly, the UI is rudimentary, but is 
sufficient for its purpose, for the moment.

## create virtual env - see https://realpython.com/intro-to-pyenv/
```commandline - in root directory
pyenv virtualenv django
pyenv activate django
```
Once created, you can then create a `.python-version` file containing simply the word `django` so that any time 
you cd into that directory the `django` virtual environment will automatically be activated

## dependencies
```commandline
pip install -r requirements.txt
```

## to run application locally
```commandline
python manage.py runserver
```
