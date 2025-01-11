import json
import logging
import time
import enum
import threading
import pkgutil
import jsonschema
from .exceptions import APIError
from .constants import ResponseStatus


runner_pool = {}


def connected(func):
    def wrapper(*args, **kwargs):
        log = logging.getLogger("ConnectionCheck")
        wait_interation = 10

        if not args[0]._mqtt_client.is_connected():
            for cnt in range(wait_interation):
                time.sleep(0.2)
                if not args[0]._mqtt_client.is_connected():
                    log.info(f"wait for mqtt-connection... [attempt {cnt} of {wait_interation}]")
                else:
                    break
                raise APIError("api is not connected to any mqtt-broker")

        return func(*args, **kwargs)
    return wrapper


class JSONSchema:

    __cache = {}

    @classmethod
    def validate(cls, json_data, schema):
        if isinstance(schema, str):
            if schema not in cls.__cache:
                resource_data = pkgutil.get_data(__name__, f"schemas/{schema}.json").decode("utf-8")
                cls.__cache[schema] = json.loads(resource_data)
            schema = cls.__cache.get(schema)

        jsonschema.validate(json_data, schema)


class ResponseMessage:

    def __init__(self, message, response_status):
        # translate status code into enum string
        if isinstance(response_status, int):
            for _enum in list(ResponseStatus):
                if _enum.value == response_status:
                    response_status = ResponseStatus[_enum.name].name
        # pass string for validation check
        elif isinstance(response_status, str):
            response_status = response_status
        # translate enum in to string
        elif isinstance(response_status, enum.Enum):
            response_status = response_status.name

        # convert to dict if message is a string
        if isinstance(message, str):
            try:
                message = json.loads(message)
            except:
                message = {"message": message}

        # convert a none value to a json response
        #if message is None:
        #    message = {"message": None}

        self.__resp = {
                "responseStatus": response_status,
                "payload": message
            }

    def make(self):
        JSONSchema.validate(self.__resp, "response")
        return json.dumps(self.__resp)


class KeepAlive(threading.Thread):

    def __init__(self, daemon=False):
        threading.Thread.__init__(self)
        self.daemon = daemon
        self.__terminate = False
        self.__was_started_once = False

    def set_active(self):
        if not self.__was_started_once:
            self.start()

    def run(self):
        self.__was_started_once = True
        while not self.__terminate:
            time.sleep(1)

    def terminate(self):
        self.__terminate = True

    def is_terminating(self):
        return self.__terminate


class MethodResponse:

    def __init__(self, payload, response_status: ResponseStatus):
        self.payload = payload
        self.response_status = response_status
