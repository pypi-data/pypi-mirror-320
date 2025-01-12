import json

from django_scaffolding_tools._experimental.reqs_utilities.db import RequirementDatabase


class TestRequirementsDatabase:
    def test_r(self, output_folder, fixtures_folder):
        local_file = fixtures_folder / "_experimental" / "requirements"
        json_db_file = output_folder / "json_db.json"
        parsed = output_folder / "_local.json"
        db = RequirementDatabase(json_db_file)
        reqs = db.get_from_requirements_folder(local_file)
        reqs_dict = dict()
        for name, req in reqs.items():
            reqs_dict[name] = req.dict()
        with open(parsed, "w") as f:
            json.dump(reqs_dict, f, indent=4, default=str)

    def test_get(self, fixtures_folder):
        json_db_file = fixtures_folder / "_experimental" / "req_db.json"
        db = RequirementDatabase(json_db_file)
        req = db.get("django")
        assert req is not None
        assert req.approved_version == "3.2.16"

    def test_update_db(self, fixtures_folder):
        json_db_file = fixtures_folder / "_experimental" / "req_db.json"
        db = RequirementDatabase(json_db_file)
        db.update_db()

    def test_add(self, fixtures_folder):
        json_db_file = fixtures_folder / "_experimental" / "req_db.json"
        db = RequirementDatabase(json_db_file)
        db.add("Werkzeug", environment="local")

    def test_greatest(self):
        version1 = "4.1.1"
        version_info1 = tuple([int(num) if num.isdigit() else num for num in version1.replace("-", ".", 1).split(".")])
        version2 = "3.2.16"
        version_info2 = tuple([int(num) if num.isdigit() else num for num in version2.replace("-", ".", 1).split(".")])
        assert version_info1 > version_info2
