import json
import unittest

from src.validate_output import validate_output_text


def valid_output():
    return {
        "supported_claims": [
            {
                "claim": "Handler returns named fields.",
                "source_ids": ["SRC-002"],
                "limitations": "Not independently inspected.",
            }
        ],
        "unsupported_claims": [
            {
                "claim": "Automatic programme approval.",
                "asserted_in": ["SRC-001"],
                "assessment_sources": ["SRC-002"],
                "limitations": "Unsupported by this packet.",
            }
        ],
        "missing_evidence": [
            {
                "needed": "Deployment record.",
                "related_claim": "Public deployment.",
                "source_ids": ["SRC-006"],
            }
        ],
        "contradictions": [],
        "uncertainty": [
            {
                "description": "Public deployment remains uncertain.",
                "source_ids": ["SRC-006"],
                "reason": "No deployment artifact was supplied.",
            }
        ],
        "proposed_next_action": {
            "action": "Request supplementary evidence.",
            "source_ids": ["SRC-006"],
            "limitations": "Advisory only.",
        },
        "evidence_references": [
            {"source_id": "SRC-006", "relevance": "Deployment assertion."}
        ],
    }


class ValidateOutputTests(unittest.TestCase):
    def test_valid_complete_output(self):
        self.assertEqual(validate_output_text(json.dumps(valid_output())), [])

    def test_missing_top_level_key(self):
        output = valid_output()
        del output["uncertainty"]
        errors = validate_output_text(json.dumps(output))
        self.assertIn("missing required top-level key: uncertainty", errors)

    def test_invented_source_id(self):
        output = valid_output()
        output["supported_claims"][0]["source_ids"] = ["SRC-008"]
        errors = validate_output_text(json.dumps(output))
        self.assertTrue(any("invalid source ID SRC-008" in error for error in errors))

    def test_next_action_array_is_invalid(self):
        output = valid_output()
        output["proposed_next_action"] = [
            {"action": "Request evidence.", "source_ids": ["SRC-006"]}
        ]
        errors = validate_output_text(json.dumps(output))
        self.assertIn(
            "proposed_next_action: expected one non-null object", errors
        )

    def test_one_source_src_005_contradiction_is_valid(self):
        output = valid_output()
        output["contradictions"] = [
            {
                "description": "SRC-005 internally conflicts.",
                "source_ids": ["SRC-005"],
                "resolution": "unresolved",
            }
        ]
        self.assertEqual(validate_output_text(json.dumps(output)), [])

    def test_invalid_source_id_in_evidence_references(self):
        output = valid_output()
        output["evidence_references"][0]["source_id"] = "SRC-008"
        errors = validate_output_text(json.dumps(output))
        self.assertTrue(any("invalid source ID SRC-008" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
