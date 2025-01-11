from genx_ai_camera_panel.db import DB
from onvif.onvif_client import OnvifClient, WsDiscoveryClient


class OnvifWrapper:
    db: DB

    def __init__(self) -> None:
        self.db = DB()

    def scan(self):
        """
        Scan for available ONVIF devices.

        Returns:
            A list of dictionaries, each containing the device's IP address,
            port, and protocol (TCP or UDP).
        """

        wsd_client = WsDiscoveryClient()
        nvts = wsd_client.search()

        for nvt in nvts:
            try:
                onvif_client = OnvifClient(
                    nvt.ip_address,
                    nvt.port,
                    self.db.get("username"),
                    self.db.get("password"),
                )

                device_information = onvif_client.get_device_information()
                if device_information is None:
                    continue

                manufacturer = device_information["Manufacturer"] or ""
                model = device_information["Model"] or ""
                firmware_version = device_information["FirmwareVersion"] or ""
                serial_number = device_information["SerialNumber"] or ""
                hardware_id = device_information["HardwareId"] or ""

                profile_tokens = onvif_client.get_profile_tokens()
                video_configurations = onvif_client.get_video_encoder_configurations()

                for index, profile_token in enumerate(profile_tokens):
                    stream_url = onvif_client.get_streaming_uri(profile_token)
                    video_configuration = video_configurations[index]
                    resolution = f"{video_configuration['Resolution']['Width']}x{video_configuration['Resolution']['Height']}"
                    fps = video_configuration["RateControl"]["FrameRateLimit"]
                    bitrate = video_configuration["RateControl"]["BitrateLimit"]
                    encoding = video_configuration["Encoding"]

                    self.db.add_camera(
                        nvt.ip_address,
                        nvt.port,
                        stream_url,
                        profile_token,
                        manufacturer,
                        model,
                        firmware_version,
                        serial_number,
                        hardware_id,
                        resolution,
                        fps,
                        bitrate,
                        encoding,
                    )
            except Exception as exception:
                print(exception)

        wsd_client.dispose()
