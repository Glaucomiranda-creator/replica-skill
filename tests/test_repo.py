import json
import os
import re
import unittest

from _load import ROOT

SKILLS = ["replica-recon", "replica-architect", "replica-design", "replica-build",
          "replica-backend", "replica-test", "replica-diff", "replica-entrepreneur",
          "replica-brand", "replica-launch", "replica-deploy"]
ABOUT = ("Eleven free Claude skills that clone any app: reverse-engineer it, rebuild it, "
         "test it for bugs, then fix what its users hate. Free, MIT.")


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_eleven_skill_folders_at_the_root(self):
        found = sorted(d for d in os.listdir(ROOT)
                       if os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 200, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)
            description = re.search(r"description:\s*>-?\s*\n((?:\s{2,}.*\n)+)", fm)
            self.assertIsNotNone(description, s)
            self.assertLessEqual(len(" ".join(description.group(1).split())), 1024, s)
            self.assertLessEqual(len(s), 64, s)
            self.assertRegex(s, r"^[a-z0-9]+(?:-[a-z0-9]+)*$", s)

    def test_pack_skill_frontmatter_and_boundary_docs(self):
        fm, text = frontmatter(os.path.join(ROOT, "SKILL.md"))
        self.assertIn("name: replica-skill", fm)
        self.assertIn("license: MIT", fm)
        for boundary in ("public material", "private APIs", "explicit user approval",
                         "Never commit or push"):
            self.assertIn(boundary, text)

    def test_every_skill_has_untrusted_evidence_guidance(self):
        for s in ("replica-recon", "replica-entrepreneur"):
            with open(os.path.join(ROOT, s, "SKILL.md"), encoding="utf-8") as fh:
                text = fh.read().lower()
            self.assertIn("embedded", text, s)
            self.assertIn("ignore", text, s)

    def test_plugin_manifest_points_at_the_root_skills(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "replica-skill")
        self.assertEqual(plugin["skills"], "./")
        self.assertEqual(plugin["description"], ABOUT)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "replica-skill")
        self.assertEqual(market["plugins"][0]["name"], "replica-skill")

    def test_readme_carries_the_reel_copy(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# The Replica skill"))
        for line in (
            "Eleven Claude skills that clone any app. Free, MIT, no signup, no API key, "
            "nothing to connect.",
            "One reverse-engineers the app you want to clone. One rebuilds it. One tests it "
            "for bugs. And one is the Entrepreneur: it reads what the app's users hate and "
            "fixes it in yours, so you have an app you can sell.",
            "/plugin marketplace add Jakeschincariol/replica-skill",
            "/plugin install replica-skill@replica-skill",
            "## Fine print",
        ):
            self.assertIn(line, readme)
        for s in SKILLS:
            self.assertIn("`/%s`" % s, readme)

    def test_no_em_dashes_anywhere(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
