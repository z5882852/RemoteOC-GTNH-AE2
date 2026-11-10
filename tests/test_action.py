import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
sys.modules.setdefault("requests", types.SimpleNamespace(request=None))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

import action


class CraftActionTests(unittest.TestCase):
    @patch.object(action.task_manager, "add_task")
    def test_native_fluid_command(self, add_task):
        action.craft_item("client_01", "water", item_amount=4000, stack_type="fluid")
        command = add_task.call_args.kwargs["commands"][0]
        self.assertEqual(command, 'return ae.requestFluid("water", 4000)')

    @patch.object(action.task_manager, "add_task")
    def test_item_command_escapes_strings(self, add_task):
        action.craft_item("client_01", 'mod:item"quoted', 2, 3, "Main CPU")
        command = add_task.call_args.kwargs["commands"][0]
        self.assertEqual(
            command,
            'return ae.requestItem("mod:item\\"quoted", 2, 3, "Main CPU")',
        )


if __name__ == "__main__":
    unittest.main()
