# trips.py

import requests
from datetime import datetime, timedelta

from .auth import TelematicsAuth
from .core import TelematicsCore
from .utility import handle_response, adjust_date_range
import json
from requests.exceptions import HTTPError



class BaseTrips:
    BASE_URL = "https://api.telematicssdk.com/trips/get/admin/v1"

    def __init__(self, auth_client: TelematicsAuth):
        self.auth_client = auth_client

    def _get_headers(self):
        return {
            'accept': 'application/json',
            'authorization': f'Bearer {self.auth_client.get_access_token()}'
        }

class TripsModule:
    def __init__(self, core: TelematicsCore):
        self.core = core  # Ensuring naming consistency

    @property
    def trips(self):
        return Trips(self.core.auth_client)


class Trips(BaseTrips):

    def get_list_trips(self, user_id,
                       start_date=None, end_date=None,
                       start_date_timestamp_sec=None, end_date_timestamp_sec=None,
                       include_details=True, include_statistics=False,
                       include_scores=False, include_related=False,
                       tags_included=None, tags_included_operator=None,
                       tags_excluded=None, tags_excluded_operator=None,
                       locale="EN", unit_system=None,
                       vehicles=None, sort_by=None,
                       limit=None, page=None):
        """
        Retrieves trip details for a specific user, with support for automatic pagination.

        :return: Aggregated trip details in JSON format.
        """
        # Set default limit and adjust if necessary
        if limit is None:
            limit = 14
        elif limit > 14:
            print("[NOTIFICATION] Limit was adjusted to 14")
            limit = 14

        if sort_by is None:
            sort_by = "StartDateUtc_Desc"

        if unit_system not in ["Si", "km", "ml", "Imperial"]:
            print("[NOTIFICATION] Invalid unit_system provided. Defaulting to 'Si'.")
            unit_system = "Si"
        if unit_system == "km":
            unit_system = "Si"
        elif unit_system == "ml":
            unit_system = "Imperial"

        url = f"{self.BASE_URL}"

        payload = {
            "Identifiers": {
                "UserId": user_id
            },
            "IncludeDetails": include_details,
            "IncludeStatistics": include_statistics,
            "IncludeScores": include_scores,
            "IncludeRelated": include_related,
            "Locale": locale,
            "UnitSystem": unit_system,
            "SortBy": sort_by,

        }

        if start_date and end_date:
            payload["StartDate"] = start_date
            payload["EndDate"] = end_date
        elif start_date_timestamp_sec and end_date_timestamp_sec:
            payload["StartDateTimestampSec"] = start_date_timestamp_sec
            payload["EndDateTimestampSec"] = end_date_timestamp_sec

        if tags_included is not None and not isinstance(tags_included, list):
            tags_included = [tags_included]

        if tags_excluded is not None and not isinstance(tags_excluded, list):
            tags_excluded = [tags_excluded]

        self._add_to_payload_if_exists(payload, "TagsIncluded", tags_included)
        self._add_to_payload_if_exists(payload, "TagsIncludedOperator", tags_included_operator)
        self._add_to_payload_if_exists(payload, "TagsExcluded", tags_excluded)
        self._add_to_payload_if_exists(payload, "TagsExcludedOperator", tags_excluded_operator)
        self._add_to_payload_if_exists(payload, "Vehicles", vehicles)

        # Initialize variables for pagination
        all_trips = []
        current_page = 1
        total_pages = 1  # Start with assumption there's at least one page

        if page is None:
            while current_page <= total_pages:
                payload["Paging"] = {
                    "Page": current_page,
                    "Count": limit,
                    "IncludePagingInfo": True
                }

                # Fetch current page of trips
                trips_response = self._fetch_trip_details(url, payload, limit)
                # Correctly access the trips using the .trips property of TripsResponse
                all_trips.extend(trips_response.trips)

                # Update paging information based on the current response
                paging_info = trips_response.paging_info
                current_page = paging_info.get("CurrentPage", current_page) + 1
                total_pages = paging_info.get("TotalPages", total_pages)
        else:
            payload["Paging"] = {
                "Page": page,
                "Count": limit,
                "IncludePagingInfo": True
            }

            # Fetch current page of trips
            trips_response = self._fetch_trip_details(url, payload, limit)
            # Correctly access the trips using the .trips property of TripsResponse
            all_trips.extend(trips_response.trips)

        final_response = {
            "Result": {
                "Trips": all_trips,
                "PagingInfo": {
                    "CurrentPage": current_page - 1,  # Adjust because of the loop increment
                    "TotalPages": total_pages
                }
            },
            "InitialPayload": payload  # Include for reference
        }

        return TripsResponse(final_response)

    def _fetch_trip_details(self, url, payload, limit=None):
        try:
            response = self.auth_client.post_with_retry(url, headers=self._get_headers(), json=payload)

            if response.status_code == 200:
                # Successful response, parse JSON
                data = response.json()
                return TripsResponse(data)

            # For any non-200 response, return an empty TripsResponse with an additional status attribute
            return TripsResponse({"status": response.status_code, "content": response.text})

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return TripsResponse({"status": "error", "message": str(e)})

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {response.text}")
            return TripsResponse({"status": "error", "message": "JSON decode error"})

        

    def _add_to_payload_if_exists(self, payload, key, value):
        if value:
            payload[key] = value

