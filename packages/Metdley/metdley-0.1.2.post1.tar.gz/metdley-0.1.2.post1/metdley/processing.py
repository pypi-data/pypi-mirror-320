import csv
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from .auth import get_client


class Process:
    """Handles interactions with the Metdley API and CSV processing."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_client()
        return self._client

    def _process_json_results(self, results: List[Any]) -> List[Dict[str, Any]]:
        """
        Processes JSON results into a format suitable for CSV writing.
        Handles nested arrays of results where each UPC might have multiple tracks.

        Args:
            results: List of JSON results from the API

        Returns:
            List of dictionaries ready for CSV writing
        """
        processed_rows = []
        for result_set in results:
            # Skip null or invalid results
            if not result_set or result_set == "null":
                processed_rows.append({})
                continue

            # If the result is a string, try to parse it
            if isinstance(result_set, str):
                try:
                    result_set = json.loads(result_set)
                except json.JSONDecodeError:
                    processed_rows.append({})
                    continue

            # Directly append tracks or handle the list of results
            if isinstance(result_set, list):
                for track in result_set:
                    if isinstance(track, dict):
                        # Create a copy of the track to avoid modifying the original
                        processed_track = track.copy()

                        # Handle "Track Artists" field
                        if "Track Artists" in processed_track and isinstance(
                            processed_track["Track Artists"], list
                        ):
                            processed_track["Track Artists"] = ", ".join(
                                processed_track["Track Artists"]
                            )

                        processed_rows.append(processed_track)
            else:
                # If it's a single track, process it directly
                if isinstance(result_set, dict):
                    processed_track = result_set.copy()
                    if "Track Artists" in processed_track and isinstance(
                        processed_track["Track Artists"], list
                    ):
                        processed_track["Track Artists"] = ", ".join(
                            processed_track["Track Artists"]
                        )
                    processed_rows.append(processed_track)
                else:
                    processed_rows.append(result_set)

        return processed_rows

    def csv(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Process a CSV file through the Metdley API.

        Takes a CSV file containing identifiers (ISRC, UPC, or Artist/Track, Artist/Album pairs)
        and returns enriched metadata from various music services.

        Args:
            input_file (str): Path to the input CSV file
            output_file (str, optional): Path for the output CSV file. If not provided,
                                       creates 'metdley_<input_filename>' in the same directory

        Returns:
            str: Path to the output file containing the enriched data
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_file is None:
            output_path = input_path.parent / f"metdley_{input_path.name}"
        else:
            output_path = Path(output_file)

        # Send the CSV file to the API
        client = self._get_client()
        original_content_type = client.headers["Content-Type"]
        client.headers["Content-Type"] = "application/octet-stream"

        try:
            with open(input_path, "rb") as f:
                csv_data = f.read()
                response = client.request("POST", "/v1/process", body=csv_data)

                # Check for valid response
                if not isinstance(response, dict) or "results" not in response:
                    raise ValueError("Unexpected response format from API")

                if response.get("error"):
                    raise RuntimeError(f"API Error: {response['error']}")

                # Process the API response
                processed_results = self._process_json_results(response["results"])

        finally:
            client.headers["Content-Type"] = original_content_type

        # Write results to CSV
        if processed_results:
            fieldnames = []
            for row in processed_results:
                if isinstance(row, dict):
                    for key in row.keys():
                        if key not in fieldnames:
                            fieldnames.append(key)

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_results)

        return str(output_path)


process = Process()
