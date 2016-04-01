import re
#last updated:2016.01.11
import xml.etree.ElementTree as ET
#from elementtree import ElementTree as ET
#import yaml

from datetime import date

#=====regex=====
moDay = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
expression_both = '(\d*_VBG |\d*_VBN |\d*_JJ |\d*_JJR |\d*_JJS )*(\d*_NN \d*_POS |\d*_NNS \d*_POS )*(\d*_NN |\d*_NNS )+'
expression_both = '(\d*_VBG_O |\d*_VBN_O |\d*_JJ_O |\d*_JJR_O |\d*_JJS_O )*(\d*_NN_O \d*_POS_O |\d*_NNS_O \d*_POS_O )*(\d*_NN_O |\d*_NNS_O )+'
prog_np = re.compile(expression_both)

re_it_i = '(send |give |show |pass |tell |suggest |recommend )(me|us) .*?(NP_\d+)'
re_it_t = '(send |give |show |pass |recommend |suggest ).*?(NP_\d+) to '
#recommend and suugets are added per request 20151207
re_i = '(find |recommend |introduce |suggest )(NP_\d+) .*?(for|to)'
re_have = ""
re_know = ""
re_suggest = '(suggestion|recommendation)'
prog_pat_it_i = re.compile(re_it_i)
prog_pat_it_t = re.compile(re_it_t)
prog_pat_i = re.compile(re_i)
prog_pat_su = re.compile(re_suggest)
prog_wh = re.compile(r"\b(who|what|where|when|why|which|how|whose)\b")
prog1 = re.compile("(Could|could|Would|would|Can|can) you")

target_obj=["article", "information", "book", "paper"]



#=====regex=====

def NPchunk_and_replace(new_s, wl):
	#print new_s
	token_id = 0
	replaced_sentence = ""
	cur_phrase = ""
	token_r = []
	last = 0
	for m in prog_np.finditer(new_s):
		m_ind = re.split(" ", m.group(0))
		start = re.split("_", m_ind[0])
		start_pos = int(start[0])
		end = re.split("_", m_ind[-2])
		end_pos = int(end[0])	
		token_r.append(" ".join(wl[start_pos-1:end_pos]))
		replaced_sentence += " ".join(wl[last:start_pos-1])
		np_token =  " NP_"+str(token_id)+" "
		replaced_sentence += np_token
		last = end_pos
		token_id += 1
	replaced_sentence += " ".join(wl[last:])
	#print replaced_sentence, token_r
	return (replaced_sentence, token_r)


#=====regex=====
list_wh=["who", "what", "when", "where", "why", "which", "how"]
greeting_wlist = r"^(\b(hi|hey|there|going|how is it|how's|doing|good|day|morning|afternoon|night|yo|what's|up|bro|sis|hello|thanks|thank you|it helps)\b)+"
prog_greeting = re.compile(greeting_wlist)

#=====regex_end=====
def greeting_detect(s):

	m = prog_greeting.search(s.lower())

	if m!=None:
		return True

	return False

#=====regex=====
ind_sa_1 = r'do you .*?(know|have)'
ind_sa_2 = r'(can|Can|may|May) (I|i|we) (know|get|have)\b'
ind_sa_3 = r''
author_exp = '(writer|author|composer|creater|director|inventor|issued by|published by|brought out by|written by|authored by|co-authored by|made by|created by|invented by)'
prog_sa_1 = re.compile(ind_sa_1)
prog_sa_2 = re.compile(ind_sa_2)

#=====regex_end=====
def requestDetection(s, wordlist, dep):
	#"do you know anyone good at Java?", know has no dobj in this structure, it has to be "do you know anyone who is good at Java?" 20151201
	if prog_sa_1.search(s):
		m = prog_sa_1.search(s)
		main_verb = m.group(1)
		main_verb_pos = wordlist.index(main_verb)+1
		obj = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(main_verb_pos)+"\"]/..")
		try:
			main_obj = obj.find("dependent").text
		
			#obj_wn_name = wn.synsets(main_obj)[0].name
			return [main_verb, main_obj]
		except:
			return []


	elif prog_sa_2.search(s):
		m = prog_sa_2.search(s)
		main_verb = m.group(3)
		main_verb_pos = wordlist.index(main_verb)+1
		obj = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(main_verb_pos)+"\"]/..")
		try:
			main_obj = obj.find("dependent").text
			return [main_verb, main_obj]
			#obj_wn_name = wn.synsets(main_obj)[0].name
		except:
			return []

	else:
		return []

