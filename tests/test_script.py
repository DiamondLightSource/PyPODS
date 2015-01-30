import sys
sys.path.append("c:\\Users\\mjc23\\Documents\\GitHub\\PyPODS")

from pypods.loc.locdatasource import LocDataSource


lds = LocDataSource()
# Create channel name test31 and value 45.
ch1 = lds.create_channel('test31(45)')

def test_callback_function(n, v):
    print "%s returned %s" % (n, v)

def test_callback_function2(n, v):
    print "%s returned %s too" % (n, v)

ch1.add_read_callback(test_callback_function)
ch1.add_read_callback(test_callback_function2)

ch1.write(68)