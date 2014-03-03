#coding=utf-8
import tornado.ioloop
import tornado.web
import datetime
from pyes import *

conn = ES('127.0.0.1:9200')
conn.default_indices=["pinbot"]

html_src=u"<html>\
<head> \
<title>resume search</title> \
<script> \
	function doSearch (kw,addr) { \
		document.location.href='/search?kw='+encodeURIComponent(kw)+'&addr='+addr; \
	} \
</script> \
</head>\
<body> \
<div style='text-align:center'> \
<form> \
	关键词: <input type='text' name='kw'/> \
	地点：<input type='text' name='addr' size=20px> \
	<input type='button' name='Search' value='Search' onClick='doSearch(this.form.kw.value,this.form.addr.value);'/> \
</form> \
<div> \
%s \
</div> \
<div>&copy;HopperClouds</div> \
</div> \
</body> \
</html>"

def escape_query(origin_qstr):
	special_chars = "+!"
	for s in special_chars:
		origin_qstr = origin_qstr.replace(s,"\\%s" % s)
	return origin_qstr

class MainHandler(tornado.web.RequestHandler):
	def parse_arguments(self):
		q=self.get_argument("kw",default=None)
		addr=self.get_argument("addr",default=None)
		query_info={}
		print "kw=%s" % q
		print "addr=%s" % addr
		query_info['keywords'] = q
		query_info['addr'] = addr
		return query_info

	def get(self):
		query_info=self.parse_arguments()
		if query_info['keywords']:
			qstr=escape_query(query_info['keywords'])
			q_kw=StringQuery(qstr,search_fields=["workExperience.positionTitle^3",\
			"workExperience.jobDesc",\
			"jobTarget.jobCareer",\
			"projectExperience.responsibleFor"])
			if query_info['addr']:
				q_addr=TermQuery("jobTarget.jobLocation",query_info['addr'])
				q = BoolQuery(must=[q_kw, q_addr])
			else:
				q = q_kw
			begin_date_from=datetime.date.today()+datetime.timedelta(-1000)
			begin_date_from_str=begin_date_from.strftime("%Y-%m-%d")
			print begin_date_from_str
			filter_q=FilteredQuery(q,RangeFilter(ESRangeOp('updateTime', 'gt', begin_date_from_str)))
			results=conn.search(query=filter_q,start=0,size=36)
			result_str="<div>Search for: <b>%s</b></div><br>" % query_info['keywords']
			for r in results:
				gender=r.get('gender','unknown')
				age=r.get('age','unknown')
				updateTime=r.get('updateTime','unknown')
				work_exp_len=r.get('workExperienceLength','unknown')
				edu_dgree='unknown'
				school='unknown'
				company_name=None
				position_title=None
				url="http://www.pinbot.me/resumes/display/%s/" % (r['_id']['$oid'])
				if 'educationExperience' in r:
					for edu_exps in r['educationExperience']:
						edu_dgree=edu_exps['degree']
						school=edu_exps['school']
						break
				if 'workExperience' in r:
					for we in r['workExperience']:
						company_name=we['companyName']
						position_title=we['positionTitle']
						break
				resume_info=u"%s %s岁 %s年经验<br>教育:%s 学校:%s 公司:%s 职位:%s %s <a href='%s' target='_blank'>详情</a><hr>" \
				% (gender,age,work_exp_len,edu_dgree,school,company_name,position_title,updateTime,url)
				result_str += resume_info
			self.write(html_src % (result_str))
		else:
			self.write(html_src % (""))

application = tornado.web.Application([
	(r"/search", MainHandler),
])

if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
