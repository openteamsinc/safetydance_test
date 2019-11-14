from collections import OrderedDict
from copy import deepcopy
from llstep import step, step_data, Context # FIXME shouldn't need to import Context
from llstep_test import TestStepPrefix
from llstep_test.step_extension import step_extension
from rest_framework.test import APIClient
from type_extension import extension
import pytest


class Http:
    '''
    Context and steps for interacting with HTTP web services.
    '''
    ...


_HTTP = Http()

@property
@extension
def http(self: TestStepPrefix) -> Http:
    return _HTTP


http_client = step_data(APIClient)
http_response = step_data(None)


@step_extension
def http_client(self: Http) -> APIClient:
    if http_client not in context:
        http_client = APIClient()
    return http_client

@step_extension
def with_defaults(self: Http, **kwargs):
    http_client().defaults = {**http_client().defaults, **kwargs}

@step_extension
def force_authenticate(self: Http, *args, **kwargs):
    """Can be used by rest_framework.test.APIClient"""
    http_client().force_authenticate(*args, **kwargs)

@step_extension
def force_login(self: Http, *args, **kwargs):
    """Can be used by django.test.Client"""
    http_client().force_login(*args, **kwargs)

@step_extension
def login(self: Http, *args, **kwargs):
    http_client().login(*args, **kwargs)

@step_extension
def delete(self: Http, *args, **kwargs):
    '''Perform HTTP DELETE'''
    http_response = http_client().delete(*args, **kwargs)

@step_extension
def get(self: Http, *args, **kwargs):
    '''Perform HTTP GET'''
    http_response = http_client().get(*args, **kwargs)

@step_extension
def post(self: Http, *args, **kwargs):
    http_response = http_client().post(*args, **kwargs)

@step_extension
def put(self: Http, *args, **kwargs):
    http_response = http_client().put(*args, **kwargs)

@step_extension
def status_code_is(self: Http, expected):
    '''
    Check that the expected status code matches the received status code
    '''
    assert http_response.status_code == expected

@step_extension
def content_type_is(self: Http, expected):
    assert 'Content-Type' in http_response
    assert http_response['Content-Type'].startswith(expected)

@step_extension
def response_json_is(self: Http, expected):
    '''
    Check that the expected response json body matches the received response
    body.
    '''
    self.content_type_is('application/json')
    observed = http_response.json()
    assert json_values_match(expected, observed)

@step_extension
def response_data_is(self: Http, expected, excluded_fields=None):
    '''
    Check that the expected response json body matches the received response
    body.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj

    self.content_type_is('application/json')

    observed = clean_item(deepcopy(http_response.data))
    expected = clean_item(deepcopy(expected))
    assert expected == observed

@step_extension
def assert_data(self: Http, expected, observed, excluded_fields=None):
    '''
    Check that the expected response json body matches the received response
    body.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj

    observed = clean_item(deepcopy(observed))
    expected = clean_item(deepcopy(expected))
    assert expected == observed

@step_extension
def response_data_list_is(self: Http, list_expected, excluded_fields=None):
    '''
    Check that the expected response json body matches the received response
    body.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj
    self.content_type_is('application/json')

    _list_observed = deepcopy(http_response.data)
    list_expected = deepcopy(list_expected)

    list_observed = []

    is_enveloped = None

    for item in _list_observed:
        if is_enveloped is None:
            if 'etag' in item:
                is_enveloped = True
            else:
                is_enveloped = False
        if is_enveloped:
            item = item['content']
        elif isinstance(item, OrderedDict):
            item = dict(item)

        list_observed.append(clean_item(item))

    for i, item in enumerate(list_expected):
        list_expected[i] = clean_item(item)

    assert list_expected == list_observed

@step_extension
def response_url_is(self: Http, url_expected):
    assert http_response.url == url_expected

@step_extension
def response_location_header_is(self: Http, location_expected):
    header = http_response['location']
    assert header == location_expected


def json_values_match(expected, observed):
    '''
    Recursively walk the expected json value validating that the observed json
    value matches. Returns False on any missing or mismatched value.
    '''
    if isinstance(expected, list):
        return lists_match(expected, observed)
    if isinstance(expected, dict):
        return dictionaries_match(expected, observed)
    return expected == observed


def lists_match(expected, observed):
    '''
    Recursively walk the expected list validating that the observed list
    matches. Returns False on any missing or mismatched value.
    '''
    if not isinstance(observed, list):
        return False
    if len(expected) != len(observed):
        return False
    for i in range(0, len(expected)):
        if not json_values_match(expected[i], observed[i]):
            return False
    return True


def dictionaries_match(expected, observed):
    '''
    Recursively walk the expected dictionary validating that the observed
    dictionary matches. Returns False on any missing key or mismatched
    value.

    Note that keys that occur in observed or its nested dictionary objects
    that don't occur in expected or its matching nested dictionary objects
    are ignored.
    '''
    if observed is None:
        return False
    for key, value in expected.items():
        if not json_values_match(value, observed.get(key)):
            return False
    return True


@pytest.fixture(scope='function')
def http_api_client():
    '''A Django test HTTP client'''
    return APIClient()
