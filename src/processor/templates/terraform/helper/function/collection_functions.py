"""
Performs all in built collection functions which are supported by terraform processor
"""
from processor.logging.log_handler import getlogger

logger = getlogger()

def element(ele, index):
    "return the element at given index from the list"
    if not ele:
        return
    # if index is more then the length of element then search the element wrap around
    while len(ele) <= index:
        index = index - len(ele)
    return ele[index]

def length(ele):
    "return length of given element"
    return len(ele) if ele else None

def chunklist(ele_list, n):
    "splits a single list into fixed-size chunks, returning a list of lists."
    def chunk(ele_list, n):
        for i in range(0, len(ele_list), n):  
            yield ele_list[i:i + n]
    return list(chunk(ele_list, n))    

def concat(*argv):
    "takes two or more lists and combines them into a single list"
    concat_list = []
    for arg in argv:  
        concat_list += arg
    return concat_list

def coalesce(*argv):
    "takes any number of arguments and returns the first one that isn't null or an empty string"
    for arg in argv:  
        if arg:
            return arg

def coalescelist(*argv):
    "takes any number of list arguments and returns the first one that isn't empty."
    return coalesce(*argv)

def compact(ele_list):
    "takes a list of strings and returns a new list with any empty string elements removed"
    return [ele for ele in ele_list if ele]

def distinct(ele_list):
    "takes a list and returns a new list with any duplicate elements removed"
    return list(set(ele_list))

def index(ele_list, value):
    "finds the element index for a given value in a list"
    return ele_list.index(value) if value in ele_list else -1

def lookup(json_data, find_key, default=None):
    "retrieves the value of a single element from a map. If the given key does not exist, return the default value."
    return json_data.get(find_key, default)

def contains(ele_list, search_ele):
    "check element contains in a list or not"
    return True if search_ele in ele_list else False

def keys(json_data):
    "return the list of keys contains in given json"
    return list(json_data.keys())

def to_list(*args):
    "convert given arguments into list"
    return list(args)

def to_map(*args): 
    "convert given arguments into map"
    it = iter(args) 
    res_dict = dict(zip(it, it)) 
    return res_dict

def merge(*args):
    "merge more then one dict into single dict"
    res_dict = {}
    for arg in args:
        res_dict.update(arg)
    return res_dict

def reverse(ele_list):
    " takes the list as an argument and returns the list with reverse order "
    ele_list.reverse() 
    return ele_list  

def setintersection(*args):
    " takes multiple lists and produces a single list containing common elements "
    sets = iter(map(set, args))
    result = sets.next()
    for s in sets:
        result = result.intersection(s)
    return result