def getTimex(ts):
	tids = []
	unit = ""
	today = date.today()
	year = today.year
	month = today.month
	day = today.day
	week = 0
	continuous = 0
	timerex1 = r"OFFSET P(-?\d+)([YMWD])" 
	#timerex2 = r"OFFSET P(-\d+)([YMD])" 

	timerex3 = r"([\dX]{4})(?!/)-?([\dX]{0,2})-?([\d]{0,2})" #date
	timerex4 = r"([\dX]{4})-([\dXW]{3})-[\d]{1}" #day

	timerex5 = r"(\d{4})/(\d{4})" #between
	timerex6 = r"(THIS P\d)"
	timerex7 = r"(P(\d+)([YMD]))"

	startdate = date(1960, 01, 01)
	enddate = today
	for t in ts:
		
		if t.find("NormalizedNER") != None:
			#tid = t.find("Timex").attrib["tid"]
			timeframe = t.find("NormalizedNER").text
			if timeframe in tids:
				continue
			if re.search("\d+\.\d+", timeframe) != None:
				continue
			tids.append(timeframe)
			tpos = int(t.attrib["id"])	
			m = re.search(r'([\d]{4})', timeframe)
			t1 = re.search(timerex1, timeframe)
			# t1 (t3/t4) have combination!
			t3 = re.search(timerex3, timeframe)
			t4 = re.search(timerex4, timeframe)

			# t5 is independent
			t5 = re.search(timerex5, timeframe)
			# get time format first and preposition secondly
			
			t7 = re.search(timerex7, timeframe)
			if re.search(timerex5, timeframe)!=None:
				x = re.search(timerex5, timeframe)
			if t1 != None:
				unit = t1.group(2)
				if t1.group(2) == "Y":
					year = year + int(t1.group(1))
				elif t1.group(2) == "M":
					month = month + int(t1.group(1))
				elif t1.group(2) == "W":
					weekinterval = int(t1.group(1))
					#day = 7*weekinterval
				else:
					day = day+int(t1.group(1))
			elif t7 != None:
				unit = t7.group(3)
				if unit == "Y":
					year = year - int(t7.group(2)) #here the t7.group(2) is always positive integer
				elif unit == "M":
					month = month - int(t7.group(2))
				elif unit == "D":
					day = day - int(t7.group(2))
			
			if t3 != None:
				#if t3.group(2) != None and re.search(r"\d{4}", t3.group(1))!= None:
				if t3.group(2) != None and re.search(r"\d{4}", t3.group(1))!= None:
					year = int(t3.group(1))
					unit = "Y"
				if t3.group(2) != "XX" and t3.group(3)!="":
					day = int(t3.group(3))
					month = int(t3.group(2))
					unit = "D"
				elif t3.group(2) != "XX" and t3.group(2) != "":
					month = int(t3.group(2))
					unit = "M"
			elif t4 != None:
				pass
			
			if re.search(timerex6, timeframe) != None or t.find("NER").text == "DURATION":
				continuous = 1
				 
			if ts[tpos-2].find("word").text in ["by", "before", "to"]:
				if unit == "Y":
					enddate = date(year, 1, 1)
				elif unit == "M":
					enddate = date(year, month, 1)
				elif unit == "W":
					pass
				elif unit =="D":
					enddate = date(year, month, day)
			elif ts[tpos-2].find("word").text in ["after", "since"]:
				if unit == "Y":
					startdate = date(year, 1, 1)
				elif unit == "M":
					startdate = date(year, month, 1)
				elif unit == "D":
					startdate = date(year, month, day)

			elif ts[tpos-2].find("word").text in ["between", "from"]:
				if t5 != None:
					year1 = int(t5.group(1))
					startdate = date(year1, 1, 1)	
					year2 = int(t5.group(2))
					enddate = date(year2, 12, 31)
			elif ts[tpos-2].find("word").text in ["in", "on", "over", "during"]:
				if unit == "Y":
					startdate = date(year, 1, 1)
					if continuous != 1:
						enddate = date(year, 12, 31)
				elif unit == "M":
					startdate = date(year, month, 1)
					if continuous == 0: 
						enddate = date(year, month, moDay[month])
			elif ts[tpos-2].find("POS").text != "IN":
				if unit == "Y":
					startdate = date(year, 1, 1)
					enddate = date(year, 12, 31)
				elif unit == "M":
					startdate = date(year, month, 1)
					enddate = date(year, month, moDay[month])
				elif unit == "D":
					startdate = date(year, month, day)
					enddate = startdate
	
		elif t.find("Timex") != None:					#newly added in Sep2014, for patterns such as "over the past three months", information appears in timex and there is no NormalizedNER
			timeframe = t.find("Timex").text
			if timeframe in tids:
				continue
			tids.append(timeframe)
			tpos = int(t.attrib["id"])
			t7 = re.search(timerex7, timeframe)
			
			if t7 != None:
				unit = t7.group(3)
				if unit == "Y":
					year = year - int(t7.group(2)) #here the t7.group(2) is always positive integer
				elif unit == "M":
					month = month - int(t7.group(2))
				elif unit == "D":
					day = day - int(t7.group(2))

			if ts[tpos-2].find("word").text !="":
				if unit == "Y":
					startdate = date(year, 1, 1)
				elif unit == "M":
					startdate = date(year, month, 1)
				else:
					startdate = date(year, month, max(1, day))
			
			#timeframe = t.find("NormalizedNER").text
			#target_d = timeRange(timeframe, today, startdate)
			
	#print enddate, startdate
	if startdate!=date(1960,01,01) or enddate != today:
		return str(startdate) + " and "+ str(enddate)

	else:
		return ""

