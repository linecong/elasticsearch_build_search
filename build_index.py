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

#conn.index({"title":"java软件工程师", "content":"非常精通java"}, INDEX_NAME, "test-type", id=1)
#conn.index({"title":"前端工程师", "content":"多年javascript经验"}, INDEX_NAME, "test-type", id=2)

for line in open(sys.argv[1]):
	resume_json = json.loads(line)
	resume_id=resume_json['_id']['$oid']
	if resume_id and resume_id != "":
		conn.index(resume_json, INDEX_NAME, "test-type", id=resume_id)

conn.indices.refresh(INDEX_NAME)

