class Hosts:
    """Helper class to deal with the different DSP environments."""

    LOCALHOST = "http://0.0.0.0:3333"
    PROD = "https://api.dasch.swiss"
    DEV = "https://api.dev.dasch.swiss"

    @staticmethod
    def get_host(identifier: str) -> str:
        match identifier:
            case "localhost":
                return Hosts.LOCALHOST
            case "prod":
                return Hosts.PROD
            case _:
                return f"https://api.{identifier}.dasch.swiss"
