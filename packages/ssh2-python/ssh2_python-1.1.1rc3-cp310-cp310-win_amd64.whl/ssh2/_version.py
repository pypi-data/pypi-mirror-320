
import json

version_json = '''
{"date": "2025-01-12T21:25:25.840272", "dirty": false, "error": null, "full-revisionid": "46088cc472018d49f375336313e221b4fe6a3681", "version": "1.1.1rc3"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

