import uuid
import logging
import time
import threading
from paho.mqtt.client import Client as MQTTClient
from .exceptions import APIError
from .message_handler import MessageHandler
from .method_handler import MethodHandler
from .method_runner import MethodRunner
from .node_observer import NodeObserver
from .constants import MQTTConnectionInfo, ConnectionState, ResponseStatus, ApiConnectionState
from .helper import ResponseMessage, runner_pool, connected, KeepAlive


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


class SealmanEdgeAPI:

    __instance = None

    def __init__(self, namespace: str, equipment_id: str, node_id: str,
                 mqtt_client: MQTTClient or None = None, daemon: bool = False):
        SealmanEdgeAPI.__instance = self
        self._log = logging.getLogger(self.__class__.__name__)
        if mqtt_client is None:
            mqtt_client = MQTTClient(str(uuid.uuid4()), clean_session=True)
        if not isinstance(mqtt_client, MQTTClient):
            raise APIError(f"only paho-mqtt is supported -> try: pip install paho-mqtt")
        self._namespace = namespace
        self._equipment_id = equipment_id
        self._api_version = "v1"
        self._node_id = node_id
        self._mqtt_client = mqtt_client
        self._mqtt_client.on_connect = self.__on_connect
        self._mqtt_client.on_message = MessageHandler.handle
        self._mqtt_client.on_disconnect = self.__on_disconnect
        self.__keepalive = KeepAlive(daemon)
        self.__api_conn_state = ApiConnectionState.NEVER_CONNECTED
        # link event emitters
        NodeObserver.set_api_ref(self)
        self._callback_mutex = threading.RLock()
        self._on_update_endpoints = None
        self._on_update_connection_status = None

    @property
    def on_update_connection_status(self):
        return self._on_update_connection_status

    @on_update_connection_status.setter
    def on_update_connection_status(self, func):
        with self._callback_mutex:
            self._on_update_connection_status = func

    @property
    def on_update_endpoints(self):
        return self._on_update_endpoints

    @on_update_endpoints.setter
    def on_update_endpoints(self, func):
        with self._callback_mutex:
            self._on_update_endpoints = func

    @staticmethod
    def method(req, res):

        def decorator(func):
            api = SealmanEdgeAPI.__instance
            api.register_method(func.__name__, req, res, func)

            def wrapper(*args, **kwargs):
                result, status_code = func(req, res, *args, **kwargs)
                return result

            return wrapper

        return decorator

    def connection_state(self):
        return self.__api_conn_state

    def connect(self, host, port=1883):
        self._log.info(f"connect API to: {host}:{port}")
        self.__api_conn_state = ApiConnectionState.CONNECTING
        self.__setup_connection_state()
        self.__keepalive.set_active()

        try:
            self._mqtt_client.connect(host, port)
            self._mqtt_client.loop_start()
        except ConnectionRefusedError or ConnectionError as ex:
            raise APIError(f"could not connect to [{host}:{port}] -> {str(ex)}")

        # block method until mqtt broker answers in __on_connect
        while self.__api_conn_state == ApiConnectionState.CONNECTING:
            time.sleep(0.1)
        return self.__api_conn_state

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._log.info(MQTTConnectionInfo[rc])
            self.__subscribe_method_requests()
            self.__subscribe_communication_status()
            self.__subscribe_endpoint_info()
            self.__api_conn_state = ApiConnectionState.CONNECTED
            self.__update_connection_state(ConnectionState.ONLINE)
            self.__update_endpoints()
        else:
            self.__api_conn_state = ApiConnectionState.DISCONNECTED
            raise APIError(f"could not connect mqtt-broker: {MQTTConnectionInfo[rc]}")

    def disconnect(self):
        self._log.info("start disconnect api by user")
        self.__api_conn_state = ApiConnectionState.DISCONNECTING
        self.__update_connection_state(ConnectionState.OFFLINE)
        self.__keepalive.terminate()
        self._mqtt_client.disconnect()
        while self.__api_conn_state not in (ApiConnectionState.DISCONNECTED, ApiConnectionState.NEVER_CONNECTED):
            time.sleep(0.1)
        self._log.info("api state: disconnected")

    def __on_disconnect(self, client, userdata, rc):
        self._log.info(f"api disconnected from broker rc[{rc}]")
        self.__api_conn_state = ApiConnectionState.DISCONNECTED
        if not self.__keepalive.is_terminating():
            self._log.warning("enter reconnect...")

    def __subscribe_method_requests(self):
        topic = f"{self._namespace}/{self._equipment_id}/api/{self._api_version}/{self._node_id}/methods/req/#"
        self._mqtt_client.subscribe(topic)
        self._log.info(f"listen for method requests on: {topic}")

    def __subscribe_communication_status(self):
        topic = f"{self._namespace}/+/api/v1/+/communicationStatus"
        self._mqtt_client.subscribe(topic)
        self._log.info(f"listen for communication-state change on: {topic}")

    def __subscribe_endpoint_info(self):
        topic = f"{self._namespace}/+/api/v1/+/endpoints"
        self._mqtt_client.subscribe(topic)
        self._log.info(f"listen for endpoint change on: {topic}")

    def __setup_connection_state(self):
        message = {
            "nodeId": self._node_id,
            "equipmentId": self._equipment_id,
            "state": ConnectionState.OFFLINE
        }
        self._mqtt_client.will_set(
            f"{self._namespace}/{self._equipment_id}/api/{self._api_version}/{self._node_id}/communicationStatus",
            payload=ResponseMessage(message, ResponseStatus.OK).make(), retain=True
        )

    def __update_connection_state(self, connection_state):
        self._log.info("update connection state")
        message = {
            "nodeId": self._node_id,
            "equipmentId": self._equipment_id,
            "state": connection_state
        }
        self._mqtt_client.publish(
            f"{self._namespace}/{self._equipment_id}/api/{self._api_version}/{self._node_id}/communicationStatus",
            payload=ResponseMessage(message, ResponseStatus.OK).make(),
            retain=True
        )

    def __update_endpoints(self):
        self._log.info("update endpoints")
        endpoints = MethodHandler.get_endpoints(self._equipment_id, self._node_id)
        self._mqtt_client.publish(
            f"{self._namespace}/{self._equipment_id}/api/{self._api_version}/{self._node_id}/endpoints",
            payload=ResponseMessage(endpoints, ResponseStatus.OK).make(),
            retain=True
        )

    @connected
    def register_method(self, method_name, req_payload_schema, res_payload_schema, callback_function):
        self._log.info(f"register method: {method_name}")
        MethodHandler.add_method(
            self._namespace,
            self._equipment_id,
            self._node_id, method_name,
            req_payload_schema,
            res_payload_schema,
            callback_function
        )
        self.__update_endpoints()

    @connected
    def call_method(self, equipment_id, node_id, method_name, method_payload, timeout=5.0):
        m_runner = MethodRunner(
            self._mqtt_client,
            self._namespace,
            equipment_id,
            self._api_version,
            node_id,
            method_name,
            method_payload,
            timeout
        )
        runner_pool.update({m_runner.transaction_id: m_runner})
        m_runner.start()
        m_runner.join(timeout=timeout)
        if m_runner.is_alive():
            raise TimeoutError(f"timeout for method: {m_runner.method_name} "
                               f"[transaction-id: {m_runner.transaction_id}]")
        return m_runner.resp

    @connected
    def show_nodes(self, node_filter: None or str = None):
        if node_filter is None:
            return NodeObserver.get_all_nodes()
        elif node_filter.lower() == "online":
            return NodeObserver.get_online_nodes()
        elif node_filter.lower() == "offline":
            return NodeObserver.get_offline_nodes()
        else:
            raise APIError(f"unknown filter: {node_filter} -> use [ None | online | offline ]")
