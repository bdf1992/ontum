"""The tabletop forge's teeth (done-line 0198, §10).

The check that matters: a spec that breaks the compendium's laws is
REFUSED — not exactly 8 elements, opposition that is not XOR 7,
non-monotonic tiers — and the build is a pure function of its inputs
(two builds are byte-identical, no placeholder survives, no GUID
collides). A fabricated unlawful spec of each kind is caught, so the
check is proven non-vacuous.
"""

import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tabletop"))

import forge  # noqa: E402


class TestSpecLaws(unittest.TestCase):
    def setUp(self):
        self.spec = forge.load_spec()

    def test_committed_spec_is_lawful(self):
        self.assertEqual(forge.validate(self.spec), [])

    def test_refuses_wrong_element_count(self):
        broken = copy.deepcopy(self.spec)
        broken["elements"].pop()
        problems = forge.validate(broken)
        self.assertTrue(any("exactly 8" in p for p in problems), problems)

    def test_refuses_non_xor7_opposition(self):
        broken = copy.deepcopy(self.spec)
        # Fire's true opposite is Water (1 ^ 7 = 6); claim Earth instead
        fire = next(e for e in broken["elements"] if e["name"] == "Fire")
        fire["opposite"] = "Earth"
        problems = forge.validate(broken)
        self.assertTrue(any("XOR" in p and "Fire" in p for p in problems), problems)

    def test_refuses_non_monotonic_tiers(self):
        broken = copy.deepcopy(self.spec)
        broken["tiers"][1]["capacity"] = broken["tiers"][0]["capacity"]
        problems = forge.validate(broken)
        self.assertTrue(any("capacity must strictly increase" in p for p in problems),
                        problems)
        broken2 = copy.deepcopy(self.spec)
        broken2["tiers"][4]["timecoin"] = 1
        problems2 = forge.validate(broken2)
        self.assertTrue(any("timecoin must strictly increase" in p for p in problems2),
                        problems2)

    def test_build_refuses_unlawful_spec(self):
        broken = copy.deepcopy(self.spec)
        broken["elements"].pop()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                forge.build(broken, tmp)

    def test_sample_census_example_intact(self):
        """bdo's worked example: Region A (5 Fire) + Region B (10 Fire)
        + Herald (5 Fire) = the world holds 20 Fire."""
        fire = 0
        for b in self.spec["samples"]["biomes"]:
            if b["element"] == "Fire":
                fire += b["own"]
        for p in self.spec["samples"]["personas"]:
            fire += p["pool"].get("Fire", 0)
        self.assertEqual(fire, 20)


class TestBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = forge.load_spec()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name)
        cls.written = forge.build(cls.spec, cls.out / "a")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _files(self, sub):
        return sorted((self.out / "a" / sub).rglob("*"))

    def test_deterministic(self):
        forge.build(self.spec, self.out / "b")
        a_files = sorted(p for p in (self.out / "a").rglob("*") if p.is_file())
        b_files = sorted(p for p in (self.out / "b").rglob("*") if p.is_file())
        self.assertEqual([p.relative_to(self.out / "a") for p in a_files],
                         [p.relative_to(self.out / "b") for p in b_files])
        for pa, pb in zip(a_files, b_files):
            self.assertEqual(pa.read_bytes(), pb.read_bytes(), pa.name)

    def test_no_unresolved_placeholders(self):
        for p in (self.out / "a").rglob("*"):
            if p.is_file():
                self.assertNotIn("{{FORGE:", p.read_text(encoding="utf-8"), p.name)

    def test_saved_objects_are_valid(self):
        objs = list((self.out / "a" / "objects").glob("*.json"))
        self.assertGreaterEqual(len(objs), 8)
        for p in objs:
            doc = json.loads(p.read_text(encoding="utf-8"))
            self.assertIn("ObjectStates", doc)
            for state in doc["ObjectStates"]:
                for key in ("GUID", "Name", "Transform", "Nickname"):
                    self.assertIn(key, state, p.name)

    def test_full_save_has_global_and_unique_guids(self):
        doc = json.loads((self.out / "a" / "save" / "CatalystCore-PaperPlay.json")
                         .read_text(encoding="utf-8"))
        self.assertIn("onChat", doc["LuaScript"])
        guids = [s["GUID"] for s in doc["ObjectStates"]]
        self.assertEqual(len(guids), len(set(guids)))
        # the kit's core pieces are all on the table
        nicks = " | ".join(s["Nickname"] for s in doc["ObjectStates"])
        for needle in ("Spawner Console", "The Global Clock", "Hourglass T5",
                       "Aether Grains", "Region A", "Timecoin 1000 Mint"):
            self.assertIn(needle, nicks)

    def test_console_embeds_the_kit_scripts(self):
        console = (self.out / "a" / "lua" / "console.ttslua").read_text(encoding="utf-8")
        self.assertIn("CC_SCRIPTS", console)
        for key in ("hourglass", "clock", "biome", "persona"):
            self.assertIn(f"{key} = [=====[", console)

    def test_eight_grain_bags_one_per_element(self):
        doc = json.loads((self.out / "a" / "objects" / "element-grain-bags.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(len(doc["ObjectStates"]), 8)
        for state in doc["ObjectStates"]:
            self.assertEqual(state["Name"], "Infinite_Bag")
            self.assertEqual(len(state["ContainedObjects"]), 1)


if __name__ == "__main__":
    unittest.main()
