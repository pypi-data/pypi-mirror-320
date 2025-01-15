from fhir.resources.codesystem import CodeSystem, CodeSystemConcept
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code


class Extraoral2DPhotographicViewsCodeSystem(CodeSystem):

    @classmethod
    def static_url(cls) -> str:
        ns = OpenOrthoNamingSystem()
        return f"{ns.url}/extraoral-2d-photographic-views"

    def __init__(self):
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            url=self.static_url(),
            version="1.0.0",
            name="Extraoral2DPhotographicViews",
            title="Extraoral 2D Photographic Views",
            status="draft",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher="Open Ortho",
            description="Common extraoral 2D photographic views used in an orthodontic provider's practice",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


EV01 = CodeSystemConcept(
    code=f"{make_code('EV01')}",
    display="EV-01, EO.RP.LR.CO",
    definition="Photographic extraoral image of right half of face with lips relaxed and teeth in centric occlusion (record artifact)"
)

EV02 = CodeSystemConcept(
    code=f"{make_code('EV02')}",
    display="EV-02, EO.RP.LR.CR",
    definition="Photographic extraoral image of right half of face with lips relaxed and jaws in centric relation (record artifact)"
)

EV03 = CodeSystemConcept(
    code=f"{make_code('EV03')}",
    display="EV-03, EO.RP.LC.CO, po1",
    definition="Photographic extraoral image of right half of face with lips closed and teeth in centric occlusion (record artifact)"
)

EV04 = CodeSystemConcept(
    code=f"{make_code('EV04')}",
    display="EV-04, EO.RP.LC.CR",
    definition="Photographic extraoral image of right half of face with lips closed and jaws in centric relation (record artifact)"
)

EV05 = CodeSystemConcept(
    code=f"{make_code('EV05')}",
    display="EV-05, EO.RP.FS.CO, prs",
    definition="Photographic extraoral image of right half of face with full smile and teeth in centric occlusion (record artifact)"
)

EV06 = CodeSystemConcept(
    code=f"{make_code('EV06')}",
    display="EV-06, EO.RP.FS.CR",
    definition="Photographic extraoral image of right half of face with full smile and jaws in centric relation (record artifact)"
)

EV07 = CodeSystemConcept(
    code=f"{make_code('EV07')}",
    display="EV-07 EO.RP.MD.PF",
    definition="Extraoral, Right Profile (subject is facing observer's right), Mandible Postured Forward",
)

EV08 = CodeSystemConcept(
    code=f"{make_code('EV08')}",
    display="EV-08, EO.RP.LR.CO.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with lips relaxed and teeth in centric occlusion (record artifact)"
)

EV09 = CodeSystemConcept(
    code=f"{make_code('EV09')}",
    display="EV-09, EO.RP.LR.CR.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with lips relaxed and jaws in centric relation (record artifact)"
)

EV10 = CodeSystemConcept(
    code=f"{make_code('EV10')}",
    display="EV-10, EO.RP.LC.CO.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with lips closed and teeth in centric occlusion (record artifact)"
)

EV11 = CodeSystemConcept(
    code=f"{make_code('EV11')}",
    display="EV-11, EO.RP.LC.CR.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with lips closed and jaws in centric relation (record artifact)"
)

EV12 = CodeSystemConcept(
    code=f"{make_code('EV12')}",
    display="EV-12, EO.RP.FS.CO.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with full smile and teeth in centric occlusion (record artifact)"
)

EV13 = CodeSystemConcept(
    code=f"{make_code('EV13')}",
    display="EV-13, EO.RP.FS.CR.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with full smile and jaws in centric relation (record artifact)"
)

EV14 = CodeSystemConcept(
    code=f"{make_code('EV14')}",
    display="EV-14, EO.RP.MD.PF.45",
    definition="Photographic extraoral image of 45 degree view of right half of face with mandible postured forward (record artifact)"
)

EV15 = CodeSystemConcept(
    code=f"{make_code('EV15')}",
    display="EV-15, EO.FF.LR.CO",
    definition="Photographic extraoral image of full face with lips relaxed and teeth in centric occlusion (record artifact)"
)

EV16 = CodeSystemConcept(
    code=f"{make_code('EV16')}",
    display="EV-16, EO.FF.LR.CR",
    definition="Photographic extraoral image of full face with lips relaxed and jaws in centric relation (record artifact)"
)

EV17 = CodeSystemConcept(
    code=f"{make_code('EV17')}",
    display="EV-17, EO.FF.LC.CO, pfr",
    definition="Photographic extraoral image of full face with lips closed and teeth in centric occlusion (record artifact)"
)

EV18 = CodeSystemConcept(
    code=f"{make_code('EV18')}",
    display="EV-18, EO.FF.LC.CR",
    definition="Photographic extraoral image of full face with lips closed and jaws in centric relation (record artifact)"
)

EV19 = CodeSystemConcept(
    code=f"{make_code('EV19')}",
    display="EV-19, EO.FF.FS.CO, pfs",
    definition="Photographic extraoral image of full face with full smile and teeth in centric occlusion (record artifact)"
)

EV20 = CodeSystemConcept(
    code=f"{make_code('EV20')}",
    display="EV-20, EO.FF.FS.CR",
    definition="Photographic extraoral image of full face with full smile and jaws in centric relation (record artifact)"
)

