# gmlutil-data-extraction

## Dependencies

botocore==1.35.0 <br />
aiobotocore==2.14.0 <br />
boto3==1.35.0 <br />
awscli==1.34.0 <br />
numpy==1.26.4 <br />
pandas>2.1.0<=2.2.2 <br />
astropy>=6.0.0 <br />
fuzzywuzzy>=0.18.0 <br />
geopandas>=0.10.2 <br />
hana-ml <br />
numba>=0.60.0 <br />
oracledb>=1.4.2 <br />
psycopg2-binary>=2.9.1 <br />
pyarrow>=17.0.0 <br />
pymssql>=2.2.1 <br />
python-levenshtein-wheels>=0.13.1 <br />
pytrends>=4.7.3 <br />
redshift_connector>=2.0.916 <br />
sagemaker>=2.229.0 <br />
sagemaker-data-insights>=0.4.0 <br />
sqlalchemy-redshift>=0.8.6 <br />

## How to install this package: RUN THESE COMMANDS IN SageMaker Environment or Jupyter Lab

gitlab_token='glpat-8xBrvJGUx7tdnnApwttb'

! git config --global http.sslVerify false

! pip install --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org git+https://gmlutil_data_extraction_token:{gitlab_token}@git.ejgallo.com/prophet-data-science/central-data-science-library/gmlutil-data-extraction.git@1.0.0

## How to set up in Dockerfile: ADD THESE COMMANDS in DOCKERFILE!!!

ARG gitlab_token="glpat-8xBrvJGUx7tdnnApwttb" <br />
ENV gitlab_token=${gitlab_token} <br />

RUN git config --global http.sslVerify false

RUN pip install --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org git+https://gmlutil_data_extraction_token:${gitlab_token}@git.ejgallo.com/prophet-data-science/central-data-science-library/gmlutil-data-extraction.git@1.0.0