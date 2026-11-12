import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "realme_debloater.py"
spec = importlib.util.spec_from_file_location("realme_debloater", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SafetyTests(unittest.TestCase):
    def test_rejects_core_android_package(self):
        with self.assertRaises(RuntimeError):
            mod.validate_package("com.android.systemui")

    def test_rejects_realme_ota_package(self):
        with self.assertRaises(RuntimeError):
            mod.validate_package("com.oplus.ota")

    def test_rejects_malformed_name(self):
        with self.assertRaises(RuntimeError):
            mod.validate_package("not a package")

    def test_accepts_well_formed_non_protected_name(self):
        mod.validate_package("com.example.optionalapp")

if __name__ == "__main__":
    unittest.main()