EV21 = CodeSystemConcept(
    code=f"{make_code('EV21')}",
    display="EV-21, EO.FF.MD.PF",
    definition="Photographic image extraoral with mandible postured forward (record artifact)"
)

EV22 = CodeSystemConcept(
    code=f"{make_code('EV22')}",
    display="EV-22, EO.LP.LR.CO",
    definition="Photographic extraoral image of left half of face with lips relaxed and teeth in centric occlusion (record artifact)"
)

EV23 = CodeSystemConcept(
    code=f"{make_code('EV23')}",
    display="EV-23, EO.LP.LR.CR",
    definition="Photographic extraoral image of left half of face with lips relaxed and jaws in centric relation (record artifact)"
)

EV24 = CodeSystemConcept(
    code=f"{make_code('EV24')}",
    display="EV-24, EO.LP.LC.CO",
    definition="Photographic extraoral image of left half of face with lips closed and teeth in centric occlusion (record artifact)"
)

EV25 = CodeSystemConcept(
    code=f"{make_code('EV25')}",
    display="EV-25, EO.LP.LC.CR",
    definition="Photographic extraoral image of left half of face with lips closed and jaws in centric relation (record artifact)"
)

EV26 = CodeSystemConcept(
    code=f"{make_code('EV26')}",
    display="EV-26, EO.LP.FS.CO",
    definition="Photographic extraoral image of left half of face with full smile and teeth in centric occlusion (record artifact)"
)

EV27 = CodeSystemConcept(
    code=f"{make_code('EV27')}",
    display="EV-27, EO.LP.FS.CR",
    definition="Photographic extraoral image of left half of face with full smile and jaws in centric relation (record artifact)"
)

EV28 = CodeSystemConcept(
    code=f"{make_code('EV28')}",
    display="EV-28 EO.LP.MD.PF",
    definition="Extraoral, Left Profile (subject is facing observer's left), Mandible Postured Forward",
)

EV29 = CodeSystemConcept(
    code=f"{make_code('EV29')}",
    display="EV-29, EO.LP.LR.CO.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with lips relaxed and teeth in centric occlusion (record artifact)"
)

EV30 = CodeSystemConcept(
    code=f"{make_code('EV30')}",
    display="EV-30, EO.LP.LR.CR.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with lips relaxed and jaws in centric relation (record artifact)"
)

EV31 = CodeSystemConcept(
    code=f"{make_code('EV31')}",
    display="EV-31, EO.LP.LC.CO.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with lips closed and teeth in centric occlusion (record artifact)"
)

EV32 = CodeSystemConcept(
    code=f"{make_code('EV32')}",
    display="EV-32, EO.LP.LC.CR.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with lips closed and jaws in centric relation (record artifact)"
)

EV33 = CodeSystemConcept(
    code=f"{make_code('EV33')}",
    display="EV-33, EO.LP.FS.CO.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with full smile and teeth in centric occlusion (record artifact)"
)

EV34 = CodeSystemConcept(
    code=f"{make_code('EV34')}",
    display="EV-34, EO.LP.FS.CR.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with full smile and jaws in centric relation (record artifact)"
)

EV35 = CodeSystemConcept(
    code=f"{make_code('EV35')}",
    display="EV-35, EO.LP.MD.PF.45",
    definition="Photographic extraoral image of 45 degree view of left half of face with mandible postured forward (record artifact)"
)

EV36 = CodeSystemConcept(
    code=f"{make_code('EV36')}",
    display="EV-36, EO.OF.IV",
    definition="Photographic extraoral image of inferior view of face (record artifact)"
)

EV37 = CodeSystemConcept(
    code=f"{make_code('EV37')}",
    display="EV-37 EO.OF.SV",
    definition="Extraoral, Other Face (viewed from above), Superior View (showing forehead, infraorbital rim contour, dorsum of nose, upper lip, chin)",
)

EV38 = CodeSystemConcept(
    code=f"{make_code('EV38')}",
    display="EV-38 EO.OF.CS",
    definition="Extraoral, Other Face, Close-Up Smile (with lips)",
)

EV39 = CodeSystemConcept(
    code=f"{make_code('EV39')}",
    display="EV-39 EO.OF.OC",
    definition="Extraoral, Other Face, Occlusal Cant (e.g., tongue depressor between the teeth)",
)

EV40 = CodeSystemConcept(
    code=f"{make_code('EV40')}",
    display="EV-40 EO.OF.FI",
    definition="Extraoral, Other Face, Forensic Interest (tattoos, jewelry, scars)",
)

EV41 = CodeSystemConcept(
    code=f"{make_code('EV41')}",
    display="EV-41 EO.OF.AN",
    definition="Extraoral, Other Face, Anomalies (ears, skin tags, etc.)",
)

EV42 = CodeSystemConcept(
    code=f"{make_code('EV42')}",
    display="EV-42 EO.FF.MO",
    definition="Extraoral, Full Face, Mouth Open",
)

EV43 = CodeSystemConcept(
    code=f"{make_code('EV43')}",
    display="EV-43 EO.FF.NW",
    definition="Extraoral, Full Face, demonstrating Nerve Weakness",
)
