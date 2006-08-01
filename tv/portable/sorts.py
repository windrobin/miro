def _compare(x, y):
    if x < y:
        return -1
    if x > y:
        return 1
    return 0

def item(x,y):
    from item import Item, FileItem
    if x.parent_id is not None and x.parent_id == y.getID():
        # y is x's parent
        return 1
    if y.parent_id is not None and y.parent_id == x.getID():
        # x is y's parent
        return -1
    if x.parent_id is None or y.parent_id is None or x.parent_id != y.parent_id:
        # x and y are not children of the same item, so sort by the parent (which might be the self)
        x = x.getParent()
        y = y.getParent()
            
    if x.releaseDateObj > y.releaseDateObj:
        return -1
    if x.releaseDateObj < y.releaseDateObj:
        return 1
    if x.linkNumber > y.linkNumber:
        return -1
    if x.linkNumber < y.linkNumber:
        return 1

    # Since we're sorting Items and FileItems differently, one has to
    # come before the other for this to be a proper sorting function.

    if x.__class__ is Item and y.__class__ is FileItem:
        return -1
    if x.__class__ is FileItem and y.__class__ is Item:
        return 1
    if x.__class__ is FileItem and y.__class__ is FileItem:
        if x.getTitle() < y.getTitle():
            return -1
        if x.getTitle() > y.getTitle():
            return 1
    if x.id > y.id:
        return -1
    if x.id < y.id:
        return 1
    if x.__class__ is Item and y.__class__ is Item:
        if x.getTitle() < y.getTitle():
            return -1
        if x.getTitle() > y.getTitle():
            return 1
    return 0

def alphabetical(x,y):
    if x.getTitle() < y.getTitle():
        return -1
    elif x.getTitle() > y.getTitle():
        return 1
    elif x.getDescription() < y.getDescription():
        return -1
    elif x.getDescription() > y.getDescription():
        return 1
    else:
        return 0

def downloadStartedSort(x,y):
    if x.getTitle() < y.getTitle():
        return -1
    elif x.getTitle() > y.getTitle():
        return 1
    elif x.getDescription() < y.getDescription():
        return -1
    elif x.getDescription() > y.getDescription():
        return 1
    else:
        return 0

# The sort function used to order tabs in the tab list: just use the
# sort keys provided when mapToTab created the Tabs. These can be
# lists, which are tested left-to-right in the way you'd
# expect. Generally, the way this is used is that static tabs are
# assigned a numeric priority, and get a single-element list with that
# number as their sort key; feeds get a list with '100' in the first
# position, and a value that determines the order of the feeds in the
# second position. This way all of the feeds are together, and the
# static tabs can be positioned around them.
def tabs(x, y):
    if x.sortKey < y.sortKey:
        return -1
    elif x.sortKey > y.sortKey:
        return 1
    return 0

def text(x, y):
    return _compare(str(x), str(y))

def number(x, y):
    return _compare(float(x), float(y))
