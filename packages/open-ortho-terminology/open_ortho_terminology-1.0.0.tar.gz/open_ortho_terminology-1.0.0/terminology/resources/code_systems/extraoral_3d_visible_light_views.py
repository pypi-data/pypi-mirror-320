from fhir.resources.codesystem import CodeSystem, CodeSystemConcept
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code


class Extraoral3DVisibleLightViewsCodeSystem(CodeSystem):

    @classmethod
    def static_url(cls) -> str:
        ns = OpenOrthoNamingSystem()
        return f"{ns.url}/extraoral-3d-visible-light-views"

    def __init__(self):
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            url=self.static_url(),
            version="1.0.0",
            name="Extraoral3DVisibleLightViews",
            title="Extraoral 3D Visible Light Views",
            status="draft",
            experimental=True,
            date=datetime.now().date().isoformat(),
            publisher="Open Ortho",
            description="Common extraoral 3D visible light views used in an orthodontic provider's practice, producing a 3D surface of the head and neck",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


EV3D01 = CodeSystemConcept(
    code=f"{make_code('EV3D01')}",
    display="EV3D-01 EO.WH.LC.CO",
    definition="Whole head, lips closed, centric occlusion",
)

EV3D02 = CodeSystemConcept(
    code=f"{make_code('EV3D02')}",
    display="EV3D-02 EO.WH.LC.CR",
    definition="Whole head, lips closed, centric relation",
)

EV3D03 = CodeSystemConcept(
    code=f"{make_code('EV3D03')}",
    display="EV3D-03 EO.WH.LR.CO",
    definition="Whole head, lips relaxed, centric occlusion",
)

EV3D04 = CodeSystemConcept(
    code=f"{make_code('EV3D04')}",
    display="EV3D-04 EO.WH.LR.CR",
    definition="Whole head, lips relaxed, centric relation",
)

EV3D05 = CodeSystemConcept(
    code=f"{make_code('EV3D05')}",
    display="EV3D-05 EO.WH.FS.CO",
    definition="Whole head, full smile, centric occlusion",
)

EV3D06 = CodeSystemConcept(
    code=f"{make_code('EV3D06')}",
    display="EV3D-06 EO.WH.FS.CR",
    definition="Whole head, full smile, centric relation",
)
