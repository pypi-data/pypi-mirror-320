import json
from unittest import TestCase
from unittest.mock import patch

from pyinfra.api.exceptions import InventoryError
from pyinfra.connectors.terraform import TerraformInventoryConnector


class TestTerraformConnector(TestCase):
    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_no_output(self, fake_shell):
        fake_shell.return_value = json.dumps(
            {
                "hello": {
                    "world": [],
                },
            },
        )

        with self.assertRaises(InventoryError) as context:
            list(TerraformInventoryConnector.make_names_data("output_key"))

        assert context.exception.args[0] == (
            "No Terraform output with key: `output_key`, "
            "valid keys:\n   - hello\n   - hello.world"
        )

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_invalid_output(self, fake_shell):
        fake_shell.return_value = json.dumps({"output_key": "wrongvalue"})

        with self.assertRaises(InventoryError) as context:
            list(TerraformInventoryConnector.make_names_data("output_key"))

        assert (
            context.exception.args[0]
            == "Invalid Terraform output type, should be `list`, got `str`"
        )

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_dict_invalid_item(self, fake_shell):
        fake_shell.return_value = json.dumps({"output_key": [None]})

        with self.assertRaises(InventoryError) as context:
            list(TerraformInventoryConnector.make_names_data("output_key"))

        assert (
            context.exception.args[0]
            == "Invalid Terraform list item, should be `dict` or `str` got `NoneType`"
        )

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data(self, fake_shell):
        fake_shell.return_value = json.dumps({"output_key": ["somehost"]})
        data = list(TerraformInventoryConnector.make_names_data("output_key"))

        assert data == [
            (
                "@terraform/somehost",
                {"ssh_hostname": "somehost"},
                ["@terraform", "all"],
            ),
        ]

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_nested(self, fake_shell):
        fake_shell.return_value = json.dumps({"output_key": {"nested_key": ["somehost"]}})
        data = list(TerraformInventoryConnector.make_names_data("output_key.nested_key"))

        assert data == [
            (
                "@terraform/somehost",
                {"ssh_hostname": "somehost"},
                ["@terraform", "all"],
            ),
        ]

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_dict(self, fake_shell):
        host = {
            "name": "a name",
            "ssh_hostname": "hostname",
        }
        fake_shell.return_value = json.dumps({"output_key": [host]})
        data = list(TerraformInventoryConnector.make_names_data("output_key"))

        assert data == [
            (
                "@terraform/a name",
                {"ssh_hostname": "hostname"},
                ["@terraform", "all"],
            ),
        ]

    @patch("pyinfra.connectors.terraform.local.shell")
    def test_make_names_data_dict_no_name(self, fake_shell):
        host = {
            "not_a_name": "hostname",
        }
        fake_shell.return_value = json.dumps({"output_key": [host]})

        with self.assertRaises(InventoryError) as context:
            list(TerraformInventoryConnector.make_names_data("output_key"))

        assert (
            context.exception.args[0]
            == "Invalid Terraform list item, missing `name` or `ssh_hostname` keys"
        )
