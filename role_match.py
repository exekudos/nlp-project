import sys
import jsontrips
import xml.etree.ElementTree as ET
ont = jsontrips.ontology()
word = str(sys.argv[1])               #Word that corresponds to xml file - e.g. 'eat'      
word1 = str(sys.argv[2])              #Word sense from propbank - e.g. 'eat.01'
word2 = str(sys.argv[3])              #Ontology Type from TRIPS - e.g. 'EAT'

## Get TRIPS roles and their optionality corresponding to the ontology type
def trips_roles(onttype):
    roles = []
    for role_dic in ont[onttype]['arguments']:
        roles.append([role_dic['role'] , role_dic['optionality']])
    return roles

## Get the <role> information from the xml file which contains role numbers , their description etc.
def parse(root , rolesetid):
    if root == None:
        return
    for predicate in root:
        for roleset in predicate:
            if roleset.attrib['id'] == rolesetid:
                roles = extract_roles(roleset)
                break
        if roleset.attrib['id'] == rolesetid:
            break
    return roles

## Get the role numbers (0 for ARG0 , 1 for ARG1 , etc.) , the definition of those roles and vnroles
def extract_roles(roleset):
    roles_list = []
    vnroles = []
    for things in roleset:
        if things.tag == "roles":
            for role_thing in things:
                if role_thing.tag == "role":
                    roles_list.append([role_thing.attrib['n'],role_thing.attrib['f'],role_thing.attrib['descr']])
                    vnr = []
                    for vn in role_thing:
                        if vn.tag == 'vnrole':
                            vnr.append(vn.attrib['vntheta'])
                    vnroles.append(vnr)
            break
    return roles_list , vnroles

## Get TRIPS roles from the binded (TRIPS ROLE , OPTIONALITY) , by discarding OPTIONALITY
def get_trips_roles(c):
    l = []
    for i in range(len(c)):
        l.append(c[i][0])
    return set(l)

## Check if a particular number corresponding to a role (0 for ARG0) is present or not
def present(num , a):
    for i in range(len(a)):
        if a[i][0] == num:
            return (True , i)
    return (False , 0)

## Remove a given word from a list
def remove(listi , word):
    for i in range(len(listi)):
        if listi[i] == word:
            del listi[i]
            break
            
## Given a verbnet role , return a set of corresponding TRIPS roles. 
## This is done by using the dictionary defined below which was made after seeing a number of examples and taking reference from class slides
def from_vn(num , role , vnrole):
    dic = {'agent':['AGENT','EXPERIENCER'],'causer':['AGENT'],'instrument':['AGENT'],'stimulus':['AGENT','NEUTRAL','FORMAL'],
           'theme':['AGENT','AFFECTED','NEUTRAL','FORMAL'],'patient':['AFFECTED'],'destination':['AFFECTED'],'source':['AFFECTED' , 'SOURCE'],
           'experiencer':['AFFECTED','NEUTRAL','EXPERIENCER'],'product':['AFFECTED'],'result':['AFFECTED' , 'RESULT' , 'FORMAL'],'pivot':['AFFECTED'],
           'location':['NEUTRAL'],'topic':['NEUTRAL'],'attribute':['FORMAL'],'predicate':['FORMAL'],'beneficiary':['BENEFICIARY'],'recepient':['BENEFICIARY'], 'instrument':['METHOD'] , 'co-agent':['AGENT1']
          }
    if num == 1:
        if role == 'EXPERIENCER':
            try:
                l = dic[vnrole]
                remove(l,'EXPERIENCER')
                remove(l,'AGENT')
                remove(l,'AFFECTED')
            except:
                l = []
            return l
        elif role == 'AGENT':
            try:
                l = dic[vnrole]
                remove(l,'EXPERIENCER')
                remove(l,'AGENT')
            except:
                l = []
            return l

## Given a label (GOL , etc.) return which TRIPS roles that label could correspond to
## The connection between labels and TRIPS roles was made after looking at a lot of examples and reading the annotation guidelines for PropBank 
def get_list(num):
    if num == 'COM':
        return ['MANNER']
    elif num == 'LOC':
        return ['LOCATION']
    elif num == 'DIR':
        return ['RESULT' , 'SOURCE' , 'TRANSIENT-RESULT']
    elif num == 'GOL':
        return ['BENEFICIARY' , 'RESULT']
    elif num == 'MNR':
        return ['MANNER']
    elif num == 'TMP':
        return ['TIME']
    elif num == 'EXT':
        return ['EXTENT' , 'DEGREE']
    elif num == 'REC':
        return ['AFFECTED']
    elif num == 'PRD':
        return ['RESULT'] ## , 'FORMAL' , 'NEUTRAL']
    elif num == 'PRP':
        return ['REASON']
    elif num == 'CAU':
        return ['REASON']
    elif num == 'CXN':
        return ['COMPARE']
    else:
        return []
 
