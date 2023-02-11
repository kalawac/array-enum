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
    # foci = db.Column(db.ARRAY(db.Enum(WF, name="wf", create_constraint=False, native_enum=False)))
    foci = db.Column(db.ARRAY(db.Enum(WF, name="wf")))
    # remember to add create_constraint=False to migration before db upgrade

    def __repr__(self):
        return '<Org %r>' % self.name

    @classmethod
    def new_from_dict(cls, data_dict):
        new_org = cls(
            name=data_dict["name"], 
            org_sector=data_dict["sector"]
            )

        wf_data = data_dict.get("foci")

        if wf_data:
            if type(wf_data) == list or type(wf_data) == tuple:
                wf_list = []
                for wf_id in wf_data:
                    wf_enum = WF(wf_id) if (type(wf_id) == int) else WF[wf_id]
                    wf_list.append(wf_enum.name)
                new_org.foci = wf_list
            else:
                wf_enum = WF(wf_data) if (type(wf_data) == int) else WF[wf_data]
                new_org.foci=[wf_enum.name]

        return new_org

    def to_dict(self):
        org_dict = {
                "id": self.id,
                "name": self.name,
                "sector": self.org_sector,
                "foci": self.foci,
            }
        
        return org_dict