def question_detect(whIndicator):
	if whIndicator.lower() in ["who", "whose"]:
		return "PERSON"
	elif whIndicator.lower() in ["what"]:
		return "OBJECT"
	else:
		return ""

class EnNLParser:
	def __init__(self):
		self.content = {"keywords":[],"action":"","target":"","date":"","ne":[], "lang":"en"}
	
	def getNNP(self, w, t, n):
		ind = 0
		flag = 0
		nnp = ""
		for tt, nn in zip(t, n):
			if nn not in ["PERSON", "LOCATION", "ORGANIZATION", "O"]:
				ind += 1
				continue
			if tt in ["NNP", "NNPS"] and flag:
				nnp = nnp + w[ind] + " "
			elif tt in ["NNP", "NNPS"] and not flag:
				nnp = w[ind] + " "
				flag = 1
			elif tt not in ["NNP", "NNPS"] and flag:
				#print "Clues :" + nnp
				self.content["ne"].append(nnp)
				nnp = ""
				flag = 0
			ind+=1
		if flag:
			#print "Clues :" + nnp
			self.content["ne"].append(nnp)
	def parse(self, input_f):
		#add a little bit "memories" to my bot. if the first sentence is empty or Greeting!, check if there is a second sentence. 20151231
		tree = ET.parse(input_f)
		root = tree.getroot()
		sentences = root.findall("./document/sentences/sentence")
		for se in sentences:
			dep = se.find("./dependencies[@type=\"basic-dependencies\"]")
			tokens = se.find("tokens")
			wl = []
			if dep.attrib.get("type")=="basic-dependencies" and dep.text != None:
				for t in tokens:
					wl.append(t.find("word").text)
				rawT = " ".join(wl)	
				rawT = rawT[0].lower()+rawT[1:]

				g = greeting_detect(rawT)
				if g:
					self.content["action"] = "Greeting!"
					#return self.content
				#if "your" in wordlist:
				elif rawT.find("your")!=-1 or rawT.find("are you")!= -1 or rawT.find("you are") != -1 or rawT.find("you're") != -1:
					self.content["action"] = "Greeting!"
					#return self.content
				else:
					self.reset()
					return self.parse_second(se)

		return self.content
	def parse_second(self, se):
		#tree = ET.parse(input_f)
		#root = tree.getroot()
		wordlist = []
		taglist = []
		nertaglist = []
		new_str = ""
		"""
		sentences = root.findall("./document/sentences/sentence")
		for se in sentences:
			deps = se.findall("./dependencies")
			for dep in deps:
				if dep.attrib.get("type")=="basic-dependencies":
					break
		"""
		dep = se.find("./dependencies[@type=\"basic-dependencies\"]")
		#tokens = root.find("./document/sentences/sentence/tokens")
		tokens = se.find("./tokens")
		for t in tokens:
			wordlist.append(t.find("word").text)
			taglist.append(t.find("POS").text)
			if " ".join(wordlist).lower().endswith("machine learning"):
				taglist[-1] = "NN"
			nertaglist.append(t.find("NER").text)
			new_str = new_str+t.attrib["id"] +"_"+taglist[-1]+"_"+t.find("NER").text+" "
			
		(replaced_sentence, token_r) = NPchunk_and_replace(new_str, wordlist)
		"""
		deps = root.findall("./document/sentences/sentence/dependencies")
		for dep in deps:
			if dep.attrib.get("type")=="basic-dependencies":
				break
		"""
		#dep_root = dep.find("dep[@type=\"root\"]")
		dep_roots = dep.findall("dep")
		for dep_root in dep_roots:
			if dep_root.attrib.get("type")=="root":
				break
		
		h_pos = int(dep_root.find("dependent").attrib["idx"])
		
		s = " ".join(wordlist)	
		s = s[0].lower()+s[1:]	
		
		### add isNL
		NL = 0
		g = greeting_detect(s)
		if g:
			self.content["action"] = "Greeting!"
			return self.content
		#if "your" in wordlist:
		if s.find("your")!=-1 or s.find("are you")!= -1 or s.find("you are") != -1 or s.find("you're") != -1:
			self.content["action"] = "Greeting!"
			return self.content

		if len(wordlist) < 3:
			NL = 0
		if set(list_wh)&set(wordlist)!=set([]):
			NL = 1
		elif taglist[h_pos-1] in ["VBZ", "VB", "VBP", "VBD"] or (taglist[h_pos-1] in ["VBG", "VBN"] and set(["VBZ", "VB", "VBP", "VBD"])&set(taglist)!=set([])) or set(["is", "are", "was", "were"])&set(wordlist)!=set([]):
			NL = 1
		else:
			pass
		if  not NL:
			#return "redirect to Keywords Query:"+s+" !@#N/A!@#N/A!@#N/A!@#N/A"
			self.content["keywords"].append(s)
			return self.content
																	
		### end 

		if taglist[h_pos-1] != "VB" and prog_wh.search(s) == None:
			#print "Assign me jobs!"
			self.content["action"] = ""
			return self.content
		elif taglist[h_pos-1]=="VB" and prog_wh.search(s) != None:
			#qd = question_detect(s, wordlist, taglist, prog_wh.search(s).group(1), token_r)
			qd = question_detect(prog_wh.search(s).group(1))
			if qd in ["PERSON"]:
				qd_pos = wordlist.index("who")
				main_pair = dep.find("dep/dependent[@idx=\""+str(qd_pos+1)+"\"]/..")
				main_verb = main_pair.find("governor")
				main_vid = main_verb.attrib["idx"]
				main_obj = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(main_vid)+"\"]/..")
				if main_obj == None:
					action = main_verb.text
				else:
					action = "#SP#" + main_obj.find("governor").text +" "+main_obj.find("dependent").text+"#EP#"
				#print "Action : find out "+qd if action =="" else "find out "+qd+" "+action
				self.content["action"] = "find"
				self.content["target"] = "PERSON"
				#self.content["keywords"].append(action)
				self.content["keywords"] += token_r #.add
				
			elif qd in ["OBJECT"]:
				#print "Under Construction......"
				main_pair = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(h_pos)+"\"]/..")
				main_dobj = main_pair.find("dependent").text
				action = main_pair.find("governor").text 
				#print "Action : "+action
				self.content["action"] = main_pair.find("governor").text
				self.content["target"] = main_dobj
				k = 0
				for t in token_r:
					if t.endswith(main_dobj):
						token_r.pop(k)
						break
					k += 1

				#print "Hint : "+";".join(token_r)
				self.content["keywords"]+=token_r #.add	
			
			else:
				pass
		elif prog_wh.search(s) != None:
			#qd = question_detect(s, wordlist, taglist, prog_wh.search(s).group(1), token_r)
			qd = question_detect(prog_wh.search(s).group(1))
			#print token_r
			if qd in ["PERSON", "OBJECT"]:
				main_obj = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(h_pos)+"\"]/..")
				#print main_obj
				if main_obj == None:
					action = dep_root.find("dependent").text
				else:
					action = "#SP#" + main_obj.find("governor").text + " " + main_obj.find("dependent").text + "#EP#"
				if qd == "OBJECT" and "WDT" in taglist:
					action = main_obj.find("governor").text
					qd = main_obj.find("dependent").text
				#print "Action : find out "+qd if action =="" else "find out "+qd+" "+action
				self.content["action"] = "find"
				self.content["target"] = qd
				#self.content["keywords"].append(action)
				self.content["keywords"] += token_r #.add
			else:
				pass
	  
		else:
			action = ""
			target = ""
			v = -1
			#v = 0 why is it initiated as 0???
			
			if prog_pat_it_i.search(replaced_sentence)!= None:
				m =  prog_pat_it_i.search(replaced_sentence)
				v = int(m.group(3).split("_")[1])
				action = m.group(1)
				target = token_r[v]
			elif prog_pat_it_t.search(replaced_sentence)!= None:
				m =  prog_pat_it_t.search(replaced_sentence)
				v = int(m.group(2).split("_")[1])
				action = m.group(1)
				target = token_r[v]	
			elif prog_pat_i.search(replaced_sentence)!= None:
				m =  prog_pat_i.search(replaced_sentence)
				v = int(m.group(2).split("_")[1])
				action = m.group(1)
				target = token_r[v]		
			else:

				act = requestDetection(replaced_sentence, wordlist, dep)
				if len(act)== 2:
					action = "find"
					#target = act[2] + act[3]
					target = act[1]
					for p,q in enumerate(token_r):
						if q.endswith(act[1]):
							token_r.pop(p)
				else:
					main_obj = dep.find("dep[@type=\"dobj\"]/governor[@idx=\""+str(h_pos)+"\"]/..")
					if main_obj != None:
						action = main_obj.find("governor").text 
						target = main_obj.find("dependent").text
						k = 0
						for t in token_r:
							if t.endswith(target):
								token_r.pop(k)
								break
							k += 1
	 
			if action!="":
				self.content["action"] = action
				self.content["target"] = target
				#print "Action : " + action
				if v != -1:
				
					"""
					ex: show me data_mining_books, target is data_mining_books which should be eliminated from keywords
					token_r.pop(v)
					"""
					target_s = target.split(" ")
					if len(target_s) > 1:
						self.content["target"] = target_s[-1]
						token_r[v] = " ".join(target_s[:-1])
					else:
						token_r.pop(v)
				#outStru.keyword +=", "
				self.content["keywords"] += token_r #.add

		self.getNNP(wordlist, taglist, nertaglist)

		self.content["date"] = getTimex(tokens)
		if self.content["action"] !="" :
			self.content["action"] = "find"
		if self.content["target"].lower() in ["people", "architect", "architects","consultant", "consultants","developer","developers","analyst","analysts","expert","experts", "manager", "managers", "planner", "planners","lead", "representative", "representatives","modeler", "modelers","specialist","specialists", "administrator","administrators", "engineer", "engineers", "employee", "employees"]:
			self.content["keywords"].append(self.content["target"])
			self.content["target"] = "PERSON"

		elif self.content["target"].lower() in ["document", "documents", "book", "books"]:
			self.content["keywords"].append(self.content["target"])
			self.content["target"] = "NEWS"

		elif self.content["target"].lower() in ["paper", "journal", "journals", "publication"]:
			self.content["keywords"].append(self.content["target"])
			self.content["target"] = "PAPERS"

			
		return self.content

	def reset(self):
		self.content = {"keywords":[],"action":"find","target":"","date":"","ne":[], "lang":"en"}



if __name__ == "__main__":
	import sys, os
	from subprocess import call

	enParser = EnNLParser()
	while True:
		s = raw_input("what's your question?")
		if s == "exit":
			break
		if s != "debug":
			inw = open("/home/yhlin/corenlp/raw_text/input", "w")
			inw.write(s)
			inw.close()
			cwd = os.getcwd()
			os.chdir("/home/yhlin/corenlp/")
			res = call("python '/home/yhlin/corenlp/callParser.py'", shell=True)
			os.chdir(cwd)

		#o = qTypeDetect("/home/yhlin/corenlp/outputXML/input.xml")
		o = enParser.parse("/home/yhlin/corenlp/outputXML/input.xml")
		print o.__str__()
		enParser.reset()
