import re
import json
import backoff
import logging
import requests
import pkg_resources
from typing import List, Dict, Any
from rettxmutation.analysis.models import (
    MutationDetail,
    GeneMutationCollection,
    GeneMutation,
    ProteinMutation,
    STANDARD_GENE_TRANSCRIPT,
    STANDARD_PROTEIN_TRANSCRIPT
)


# Initialize the logger
logger = logging.getLogger(__name__)


class GeneMutationNormalizer:
    @staticmethod
    def normalize_ensembl_output(ensembl_output: list) -> list:
        """
        Normalize the Ensembl API output by explicitly structuring the data
        with reference and variant nucleotides as keys.
        """
        normalized_output = []

        for mutation_entry in ensembl_output:
            for alt_base, mutation_data in mutation_entry.items():
                # Extract the reference nucleotide from `hgvsg` or `spdi` if available
                hgvsg = mutation_data.get("hgvsg", [])
                ref_base = None
                if hgvsg and ">" in hgvsg[0]:
                    ref_base = hgvsg[0].split(">")[0][-1]
                elif "spdi" in mutation_data and ":" in mutation_data["spdi"][0]:
                    ref_base = mutation_data["spdi"][0].split(":")[2][0]

                # Ensure ref_base is valid
                if not ref_base:
                    logger.warning("Reference base not found. Skipping entry.")
                    continue

                # Normalize the entry
                normalized_entry = {
                    "ref": ref_base,
                    "alt": alt_base,
                    "hgvsp": mutation_data.get("hgvsp", []),
                    "hgvsc": mutation_data.get("hgvsc", []),
                    "hgvsg": mutation_data.get("hgvsg", []),
                    "id": mutation_data.get("id", []),
                    "spdi": mutation_data.get("spdi", []),
                    "input": mutation_data.get("input", "")
                }

                normalized_output.append(normalized_entry)

        return normalized_output


class InvalidMutationError(Exception):
    """Custom exception for invalid mutations."""
    def __init__(self, transcript: str, variant: str, message: str = "Invalid mutation provided."):
        self.transcript = transcript
        self.variant = variant
        self.message = message
        super().__init__(f"{message} Transcript: {transcript}, Variant: {variant}")


