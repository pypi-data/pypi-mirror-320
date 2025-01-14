from rest_framework.decorators import api_view

from aeotrade_connector.exceptions import InvalidConnectorCode
from aeotrade_connector.helpers import (connector_code_mapping,
                                        connector_views_mapping)
from aeotrade_connector.serializers import ConnectorCodeSerializer
from aeotrade_connector.utils import APIResponse, check_request

conn_codes = connector_code_mapping()
conn_views = connector_views_mapping()


def dispatch_views_module(request):
    req_data = check_request(request, ConnectorCodeSerializer)
    connector_name = conn_codes.get(req_data["connector_code"])
    connector_view = conn_views.get(connector_name)
    if connector_view is None:
        raise InvalidConnectorCode
    return connector_view


@api_view(["POST"])
def task_account_check(request):
    return dispatch_views_module(request).task_account_check(request._request)


@api_view(["POST"])
def task_create(request):
    return dispatch_views_module(request).task_create(request._request)


@api_view(["POST"])
def task_start(request, task_id):
    return dispatch_views_module(request).task_start(request._request, task_id)


@api_view(["POST"])
def task_stop(request, task_id):
    return dispatch_views_module(request).task_stop(request._request, task_id)


def task_delete(request, task_id):
    return dispatch_views_module(request).task_delete(request._request, task_id)


def task_update(request, task_id):
    return dispatch_views_module(request).task_update(request._request, task_id)


@api_view(["POST", "DELETE"])
def task_update_or_delete(request, task_id):
    connector_view = dispatch_views_module(request)
    if request.method == "POST":
        return connector_view.task_update(request._request, task_id)
    return connector_view.task_delete(request._request, task_id)
