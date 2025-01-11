import logging
import re
import json
import jsonschema
from .helper import runner_pool, ResponseMessage, ResponseStatus, JSONSchema
from .node_observer import NodeObserver
from .method_handler import MethodHandler


class MessageHandler:

    _log = logging.getLogger("MessageHandler")

    @classmethod
    def handle(cls, client, ud, msg):
        cls._log.debug(f"Received message on topic: {msg.topic}")
        msg_payload = cls._parse_payload(msg)
        if msg_payload is None:
            return

        topic_handlers = [
            (r"^(.+)/(.+)/api/([vV][1-9]{1,2})/(.+)/methods/(req)?(res)?/(.+)/(.+)$", cls._process_method),
            (r"^(.+)/(.+)/api/([vV][1-9]{1,2})/(.+)/communicationStatus$", cls._process_communication_status),
            (r"^(.+)/(.+)/api/([vV][1-9]{1,2})/(.+)/endpoints$", cls._process_endpoint_update),
        ]

        for pattern, handler in topic_handlers:
            match = re.match(pattern, msg.topic)
            if match:
                handler(client, match, msg_payload)
                break

    @classmethod
    def _parse_payload(cls, msg):
        try:
            return json.loads(msg.payload)
        except json.JSONDecodeError:
            cls._log.error(f"Invalid payload [{msg.payload}] on topic [{msg.topic}]: needs to be a JSON object")
            return None

    @classmethod
    def _process_method(cls, client, match, msg_payload):
        namespace, equipment_id, _, node_id, method_req, method_res, method_name, transaction_id = match.groups()

        if method_res:
            cls._handle_method_response(transaction_id, msg_payload)
        elif method_req:
            cls._handle_method_request(client, namespace, equipment_id, node_id, method_name, transaction_id, msg_payload)

    @classmethod
    def _handle_method_response(cls, transaction_id, msg_payload):
        cls._log.info(f"Received method response [transactionId: {transaction_id}]")
        runner_pool.pop(transaction_id).resp = msg_payload

    @classmethod
    def _handle_method_request(cls, client, namespace, equipment_id, node_id, method_name, transaction_id, msg_payload):
        cls._log.info(f"Processing method request: {equipment_id}->{node_id}->{method_name} [transactionId: {transaction_id}]")

        if not cls._validate_request(client, namespace, equipment_id, node_id, method_name, transaction_id, msg_payload):
            return

        response_topic = msg_payload.get("responseTopic")
        try:
            resp = MethodHandler.exec_method_callback(equipment_id, node_id, method_name, msg_payload.get("payload"))
            cls._send_response(client, response_topic, resp, equipment_id, node_id, method_name, transaction_id)
        except Exception as err:
            cls._log.error(f"Error during method execution: {str(err)}")
            cls._send_error(client, response_topic, ResponseStatus.INTERNAL_SERVER_ERROR, transaction_id, str(err))

    @classmethod
    def _validate_request(cls, client, namespace, equipment_id, node_id, method_name, transaction_id, msg_payload):
        try:
            JSONSchema.validate(msg_payload, "method_req")
        except jsonschema.ValidationError as err:
            cls._send_error(client, f"{namespace}/{equipment_id}/api/v1/{node_id}/methods/res/{method_name}/{transaction_id}", ResponseStatus.BAD_REQUEST, transaction_id, str(err))
            return False

        if not MethodHandler.is_method_registered(equipment_id, node_id, method_name):
            cls._send_error(client, msg_payload.get("responseTopic"), ResponseStatus.NOT_FOUND, transaction_id, "Unknown method")
            return False

        req_schema = MethodHandler.get_method_req_schema(equipment_id, node_id, method_name)
        if req_schema:
            try:
                JSONSchema.validate(msg_payload.get("payload"), req_schema)
            except jsonschema.ValidationError as err:
                cls._send_error(client, msg_payload.get("responseTopic"), ResponseStatus.BAD_REQUEST, transaction_id, str(err))
                return False

        return True

    @classmethod
    def _send_response(cls, client, topic, response, equipment_id, node_id, method_name, transaction_id):
        res_schema = MethodHandler.get_method_res_schema(equipment_id, node_id, method_name)
        try:
            if res_schema:
                JSONSchema.validate(response.get("resp"), res_schema)
            client.publish(topic, ResponseMessage(response.get("resp"), response.get("status_code")).make())
        except jsonschema.ValidationError as err:
            cls._send_error(client, topic, ResponseStatus.CONFLICT, transaction_id, str(err))

    @classmethod
    def _send_error(cls, client, topic, status, transaction_id, error_message):
        cls._log.warning(f"Error: {error_message}")
        client.publish(topic, ResponseMessage(error_message, status).make())

    @classmethod
    def _process_communication_status(cls, client, match, msg_payload):
        _, equipment_id, _, node_id = match.groups()
        state = msg_payload.get("payload", {}).get("state")
        cls._log.info(f"Communication status update: {equipment_id}->{node_id}: {state}")
        NodeObserver.update_node_id_status(equipment_id, node_id, state)

    @classmethod
    def _process_endpoint_update(cls, client, match, msg_payload):
        _, equipment_id, _, node_id = match.groups()
        NodeObserver.update_node_id_endpoints(equipment_id, node_id, msg_payload.get("payload"))
