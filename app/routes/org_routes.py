from app import db
from flask import Blueprint, jsonify, request, make_response, abort
from app.models.org import Org
from app.models.types.org_sector import OrgSector
from app.models.types.work_focus import WF
from .utils import validate_UUID, validate_intID, append_dicts_to_list

bp = Blueprint("orgs_bp", __name__, url_prefix="/orgs")

def validate_sector_enum(sector_id):
    try:
        return OrgSector(int(sector_id))
    except ValueError:
        try:
            return OrgSector[sector_id]
        except KeyError:
            abort(make_response({"message": "Invalid sector value submitted"}, 400))

def validate_wf_enum(wf_id):
    try:
        return WF(int(wf_id))
    except ValueError:
        try:
            return WF[wf_id]
        except KeyError:
            abort(make_response({"message": "Invalid work focus value(s) submitted"}, 400))


def validate_request_body(request_body):
    if not request_body.get("name"):
        abort(make_response({"message": "Organization requires a name"}, 400))

    if (("sector" not in request_body) or ("foci" not in request_body)):
        abort(make_response(
            {"message": "Request body requires the following keys: 'name', 'sector', 'foci'"}, 400))

    sector_id = request_body["sector"]

    validate_sector_enum(sector_id)

    wf_data = request_body["foci"]

    for wf_id in wf_data:
        validate_wf_enum(wf_id)

@bp.route("", methods=["POST"], strict_slashes=False)
def create_org():
    request_body = request.get_json()

    validate_request_body(request_body)

    new_org = Org.new_from_dict(request_body)

    db.session.add(new_org)
    db.session.commit()

    return make_response(jsonify(new_org.to_dict()), 201)


@bp.route("", methods=["GET"], strict_slashes=False)
def get_all_orgs():
    sort_query = request.args.get("sort")
    name_query = request.args.get("name")
    sector_query = request.args.get("sector")
    wf_query = request.args.get("wf")
    logical_or = request.args.get("OR")

    orgs_query = Org.query

    if logical_or:
        existing_query = False

        if name_query:
            orgs_query = orgs_query.filter(Org.name.ilike(f'%{name_query}%'))
            existing_query = True
        
        if sector_query:
            sector_enum = validate_sector_enum(sector_query)

            if existing_query:
                q_sector = Org.query.filter_by(org_sector=sector_enum)
                orgs_query = orgs_query.union(q_sector)
            else:
                orgs_query = orgs_query.filter_by(org_sector=sector_enum)
                existing_query = True

        if wf_query:
            if wf_query.find("+") > -1:
                query_items = wf_query.split["+"]
                item_query = Org.query
                for item in query_items:
                    wf_enum = validate_wf_enum(item)
                    item_query = item_query.filter_by(foci=wf_enum)
                
                if existing_query:
                    orgs_query = orgs_query.union(item_query)
                else:
                    orgs_query = item_query
            elif wf_query.find("_") > -1:
                query_items = wf_query.split["_"]
                for item in query_items:
                    wf_enum = validate_wf_enum(item)
                    item_query = Org.query.filter_by(foci=wf_enum)
                    orgs_query = orgs_query.union(item_query)
            else:
                wf_enum = validate_wf_enum(wf_query)
                if existing_query:
                    q_wf = orgs_query.filter_by(foci=wf_enum)
                    orgs_query = orgs_query.union(q_wf)
                else:
                    orgs_query = orgs_query.filter_by(foci=wf_enum)

    else:
        if name_query:
            orgs_query = orgs_query.filter(Org.name.ilike(f'%{name_query}%'))
        
        if sector_query:
            sector_enum = validate_sector_enum(sector_query)
            orgs_query = orgs_query.filter_by(org_sector=sector_enum)

        if wf_query:
            if wf_query.find("+") > -1:
                query_items = wf_query.split["+"]
                for item in query_items:
                    wf_enum = validate_wf_enum(item)
                    orgs_query = orgs_query.filter_by(foci=wf_enum)
            elif wf_query.find("_") > -1:
                query_items = wf_query.split["_"]
                for item in query_items:
                    wf_enum = validate_wf_enum(item)
                    item_query = Org.query.filter_by(foci=wf_enum)
                    orgs_query = orgs_query.union(item_query)
            else:
                wf_enum = validate_wf_enum(wf_query)
                orgs_query = orgs_query.filter_by(foci=wf_enum)

    if sort_query:
        if sort_query == "desc":
            orgs_query = orgs_query.order_by(Org.name.desc())
    else:
        orgs_query = orgs_query.order_by(Org.name)

    orgs = orgs_query.all()

    if not orgs:
        return jsonify([])

    orgs_response = append_dicts_to_list(orgs)

    return jsonify(orgs_response)


@bp.route("/<uuid:id>", methods=["GET"], strict_slashes=False)
def get_org(id):
    org = validate_UUID(Org, id)
    return org.to_dict()


@bp.route("/<uuid:id>", methods=["PUT"])
def update_org(id):
    org = validate_UUID(Org, id)
    request_body = request.get_json()
    
    validate_request_body(request_body)

    org.name = request_body["name"]
    org.org_sector = request_body["sector"]

    if len(request_body.get("foci", [])) >= 1:
        if not org.foci:
            wf_list = []
        
        for wf_id in request_body["foci"]:
            wf_enum = validate_wf_enum(item)
            if org.foci:
                org.foci.append(wf_enum)
            else:
                wf_list.append(wf_enum)
                org.foci = tuple(wf_list)

    db.session.add(org)
    db.session.commit()

    return jsonify(org.to_dict())


@bp.route("/<uuid:id>", methods=["DELETE"])
def delete_org(id):
    org = validate_UUID(Org, id)
    db.session.delete(org)
    db.session.commit()
    return make_response({"message": f"Organization '{org.name}' successfully deleted"}, 200)