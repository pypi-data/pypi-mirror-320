
import json

version_json = '''
{"date": "2025-01-13T00:59:52.399714", "dirty": false, "error": null, "full-revisionid": "5d09370e9c61f129c0afbaa851050ed118b54384", "version": "1.1.0rc1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

