#coding=utf-8
import sys
import json
from pyes import *

INDEX_NAME='pinbot'

conn = ES('127.0.0.1:9200')
try:
	conn.indices.delete_index(INDEX_NAME)
except:
	pass
conn.indices.create_index(INDEX_NAME)


"""
mapping = {
	'content': {
		'boost': 1.0,
		'index': 'analyzed',
		'store': 'yes',
		'type': 'string',
		"indexAnalyzer":"mmseg",
		"searchAnalyzer":"mmseg",
		"term_vector": "with_positions_offsets"
	},
	'title': {
		'boost': 1.0,
		'index': 'analyzed',
		'store': 'yes',
		'type': 'string',
		"indexAnalyzer":"mmseg",
		"searchAnalyzer":"mmseg",
		"term_vector": "with_positions_offsets"
	}
}
conn.indices.put_mapping("resume", {'properties':mapping}, [INDEX_NAME])
"""

for line in open(sys.argv[1]):
	resume_json = json.loads(line)
	resume_id=resume_json['_id']['$oid']
	try:
		conn.index(resume_json, INDEX_NAME, "test-type", id=resume_id)
	except Exception, e:
		print e

conn.indices.refresh(INDEX_NAME)

