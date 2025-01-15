from fhir.resources.codesystem import CodeSystem, CodeSystemConcept
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code
from terminology.resources.code_systems import add_meta_to_resource


class Intraoral2DPhotographicViewsCodeSystem(CodeSystem):

    @classmethod
    def static_url(cls) -> str:
        ns = OpenOrthoNamingSystem()
        return f"{ns.url}/intraoral-2d-photographic-views"

    def __init__(self):
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            url=self.static_url(),
            version="1.0.0",
            name="Intraoral2DPhotographicViews",
            title="Intraoral 2D Photographic Views",
            status="draft",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher="Open Ortho",
            description="Common intraoral 2D photographic views used in an orthodontic provider's practice",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


IV01 = CodeSystemConcept(
    code=f"{make_code('IV01')}",
    display="IV-01 IO.RB.CO",
    definition="Intraoral Right Buccal Segment, Centric Occlusion, Direct View",
)

IV02 = CodeSystemConcept(
    code=f"{make_code('IV02')}",
    display="IV-02 IO.RB.CO.WM",
    definition="Intraoral, Right Buccal Segment, Centric Occlusion, With Mirror",
)

IV03 = CodeSystemConcept(
    code=f"{make_code('IV03')}",
    display="IV-03 IO.RB.CO.WM.BC",
    definition="Intraoral, Right Buccal Segment, Centric Occlusion, With Mirror, But Corrected",
)

IV04 = CodeSystemConcept(
    code=f"{make_code('IV04')}",
    display="IV-04 IO.LB.CO",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, Direct View",
)

IV05 = CodeSystemConcept(
    code=f"{make_code('IV05')}",
    display="IV-05 IO.LB.CO.WM",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, With Mirror",
)

IV06 = CodeSystemConcept(
    code=f"{make_code('IV06')}",
    display="IV-06 IO.LB.CO.WM.BC",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, With Mirror, But Corrected",
)

IV07 = CodeSystemConcept(
    code=f"{make_code('IV07')}",
    display="IV-07 IO.AO",
    definition="Intraoral, Anterior Occlusal, Direct View",
)

IV08 = CodeSystemConcept(
    code=f"{make_code('IV08')}",
    display="IV-08 IO.AO.WM",
    definition="Intraoral, Anterior Occlusal, With Mirror",
)

IV09 = CodeSystemConcept(
    code=f"{make_code('IV09')}",
    display="IV-09 IO.AO.WM.BC",
    definition="Intraoral, Anterior Occlusal, With Mirror, But Corrected",
)

IV10 = CodeSystemConcept(
    code=f"{make_code('IV10')}",
    display="IV-10 IO.MD.MO.OV",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View",
)

IV11 = CodeSystemConcept(
    code=f"{make_code('IV11')}",
    display="IV-11 IO.MD.MO.OV.WM",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror",
)

IV12 = CodeSystemConcept(
    code=f"{make_code('IV12')}",
    display="IV-12 IO.MD.MO.OV.WM.BC",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV13 = CodeSystemConcept(
    code=f"{make_code('IV13')}",
    display="IV-13 IO.MX.MO.OV",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View",
)

IV14 = CodeSystemConcept(
    code=f"{make_code('IV14')}",
    display="IV-14 IO.MX.MO.OV.WM",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror",
)

IV15 = CodeSystemConcept(
    code=f"{make_code('IV15')}",
    display="IV-15 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV16 = CodeSystemConcept(
    code=f"{make_code('IV16')}",
    display="IV-16 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV17 = CodeSystemConcept(
    code=f"{make_code('IV17')}",
    display="IV-17 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV18 = CodeSystemConcept(
    code=f"{make_code('IV18')}",
    display="IV-18 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV19 = CodeSystemConcept(
    code=f"{make_code('IV19')}",
    display="IV-19 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV20 = CodeSystemConcept(
    code=f"{make_code('IV20')}",
    display="IV-20 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV21 = CodeSystemConcept(
    code=f"{make_code('IV21')}",
    display="IV-21 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV22 = CodeSystemConcept(
    code=f"{make_code('IV22')}",
    display="IV-22 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV23 = CodeSystemConcept(
    code=f"{make_code('IV23')}",
    display="IV-23 IO.LB.CR.WM.BC",
    definition="Intraoral, Left Buccal Segment, Centric Relation, With Mirror, But Corrected",
)

IV24 = CodeSystemConcept(
    code=f"{make_code('IV24')}",
    display="IV-24 IO.MX.MO.OV.WM",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror",
)

IV25 = CodeSystemConcept(
    code=f"{make_code('IV25')}",
    display="IV-25 IO.MX.MO.OV.WM.BC",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV26 = CodeSystemConcept(
    code=f"{make_code('IV26')}",
    display="IV-26 IO.MD.MO.OV.WM",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror",
)

IV27 = CodeSystemConcept(
    code=f"{make_code('IV27')}",
    display="IV-27 IO.MD.MO.OV.WM.BC",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror, But Corrected",
)

IV28 = CodeSystemConcept(
    code=f"{make_code('IV28')}",
    display="IV-28 IO.GR.[tooth number]",
    definition="Intraoral, showing Gingival Recession (ISO tooth numbers)",
)

IV29 = CodeSystemConcept(
    code=f"{make_code('IV29')}",
    display="IV-29 IO.FR.[tooth number]",
    definition="Intraoral, showing Frenum (ISO tooth numbers)",
)

IV30 = CodeSystemConcept(
    code=f"{make_code('IV30')}",
    display="IV-30 IO.[modifier].PA",
    definition="Intraoral, any photo using a photo accessory device (modifiers)",
)
