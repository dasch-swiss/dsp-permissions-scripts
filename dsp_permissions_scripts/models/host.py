class Hosts:
    """Helper class to deal with the different DSP environments."""

    LOCALHOST = "localhost:3333"
    PROD = "api.dasch.swiss"
    TEST = "api.test.dasch.swiss"
    DEV = "api.dev.dasch.swiss"
    LS_PROD = "api.ls-prod.admin.ch"
    STAGE = "api.stage.dasch.swiss"

    @staticmethod
    def get_host(identifier: str) -> str:
        match identifier:
            case "localhost":
                return Hosts.LOCALHOST
            case "prod":
                return Hosts.PROD
            case _:
                return f"api.{identifier}.dasch.swiss"
