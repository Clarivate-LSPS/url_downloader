# URL File Downloader

This tool will download the files in a given URL. It will download all files and subfolders from a given url and output to `files/` path.

For example, setting the url to `https://example.com` will download all files in that url, whereas if the url is `https://example.com/files` will only download files and folders found in the `files` path.

## Setup

In order to use this tool, you will need to install the dependancies via pip. This can be done with the following:

```bash
pip install -r requirements.txt
```

## Config

This tool uses a config file to set some parameters for usage. This file should be saved as `config.ini`

```txt
username - Username to authenticate with site
password - Password to authenticate with site

base_url - URL to download from
```

## Usage

In order to run this tool, set up the `config.ini` with the desired values and run:

```bash
python3 main.py
```
