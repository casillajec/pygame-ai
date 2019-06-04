

def remove_if_exists(mylist, item):
    """ Remove item from mylist if it exists, do nothing otherwise """
    to_remove = []
    for i in range(len(mylist)):
        if mylist[i] == item:
            to_remove.append(mylist[i])
            
    for el in to_remove:
        mylist.remove(el)
        
def remove_if_exists_copy(mylist, item):
    """ Return new list with item removed """
    new_list = []
    for el in mylist:
        if el != item:
            new_list.append(el)
            
    return new_list
    
def find_first(mylist, item):
    """ Returns index of the first occurence of item in mylist, returns -1 if not found """
    try:
        idx = mylist.index(item)
    except ValueError:
        idx = -1
    
    return idx
        
