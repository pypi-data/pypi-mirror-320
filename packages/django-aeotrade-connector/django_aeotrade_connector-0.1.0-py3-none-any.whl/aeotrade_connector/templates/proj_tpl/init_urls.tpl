
from django.urls import re_path
from .dispatcher import (task_account_check, task_create, task_start,
                         task_stop, task_update_or_delete)

urlpatterns += [
    path("org-connectors-accounts/check", task_account_check, name="账号校验"),
    re_path(r"org-connectors-tasks$", task_create, name="新增任务"),
    re_path(r"org-connectors-tasks/(?P<task_id>\w+)$", task_update_or_delete, name="更新/删除任务"),
    re_path(r"org-connectors-tasks/(?P<task_id>\w+)/start$", task_start, name="启动任务"),
    re_path(r"org-connectors-tasks/(?P<task_id>\w+)/stop$", task_stop, name="暂停任务"),
]
