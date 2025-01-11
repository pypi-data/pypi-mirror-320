import json
from .constants import ResponseStatus
from .helper import MethodResponse


class MethodHandler:

    __db = {}

    @staticmethod
    def __unique_node_id(equipment_id, node_id):
        return f"{equipment_id}-{node_id}"

    @classmethod
    def __get_method_info(cls, equipment_id, node_id, method_name):
        return cls.__db.get(cls.__unique_node_id(equipment_id, node_id)).get(method_name)

    @classmethod
    def add_method(cls, namespace, equipment_id, node_id, method_name, req_payload_schema,
                   res_payload_schema, callback_function):
        unique_node_id = cls.__unique_node_id(equipment_id, node_id)
        if unique_node_id not in cls.__db.keys():
            cls.__db.update({unique_node_id: {}})

        topic_path = f"{namespace}/{equipment_id}/api/v1/{node_id}/methods/req/{method_name}"
        methods = cls.__db.get(unique_node_id)

        method_info = {
            "callback": callback_function,
            "signature": {
                "topicPath": topic_path,
                "requestPayloadSchema": req_payload_schema,
                "responsePayloadSchema": res_payload_schema
            }
        }
        methods.update({method_name: method_info})

    @classmethod
    def get_endpoints(cls, equipment_id, node_id):
        known_methods = cls.__db.get(cls.__unique_node_id(equipment_id, node_id))
        endpoints = []
        if known_methods is not None:
            for method_name in known_methods:
                endpoints.append(known_methods[method_name]["signature"])
        return endpoints

    @classmethod
    def get_method_callback(cls, equipment_id, node_id, method_name):
        callback = cls.__db.get(cls.__unique_node_id(equipment_id, node_id)).get(method_name).get("callback")
        return callback

    @classmethod
    def exec_method_callback(cls, equipment_id, node_id, method_name, payload):
        def response_patch(func):
            def add_status_code(*args, **kwargs):
                resp = func(*args, **kwargs)
                if isinstance(resp, tuple):
                    return {"resp": resp[0], "status_code": resp[1]}
                elif isinstance(resp, MethodResponse):
                    return {"resp": resp.payload, "status_code": resp.response_status}
                else:
                    return {"resp": resp, "status_code": ResponseStatus.OK}

            return add_status_code

        callback = cls.__db.get(cls.__unique_node_id(equipment_id, node_id)).get(method_name).get("callback")
        return response_patch(callback)(payload)

    @classmethod
    def get_method_req_schema(cls, equipment_id, node_id, method_name):
        return cls.__get_method_info(equipment_id, node_id, method_name).get("signature").get("requestPayloadSchema")

    @classmethod
    def get_method_res_schema(cls, equipment_id, node_id, method_name):
        return cls.__get_method_info(equipment_id, node_id, method_name).get("signature").get("responsePayloadSchema")

    @classmethod
    def is_method_registered(cls, equipment_id, node_id, method_name):
        if cls.__get_method_info(equipment_id, node_id, method_name) is None:
            return False
        return True
