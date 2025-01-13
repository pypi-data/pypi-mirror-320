
import json

version_json = '''
{"date": "2025-01-12T22:15:56.323104", "dirty": false, "error": null, "full-revisionid": "4b771590477282107016d3ddeea769b62785f935", "version": "1.1.1rc4"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

