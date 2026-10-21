"""Check the boundaries that could produce an uninstallable store release."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load("release", "release.py")
submit = load("submit", "submit-store-pr.py")


class StoreReleaseTests(unittest.TestCase):
    def setUp(self):
        self.plugin = release.metadata()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        for (goos, goarch), (ext, machine) in release.TARGETS.items():
            # Synthetic headers exercise artifact validation; CI separately
            # builds and loads each real library through its C ABI.
            data = bytearray(256)
            if goos == "linux":
                data[:6] = b"\x7fELF\x02\x01"
                struct.pack_into("<HH", data, 16, 3, machine)
            else:
                data[:2] = b"MZ"
                struct.pack_into("<I", data, 0x3c, 128)
                data[128:132] = b"PE\0\0"
                struct.pack_into("<H", data, 132, machine)
                struct.pack_into("<H", data, 150, 0x2000)
            path = self.directory / release.asset_name(self.plugin, goos, goarch)
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(self.plugin["id"] + "." + ext, data)

    def linux_archive(self):
        return self.directory / release.asset_name(self.plugin, "linux", "amd64")

    def test_complete_release_and_tampered_checksum(self):
        expected = release.checksums(self.directory, self.plugin, complete=True)
        self.assertEqual(len(expected.splitlines()), 3)
        with zipfile.ZipFile(self.linux_archive(), "a") as archive:
            archive.comment = b"modified after checksumming"
        self.assertNotEqual(release.checksums(self.directory, self.plugin, complete=True), expected)

    def test_missing_platform_is_rejected(self):
        self.linux_archive().unlink()
        with self.assertRaises(AssertionError):
            release.checksums(self.directory, self.plugin, complete=True)

    def test_unsafe_and_nested_zip_paths_are_rejected(self):
        for name in ("../spancerxing-cursor.so", "dist/spancerxing-cursor.so", "/spancerxing-cursor.so"):
            with self.subTest(name=name):
                with zipfile.ZipFile(self.linux_archive(), "w") as archive:
                    archive.writestr(name, b"untrusted")
                with self.assertRaises(AssertionError):
                    release.verify_archive(self.linux_archive(), self.plugin, "linux", "amd64")

    def test_wrong_binary_architecture_is_rejected(self):
        with zipfile.ZipFile(self.linux_archive()) as archive:
            data = archive.read(archive.namelist()[0])
        with self.assertRaisesRegex(AssertionError, "architecture mismatch"):
            release.check_binary(data, "linux", "arm64")

    def test_registry_append_preserves_existing_entries_and_rejects_duplicates(self):
        other = {"id": "other", "repository": "https://github.com/other/plugin"}
        original = json.dumps({"schema_version": 1, "plugins": [other]}, indent=2) + "\n"
        result = submit.append_entry(original, self.plugin)
        self.assertEqual(json.loads(result)["plugins"], [other, self.plugin])
        self.assertTrue(result.startswith(original[:original.rfind("]")].rstrip()))
        with self.assertRaises(AssertionError):
            submit.append_entry(result, self.plugin)

    def test_store_submission_stops_before_writing_when_release_is_missing(self):
        with patch.object(submit.sys, "argv", ["submit-store-pr.py", "--submit"]), \
                patch.dict(submit.os.environ, {"GH_TOKEN": "synthetic-test-token"}), \
                patch.object(submit, "api", return_value={
                    "tag_name": "v0.1.0", "draft": False, "prerelease": False, "assets": [],
                }) as api:
            with self.assertRaisesRegex(AssertionError, "missing release asset"):
                submit.main()
            self.assertEqual(api.call_count, 1)
            self.assertTrue(api.call_args.args[0].endswith("/releases/latest"))


if __name__ == "__main__":
    unittest.main()
