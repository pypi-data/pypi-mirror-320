# Qingping IoT (cloud)

Library for accessing cloud service of Qingping IoT (instead of Bluetooth).

## Background

This is designed for users who:

- have Qingping IoT supported devices
  - see [docs](https://developer.qingping.co/cloud-to-cloud/specification-guidelines#2-products-list-and-support-note) for full list
  - boils down to ones with native Wi-Fi and selected BT-only via Qingping gateway
- do not want to use Bluetooth to poll devices directly
  - at least 2nd generation of Qingping Air Monitor does not have BT at all
  - for larger houses and offices it's problematic to set up several non-Qingping BT gateways
- do not want to "privatize" devices
  - said operation eliminates access from Qingping IoT mobile app and ability to upgrade firmware
  - it requires local MQTT server and all responsibility is shifted on user

This library is mainly created for use with Home Assistant integration (not yet implemented), but also offers CLI.

The scope of APIs implemented is shown in [API.md](./API.md).

## How to get credentials

Normal users have static *App Key* and *App Secret* tied to their account. 

1. register on [qingpingiot.com](https://www.qingpingiot.com)
2. download mobile app linked there
3. bind devices in app
4. go back to [qingpingiot.com](https://www.qingpingiot.com/devices) and validate that you see all the devices
5. log in to [developer.qingping.co](https://developer.qingping.co/personal/permissionApply) using the same credentials as for the app
6. go to [Access Management](https://developer.qingping.co/personal/permissionApply) and get credentials

---

## Install

[![PyPI: qingping-iot-cloud](https://img.shields.io/pypi/v/qingping_iot_cloud?style=flat-square&label=PyPI%3A%20qingping-iot-cloud)](https://pypi.org/project/qingping-iot-cloud/)

```bash
pip install qingping-iot-cloud
```

## CLI usage

```bash
export QINGPINGIOT_APPKEY=...
export QINGPINGIOT_APPSECRET=...
qingping-iot-cloud -h
qingping-iot-cloud list_devices
```

example response from `list_devices`:

```
AAAAAAAAAAAA: sensor_A (CO2& Temp & RH Monitor)
  timestamp: 1735593815 
  battery: 100 %
  signal: -61 dBm
  temperature: 21.4 °C
  humidity: 56 %
  co2: 959 ppm
BBBBBBBBBBBB: sensor_B (CO2& Temp & RH Monitor)
  timestamp: 1735593520 
  battery: 100 %
  signal: -47 dBm
  temperature: 24.4 °C
  humidity: 42 %
  co2: 876 ppm
CCCCCCCCCCCC: sensor_C (Qingping Air Monitor Lite)
  timestamp: 1735593600 
  battery: 100 %
  temperature: 26.4 °C
  humidity: 44.3 %
  co2: 1053 ppm
  pm25: 12 μg/m³
  pm10: 12 μg/m³
```
