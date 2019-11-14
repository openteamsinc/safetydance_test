import llstep_test.http as http
import pytest
from llstep_test import Given, When, Then, And, test


@test
def test_get():
    When.http.get("http://localhost:8080/")
    Then.http.status_is(404)
