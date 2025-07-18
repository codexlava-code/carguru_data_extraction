import pytest

# Navigation callback function
from apps.back_end.utils.nav_callback import display_page


@pytest.fixture()  # allow for re-use of setup and teardown code across tests.
def nav_url():
    """_navigation page url (setup test)_

    Returns:
        _url_: _return page url address_
    """
    url_address = "/login"
    nav_url = display_page(
        url_address
    )  # navigation function called to get the url path
    return nav_url


@pytest.fixture
def nav_data_url():
    """_getting page url address (action test)_

    Returns:
        _url_: _url address returned_
    """
    url_address = "/login"
    return url_address


def test_lgn_field_check(nav_url):
    """_test feedback link data (assertion test)_

    Args:
        nav_data_url (_string_): _check return data with assertion_
    """
    # assert statement for performing varifications unit test.
    assert nav_url == "/login"
