import asyncio
import copy
import json
import time
import aiohttp
import requests
from salesmanago_tools.utils.constants import export_url, job_status_url, export_pages_url, import_url, contact_list_url
from salesmanago_tools.service.sales_manago_actions import create_import_payload, get_file, process_data_to_csv


class SalesmanagoBaseClient:
    def __init__(self, clientId: str, apiKey: str, sha: str, owner: str, account_name: str | None = None):
        """
        Initialize the SalesmanagoBaseClient with required credentials.

        :param clientId: Client ID for authentication with the Salesmanago API.
        :param apiKey: API key for authentication.
        :param sha: Security hash for additional validation.
        :param owner: Owner email address for account management.
        :param account_name: Optional account name (default is None).
        """
        self.api_key = apiKey
        self.sha = sha
        self.client_id = clientId
        self.owner_email = owner
        self.account_name = account_name
    
    async def _wait_for_response(self, job_status_url: str, payload: dict) -> str:
        """
        Wait for the export task to complete and retrieve a link to the generated file.

        :param job_status_url: The URL for checking the status of the job.
        :param payload: The request payload containing the necessary information to check the job status.
        :return: A string URL of the file once the export task is completed.
        """
        while True:
            response_data = await self._post_request(job_status_url, payload)
            if response_data.get("message") == []:
                file_url = response_data.get("fileUrl")
                print("FILE URL: ", file_url)
                return file_url
            await asyncio.sleep(5)

    async def _post_request(self, url: str, payload: dict) -> dict:
        """
        Send a POST request to the API and return a JSON response.

        :param url: The URL to which the POST request will be sent.
        :param payload: The data to be sent in the POST request body, typically in JSON format.
        :return: A dictionary containing the parsed JSON response from the API.
        """
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(await response.text())
                print("RESPONSE: ", await response.json(), flush=True)
                return await response.json()

    async def _check_job_status(self, request_id):
        """
        Check the job status and retrieve the file URL once the job is completed.

        :param request_id: The ID of the job to check the status for.
        :return: The file URL of the completed job.
        """
        job_status_payload = {
            "clientId": self.client_id,
            "apiKey": self.api_key,
            "requestTime": int(time.time()),
            "sha": self.sha,
            "owner": self.owner_email,
            "requestId": request_id,
        }
        return await self._wait_for_response(job_status_url, job_status_payload)


