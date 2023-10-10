from dsp_permissions_scripts.models.doap import Doap

class DspConnectionServiceMock:
    def get_all_doaps_of_project(
        self,
        project_iri: str,
        host: str,
        token: str,
    ) -> list[Doap]:
        return []

def test_get_all_doaps_of_project() -> None:
    dsp_connection = 
    
