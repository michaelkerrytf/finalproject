# CSCI E33A Final Project

A tool to enable tenants of Harvard Apigee to perform operations against artifacts therein, to better
facilitate CI/CD. 
> @author Michael Kerry

## Notes
The 'real' version of this tool actually runs against the Apigee Management API, 
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

Given that I set up the postman tests, the unit tests are meager and were really more about getting things started. 
If this were a 'real' project there would be more and better unit tests (and in fact in the 'work' version of this 
project there are).

## Setup and Execution of application

### create virtual env - see https://realpython.com/intro-to-pyenv/
```commandline - in root directory
pyenv virtualenv django
pyenv activate django
```
Once created, you can then create a `.python-version` file containing simply the word `django` so that any time 
you cd into that directory the `django` virtual environment will automatically be activated

### dependencies
```commandline
pip install -r requirements.txt
```

### to run application tests
```commandline
python manage.py test
```

### test coverage
```commandline
coverage run --source='.' manage.py test 
coverage annotate -d coverage_annotations  
coverage html 
```
will produce test coverage that should be viewable at `<path_to_parent>/finalproject/htmlcov/index.html`

In a typical project I would be shooting for a fairly high coverage (85-90%) but as mentioned above, these unit tests
were more of jumping-off point, and I relied more on the postman tests to confirm behavior

### to run application locally
```commandline
python manage.py runserver
```
