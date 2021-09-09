import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import pytest
from main import split_content, get_file_paths, main
from requests import Session
from pathlib import Path
from pytest_mock import MockerFixture


BASE_URL = "http://mock.com/"

@pytest.mark.parametrize(
  "content_list, expected_files, expected_folders",
  [
    (
      ["my_file", "my_folder/", "tmp/", "test_file"],
      ["my_file", "test_file"],
      ["my_folder/", "tmp/"]
    ),
    (
      ["my_file", "my_folder/", "tmp/", "test_file", "../"],
      ["my_file", "test_file"],
      ["my_folder/", "tmp/"]
    ),   
    (
      [],
      [],
      []
    ),
    (
      ["../"],
      [],
      [] 
    ),   
    (
      [1, "test_file", 3, 20202, "tmp/", "223231/"],
      ["1", "test_file", "3", "20202" ],
      ["tmp/", "223231/"]
    )
  ]
)
def test_split_content(content_list, expected_files, expected_folders):
  files, folders = split_content(content_list)

  assert files == expected_files
  assert folders == expected_folders


def get_page_content_mock(url: str, session: Session) -> str:

    if url == BASE_URL:
      file = Path(__file__).parent / "fixtures" / "base_url.html"
      with open(file, mode="r") as f:
          return f.read()
    elif url == BASE_URL + "Data/":
      file = Path(__file__).parent / "fixtures" / "data.html"
      with open(file, mode="r") as f:
          return f.read()

def test_get_filenames(mocker: MockerFixture):
    mocker.patch("main.get_page_content", get_page_content_mock)
    expected_item_list = ["my_file", "Data/my_file_data"]

    test_item_list = get_file_paths(base_url=BASE_URL, session=None)

    assert set(test_item_list) == set(expected_item_list)


def test_main(mocker: MockerFixture):
    mocker.patch("main.get_page_content", get_page_content_mock)
    mocker.patch("main.get_url", return_value=BASE_URL)

    download_file_stub = mocker.patch("main.download_file")

    main()

    assert 2 == download_file_stub.call_count