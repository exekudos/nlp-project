import xml.etree.ElementTree as ET
from pytrips import ontology
from nltk.stem import PorterStemmer

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


stemmer = PorterStemmer()
query = "cover"
tree = ET.parse(query+".xml")
root = tree.getroot()
#print(parse(root))
data = parse(root)
ont = ontology.load()
ontologies = ont["w::"+query]
synset = {}
for onto in ontologies:
	synset[onto] = [stemmer.stem(x[:-2]) for x in onto.words]
#print(synset)

for word in data.keys():
	if word == query:
		for roleset in data[word].keys():
			list_of_words = list(data[word][roleset].split(","))
			list_of_words = [stemmer.stem(x.strip()) for x in list_of_words]
			#print(list_of_words)
			for item1 in list_of_words:
				for onto in synset.keys():
					for item2 in synset[onto]:
						if item1 == item2:
							print(str(roleset)+" = "+str(onto))
							break
			
