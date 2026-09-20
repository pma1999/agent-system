"""Regression checks for existing browser MCP configurations."""
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import _deploy


class BrowserPathsTests(unittest.TestCase):
    def test_existing_configs_and_repeated_install(self):
        cases = {
            "config.toml": '[mcp_servers.playwright]\nargs = ["-y", "@playwright/mcp@latest", "--headless"]\n',
            "claude.json": '{"mcpServers":{"chrome-devtools":{"args":["-y","chrome-devtools-mcp@latest","--isolated"]}}}',
            "opencode.jsonc": '// keep this comment\n{"mcp":{"playwright":{"command":["npx", "@playwright/mcp@latest", "--executable-path", "/snap/bin/chromium"]}}}',
            "v2.jsonc": '{"mcp":{"servers":{"chrome-devtools":{"command":["npx","chrome-devtools-mcp@latest","--headless"]}}}}',
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(_deploy, "backups", return_value=root / "backups"):
                for name, original in cases.items():
                    with self.subTest(name=name):
                        target = root / name
                        target.write_text(original, encoding="utf-8")
                        self.assertEqual(_deploy.migrate_browser_paths(target, True), 1)
                        self.assertEqual(target.read_text(), original)
                        self.assertEqual(_deploy.migrate_browser_paths(target, False), 1)
                        updated = target.read_text()
                        self.assertIn("--allow-unrestricted-", updated)
                        self.assertEqual(_deploy.migrate_browser_paths(target, False), 0)
                        self.assertEqual(target.read_text(), updated)
                        if name.endswith(".toml"):
                            self.assertEqual(tomllib.loads(updated)["mcp_servers"]["playwright"]["args"][-1], "--headless")
                        else:
                            json.loads(_deploy._strip_jsonc(updated))
                        if name == "opencode.jsonc":
                            self.assertTrue(updated.startswith("// keep this comment"))
                            self.assertIn("/snap/bin/chromium", updated)
                self.assertEqual(len(list((root / "backups").rglob("*.jsonc"))), 2)

    def test_explicit_policy_pins_and_other_servers_are_preserved(self):
        original = '{"args":["chrome-devtools-mcp@latest","--allow-unrestricted-paths=false"],"command":["@playwright/mcp@0.0.36"],"other":{"args":["different-mcp"]}}'
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "config.json"
            target.write_text(original)
            self.assertEqual(_deploy.migrate_browser_paths(target, False), 0)
            self.assertEqual(target.read_text(), original)


if __name__ == "__main__":
    unittest.main()
