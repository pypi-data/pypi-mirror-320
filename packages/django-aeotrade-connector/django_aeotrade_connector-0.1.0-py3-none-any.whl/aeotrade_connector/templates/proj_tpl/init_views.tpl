
from aeotrade_connector.exceptions import MethodNotAllowedException
from aeotrade_connector.helpers import connector_mapping

connectors = connector_mapping()


class ConnectorDispatcher:

    @classmethod
    def connector_account_check(cls, request):
        method = request.method
        if method != "POST":
            raise MethodNotAllowedException

        connector_code = connectors.get()

    @classmethod
    def task_create(cls, request):
        method = request.method
        if method != "POST":
            raise MethodNotAllowedException

    @classmethod
    def task_start(cls, request):
        method = request.method
        if method != "POST":
            raise MethodNotAllowedException

    @classmethod
    def task_stop(cls, request):
        method = request.method
        if method != "POST":
            raise MethodNotAllowedException

    @classmethod
    def task_delete(cls, request, task_id):
        pass

    @classmethod
    def task_update(cls, request, task_id):
        pass

    @classmethod
    def task_update_or_delete(cls, request, task_id):
        if request.method == "POST":
            return cls.task_update(request, task_id)
        elif request.method == "DELETE":
            return cls.task_delete(request, task_id)
        else:
            raise MethodNotAllowedException
