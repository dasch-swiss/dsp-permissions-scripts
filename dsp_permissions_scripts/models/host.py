class Hosts:
    """Helper class to deal with the different DSP environments."""

    LOCALHOST = "http://0.0.0.0:3333"
    PROD = "https://api.dasch.swiss"
    DEV = "https://api.dev.dasch.swiss"
    STAGE = "https://api.stage.dasch.swiss"
    RDU = "https://api.rdu.dasch.swiss"

    @staticmethod
    def get_host(identifier: str) -> str:
        match identifier:
            case "localhost":
                return Hosts.LOCALHOST
            case "prod":
                return Hosts.PROD
            case "stage":
                return Hosts.STAGE
            case "dev":
                return Hosts.DEV
            case "rdu":
                return Hosts.RDU
            case _:
                return f"https://api.{identifier}.dasch.swiss"
