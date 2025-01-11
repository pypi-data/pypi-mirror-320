#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
from epic_api_client.SimpleHttpClient import SimpleHttpClient
from epic_api_client.JWTGenerator import JWTGenerator
import requests
import warnings
import importlib


class EPICHttpClient(SimpleHttpClient):
    def __init__(
        self,
        base_url: str = None,
        headers: dict = None,
        client_id: str = None,
        jwt_generator: JWTGenerator = None,
    ):
        super().__init__(base_url, headers)
        self.set_header("Epic-Client-ID", client_id)
        if not self.base_url:
            print("No base URL provided, using sandbox URL")
            self.base_url = (
                "https://vendorservices.epic.com/interconnect-amcurprd-oauth"
            )
        else:
            print("base url: ", self.base_url)
        self.jwt_generator = jwt_generator
        self.client_id = client_id
        self.dino = "Mrauw!"

    def set_token(self, token: str):
        self.set_header("Authorization", f"Bearer {token}")
        self.set_header("Accept", "application/fhir+json")

    def obtain_access_token(self) -> dict:
        print("obtaining access token...")
        token_endpoint = self.base_url + "/oauth2/token"
        # Generate JWT
        jwt_token = self.jwt_generator.create_jwt(self.client_id, token_endpoint)

        # Set up the POST request data
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_token,
        }

        # POST the JWT to the token endpoint
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(token_endpoint, data=data, headers=headers)
        response_data = response.json()
        # Check for successful response
        if response.status_code == 200:
            print("authentication successful")
            self.access_token = response_data.get("access_token")
            self.set_token(self.access_token)
            # self.set_header('prefer', 'return=representation')
            if "scope" in response_data:
                print("scope of client id: ", response_data["scope"])
            else:
                print("no scope of client id available")
            return response.json()  # Returns the access token and other data
        else:
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)
            response.raise_for_status()

    def print_json(self, json_object: dict):
        """
        Prints a JSON object in a readable, formatted way.

        Args:
        json_object (dict): The JSON object to be printed.
        """
        formatted_json = dumps(json_object, indent=2, sort_keys=True)
        print(formatted_json)
