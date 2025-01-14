import requests
import time
import logging
import requests_oauth2client

from requests_oauth2client import OAuth2Client, OAuth2ClientCredentialsAuth, ClientSecretBasic

from .QingpingDevice import QingpingDevice
from .QingpingDeviceProperty import QingpingDeviceProperty

_LOGGER = logging.getLogger(__name__)

class QingpingCloud:
  OAUTH_TOKEN_URL = 'https://oauth.cleargrass.com/oauth2/token'
  API_URL_PREFIX = 'https://apis.cleargrass.com/v1/apis'
  
  def _api_get(self, endpoint) -> dict:
    timestamp=int(time.time()*1000)
    if "?" in endpoint:
      url=f"{self.API_URL_PREFIX}/{endpoint}&timestamp={timestamp}"
    else:
      url=f"{self.API_URL_PREFIX}/{endpoint}?timestamp={timestamp}"
    
    api_request = requests.get(
      url,
      auth=self._auth
    )
    
    api_response={}
    if api_request.ok:
      try:
        api_response=api_request.json()
      except Exception as e:
        raise APIConnectionError(f"Error parsing data: {e}")
    else:
      raise APIAuthError(f"Error getting data: {api_request.status_code}")
      
    return api_response
  
  def get_token(self) -> str|None:
    """ Helper only for CLI: get last auth token """
    if self.is_connected():
      return self._auth.token.access_token
    else:
      return None
  
  def get_devices(self) -> list[QingpingDevice]:
    api_response=self._api_get("devices")
    raw_devices=api_response.get("devices", [])
    devices = []
    for raw_device in raw_devices:
      data = {}
      for property_name, property_data in raw_device["data"].items():
        data[property_name] = QingpingDeviceProperty(
          property=property_name,
          value=property_data.get("value", None),
          status=property_data.get("status", 0)
        )
      device = QingpingDevice(
        name=raw_device["info"]["name"],
        mac=raw_device["info"]["mac"],
        group_id=raw_device["info"]["group_id"],
        group_name=raw_device["info"]["group_name"],
        status_offline=raw_device["info"]["status"]["offline"],
        version=raw_device["info"]["version"],
        created_at=raw_device["info"]["created_at"],
        product_id=raw_device["info"]["product"]["id"],
        product_name=raw_device["info"]["product"]["name"],
        product_en_name=raw_device["info"]["product"]["en_name"],
        setting_report_interval=raw_device["info"]["setting"]["report_interval"],
        setting_collect_interval=raw_device["info"]["setting"]["collect_interval"],
        data=data
      )
      devices.append(device)

    return devices
  
  def connect(self, force=False) -> bool:
    if not force and self.is_connected():
      return True
    
    try:
      self._auth.renew_token()
    except requests_oauth2client.exceptions.InvalidClient as e:
      raise APIAuthError(f"Error getting token ({e})")
    except Exception as e:
      raise APIConnectionError(f"Error connecting to API ({e})")
    
    return True
  
  def disconnect(self) -> bool:
    self._auth.forget_token()
    return True
  
  def is_token_expired(self) -> bool|None:
    return self._auth.token.is_expired()
  def is_connected(self) -> bool:
    if self._auth.token and not self._auth.token.is_expired():
      return True
    else:
      return False
  
  def __init__(self, app_key, app_secret, access_token=None) -> None:
    self._app_key = app_key
    self._app_secret = app_secret
    self._oauth2client = OAuth2Client(
      token_endpoint=self.OAUTH_TOKEN_URL,
      auth=ClientSecretBasic(self._app_key, self._app_secret)
    )
    self._auth = OAuth2ClientCredentialsAuth(
      self._oauth2client, 
      scope="device_full_access",
      token=access_token
    )

class APIAuthError(Exception):
    """Exception class for auth error."""

class APIConnectionError(Exception):
    """Exception class for connection error."""