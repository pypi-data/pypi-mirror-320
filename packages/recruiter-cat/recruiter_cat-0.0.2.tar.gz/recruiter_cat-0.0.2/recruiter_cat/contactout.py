import requests
import json
import time
import os
class ContactOutAPI:
    def __init__(self, api_token):
        """
        Initialize the ContactOut API client with the given API token.
        """
        self.api_token = api_token

    def format_json(self, json_data,):
        """
        Format the JSON data for better readability.
        """
        print(json.dumps(json_data, indent=4, ensure_ascii=False))

    def profile_url_clean(self, profile_url):
        """
        Clean the profile URL to ensure it's in the correct format.
        """
        if profile_url.endswith('/'):
            profile_url = profile_url[:-1]
        return profile_url

    def profile_url_to_json_filename(self, profile_url):
        """
        Convert the profile URL to a file name.
        """
        clean_url = self.profile_url_clean(profile_url)
        json_filename = clean_url.split('/')[-1] + '.json'
        return json_filename


    def save_data_to_json(self,json_data, folder,json_filename):
        """
        Save the JSON data to a file.
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_name = f"{folder}/{json_filename}"
        with open(file_name, "w") as f:
            json.dump(json_data, f, indent=4)
        print(f"Json Data saved to {file_name}")


    def search_filter(self, page=1, name=None, job_title=None, company=None, reveal_info=False,folder="./search_filter"):
        url = "https://api.contactout.com/v1/people/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "basic",
            "token": self.api_token
        }
        data = {
            "page": page,
            "current_company_only": False,
            "reveal_info": reveal_info
        }
        if name:
            data["name"] = name

        if job_title:
            data["job_title"] = [job_title]

        if company:
            data["company"] = [company]

        try:
            response = requests.post(url, headers=headers, json=data, verify=False)
            response.raise_for_status()  # 检查请求是否成功
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("An Error Occurred:", err)
        else:
            self.save_data_to_json(response.json(), folder, f"{page}_{name}_{job_title}_{company}.json")


    def search_people(self, search_params):
        """
        Search for people using the ContactOut API.
        :param search_params: A dictionary of search parameters.
        :return: A list of matching people.
        """
        url = f"https://api.contactout.com/v1/people/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "basic",
            "token": self.api_token
        }

        try:
            response = requests.post(url, headers=headers, json=search_params)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Request error occurred: {err}")

        return None  # Return None or handle the error as needed


    def base_request(self, url, max_retries=3, backoff_factor=1.0):
        """
        Enrich LinkedIn profile data using ContactOut API.

        Args:
            url (str): URL to request.
            max_retries (int): Maximum number of retries on failure.
            backoff_factor (float): Backoff factor for retries.

        Returns:
            dict: Enriched profile data.

        Raises:
            Exception: If the request fails after the maximum number of retries.
        """

        headers = {
            "authorization": "basic",
            "token": self.api_token
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
                return response.json()
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
            except requests.exceptions.RequestException as err:
                print(f"Request error occurred: {err}")

            # Exponential backoff
            sleep_time = backoff_factor * (2 ** attempt)
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

        raise Exception(f"Failed to fetch profile data after {max_retries} retries")

    def usage_status(self):
        """
        Returns the API usage information.

        Returns:
            dict: API usage information.
        """
        url = "https://api.contactout.com/v1/stats?period=2025-01"
        result = self.base_request(url)
        self.format_json(result)
        return result

    def search_profile_by_linkedin_url(self, profile_url,profile_only='true',folder='./linkedin_profile'):
        """
        Searches for a profile by LinkedIn URL.

        Args:
            profile_url (str): LinkedIn profile URL.

        Returns:
            dict: Enriched profile data.
        """
        # if folder not exists, create it
        if not os.path.exists(folder):
            os.makedirs(folder)

        json_filename = self.profile_url_to_json_filename(profile_url)
        # Check if the JSON file already exists
        if os.path.exists(f"{folder}/{json_filename}"):
            print(f"Skipping: {json_filename} already exists. ")
            return

        url = f"https://api.contactout.com/v1/linkedin/enrich?profile={profile_url}&profile_only={profile_only}"
        result = self.base_request(url)
        self.format_json(result)
        self.save_data_to_json(result,folder,json_filename)
        return result

    def search_linkedin_url_by_email(self, email):
        """
        Searches for a LinkedIn URL by email address.

        Args:
            email (str): Email address.

        Returns:
            linkedin_url.
        """
        url = f"https://api.contactout.com/v1/people/person?email={email}"
        result = self.base_request(url)
        self.format_json(result)
        return result

    def search_linkedin_profile_by_email(self, email):
        """
        Searches for a LinkedIn profile by email address.

        Args:
            email (str): Email address.

        Returns:
            dict: Enriched LinkedIn profile data.
        """
        url = f"https://api.contactout.com/v1/email/enrich?email={email}"
        result = self.base_request(url)
        self.format_json(result)
        return result

    def search_email_by_linkedin_url(self, linkedin_url):
        """
        Searches for an email address by LinkedIn URL.

        Args:
            linkedin_url (str): LinkedIn URL.

        Returns:
            dict: Enriched LinkedIn profile data.
        """

        url = f"https://api.contactout.com/v1/people/linkedin?profile={linkedin_url}&include_phone=false"
        result = self.base_request(url)
        self.format_json(result)
        return result