## Takes in 3 parameters , the propbank roles , verbnet roles and trips roles with optionality and returns a mapping between 
## propbank roles and trips roles   
def role_matching(a,b,c):
    # Match ARG0 if present
    if present('0',a)[0]:
        if present('EXPERIENCER' , c)[0]:
            e = 'EXPERIENCER'
            print("ARG0 matched to EXPERIENCER")
        elif present('AGENT' , c)[0]:
            e = 'AGENT'
            print("ARG0 matched to AGENT")
        else:
            print("ARG0 is unmatched")
    # Match ARG1 if present
    if present('1',a)[0]:
        if 'thing' in a[present('1',a)[1]][2]:
            print("ARG1 is matched to AFFECTED")
        elif b[present('1',a)[1]]:
            p = get_trips_roles(c)
            l = set(from_vn(1 , e , b[present('1',a)[1]][0].lower()))
            p.intersection_update(l)
            print("ARG1 is matched to :")
            for ii in p:
                print(ii,D[ii])                     ## Extracts Optionality 
        else:
            print("ARG1 is matched to AFFECTED")     ## Default case 
    # Match ARG2 if present
    if present('2',a)[0]:
        if b[present('2',a)[1]]:
            l = set(get_list(a[present('2',a)[1]][1].upper()))
            m = set(from_vn(1 , 'AGENT',b[present('2',a)[1]][0].lower()))
            l.intersection_update(m)
            if l:
                print("ARG2 is matched to {}".format(l))
            else:
                p = get_trips_roles(c)
                p.intersection_update(set(get_list(a[present('2',a)[1]][1].upper())))
                if p:
                      print("ARG2 is matched to {}".format(p))
                else:
                      print("ARG2 is matched to {}".format(m))
            
        else:
            l = set(get_list(a[present('2',a)[1]][1].upper()))
            p = get_trips_roles(c)
            p.intersection_update(l)
            if p:
                print("ARG2 is matched to {}".format(p))
            else:
                print("ARG2 is matched to {}".format(l))
    
    # Match ARG3 if present            
    if present('3',a)[0]:
        if b[present('3',a)[1]]:
            l = set(get_list(a[present('3',a)[1]][1].upper()))
            m = set(from_vn(1 , 'AGENT',b[present('3',a)[1]][0].lower()))
            l.intersection_update(m)
            if l:
                print("ARG3 is matched to {}".format(l))
            else:
                p = get_trips_roles(c)
                p.intersection_update(set(get_list(a[present('3',a)[1]][1].upper())))
                if p:
                      print("ARG3 is matched to {}".format(p))
                else:
                      print("ARG3 is matched to {}".format(m))
            
        else:
            l = set(get_list(a[present('3',a)[1]][1].upper()))
            p = get_trips_roles(c)
            p.intersection_update(l)
            if p:
                print("ARG3 is matched to {}".format(p))
            else:
                print("ARG3 is matched to {}".format(l))
    
    # Match ARG4 if present
    if present('4',a)[0]:
        if b[present('4',a)[1]]:
            l = set(get_list(a[present('4',a)[1]][1].upper()))
            m = set(from_vn(1 , 'AGENT',b[present('4',a)[1]][0].lower()))
            l.intersection_update(m)
            if l:
                print("ARG4 is matched to {}".format(l))
            else:
                p = get_trips_roles(c)
                p.intersection_update(set(get_list(a[present('4',a)[1]][1].upper())))
                if p:
                      print("ARG4 is matched to {}".format(p))
                else:
                      print("ARG4 is matched to {}".format(m))
            
        else:
            l = set(get_list(a[present('4',a)[1]][1].upper()))
            p = get_trips_roles(c)
            p.intersection_update(l)
            if p:
                print("ARG4 is matched to {}".format(p))
            else:
                print("ARG4 is matched to {}".format(l))
                
tree = ET.parse( 'frames/' + word + ".xml")
root = tree.getroot()
a, b = parse(root , word1)
c = trips_roles(word2)
D = {}
for i in range(len(c)):
    D[c[i][0]] = c[i][1]
    
role_matching(a,b,c)
