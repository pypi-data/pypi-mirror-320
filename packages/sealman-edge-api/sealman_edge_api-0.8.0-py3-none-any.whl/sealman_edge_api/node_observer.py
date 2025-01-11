from .constants import ConnectionState


class NodeObserver:

    __db = {}
    __api = None

    @classmethod
    def set_api_ref(cls, api):
        cls.__api = api

    @classmethod
    def update_node_id_status(cls, equipment_id, node_id, status):
        if equipment_id not in cls.__db:
            cls.__db[equipment_id] = {}
        if node_id not in cls.__db[equipment_id]:
            cls.__db[equipment_id][node_id] = {"status": status}
        else:
            cls.__db[equipment_id][node_id]["status"] = status

        # emit event
        if cls.__api._on_update_connection_status is not None:
            cls.__api._on_update_connection_status(cls.__api, equipment_id, node_id, status)

    @classmethod
    def update_node_id_endpoints(cls, equipment_id, node_id, endpoints):
        if equipment_id not in cls.__db:
            cls.__db[equipment_id] = {}
        if node_id not in cls.__db[equipment_id]:
            cls.__db[equipment_id][node_id] = {"endpoints": endpoints}
        else:
            cls.__db[equipment_id][node_id]["endpoints"] = endpoints

        # emit event
        if cls.__api._on_update_endpoints is not None:
            cls.__api._on_update_endpoints(cls.__api, equipment_id, node_id, endpoints)

    @classmethod
    def get_online_nodes(cls):
        online_nodes = {}
        online_equipments = {}
        for equipment_id in cls.__db:
            for node_id in cls.__db.get(equipment_id):
                if cls.__db.get(equipment_id).get(node_id)["status"] == ConnectionState.ONLINE:
                    online_nodes.update({node_id: cls.__db.get(equipment_id).get(node_id)})
            if len(online_nodes.keys()) > 0:
                online_equipments[equipment_id] = online_nodes
        return online_equipments

    @classmethod
    def get_offline_nodes(cls):
        offline_nodes = {}
        offline_equipments = {}
        for equipment_id in cls.__db:
            for node_id in cls.__db.get(equipment_id):
                if cls.__db.get(equipment_id).get(node_id)["status"] == ConnectionState.OFFLINE:
                    offline_nodes.update({node_id: cls.__db.get(equipment_id).get(node_id)})
            if len(offline_nodes.keys()) > 0:
                offline_equipments[equipment_id] = offline_nodes
        return offline_equipments

    @classmethod
    def get_all_nodes(cls):
        return cls.__db
