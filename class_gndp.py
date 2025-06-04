# Python existing libraries
import requests
import json
import yaml

# The _output_raw member holds the raw output of the request
# To access relevant parts of the output / json, classes uses Python @property decorators
class class_gndp:

    # PROPERTY DECORATORS
    # ------------------------------------------------------------
    @property
    def device(self):
        return self._output_raw["devices"]

    @property
    def ssnow_meta(self):
        return self._output_raw["devices"][0]["servicenow_metadata"]

    @property
    def fqdn(self):
        return self._output_raw["devices"][0]["fqdn"]
    
    @property
    def software_version(self):
        return self._output_raw["devices"][0]["software_version"]

    @property
    def management_ip(self):
        return self._output_raw["devices"][0]["management_ip"]
    
    @property
    def interfaces(self):
        return self._output_raw["devices"][0]["interfaces"]
    
    @property
    def lldp(self):
        return self._output_raw["devices"][0]["lldp"]
    

    # CLASS FUNCTIONS
    # ------------------------------------------------------------
    
    # Class constructor
    def __init__(self, yaml_fname: str):

        self._ssoauth_url = "https://sso.gdcorp.tools/v1/api/token" 
        self._gndp_url = "https://gndp.int.gdcorp.tools/"
        self._output_raw: None
        
        # Return content of yaml file;
        # in this case this contains the service accounts
        with open(yaml_fname, 'r') as f:
            self._svc_acct = yaml.safe_load(f)


    # Python default method called for printing the object
    # Printing the object will in fact, print the output of the request
    def __str__(self):
        return json.dumps(self._output_raw, indent=4)
    

    # Internal method to get the sso_token; this should never be called 
    # from outside the class - this is to maintain class transparency and encapsulation
    def _get_sso_token(self):
        username = self._svc_acct["svc_acct"]["uname"]
        password = self._svc_acct["svc_acct"]["passwd"]
        realm = self._svc_acct["svc_acct"]["realm"]
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "username": username,
            "password": password,
            "realm": realm
        })  

        response = requests.post(self._ssoauth_url, headers=headers, data=payload)
        sso_token = response.json()['data']

        return sso_token
        

    # The names of the functions will be a direct reflection of the API methods here:
    # https://gndp.int.gdcorp.tools/ -> device, search, etc. ... 
    def dev_search(self, dev_fqdn):
        params = {
                "fqdn": f"{dev_fqdn}"
        }
    
        # A NEW TOKEN WILL ALWAYS BE GENERATED TO AVOID THE CASE OF THE TOKEN EXPIRING
        sso_token = self._get_sso_token() 
        headers = {
            "X-API-KEY": sso_token,
            'Content-Type': 'application/json'
            # 'Authorization': f'sso-jwt {sso_token}' 
        }

        # Different operations match different URLs ...
        # For instance, to search, we used /search at the end; to query device, we use /device; etc.
        ops_url_append = "search/"

        response = requests.request("GET", f"{self._gndp_url}{ops_url_append}", headers=headers, params=params)
        self._output_raw = response.json()
        
        return self._output_raw
  