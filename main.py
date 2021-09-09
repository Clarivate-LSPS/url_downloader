#! /usr/bin/env python

from collections import deque
from typing import List, Tuple
import requests
from requests.sessions import Session
import configparser
from lxml import html
from pathlib import Path
from tqdm import tqdm


def get_url(config_file: str) -> str:
    """
    Reads URL from config file. 
    Returns a string.
    """
    url_config = configparser.ConfigParser()
    url_config.read(config_file)
    base_url = url_config['url']['base_url']

    return base_url

def validate_url(url: str) -> str:
    """
    Checks a given url for a trailing / and adds if missing, 
    Returns a string. 
    """
    if not url.endswith('/'):
      return url + "/"
    else:
      return url

def get_credentails(config_file: str) -> tuple:
    """
    Reads credentials from config.ini file. 
    Returns tuple of credenitals.
    """
    creds_config = configparser.ConfigParser()
    creds_config.read(config_file)
    user = creds_config['credentials']['username']
    password = creds_config['credentials']['password']

    return user, password


def ensure_dir_exists(directory:str) -> None:
    """
    Ensure that the given directory exists on the system. 
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def split_content(content: List) -> Tuple:
    files = []
    folders = []

    for file in content:
      file = str(file)
      if file.endswith('/'):
        if file != "../":
          folders.append(file)
      else:
        files.append(file)

    return files, folders

def get_page_content(url: str, session: Session) -> str:
    return session.get(url).content

def get_folder_content(url: str, session: Session) -> Tuple:
    """
    Given a URL, 
    Return files and folders as seperate lists 
    """
    page_content = get_page_content(url=url, session=session)
    webpage = html.fromstring(page_content)

    content_list  = webpage.xpath('//a/@href')

    return split_content(content_list)

def get_file_paths(base_url: str ,session: Session) -> List:
    """
    Gathers the file names to be downloaded from the url.
    Returns a list.
    """    

    all_file_paths = []

    root_files, root_folders = get_folder_content(url=base_url, session=session)

    all_file_paths.extend(root_files)

    folders_to_check = deque(root_folders)

    while folders_to_check:
      parent_folder = folders_to_check.popleft()
      sub_files, sub_folders = get_folder_content(url=base_url+ parent_folder, session=session)
      sub_folders = [ parent_folder + folder for folder in sub_folders ]
      sub_files = [ parent_folder + file for file in sub_files ]
      all_file_paths.extend(sub_files)
      folders_to_check.extend(sub_folders)

    return all_file_paths


def download_file(url:str, filepath: str ,session: Session, destination: str = "files/") -> str:
    """
    Downloads file with restricted memory using stream. File chunk size is 10000.
    Returns string of downloaded file. 
    """

    download_dir = destination + filepath
    local_filename = url.split('/')[-1]

    # Ensure download dir(s) exists
    ensure_dir_exists(download_dir)

    with session.get(url, stream=True) as s:
        # Check for HTTP error during download
        s.raise_for_status()
        with open(download_dir + local_filename, 'wb') as f:
            for chunk in s.iter_content(chunk_size=10000):
                f.write(chunk)

    return local_filename

def strip_file_name(base_url: str, full_url) -> str:
    """
    This function takes a base url and a full url and strips down the items to return the path to the file,
    Returns a string of path.
    """
    # Strip filename from path
    filename = full_url.replace(base_url,'')
    path = filename.replace(full_url.split('/')[-1],'')

    return path

def main():

    # Get credentials from file
    user, password = get_credentails("config.ini")

    # Get base url 
    base_url = get_url("config.ini")

    validated_url = validate_url(base_url)

    print(f"Using {validated_url}")

    # Start the session
    session = requests.Session()
    session.auth = (user, password)

    items_list = get_file_paths(base_url=validated_url, session=session)

    print(f"Downloading {len(items_list)} items")
    print("Starting download...")
    for item in tqdm(items_list):
        download_file(url=validated_url+item, filepath=strip_file_name(base_url=validated_url, full_url=item) , session=session)

if __name__ == "__main__":
    exit(main())
