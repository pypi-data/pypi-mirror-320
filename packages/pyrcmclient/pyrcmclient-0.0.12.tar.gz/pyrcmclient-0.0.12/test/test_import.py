
import sys,os
from lxml.etree import _Element as Elem
from i4srcm.xml.XmlBinaryStream import from_binary, to_binary
from i4srcm.client import RCMCNT_Client
import i4srcm.lxmlutil as lx
from i4srcm.ctl import RCMCTL

def import_test():
    print("test import RCMCTL")
    ctl = RCMCTL( '127.0.0.1', 'testuser', passwd='testpass')
    print("test import RCMCNT_Client")
    client = RCMCNT_Client( 'http://127.0.0.1', username='testuser', passwd='testpass')
    print("test import lxmlutil")
    elem:Elem = lx.create_element('test')
    lx.to_str(elem)
    print("succesfull")

def main():
    import_test()

if __name__ == "__main__":
    main()