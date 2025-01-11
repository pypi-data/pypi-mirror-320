# test_models.py
import pytest
from rettxmutation.analysis.models import GeneMutation

# Mock mutalyzer json model
MOCK_MUTALYZER_MODEL = {
        "type": "description_dna",
        "reference": {
            "id": "NM_004992.4"
        },
        "coordinate_system": "c",
        "variants": [
            {
                "location": {
                        "type": "point",
                        "position": 916
                },
                "type": "substitution",
                "source": "reference",
                "deleted": [
                    {
                        "sequence": "C",
                        "source": "description"
                    }
                ],
                "inserted": [
                    {
                        "sequence": "T",
                        "source": "description"
                    }
                ]
            }
        ]
    }

def test_from_hgvs_string_valid():
    mutation = GeneMutation.from_hgvs_string("NM_004992.4:c.916C>T")
    assert mutation.gene_transcript == "NM_004992.4"
    assert mutation.gene_variation == "c.916C>T"
    assert mutation.confidence == 0
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_MODEL

def test_from_hgvs_string_invalid():
    with pytest.raises(Exception):
        GeneMutation.from_hgvs_string("InvalidString")

def test_model_validation():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T",
        confidence=0.9
    )
    assert mutation.gene_transcript == "NM_004992.4"
    assert mutation.gene_variation == "c.916C>T"
    assert mutation.confidence == 0.9
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_MODEL

def test_to_hgvs_string():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T"
    )
    assert mutation.to_hgvs_string() == "NM_004992.4:c.916C>T"

def test_get_transcript():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T"
    )
    assert mutation.get_transcript() == "NM_004992"

def test_get_transcript_without_version():
    mutation = GeneMutation(
        gene_transcript="NM_004992",
        gene_variation="c.916C>T"
    )
    assert mutation.get_transcript() == "NM_004992"

def test_invalid_gene_mutation():
    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992,4",
            gene_variation="c.916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation="c.916C>"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation=".916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation="c916>T"
        )

def test_invalid_gene_mutation_with_none_fields():
    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript=None,
            gene_variation="c.916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation=None
        )
