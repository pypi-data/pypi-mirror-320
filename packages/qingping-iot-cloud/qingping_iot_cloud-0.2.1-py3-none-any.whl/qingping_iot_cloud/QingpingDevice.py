from dataclasses import dataclass
from .QingpingDeviceProperty import QingpingDeviceProperty

@dataclass
class QingpingDevice:
  # following naming convention from https://developer.qingping.co/cloud-to-cloud/open-apis#13-device-list
  name: str
  mac: str
  group_id: str
  group_name: str
  status_offline: bool
  version: str # firmware
  created_at: str
  product_id: str
  product_name: str
  product_en_name: str
  setting_report_interval: int
  setting_collect_interval: int
  data: dict[QingpingDeviceProperty]

  def __str__(self) -> str:
    return f"{self.mac}: {self.name} ({self.product_en_name})"
  def get_property(self, property_name: str) -> QingpingDeviceProperty:
    if property_name in self.data:
      return self.data[property_name]
    elif property_name in QingpingDeviceProperty.DEV_PROP_SPEC:
      return QingpingDeviceProperty(
        property=property_name,
        value=None,
        status=0
      )
    else:
      return QingpingDeviceProperty(
        property="UNSUPPORTED",
        value=None,
        status=0
      )
