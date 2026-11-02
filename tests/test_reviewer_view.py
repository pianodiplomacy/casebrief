import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parent.parent / "src" / "reviewer_view.py"
spec = importlib.util.spec_from_file_location("reviewer_view", MODULE_PATH)
reviewer_view = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reviewer_view)

PACKET = """## SRC-001 — Project Description
ordinary evidence
## SRC-005 — Conflicting Test Note
ordinary evidence
## SRC-007 — Restricted Evidence
restricted evidence body
"""


class ReviewerViewStateATests(unittest.TestCase):
    def test_actual_frozen_heading_level_is_parsed(self):
        self.assertEqual(
            [source_id for source_id, _ in reviewer_view.packet_sources(PACKET)],
            ["SRC-001", "SRC-005", "SRC-007"],
        )

    def test_state_a_is_truthful_and_has_no_model_result(self):
        output = reviewer_view.render_state_a(PACKET)
        self.assertIn("STATE A - NO MODEL RUN AVAILABLE", output)
        self.assertIn("NOT EXECUTED", output)
        self.assertIn("Muse Spark Open", output)
        self.assertIn("NOT AVAILABLE - NO GENUINE MODEL RUN EXISTS", output)
        self.assertIn("PENDING", output)

    def test_lists_source_ids_without_evidence_bodies(self):
        output = reviewer_view.render_state_a(PACKET)
        self.assertIn("SRC-001", output)
        self.assertIn("SRC-005", output)
        self.assertIn("SRC-007", output)
        self.assertNotIn("ordinary evidence", output)
        self.assertNotIn("restricted evidence body", output)

    def test_restricted_source_title_is_not_reproduced(self):
        output = reviewer_view.render_state_a(PACKET)
        self.assertNotIn("Restricted Evidence", output)
        self.assertIn("Content withheld in reviewer preview", output)

    def test_no_state_b_or_acceptance_claims(self):
        output = reviewer_view.render_state_a(PACKET)
        self.assertNotIn("RECORDED RUN AVAILABLE", output)
        self.assertNotIn("HUMAN ACCEPTED", output)
        self.assertIn("No automated approval", output)


if __name__ == "__main__":
    unittest.main()
