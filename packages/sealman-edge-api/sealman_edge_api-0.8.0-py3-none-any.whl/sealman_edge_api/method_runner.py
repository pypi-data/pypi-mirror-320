import logging
import threading
import uuid
import json
import time


class MethodRunner(threading.Thread):

    def __init__(self, cli, namespace, equipment_id, api_version, node_id, method_name, payload, timeout):
        threading.Thread.__init__(self)
        self._log = logging.getLogger(self.__class__.__name__)
        self.daemon = True
        self.cli = cli
        self.namespace = namespace
        self.equipment_id = equipment_id
        self.api_version = api_version
        self.node_id = node_id
        self.method_name = method_name
        self.payload = payload
        self.timeout = timeout
        self.transaction_id = str(uuid.uuid4())
        self.resp = None

    def run(self):
        self._log.info(f"call method: {self.equipment_id}->{self.node_id}->{self.method_name} "
                       f"[transactionId: {self.transaction_id}")

        response_topic = (f"{self.namespace}/{self.equipment_id}/api/{self.api_version}/{self.node_id}/methods/res/"
                          f"{self.method_name}/{self.transaction_id}")
        self.cli.subscribe(response_topic)

        request_topic = (f"{self.namespace}/{self.equipment_id}/api/{self.api_version}/{self.node_id}/methods/req/"
                         f"{self.method_name}/{self.transaction_id}")
        request_payload = {
            "nodeId": self.node_id,
            "responseTopic": response_topic,
            "transactionUuid": self.transaction_id,
            "timeout": self.timeout,
            "schemaVersion": "1.0",
            "payload": self.payload
        }
        self.cli.publish(request_topic, json.dumps(request_payload))

        while self.resp is None:
            time.sleep(0.1)

        self.cli.unsubscribe(response_topic)