class TripsResponse:
    def __init__(self, data):
        self.data = data if isinstance(data, dict) else {}

    @property
    def result(self):
        # Safeguard in case 'Result' is not a dictionary
        return self.data.get('Result', {}) if isinstance(self.data.get('Result', {}), dict) else {}

    @property
    def trips(self):
        # This already safeguards against 'Result' not being a dictionary and 'Trips' not being a list
        trips = self.result.get('Trips', [])
        return trips if isinstance(trips, list) else []

    @property
    def statistics(self):
        # Similar safeguard as in 'trips'
        trip = self.result.get('Trip', {})
        return trip.get('Statistics', {}) if isinstance(trip, dict) else {}

    @property
    def details(self):
        # Since 'Data' is nested within 'Trip', the same pattern applies here
        return self.result.get('Trip', {}).get('Data', {})

    @property
    def transporttype(self):
        # Assuming 'TransportType' is always a dictionary or should be an empty one if not present
        return self.details.get('TransportType', {})

    @property
    def scores(self):
        # Assuming 'Scores' is always a dictionary or should be an empty one if not present
        return self.result.get('Trip', {}).get('Scores', {})

    @property
    def events(self):
        # Assuming 'Events' is always a list or should be an empty one if not present
        events = self.result.get('Trip', {}).get('Events', [])
        return events if isinstance(events, list) else []

    @property
    def waypoints(self):
        # Assuming 'Waypoints' is always a list or should be an empty one if not present
        waypoints = self.result.get('Trip', {}).get('Waypoints', [])
        return waypoints if isinstance(waypoints, list) else []

    @property
    def paging_info(self):
        # Assuming 'PagingInfo' is always a dictionary or should be an empty one if not present
        return self.result.get('PagingInfo', {})

    @property
    def status(self):
        # 'Status' should be a singular value, not a list or dict
        return self.data.get('Status')

    @property
    def datetime(self):
        # Assuming 'Data' is always a dictionary or should be an empty one if not present
        return self.data.get('Data', {})

    @property
    def trip_id(self):
        # Assuming 'Id' is a singular value, not a list or dict
        return self.result.get('Id')

    @property
    def full_response(self):
        # The full response is just the data provided to the instance
        return self.data
    
    def __iter__(self):
        for item in self.data:
            yield item

    def __str__(self):
        return json.dumps(self.data, indent=4)
    



    # Add at the bottom of statistics.py
def DamoovAuth(email, password):
    auth_client = TelematicsAuth(email, password)
    return Trips(auth_client)

