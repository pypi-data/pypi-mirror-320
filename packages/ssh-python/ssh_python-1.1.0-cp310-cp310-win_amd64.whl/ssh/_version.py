
import json

version_json = '''
{"date": "2025-01-13T01:39:14.226289", "dirty": false, "error": null, "full-revisionid": "d90ea3e52655b9b58aaf884bb910fef79e0594c6", "version": "1.1.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

