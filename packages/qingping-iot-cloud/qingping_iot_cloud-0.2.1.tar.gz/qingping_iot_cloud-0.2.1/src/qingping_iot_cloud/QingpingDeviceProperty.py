import datetime
from dataclasses import dataclass

@dataclass
class QingpingDeviceProperty:
  property: str
  value: int | float # raw value from API
  status: int
  
  # this must be kept in sync between API spec at https://developer.qingping.co/cloud-to-cloud/specification-guidelines#2-products-list-and-support-note
  # and HomeAssistant SensorClass consts at https://github.com/home-assistant/core/blob/master/homeassistant/components/sensor/const.py
  # and HomeAssistant Unit consts at https://github.com/home-assistant/core/blob/master/homeassistant/const.py
  DEV_PROP_SPEC = {
    "battery": {
      "ha_class": "battery",
      "ha_title": "Battery",
      "unit": "%", 
      "desc": "device battery", 
      "status": {
        0: "not plug in power", 
        1: "plug in power and in charging",
        2: "plug in power and 100%"
      }
    },
    "signal": {
      "ha_class": "signal_strength",
      "ha_title": "Wi-Fi RSSI",
      "unit": "dBm", 
      "desc": "device signal", 
      "status": None
    },
    "timestamp": {
      "ha_class": "timestamp",
      "ha_title": "last updated",
      "unit": None, 
      "desc": "time of the message", 
      "status": None
    },
    "temperature": {
      "ha_class": "temperature",
      "ha_title": "Temperature",
      "unit": "°C", 
      "desc": "value of temperature sensor", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "prob_temperature": {
      "ha_class": "temperature",
      "ha_title": "External Temperature",
      "unit": "°C", 
      "desc": "value of external temperature sensor", 
      "status": None
    },
    "humidity": {
      "ha_class": "humidity",
      "ha_title": "Humidity",
      "unit": "%", 
      "desc": "value of humidity sensor", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "pressure": {
      "ha_class": "pressure",
      "ha_title": "Pressure",
      "unit": "kPa", 
      "desc": "value of pressure sensor", 
      "status": None
    },
    "pm10": {
      "ha_class": "pm10",
      "ha_title": "PM10",
      "unit": "μg/m³", 
      "desc": "PM10", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "pm50": {
      "ha_class": None,
      "ha_title": "PM5.0",
      "unit": "μg/m³", 
      "desc": "PM5.0", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "pm25": {
      "ha_class": "pm25",
      "ha_title": "PM2.5",
      "unit": "μg/m³", 
      "desc": "PM2.5", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "co2": {
      "ha_class": "carbon_dioxide",
      "ha_title": "CO2",
      "unit": "ppm", 
      "desc": "CO2", 
      "status": None
    },
    "tvoc": {
      "ha_class": "volatile_organic_compounds_parts",
      "ha_title": "TVOC",
      "unit": "ppb", 
      "desc": "value of TVOC sensor", 
      "status": None
    },
    "tvoc_index": {
      "ha_class": None,
      "ha_title": "TVOC Index",
      "unit": None, 
      "desc": "index of TVOC sensor", 
      "status": None
    },
    "noise": {
      "ha_class": "sound_pressure",
      "ha_title": "Noise",
      "unit": "dB", 
      "desc": "inoise", 
      "status": {
        0: "sensor normal", 
        1: "sensor abnormal",
        2: "sensor in the preparation stage"
      }
    },
    "radon": {
      "ha_class": None,
      "ha_title": "Radon",
      "unit": "pCi/L", 
      "desc": "value of radon sensor", 
      "status": None
    },
    "UNSUPPORTED": {
      "ha_class": None,
      "ha_title": "UNSUPPORTED",
      "unit": "UNSUPPORTED", 
      "desc": "UNSUPPORTED PROPERTY", 
      "status": None
    }
  }

  def get_ha_class(self) -> str:
    """ HomeAssistant compatibility - str base for SensorDeviceClass enum """
    return self.DEV_PROP_SPEC[self.property]["ha_class"]
  def get_ha_title(self) -> str:
    """ HomeAssistant compatibility - human readable property name """
    return self.DEV_PROP_SPEC[self.property]["ha_title"]
  def get_ha_value(self):
    """ HomeAssistant compatibility - value in proper format """
    if self.value is None:
      return None
    
    if self.property == "timestamp":
      return datetime.datetime.fromtimestamp(self.value).astimezone(tz=datetime.timezone.utc)
    elif self.property in ["tvoc_index","battery"]:
      return int(self.value)
    else:
      return float(self.value)
  
  def get_unit(self) -> str:
    return self.DEV_PROP_SPEC[self.property]["unit"]
  def get_desc(self) -> str:
    return self.DEV_PROP_SPEC[self.property]["desc"]
  def get_status(self) -> str:  
    return self.DEV_PROP_SPEC[self.property]["status"].get(self.status, "Unknown")

  def __str__(self) -> str:
    return f"{self.property}: {self.value} {self.get_unit()}"
