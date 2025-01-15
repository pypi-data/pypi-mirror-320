from tap_api.common.siem.filters import SiemFormat, SiemThreatType, SiemThreatStatus
from tap_api.web.filter_options import FilterOptions, TFilterOptions


class SiemOptions(FilterOptions):
    __FORMAT = "format"
    __THREAT_TYPE = "threatType"
    __THREAT_STATUS = "threatStatus"
    __options: dict[str]

    def __init__(self) -> None:
        super().__init__()

    def set_format(self, format: SiemFormat) -> TFilterOptions:
        self.__options[self.__FORMAT] = format
        return self

    def get_format(self) -> SiemFormat:
        return self.__options[self.__FORMAT]

    def set_threat_type(self, threat_type: SiemThreatType) -> TFilterOptions:
        self.__options[self.__THREAT_TYPE] = threat_type
        return self

    def get_threat_type(self) -> SiemThreatType:
        return self.__options[self.__THREAT_TYPE]

    def set_threat_status(self, threat_status: SiemThreatStatus) -> TFilterOptions:
        self.__options[self.__THREAT_STATUS] = threat_status
        return self

    def get_threat_status(self) -> SiemThreatStatus:
        return self.__options[self.__THREAT_STATUS]
