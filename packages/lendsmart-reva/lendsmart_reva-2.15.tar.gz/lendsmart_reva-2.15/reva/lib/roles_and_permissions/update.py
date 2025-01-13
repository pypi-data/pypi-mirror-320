"""
    update the roles and permissions
"""
from ramda import path_or
from reva.lib.utils.get_namespaces import get_namespace_by_argument_and_path
from reva.lib.base.base import RevaUpdate
from reva.lib.utils.filter_data_with_id import filter_data_with_id
from reva.lib.graphql_queries.roles_and_permissions import (
    upsert_roles_query, upsert_permissions_query
)

class RolesAndPermissionUpdate(RevaUpdate):
    """
    update the roles and permissions
    """

    def __init__(self, arguments):
        super().__init__(arguments)
        self.argument = arguments

    def get_json_paths_to_update(self, prefixes = ["ROL_", "PRM_"]):
        """
        THis function will return the json files
        to update
        """
        namespaces_to_update = get_namespace_by_argument_and_path(
            self.argument, self.get_ui_customization_path()
        )
        return self.get_file_paths_ui(
            namespaces=namespaces_to_update,
            prefixes=prefixes,
            env=self.argument.env
        )

    def __update(self, data_list : list, query):
        query_datas = []
        for json_data in data_list:
            filtered_json_data = filter_data_with_id(path_or([],["json_data","data"], json_data))
            if not filtered_json_data:
                continue
            query_datas.append(
                query(
                    filtered_json_data
                )
            )
        return self.excecute_for_list_of_query_data(query_datas)

    def start(self):
        """
        update the roles and permissions
        """
        roles_json_data = self.get_json_files_by_path(
            self.get_json_paths_to_update(prefixes=["ROL_"])
        )
        permissions_json_data = self.get_json_files_by_path(
            self.get_json_paths_to_update(prefixes=["PRM_"])
        )
        self.__update(roles_json_data, upsert_roles_query)
        self.__update(permissions_json_data, upsert_permissions_query)