class SalesmanagoDataClient(SalesmanagoBaseClient):
    async def export_data(self, value: str, addresseeType: str = "tag"):
        """
        Initiates the export process for specific data and returns the data as a CSV generator.

        :param value: The value associated with the export, such as an email or tag.
        :param addresseeType: The type of recipient (default is "tag").
        :return: A CSV generator containing the exported data.
        """
        export_request_payload = {
            "clientId": self.client_id,
            "apiKey": self.api_key,
            "requestTime": int(time.time()),
            "sha": self.sha,
            "owner": self.owner_email,
            "contacts": [
                {"addresseeType": addresseeType, "value": value},
            ],
            "data": [
                {"dataType": "CONTACT"},
                {"dataType": "TAG"},
                {"dataType": "EXT_EVENT"},
                {"dataType": "VISITS"},
                {"dataType": "EMAILS"},
                {"dataType": "FUNNELS"},
                {"dataType": "NOTES"},
                {"dataType": "TASKS"},
                {"dataType": "COUPONS"},
                {"dataType": "SMS"},
                {"dataType": "CONSENTS"},
                {"dataType": "PROPERTIES"},
                {"dataType": "DICTIONARY_PROPERTIES"}
            ]
        }
        try:
            export_response = await self._post_request(export_url, export_request_payload)
            print("EXPORT RESPONSE: ", export_response, flush=True)
            request_id = export_response.get("requestId")
            if not request_id:
                raise ValueError("Failed to get requestId")

            file_url = await self._check_job_status(request_id)

            file_content = await get_file(file_url)

            csv_generator = process_data_to_csv(file_content)

            return csv_generator

        except aiohttp.ClientError as e:
            raise Exception(f"Error executing request: {str(e)}")

    async def fetch_all_contacts_from_salesmanago(self, page_size: int = 1000, page: int = 1):
        """
        Fetches all contacts from SalesManago and returns them as a list.

        :param page_size: The number of contacts to retrieve per request (default is 1000).
        :param page: The page number to fetch (default is 1).
        :return: A list of contacts, with each contact formatted as a list of details.
        """
        contacts_list = []

        try:
            while True:
                export_pages_payload = {
                    "clientId": self.client_id,
                    "apiKey": self.api_key,
                    "requestTime": int(time.time()),
                    "sha": self.sha,
                    "owner": self.owner_email,
                    "page": page,
                    "size": page_size,
                }

                export_response = await self._post_request(export_pages_url, export_pages_payload)
                request_id = export_response.get("requestId")

                print(f"REQUEST_ID: {request_id}. EXPORT_PAGES_PAYLOAD: {export_pages_payload}", flush=True)

                if not request_id:
                    print("Export initiation failed. Message:", export_response.get("message", []))
                    break

                file_url = await self._check_job_status(request_id)

                file_content = await get_file(file_url)
                contacts = json.loads(file_content)

                if not isinstance(contacts, dict) or "contacts" not in contacts or not contacts["contacts"]:
                    break

                for item in contacts["contacts"]:
                    if isinstance(item, dict):
                        formatted_contact = [
                            item.get("success"),
                            item.get("email"),
                            item.get("exists"),
                            item.get("id", None),
                            item.get("name", None),
                            item.get("country", None),
                            item.get("phone", None),
                        ]
                        contacts_list.append(formatted_contact)
                    else:
                        print("BAD ITEM: ", item, flush=True)

                print(f"Page {page}: Retrieved {len(contacts['contacts'])} contacts.", flush=True)
                page += 1

            return contacts_list

        except Exception as e:
            raise Exception(f"Unexpected error occurred: {e}")

    async def push_people_to_salesmanago(self, people_list_to_push: list[dict], tags: list[str] = []):
        """
        Pushes a list of people to Salesmanago for upsert, handling each person's details and tags.

        :param people_list_to_push: A list of people data (dictionaries) ("Email", "Phone", "Country", "City", "Name", "properties") to push to Salesmanago.
        :param tags: A list of tags to associate with each person (default is an empty list).
        :return: None
        """
        upsert_details = []
        for person in people_list_to_push:
            try:
                payload = await create_import_payload(row=person, tags=tags)
                upsert_details.extend(payload["upsertDetails"])

            except Exception as e:
                raise Exception(f"Error creating payload for row: {e}")

        batch_payload = {
            "apiKey": self.api_key,
            "sha": self.sha,
            "clientId": self.client_id,
            "owner": self.owner_email,
            "requestTime": int(time.time()),
            "upsertDetails": upsert_details,
        }

        import_response = await self._post_request(import_url, batch_payload)
        print("import_response: ", import_response, flush=True)
        request_id = import_response.get("requestId")
        if not request_id:
            raise ValueError("Failed to get requestId")
        
        return None

    async def update_tag_salesmanago(self, email: str, tags: list):
        """
        Updates the tags for a specific contact in Salesmanago.

        :param email: The email of the contact whose tags are to be updated.
        :param tags: A list of tags to assign to the contact.
        :return: None
        """
        tags = copy.deepcopy(tags)
        payload = {
            "clientId": self.client_id,
            "apiKey": self.api_key,
            "requestTime": int(time.time()),
            "sha": self.sha,
            "owner": self.owner_email,
            "upsertDetails": [
                {
                    "contact": {
                        "email": email
                    }
                }
            ],
        }

        if tags is not None and tags:
            payload["upsertDetails"][0]["tags"] = tags

        try:
            response = await self._post_request(import_url, payload=payload)
            print("RESPONSE: ", response, flush=True)

            return None

        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        
    async def update_standard_details_salesmanago(self, email: str, properties: dict):
        """
        Updates the standard_details for a specific contact in Salesmanago.

        :param email: The email of the contact whose tags are to be updated.
        :param properties: A dictionary of properties to assign to the contact.
        :return: None
        """
        properties = copy.deepcopy(properties)
        payload = {
            "clientId": self.client_id,
            "apiKey": self.api_key,
            "requestTime": int(time.time()),
            "sha": self.sha,
            "owner": self.owner_email,
            "upsertDetails": [
                {
                    "contact": {
                        "email": email
                    }
                }
            ],
        }

        if properties is not None and properties:
            payload["upsertDetails"][0]["properties"] = properties

        try:
            response = await self._post_request(import_url, payload=payload)
            print("RESPONSE: ", response, flush=True)

            return None

        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    async def get_contact_info_by_email(self, contact_email: str):
        """
        Retrieves detailed contact information by email from Salesmanago.

        :param contact_email: The email of the contact to retrieve information for.
        :return: A dictionary with contact details including name, company, tags, and other properties.
        """
        payload = {
            "clientId": self.client_id,
            "apiKey": self.api_key,
            "requestTime": int(time.time()),
            "sha": self.sha,
            "owner": self.owner_email,
            'email': [contact_email]
        }

        try:
            response_data = await self._post_request(contact_list_url, payload=payload)
            data = response_data.get('contacts', [{}])[0]

            return data
            # name = data.get('name')
            # dct = data.get('properties', {})
            # result = {item['name']: item['value'] for item in dct}
            # traffic = round_to_thousands(result.get('traffic'))
            # keywords = round_to_thousands(result.get('keywords'))
            # package = round_to_thousands(result.get('package'))
            # clients = round_to_thousands(result.get('clients'))
            # package_short = round_to_thousands(result.get('package_short'))

            # return_value = {
            #     "Name": name,
            #     "CompanyName": data.get('company'),
            #     "traffic": traffic,
            #     "keywords": keywords,
            #     "package": package,
            #     "tags": [x.get('tag') for x in data.get('contactTags', [])],
            #     "clients": clients,
            #     "package_short": package_short
            # }
            # return return_value
        except requests.RequestException as e:
            raise Exception(f"Failed to retrieve contact details: {e}")
        except IndexError as e:
            return {"message": "Contact not found"}