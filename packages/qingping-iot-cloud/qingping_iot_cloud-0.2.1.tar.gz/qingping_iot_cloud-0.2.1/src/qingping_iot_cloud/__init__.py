import argparse
import os
import sys
import importlib.metadata
from .QingpingCloud import QingpingCloud

def main():
  parser = argparse.ArgumentParser(description=f"Qingping IoT Cloud - {importlib.metadata.version("qingping_iot_cloud")}")
  parser.add_argument("action", 
    choices=[
      "get_token", 
      "list_devices",
    ], 
    help="Action to perform"
  )
  args = parser.parse_args()
  
  app_key = os.getenv("QINGPINGIOT_APPKEY")
  app_secret = os.getenv("QINGPINGIOT_APPSECRET")
  
  if not app_key or not app_secret:
    print("Env variables QINGPINGIOT_APPKEY or QINGPINGIOT_APPSECRET not set")
    sys.exit(1)
  
  try:
    cloud = QingpingCloud(app_key, app_secret)
    cloud.connect()
  except Exception as e:
    print(f"Error creating QingpingCloud: {e}")
    sys.exit(1)
  
  if args.action == "get_token":
    token=cloud.get_token()
    print(f"Token: {token}")
  elif args.action == "list_devices":
    devices=cloud.get_devices()
    for device in devices:
      print(device)
      for property in device.data.keys():
        print(f"  {device.get_property(property)}")

if __name__ == "__main__":
  main()
