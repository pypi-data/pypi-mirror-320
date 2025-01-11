import csv
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from .auth import get_client


class Process:
    """Process interface for the Metdley API."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_client()
        return self._client

    def _process_json_results(self, results: List[Any]) -> List[Dict[str, Any]]:
        """
        Process JSON results into a format suitable for CSV writing.
        Handles nested arrays of results where each UPC might have multiple tracks.

        Args:
            results: List of JSON results from the API

        Returns:
            List of dictionaries ready for CSV writing
        """
        processed_rows = []

        for result_set in results:
            if not result_set or result_set == "null":
                processed_rows.append({})  # Empty row for null results
                continue

            # If the result is a string, try to parse it
            if isinstance(result_set, str):
                try:
                    result_set = json.loads(result_set)
                except json.JSONDecodeError:
                    processed_rows.append({})
                    continue

            # Handle the array of results for this row
            if isinstance(result_set, list):
                # Add all tracks found for this query
                for track in result_set:
                    if isinstance(track, dict):
                        # Convert track_artists list to comma-separated string
                        if "track_artists" in track and isinstance(
                            track["track_artists"], list
                        ):
                            track = (
                                track.copy()
                            )  # Make a copy to avoid modifying the original
                            track["track_artists"] = ", ".join(track["track_artists"])
                        processed_rows.append(track)
            else:
                processed_rows.append({})

        return processed_rows

    def csv(self, input_file: str, output_file: Optional[str] = None):
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
                response = client.request(
                    "POST",
                    "/v1/process",
                    body=csv_data,
                )

                # Check if we got a proper response with results
                if not isinstance(response, dict) or "results" not in response:
                    raise ValueError("Unexpected response format from API")

                # Check for API errors
                if response.get("error"):
                    raise RuntimeError(f"API Error: {response['error']}")

                processed_results = self._process_json_results(response["results"])

        finally:
            client.headers["Content-Type"] = original_content_type

        # Write the processed results to the output file
        if processed_results:
            # Collect all possible field names from all results
            fieldnames = set()
            for row in processed_results:
                fieldnames.update(row.keys())

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=list(fieldnames))
                writer.writeheader()
                writer.writerows(processed_results)

        return str(output_path)


# Create instance
process = Process()
