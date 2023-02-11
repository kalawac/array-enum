from app import db
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from .types.org_sector import OrgSector
from .types.work_focus import WF
from app.routes.utils import validate_intID, validate_UUID

class Org(db.Model):
    id = db.Column(
        UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name = db.Column(db.String)
    org_sector = db.Column(db.Enum(OrgSector))
    foci = db.Column(db.ARRAY(db.Enum(WF, name="wf_enum", create_constraint=False, native_enum=False)))

    def __repr__(self):
        return '<Org %r>' % self.name

    @classmethod
    def new_from_dict(cls, data_dict):
        new_org = cls(
            name=data_dict["name"], 
            org_sector=data_dict["sector"],
            )

        if len(data_dict.get("foci", [])) >= 1:
            for wf_id in data_dict["foci"]:
                wf = validate_intID(WF, wf_id)
                new_org.focus_rel.append(wf)
        
        return new_org

    def to_dict(self):
        org_dict = {
                "id": self.id,
                "name": self.name,
                "sector": self.org_sector,
                "foci": self.foci,
            }
        
        return org_dict
