import requests
import json

class livescraper:
    """
    A scraper class to interact with a scraping service API.
    """

    def __init__(self, api_key):
        """
        Initialize the scraper with an API key.

        :param api_key: Your API key for the scraping service.
        """
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = 'https://api.livescraper.com/'  # Replace with your own endpoint if needed.

    def _make_request(self, endpoint, queries, language=None, region=None, dropduplicates=None, enrichment=None, fields=None):
        """
        Internal helper method to make API requests.

        :param endpoint: API endpoint to call.
        :param queries: The search queries (list of strings).
        :param language: Language code for the search.
        :param region: Region code for the search.
        :param dropduplicates: Whether to drop duplicate results.
        :param enrichment: Enrichment level for the results.
        :param fields: Specific fields to include in the response (list of strings).
        :return: The API response as a dictionary.
        """
        # Set fields to an empty array if not provided
        if queries is None:
            queries = []

         # Set fields to an empty array if not provided
        if fields is None:
            fields = []

        # Convert lists to JSON strings for the request
        queries_json = json.dumps(queries)
        fields_json = json.dumps(fields) if fields else None

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params={
                    "key": self.api_key,
                    "queries": queries_json,
                    "language": language,
                    "region": region,
                    "dropduplicates": dropduplicates,
                    "enrichment": enrichment,
                    "fields": fields_json,
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            error_message = error.response.json().get('message', str(error)) if error.response else str(error)
            raise RuntimeError(f"Failed to fetch data: {error_message}") from error

    def google_maps_search(self, queries, language=None, region=None, dropduplicates=None, enrichment=None, fields=None):
        """
        Search Google Maps for places.

        :param queries: The search queries (list of strings, e.g., ["restaurants, Manhattan, NY"]).
        :param language: Language code for the search.
        :param region: Region code for the search.
        :param dropduplicates: Whether to drop duplicate results.
        :param enrichment: Enrichment level for the results.
        :param fields: Specific fields to include in the response (list of strings).
        :return: The search results as a dictionary.
        """
        return self._make_request("api/v1/task/map", queries, language, region, dropduplicates, enrichment, fields)

    def google_review_search(self, queries, language=None, region=None, dropduplicates=None, enrichment=None, fields=None):
        """
        Search Google for reviews.

        :param queries: The search queries (list of strings, e.g., ["restaurants reviews, Manhattan, NY"]).
        :param language: Language code for the search.
        :param region: Region code for the search.
        :param dropduplicates: Whether to drop duplicate results.
        :param enrichment: Enrichment level for the results.
        :param fields: Specific fields to include in the response (list of strings).
        :return: The search results as a dictionary.
        """
        return self._make_request("api/v1/task/review", queries, language, region, dropduplicates, enrichment, fields)

    def google_email_search(self, queries, language=None, region=None, dropduplicates=None, enrichment=None, fields=None):
        """
        Search Google for emails.

        :param queries: The search queries (list of strings, e.g., ["contact emails for restaurants"]).
        :param language: Language code for the search.
        :param region: Region code for the search.
        :param dropduplicates: Whether to drop duplicate results.
        :param enrichment: Enrichment level for the results.
        :param fields: Specific fields to include in the response (list of strings).
        :return: The search results as a dictionary.
        """
        return self._make_request("api/v1/task/email", queries, language, region, dropduplicates, enrichment, fields)
