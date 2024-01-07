# Athelo Backend API

A REST API to interact with symptom tracking and messaging.

## Run App Locally

### With Docker Compose
After installing Docker and docker-compose, run
```
make build-run
```
to bring up a debug mode API container and a local postgres db container.

If you want imports to be recognized by your IDE, create a virtual environment
and install the dependecies locally. 
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### Migrations
1. Make your changes to files in `rest-api/models`. Any new models must extend Base from models.base
2. Import any new models in `rest-api/models/__init__.py`
3. Run `make bash-shell`
4. In the shell, run `flask db migrate -m "<migration description>"`
5. Still in the shell, test upgrade (`flask db upgrade`) and downgrade (`flask db downgrade`)

### With GCP (*Untested*)

To run the application locally using the Cloud SQL Python Connector, set
environment variables and install dependencies as shown below.

Note: The `INSTANCE_CONNECTION_NAME` for your instance can be found on the
**Overview** page for your instance in the
[Google Cloud console](https://console.cloud.google.com/sql) or by running
the following command:

```sh
gcloud sql instances describe <INSTANCE_NAME> --format='value(connectionName)'
```

#### Linux / Mac OS

Use these terminal commands to initialize environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service/account/key.json'
export INSTANCE_CONNECTION_NAME='<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>'
export DB_USER='<YOUR_DB_USER_NAME>'
export DB_PASS='<YOUR_DB_PASSWORD>'
export DB_NAME='<YOUR_DB_NAME>'
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.


#### Install Dependencies
Useful for syntax highlighting in your IDE. 

Next, install the requirements into a virtual environment:

```bash
virtualenv --python python3 env
source env/bin/activate
pip install -r requirements.txt
```

### Test the Application

Finally, start the application:

```bash
python app.py
```

Navigate towards `http://127.0.0.1:8080` to verify your application is running correctly.

### Deploy to Cloud Run

#### Automated
The QA GCP project Cloud Run instance automatically deploys on commits to main.

The Prod GCP project will automatically deploy tagged commits.

#### Manual

See the [Cloud Run documentation](https://cloud.google.com/sql/docs/postgres/connect-run)
for more details on connecting a Cloud Run service to Cloud SQL.

Note: If you want to connect to Cloud SQL over Private IP, add the additional
env variable `--set-env-vars PRIVATE_IP=True` and
flag `--vpc-connector <YOUR_VPC_CONNECTOR>` below.

```sh
gcloud run deploy cloud-sql-demo \
  --allow-unauthenticated \
  --set-env-vars INSTANCE_CONNECTION_NAME='<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>' \
  --set-env-vars DB_USER='<YOUR_DB_USER_NAME>' \
  --set-env-vars DB_PASS='<YOUR_DB_PASSWORD>' \
  --set-env-vars DB_NAME='<YOUR_DB_NAME>'
```

Navigate your browser to the URL output at the end of the deployment process
to view the demo app!

It is recommended to use the [Secret Manager integration](https://cloud.google.com/run/docs/configuring/secrets) for Cloud Run instead
of using environment variables for the SQL configuration. The service injects the SQL credentials from
Secret Manager at runtime via an environment variable.

Create secrets via the command line:

```sh
echo -n $INSTANCE_CONNECTION_NAME | \
    gcloud secrets create [INSTANCE_CONNECTION_NAME_SECRET] --data-file=-
```

Deploy the service to Cloud Run specifying the env var name and secret name:

```sh
gcloud run deploy cloud-sql-demo \
  --allow-unauthenticated \
  --update-secrets INSTANCE_CONNECTION_NAME=[INSTANCE_CONNECTION_NAME_SECRET]:latest,\
    DB_USER=[DB_USER_SECRET]:latest, \
    DB_PASS=[DB_PASS_SECRET]:latest, \
    DB_NAME=[DB_NAME_SECRET]:latest
```

## Cloud SQL Auth Proxy Usage

### Running locally

To run this application locally, download and install the `cloud-sql-proxy` by
following the instructions [here](https://cloud.google.com/sql/docs/postgres/sql-proxy#install).

Instructions are provided below for using the proxy with a TCP connection or a Unix Domain Socket.
On Linux or Mac OS you can use either option, but on Windows the proxy currently requires a TCP
connection.

#### Launch proxy with TCP

To run the sample locally with a TCP connection, set environment variables and launch the proxy as
shown below.

##### Linux / Mac OS

Use these terminal commands to initialize environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service/account/key.json'
export INSTANCE_HOST='127.0.0.1'
export DB_PORT='5432'
export DB_USER='<YOUR_DB_USER_NAME>'
export DB_PASS='<YOUR_DB_PASSWORD>'
export DB_NAME='<YOUR_DB_NAME>'
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.

Then use this command to launch the proxy in the background:

```bash
./cloud-sql-proxy <PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME> &
```

##### Windows/PowerShell

Use these PowerShell commands to initialize environment variables:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="/path/to/service/account/key.json"
$env:INSTANCE_HOST="127.0.0.1"
$env:DB_PORT="5432"
$env:DB_USER="<YOUR_DB_USER_NAME>"
$env:DB_PASS="<YOUR_DB_PASSWORD>"
$env:DB_NAME="<YOUR_DB_NAME>"
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.

Then use this command to launch the proxy in a separate PowerShell session:

```powershell
Start-Process -filepath "C:\<path to proxy exe>" -ArgumentList "<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>"
```

#### Launch proxy with Unix Domain Socket

NOTE: this option is currently only supported on Linux and Mac OS. Windows users should use the
[Launch proxy with TCP](#launch-proxy-with-tcp) option.

To use a Unix socket, you'll need to create a directory and give write access to the user running
the proxy. For example:

```bash
sudo mkdir /cloudsql
sudo chown -R $USER /cloudsql
```

Use these terminal commands to initialize other environment variables as well:

```bash
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service/account/key.json'
export INSTANCE_UNIX_SOCKET='/cloudsql/<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>'
export DB_USER='<YOUR_DB_USER_NAME>'
export DB_PASS='<YOUR_DB_PASSWORD>'
export DB_NAME='<YOUR_DB_NAME>'
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.

Then use this command to launch the proxy in the background:

```bash
./cloud-sql-proxy --unix-socket /cloudsql <PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME> &
```

#### Testing the application

Next, setup install the requirements into a virtual environment:

```bash
virtualenv --python python3 env
source env/bin/activate
pip install -r requirements.txt
```

Finally, start the application:

```bash
python app.py
```

Navigate towards `http://127.0.0.1:8080` to verify your application is running correctly.


### Deploy to Cloud Run

See the [Cloud Run documentation](https://cloud.google.com/sql/docs/postgres/connect-run)
for more details on connecting a Cloud Run service to Cloud SQL.

```sh
gcloud run deploy cloud-sql-demo \
  --add-cloudsql-instances '<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>' \
  --set-env-vars INSTANCE_UNIX_SOCKET='/cloudsql/<PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME>' \
  --set-env-vars DB_USER='<YOUR_DB_USER_NAME>' \
  --set-env-vars DB_PASS='<YOUR_DB_PASSWORD>' \
  --set-env-vars DB_NAME='<YOUR_DB_NAME>'
```

Navigate your browser to the URL output at the end of the deployment process
to view the demo app!

It is recommended to use the [Secret Manager integration](https://cloud.google.com/run/docs/configuring/secrets) for Cloud Run instead
of using environment variables for the SQL configuration. The service injects the SQL credentials from
Secret Manager at runtime via an environment variable.

Create secrets via the command line:

```sh
echo -n $INSTANCE_UNIX_SOCKET | \
    gcloud secrets create [INSTANCE_UNIX_SOCKET_SECRET] --data-file=-
```

Deploy the service to Cloud Run specifying the env var name and secret name:

```sh
gcloud run deploy cloud-sql-demo \
  --add-cloudsql-instances <PROJECT_ID>:<INSTANCE_REGION>:<INSTANCE_NAME> \
  --update-secrets INSTANCE_UNIX_SOCKET=[INSTANCE_UNIX_SOCKET_SECRET]:latest,\
    DB_USER=[DB_USER_SECRET]:latest, \
    DB_PASS=[DB_PASS_SECRET]:latest, \
    DB_NAME=[DB_NAME_SECRET]:latest
```

