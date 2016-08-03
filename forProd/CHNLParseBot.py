#-*- coding:utf-8 -*-
#last updated:2016.06.23
import sys, os
import re
#default structure: 
# keywords => multiple, array/list
# action => one, str
# target => one, str
# date => one range, combined as str
# ne => multiple, array/list
# lang => one, str

#sys.path.append("/home/yhlin/jieba-master")
import jieba
import jieba.posseg as pseg
from nltk.corpus import wordnet as WN

libFolder = "/data2/opt/PythonProjects/NLPQuery/python/"

re_alldigit = re.compile("\d+")
re_np1 = re.compile(r"\b((eng|x_space|m_alldigits) ?){3,}")
re_np2 = re.compile(r"\b(n[a-z]* )+n[^s ]*")
re_np3 = re.compile(r"\b([an][a-z]* )+uj_de (n[a-z]* |a[a-z]* )*n[^s ]*")
re_np4 = re.compile(r"\ba[a-z]* (n[a-z]* ?)+") # n a n n 是可以的嗎?
#re_np5 = re.compile("(a[a-z]* )+ul_de (n[^s]* )+")
re_np6 = re.compile(r"\b(ns ?){2,}")
re_np7 = re.compile(r"\b(n[a-z]* ?|avn ?){2,}\b")

wh_word = ["誰","什麼", "怎麼", "哪裡", "谁", "什么","哪里"]

def createSkillDict(filedir = libFolder):
	skillSet = []
	filelist = ["skills.txt", "job_role.txt", "cetegory.txt"]


	for f in filelist[:1]:
		#with open(filedir+f) as fin:
		fin = open(os.path.join(filedir, f), "r")
		for l in fin:
			l = l.rstrip()
			if l == "":
				continue
			l = " "+l+" "
			#skillSet.append(l)
			skillSet.append(l.lower())
		fin.close()
	return skillSet

def readCharTable(filedir = libFolder):
	dictFile = os.path.join(filedir, "utftable.txt")
	table = {}
	fin = open(dictFile, "r")
	line = fin.readline()
	while line:
		line = line.strip()
		line = unicode(line, "utf-8")
		assert len(line)==3 and line[1]=="="
		table[line[2]] = line[0]
		line = fin.readline()
	fin.close()
	return table

def readStopKeywords(filedir = libFolder):
	dictFile = os.path.join(filedir, "stopKeyword_CH.txt")
	
	keywordFilter = map(lambda x:x.strip(), open(dictFile, "r").readlines())
	return keywordFilter

def readSearchDomain(filedir = libFolder):
	dictFile = os.path.join(filedir, "searchDomainCH.txt")
	re_comp = {}
	groups = []
	newGroup = ""
	with open(dictFile, "r") as fin:
		for line in fin:
			if line.startswith("SEC:"):
				if newGroup != "":
					tmpRe = "("
					tmpRe += "|".join(groups)
					tmpRe += ")"
					tmpReComp = re.compile(tmpRe)
					re_comp[newGroup] = tmpReComp
				newGroup = line.strip()[4:]
				groups = []
				continue

			groups.append(line.strip())
		tmpRe = "("
		tmpRe += "|".join(groups)
		tmpRe += ")"
		tmpReComp = re.compile(tmpRe)
		re_comp[newGroup] = tmpReComp
	return re_comp

