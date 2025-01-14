# Overview

Django Aeotrade Connector is a framework that allows you to easily create your `connector`
with [Aeotrade OS](https://www.aeotrade.com/portal).

# Quickstart

## Install

```bash
pip install django-aeotrade-connector
```
After installing the package, you can add `aeotrade_connector` to `INSTALLED_APPS`

## Usage

### Initialize connector in django project

```bash
python manage.py initconnector
```

This will create `urls.py` and `dispatcher.py` to your project

### Create connector

```bash
python manage.py startconnector <my_connector>
```

After executing this command, you can add `my_connector` to `INSTALLED_APPS`. Then you can see a new django app named
`my_connector` in your project.
In this app, you can see `services.py` and `task.py` files. In `services.py`, you must implement some connector methods,
which are inherited from `ConnectorServices`. and in `task.py`, you can define your connector tasks. those tasks will be
registered when django setup.

### Configuration

In `app.py`:

Before you start to run your connector, you must configure your connector in the `app.py` file. The configuration file
is located in the `my_connector/app.py` file.

```Python
class MyConnectorConfig(AppConfig):
    name = 'my_connector'

    class Config:
        # required config
        connector = True
        connector_config_model = ConnectorBaseConfig(
            # required config
            label="my_first_connector",
            code="my_first_connector_code",
            mq_recv_model=MQManagerConfig(
                url="amqp://root:123456@localhost:5672/",
                exchange="test",
                queue="q_receive",
                pot=POT.Thread
            ),
            # optional config
            event_up_chain = True,
            files_up_chain = False,
            callback = some_function_name,
            callback_args = ['arg1', 'arg2'],
            callback_kwargs = {'key1': 'value1', 'key2': 'value2'},
            task_stop_when_error = False,
            auto_heartbeat = True,
            kw = {"extra_key": "extra_value"},
        )


```

In django.settings.py:

```Python
INSTALLED_APPS = [
    ...,
    'aeotrade_connector'
    'my_connector',
]

AC_MANAGEMENT_ENDPOINT = 'https://www.example.com:8000'

IS_TEST = False  # or True

# Redis Cache
CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 'redis://localhost:6379/0',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
        }
    }
}
```
