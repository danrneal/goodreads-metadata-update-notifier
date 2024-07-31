# Goodreads Metadata Update Notifier

A script that compares the metadata of epubs in a Calibre library to the metadata on Goodreads and then emails any differences.

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

Create a gmail app password using [these instructions](https://support.google.com/accounts/answer/185833?hl=en)

Set up your environment variables:

```bash
touch .env
echo export CALIBRE_LIBRARY="/home/XXX/Calibre Library" >> .env
echo export EMAIL="XXX@gmail.com" >> .env
echo export EMAIL_PASSWORD="XXX" >> .env
echo export SMTP="smtp.gmail.com:587" >> .env
```

## Usage

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

Make sure .env variables are set:

```bash
set -a; source .env; set +a
```

Then run the script:

```bash
Usage: compare.py
```

## License

Goodreads Metadata Update Notifier is licensed under the [MIT license](https://github.com/danrneal/goodreads-metadata-update-notifier/blob/master/LICENSE).

