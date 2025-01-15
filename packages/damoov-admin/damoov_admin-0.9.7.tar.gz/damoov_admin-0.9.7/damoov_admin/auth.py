# auth.py
import os
import sqlite3
import hashlib
import threading
import requests


class TelematicsAuth:
    BASE_URL = "https://user.telematicssdk.com/v1/Auth"
    LOGIN_ENDPOINT = f"{BASE_URL}/Login"
    REFRESH_ENDPOINT = f"{BASE_URL}/RefreshToken"

    def __init__(self, email, password):
        """
        Initializes the TelematicsAuth object.

        :param email: User's email.
        :param password: User's password.
        """
        self.email = email
        self.password = password
        self.lock = threading.RLock()
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None

        # Hash the email for use as a unique identifier
        self.email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()

        # Use the embedded SQLite database
        self.DEFAULT_DB_PATH = os.path.join(
            os.path.dirname(__file__), ".resources", "resources.sql"
        )

        # Ensure the database file exists
        self._ensure_db()

        # Load tokens from the database
        self._load_tokens()

    def _ensure_db(self):
        """
        Ensures the SQLite database is available in the SDK directory.
        """
        if not os.path.exists(self.DEFAULT_DB_PATH):
            raise RuntimeError(f"Database file not found: {self.DEFAULT_DB_PATH}")

        self.connection = sqlite3.connect(self.DEFAULT_DB_PATH)

    def _save_tokens(self):
        """
        Saves the access and refresh tokens to the SQLite database.
        """
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tokens (email_hash, access_token, refresh_token)
                    VALUES (?, ?, ?)
                """, (self.email_hash, self.access_token, self.refresh_token))
                self.connection.commit()
            except sqlite3.Error as e:
                raise RuntimeError(f"Error saving tokens: {e}")

    def _load_tokens(self):
        """
        Loads the access and refresh tokens from the SQLite database.
        If tokens are not found, triggers login to generate new tokens.
        """
        with self.lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT access_token, refresh_token
                FROM tokens
                WHERE email_hash = ?
            """, (self.email_hash,))
            result = cursor.fetchone()

            if result:
                self.access_token, self.refresh_token = result
            else:
                self.login()

    def login(self):
        """
        Authenticates the user and retrieves access and refresh tokens.
        """
        payload = {"LoginFields": f'{{"email":"{self.email}"}}', "Password": self.password}
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        try:
            response = self.session.post(self.LOGIN_ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()
            tokens = response.json().get('Result', {})
            self.access_token = tokens.get('AccessToken', {}).get('Token')
            self.refresh_token = tokens.get('RefreshToken')
            self._save_tokens()
        except Exception as e:
            raise RuntimeError(f"Login failed: {e}")

    def refresh(self):
        """
        Refreshes the access token using the refresh token.
        """
        if not self.refresh_token:
            self.login()
            return

        payload = {"AccessToken": self.access_token, "RefreshToken": self.refresh_token}
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        try:
            response = self.session.post(self.REFRESH_ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()
            tokens = response.json().get('Result', {})
            self.access_token = tokens.get('AccessToken', {}).get('Token')
            self.refresh_token = tokens.get('RefreshToken')
            self._save_tokens()
        except Exception:
            self.login()  # Fall back to login if refresh fails

    def get_access_token(self):
        """
        Retrieves the current access token, refreshing or logging in if necessary.
        """
        with self.lock:
            if not self.access_token:
                self._load_tokens()
            return self.access_token

    def handle_401(self):
        """
        Handles a 401 Unauthorized error by refreshing the token.
        """
        with self.lock:
            self.refresh()

    def close(self):
        """
        Closes the SQLite database connection.
        """
        if self.connection:
            self.connection.close()
            
    def get_with_retry(self, url, headers=None):
        """Performs a GET request and retries once if a 401 status is encountered."""
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 401:
                self.handle_401()
                updated_headers = headers.copy() if headers else {}
                updated_headers['authorization'] = f'Bearer {self.get_access_token()}'
                response = self.session.get(url, headers=updated_headers)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            handle_response(response)
            return response
    
    def post_with_retry(self, url, headers=None, json=None, data=None):
        """Performs a POST request and retries once if a 401 status is encountered."""
        try:
            response = self.session.post(url, headers=headers, json=json, data=data)
            if response.status_code == 401:
                self.handle_401()
                updated_headers = headers.copy() if headers else {}
                updated_headers['authorization'] = f'Bearer {self.get_access_token()}'
                response = self.session.post(url, headers=updated_headers, json=json, data=data)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            handle_response(response)
            return response

    def put_with_retry(self, url, headers=None, json=None, data=None):
        """Performs a PUT request and retries once if a 401 status is encountered."""
        try:
            response = self.session.put(url, headers=headers, json=json, data=data)
            if response.status_code == 401:
                self.handle_401()
                updated_headers = headers.copy() if headers else {}
                updated_headers['authorization'] = f'Bearer {self.get_access_token()}'
                response = self.session.put(url, headers=updated_headers, json=json, data=data)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            handle_response(response)
            return response
    
    def delete_with_retry(self, url, headers=None, json=None, data=None):
        """Performs a PUT request and retries once if a 401 status is encountered."""
        try:
            response = self.session.delete(url, headers=headers, json=json, data=data)
            if response.status_code == 401:
                self.handle_401()
                updated_headers = headers.copy() if headers else {}
                updated_headers['authorization'] = f'Bearer {self.get_access_token()}'
                response = self.session.delete(url, headers=updated_headers, json=json, data=data)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            handle_response(response)
            return response
        
    def patch_with_retry(self, url, headers=None, json=None, data=None):
        """Performs a PUT request and retries once if a 401 status is encountered."""
        try:
            response = self.session.patch(url, headers=headers, json=json, data=data)
            if response.status_code == 401:
                self.handle_401()
                updated_headers = headers.copy() if headers else {}
                updated_headers['authorization'] = f'Bearer {self.get_access_token()}'
                response = self.session.patch(url, headers=updated_headers, json=json, data=data)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            handle_response(response)
            return response