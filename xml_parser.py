import xml.etree.ElementTree as ET
from pytrips import ontology
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
import spacy
import sys


if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

def parse(root):
	data = {}
	if root == None:
		return
	for predicate in root:
		if predicate.tag == "predicate":
			data[predicate.attrib['lemma']] = {}
			for roleset in predicate:
				data[predicate.attrib['lemma']][roleset.attrib['id']] = roleset.attrib['name']
	return data

#print(wordnet.synsets("put over"))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
#print(sys.argv[1])
word_matcher = spacy.load("en_core_web_md")
query = str(sys.argv[1])
tree = ET.parse("frames/"+query+".xml")
root = tree.getroot()
#print(parse(root))
data = parse(root)
#print(data)
ont = ontology.load()
ontologies = ont["w::"+query]
synset = {}
for onto in ontologies:
	synset[onto] = [lemmatizer.lemmatize(x[:-2]) for x in onto.words]
	#synset[onto] = [stemmer.stem(x) for x in synset[onto]]
	synset[onto] = [x for x in synset[onto] if x != query]+[str(onto)[5:]]
	synset[onto] = set(synset[onto])
	list_of_synonyms = []
stop_words = set(stopwords.words('english'))
#print(synset)

for word in data.keys():
	if word == query:
		for roleset in data[word].keys():
			list_of_words = list(data[word][roleset].split(","))
			list_of_words = [x.strip() for x in list_of_words]
			list_of_words = [x for x in list_of_words if x not in stop_words]
			list_of_synonyms = []
			for item in list_of_words:
				try:
					for syn in wordnet.synsets(item):
						for l in syn.lemmas():
							list_of_synonyms.append(lemmatizer.lemmatize(l.name()))
				except LookupError:
					list_of_synonyms.append(lemmatizer.lemmatize(l.name()))
			list_of_synonyms = set(list_of_synonyms+[data[word][roleset]])
			#print(list_of_synonyms)
			max_match = 0
			result = None
			for onto in synset.keys():
				similarity = 0
				matches = []
				matched = False
				count = len(synset[onto])*len(list_of_synonyms)
				for item1 in synset[onto]:
					for item2 in list_of_synonyms:
						#print(item1, item2)
						if item1 == item2:
							matches.append(onto)
							matched = True
							similarity += 1
						else:
							word1 = word_matcher(item1)
							word2 = word_matcher(item2)
							try:
								#print(word1, word2, word1.similarity(word2))
								score = word1.similarity(word2)
								#print(score)
								if score >= 0.4:
									similarity += score
								else:
									count -= 1
							except:
								count -= 1
				if matched:
					res = [str(x) for x in matches]
					for item in res:
						print(item+" = "+str(roleset))
					break
				else:
					match = similarity/(count+0.001)
					if match > max_match:
						max_match = match
						result = str(onto)
			if not matched:
				print(str(result)+" = "+str(roleset))
			
