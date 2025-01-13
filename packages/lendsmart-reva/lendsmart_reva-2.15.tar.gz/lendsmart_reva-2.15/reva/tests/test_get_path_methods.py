# pylint: disable=all
import os
from dataclasses import dataclass
import pytest
from reva.lib.branch.create import BranchCreate
from reva.lib.advisor_profile.create import AdvisorProfileCreate
from reva.lib.document_access_control.update import DocumentAccessControlUpdate
from reva.lib.loan_productus.update import LoanProductsUpdate
from reva.lib.roles_and_permissions.update import RolesAndPermissionUpdate
from reva.lib.workflow.update import WorkflowUpdate


os.environ['LENDSMART_REVA_HOME'] = "/home/dipsy"
os.environ['LENDSMART_REVA_UI_HOME'] = "/home/dipsy/code/ui"
os.environ['LENDSMART_REVA_WORKLET_HOME'] = "/home/dipsy/code/worklet"

@dataclass
class MockArgs:
    env: str = "dev"
    namespace: str = ""

@pytest.mark.parametrize(
    "classs, type",
    [
        (BranchCreate, "create"),
        (AdvisorProfileCreate, "create"),
        (DocumentAccessControlUpdate, "update"),
        (LoanProductsUpdate, "update"),
        (RolesAndPermissionUpdate, "update"),
        (WorkflowUpdate, "update"),
    ]
)
def test_get_path_method(classs, type):
    dev_obj = classs(arguments=MockArgs(env="dev", namespace="app"))
    uat_obj = classs(arguments=MockArgs(env="uat", namespace="app"))
    if type == "create":
        dev_res = dev_obj.get_paths_to_create()
        uat_res = uat_obj.get_paths_to_create()

    if type == "update":
        dev_res = dev_obj.get_json_paths_to_update()
        uat_res = uat_obj.get_json_paths_to_update()
    assert isinstance(dev_res, list)
    assert isinstance(uat_res, list)
    assert len(dev_res) != 0
    assert len(uat_res) != 0