class EnsemblOrgService:
    BASE_URL = "https://rest.ensembl.org/variant_recoder/human"

    def __init__(self):
        self.LATEST_TRANSCRIPTS = self._load_latest_transcripts()
        self.session = requests.Session()

    def close(self):
        self.session.close()

    def _load_latest_transcripts(self):
        """
        Loads the latest transcripts configuration from a JSON file.

        Parameters:
        - config_path (str): Path to the JSON configuration file.

        Returns:
        - dict: Mapping of base transcript IDs to latest versions.
        """
        resource_path = pkg_resources.resource_filename(__name__, "data/latest_transcript_version.json")
        with open(resource_path, 'r') as file:
            latest_transcripts = json.load(file)
        return latest_transcripts

    def _get_latest_transcript(self, transcript: str) -> str:
        """
        Given a transcript identifier (with or without version),
        returns the transcript identifier with the latest version,
        according to self.LATEST_TRANSCRIPTS.

        Example:
            - Input:  "NM_001110792.1" or "NM_001110792"
            - Output: "NM_001110792.2"

        Raises:
            ValueError: If the transcript format is invalid or if the base
                        transcript ID is unrecognized.
        """
        pattern = re.compile(r"^(?P<id>[^.]+)(?:\.(?P<version>\d+))?$")
        match = pattern.match(transcript.strip())
        logger.debug(f"Matching transcript: {transcript}")
        if not match:
            logger.error(f"Invalid transcript format: '{transcript}'")
            raise ValueError(f"Invalid transcript format: '{transcript}'")

        base_id = match.group("id")

        # Confirm the base transcript ID is recognized
        if base_id not in self.LATEST_TRANSCRIPTS:
            logger.error(f"Unrecognized transcript ID: '{base_id}'")
            raise ValueError(f"Unrecognized transcript ID: '{base_id}'")

        latest_version = self.LATEST_TRANSCRIPTS[base_id]

        # If the dictionary indicates "no versioning" (e.g. None), just return the base_id as-is
        if latest_version is None:
            logger.debug(f"No versioning for transcript: '{base_id}'")
            return base_id

        # Otherwise, always return the base_id with the known latest version
        logger.debug(f"Latest version for '{base_id}': {latest_version}")
        return f"{base_id}.{latest_version}"

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ),
        max_tries=5,
    )
    def _fetch_variations(self, transcript: str, variant: str) -> Dict[str, Any]:
        """
        Fetch gene variation data from Ensembl Variant Recoder API.
        """
        # Get the latest transcript version
        transcript = self._get_latest_transcript(transcript)

        # Construct the URL
        url = f"{self.BASE_URL}/{transcript}:{variant}?content-type=application/json"
        try:
            logger.debug(f"Fetching data from URL: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                logger.error(f"Invalid mutation: {transcript}:{variant}")
                logger.error(f"Error message: {response.json()}")
                raise InvalidMutationError(transcript, variant, "The mutation position or base is invalid.")
            logger.error(f"HTTP error during API call: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during API call: {type(e).__name__} - {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API call: {type(e).__name__} - {e}")
            raise

    def _parse_to_model(self, api_response: List[Dict[str, Any]]) -> GeneMutationCollection:
        """
        Parse the API response into a GeneMutationCollection model.
        """
        try:
            # Normalize the response first
            normalized_response = GeneMutationNormalizer.normalize_ensembl_output(api_response)

            # Map normalized response to MutationDetail models
            mutation = GeneMutationCollection(
                mutation_info=[MutationDetail(**mutation) for mutation in normalized_response]
            )

            logger.debug(f"Successfully parsed API response to model: {mutation}")
            logger.debug(f"gene_transcript: {STANDARD_GENE_TRANSCRIPT}")
            logger.debug(f"gene_variation: {mutation.get_mutation_by_transcript(STANDARD_GENE_TRANSCRIPT, 'hgvsc')}")
            logger.debug(f"protein_transcript: {STANDARD_PROTEIN_TRANSCRIPT}")
            logger.debug(f"protein_variation: {mutation.get_mutation_by_transcript(STANDARD_PROTEIN_TRANSCRIPT, 'hgvsp')}")

            # Get gene and protein mutations using our standard transcripts
            gene_variation = mutation.get_mutation_by_transcript(STANDARD_GENE_TRANSCRIPT, 'hgvsc')
            protein_variation = mutation.get_mutation_by_transcript(STANDARD_PROTEIN_TRANSCRIPT, 'hgvsp')

            if not gene_variation or not protein_variation:
                logger.error("Standard gene or protein mutation not found. Skipping.")
                raise InvalidMutationError(STANDARD_GENE_TRANSCRIPT, STANDARD_PROTEIN_TRANSCRIPT)

            # Create mutation_id
            mutation.mutation_id = f"{STANDARD_GENE_TRANSCRIPT}:{gene_variation}"

            # Add standard gene and protein mutations
            mutation.gene_mutation = GeneMutation(
                gene_transcript=STANDARD_GENE_TRANSCRIPT,
                gene_variation=gene_variation
            )
            mutation.protein_mutation = ProteinMutation(
                protein_transcript=STANDARD_PROTEIN_TRANSCRIPT,
                protein_variation=protein_variation
            )

            return mutation
        except Exception as e:
            logger.error(f"Error parsing API response to model: {e}")
            raise

    def get_gene_mutation_collection(self, transcript: str, variant_description: str) -> GeneMutationCollection:
        """
        Fetch variations and return the parsed GeneMutationCollection model.
        This method combines fetching data and parsing into one transparent step.
        """
        try:
            api_response = self._fetch_variations(transcript, variant_description)
            gene_mutation_collection = self._parse_to_model(api_response)
            return gene_mutation_collection
        except InvalidMutationError as e:
            logger.error(f"Invalid mutation encountered: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