class ChNLParser:
	
	skillSet = createSkillDict()
	charTable = readCharTable()
	stopKeywords = readStopKeywords()
	searchDomainGroup = readSearchDomain()
	def __init__(self):
		self.content = {"keywords":[],"action":"find","target":"","date":"","ne":[], "lang":"ch"}
		self.localdict = {}	


	def convert(self, sentence):
		tmp = unicode(sentence, "utf-8")
		output = [ChNLParser.charTable.get(char, char) for char in tmp]
		for char in tmp:
			self.localdict[ChNLParser.charTable.get(char, char)] = char

		tmp_sen = "".join(output).encode("utf-8")
		return tmp_sen, sentence == tmp_sen

	def convertToTC(self, sentence):
		tmp = unicode(sentence, "utf-8")
		output = [self.localdict.get(char, char) for char in tmp]
		tmp_sen = "".join(output).encode("utf-8")
		return tmp_sen
		
	def resetLocalDict(self):
		self.localdict = {}	

	def postagger(self, sentence, debug=False):
		words = pseg.cut(sentence)
		ws = []
		fs = []
		for w in words:
			if debug:
				print w.word.encode("utf-8"), w.flag

			ws.append(w.word.encode("utf-8"))
			#print w.word.encode("utf-8"), w.flag
			if w.flag.startswith("b"):
				fs.append("a") 
			elif w.flag == "k": #學生"們", 監督"式"
				fs.append("nk")
			elif w.word.encode("utf-8")=="的":
				fs.append("uj_de")
			elif w.word.encode("utf-8") in ["是","不是","能","不能","会","不会","可能","是否","应","应当"]:
				fs.append("v_modal")
			elif w.word == " ":
				fs.append("x_space")
				ws.pop()
				ws.append("SPaAcE")
			elif re_alldigit.match(w.word) != None:
				fs.append("m_alldigits")
			elif w.flag.startswith("v") and len(ws) > 1 and ws[-2] == "请":#jieba sometimes pos-tag verb after "請" as "vn" because the result relies on the dictionary heavily.
				fs.append("v")

			else:
				fs.append(w.flag)
		return ws, fs

	def combineAndReplace(self, word, flag):
		ws = []
		ts = []
		wordlen = len(word)
		skipone = False
		for i in range(0, wordlen) :
			if skipone:
				skipone = False
				continue
			if flag[i:i+2] == ["v","vn"]:
				ws.append("_".join(word[i:i+2]))
				ts.append("nvn")
				#print "do_combine"
				skipone = True
			elif flag[i] == "vn":
				ws.append(word[i])
				ts.append("avn")
			elif flag[i] not in ["eng", "x_space", "m_alldigits", "uj_de", "vn"] and re.match("(a|n)", flag[i]) == None:
				ws.append("*")
				ts.append("*")
			else:
				ws.append(word[i])
				ts.append(flag[i])	

		return ws, ts

	def extractPhrase(self, word, flag, debug=False):
		sentence = " ".join(word)
		sentence += " "
		tag_seq =" ".join(flag)
		tag_seq += " "
		if debug:
			print sentence, "\n", tag_seq
		units = re.split(r"(\* ?)+", sentence)
		tag_unit = re.split(r"(\* ?)+", tag_seq)
		iid = 1
		for u, t in zip(units, tag_unit):
			if u != "* ":
				#print u, len(u.split(" ")), t, re.match("n[a-z]", t)==None
				if len(u.split(" ")) <= 2 and re.match("n[a-fh-z]", t)!=None: #single term
					#print iid, u
					self.content["keywords"].append(u)
				elif len(u.split(" ")) > 2:
					#tmp_chars = u.split()
					tmp_chars =[("" if ("有关" in ui or "关于" in ui) else ui) for ui in u.split()]
					re_list = [re_np1, re_np2, re_np3, re_np4, re_np6, re_np7]
					for r_comp in re_list:
						#print r_comp.pattern
						for m in r_comp.finditer(t):
							bstart = t[:m.start()].count(" ")
							bend = t[:m.end()].count(" ")
							if m.group().endswith(" "):
								bend -= 1
							#print m.start(), m.end()
							#print iid, m.group(), bstart, bend, (" ".join(tmp_chars[bstart:bend+1])).replace("SPACE", "")
							#self.content["keywords"].append((" ".join(tmp_chars[bstart:bend+1])).replace(" SPaAcE ", " ")) <- this one does not remove space between Chinese segments, example 数据 挖掘 => 数据挖掘
							self.content["keywords"].append((" ".join(tmp_chars[bstart:bend+1])).replace(" ","").replace("SPaAcE", " "))

			iid += 1
		## following codes handle isolated ENG words: if an ENG word can be found in wordnet dictionary and acts as a Noun more than 50%, put it in the keyword list
		cmpString = "".join(self.content["keywords"])
		for w, f in zip(word, flag):
			if f == "eng" and (w not in cmpString):
				nCat = 0
				wCat = 0
				for syn in WN.synsets(w):
					cate = syn.name.split(".")[1]
					wCat += 1
					nCat += 1 if cate == "n" else 0
				if wCat != 0 and nCat*10/wCat > 5:
					self.content["keywords"].append(w)


	def targetRulesForRMS(self, words, tags, debug=False):
		#in Chinese, the easiest way to form a question is to add "嗎?" in the end, delete this and treat it as a declarative sentence.
		if tags[-1] == "x": #x punctuation
			tags.pop()
			words.pop()
		if tags[-1] == "y": #y 吧嗎呢
			tags.pop()
			words.pop()

		word_seq = " ".join(words)
		tag_seq = " ".join(tags)
		
		m = re.search("(uj_de( [\w_]+)* n[a-z]*)$", tag_seq)
		if m != None:
			target_tag = m.group(0)
			ttags = target_tag.split()
			target_wordlist = words[1-len(ttags):]
			if debug:
				#print "TARGET IS:", " ".join(target_wordlist)
				print "TARGET IS:", words[-1]
			
			#self.content["target"]=" ".join(target_wordlist)
			self.content["target"]= words[-1]
			
			return words[:0-len(ttags)], tags[:0-len(ttags)]
		else:
			return words, tags

	def relateRulesForRMS(self, words):
		#pattern: (跟|与|和)...(有关|相关)
		#pattern: (有关于|有关|关于)...的
		pat_1 = re.compile(r"(跟|与|和)(.+)(有关|相关)")
		pat_2 = re.compile(r"(有关于|有关|关于|关於|有关於)(.+)的")
		sentence = "".join(words)
		m1 = pat_1.search(sentence)
		m2 = pat_2.search(sentence)
		if m1 != None:
			#print m1.group(2)
			self.content["keywords"].append(m1.group(2).replace("SPaAcE", " "))
		if m2 != None:
			#print m2.group(2)
			self.content["keywords"].append(m2.group(2).replace("SPaAcE", " "))


	def isKeywordContained(self, sentence):
		for s in self.skillSet:
			if s in sentence.lower() or sentence.lower().endswith(s.rstrip()):
				#print s.strip()
				self.content["keywords"].append(s.strip())

	def isNLQuery(self, ws, fs):
		fs = map(lambda x: x[0] if x !="eng" else "eng", fs)
		if len(set(fs)&set(["v", "r","n","p","eng"])) >= 2 and (set(fs)&set(["v", "p"]))!= set():
			return True
		return False

	def isRequestingQuery(self, words, flags):
		if "是" in words or "是不是" in words:
			return False
		if "了" in words[-3:]:
			return False
		#["找", "給"]
		if set(words).intersection(set(["誰", "谁", "哪里", "哪裡", "几时","几点","幾點","怎麼","为什么","為什麼","为啥","為啥"]))!= set():
			return False
		return True

	def parse(self, sentence, debug=False):
		
		sen_r = sentence.rstrip()
		#print "para-got", sen_r
		sen_r = sen_r.decode("unicode-escape")[1:-1]
		#print "after encoding", sen_r
		if sen_r == "exit":
			return self.content
		(sen_sc, converted) = self.convert(sen_r)
		(oriwords, tags) = self.postagger(sen_sc, debug)
		if self.isNLQuery(oriwords, tags) == False or self.isRequestingQuery(oriwords, tags) == False:
			self.content["action"]="No Valid Action"
			return self.content
		(words, tags) = self.targetRulesForRMS(oriwords, tags, debug)
		(nw, nt) = self.combineAndReplace(words, tags)
		self.extractPhrase(nw, nt, debug)
		self.relateRulesForRMS(oriwords)
		self.isKeywordContained(" ".join(oriwords))
		
		if "誰".decode("utf-8") in sen_r or "的人".decode("utf-8") in sen_r or "谁".decode("utf-8") in sen_r:
			self.content["keywords"].append(self.content["target"])
			self.content["target"] = "PERSON"
		
		if re.search("(師|員|長|师|员|长|家|者)$", self.content["target"]) != None:
			self.content["keywords"].append(self.content["target"])
			self.content["target"] = "PERSON"
		else:
			for domain, pattern in ChNLParser.searchDomainGroup.iteritems():
				if pattern.search(self.content["target"]) != None:
					self.content["keywords"].append(self.content["target"])
					self.content["target"] = domain
					break

		if self.content["target"] == "" and not self.content["keywords"]:#default if nothing found above, assign a category if the sentence contains special terms

			if re.search(u"(人員|人员|人才|专家|專家|师|師|学者|學者|員|長|员|长|人)", sen_r) != None:
				self.content["target"] = "PERSON"
			else:
				for domain, pattern in ChNLParser.searchDomainGroup.iteritems():
					if pattern.search(sen_sc) != None:
						self.content["target"] = domain
						break
		tmpkw = []
		for kv in self.content["keywords"]:
			if kv.strip() not in ChNLParser.stopKeywords:
				tmpkw.append(kv)
		self.content["keywords"] = tmpkw
		
		if not converted:
			self.content["keywords"] = [ self.convertToTC(k) for k in list(set(self.content["keywords"]))] # list(set()) to eliminate duplicate items
			self.content["target"] = self.convertToTC(self.content["target"])
			self.resetLocalDict()
		self.content["target"] = self.content["target"].decode("utf-8")
		return self.content 

	def reset(self):
		
		self.content = {"keywords":[],"action":"find","target":"","date":"","ne":[], "lang":"ch"}

if __name__ == "__main__":
	parser = ChNLParser()
	#enParser = EnNLParser()
	while(True):
		sen = sys.stdin.readline()
		sen = sen.rstrip()
		# if text contains more Chinese chars than English words, use English
		# else use Chinese
		if sen == "exit":
			break
		o = parser.parse(sen)
		print o.__str__()
		for oo in o["keywords"]:
			print oo
		parser.reset()

