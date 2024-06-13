Set host and username for database inside db_engine.py

Create virtual environment:
`python3 -m venv env`

Activate the environment:
`source env/bin/activate`

Update pip:
`pip install -U pip`

Install package:
`pip install  --no-cache-dir -r requirements.txt`

The specific versions stated in the requirements file can cause packages to be re-compiled if the current versions are more uptodate. This is turn may force series of packages to be installed in the operating system in order to supply the needed libraries and header files for such compilations. To avoid this, replace all instances of `==` with `>=` in requirements.txt to allow the latest versions of the packages to be installed instead. The code should work fine with the updated packages. Only if there is a problem does one need to revert to the older version specified in the requirements file.

Start the server at the top-level directory for the API code:
`uvicorn app.main:app --reload`

To deactivate the environment:
`deactivate`
