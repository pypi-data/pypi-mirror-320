"""GCMD DIF 10.2 for identifying updates in metadata over time."""

import copy
import json
import sys
from collections import OrderedDict
from logging import getLogger

from xmltodict import unparse
import xml.etree.ElementTree as ET

from envidat.api.v1 import get_protocol_and_domain
from ckanapi import RemoteCKAN
from dif_converter import convert_dif

log = getLogger(__name__)


ckan = RemoteCKAN('https://envidat.ch')

# Replace 'package_id' with the ID of the package you want to retrieve
# with geom collection
# package_id = 'data-reliability-study-avalanche-size-and-outlines'
package_id = 'calishto'
# with polygon
#package_id = '1d2d5111-0c08-4549-b238-1345c550d580'
#package_id = 'resolution-in-sdms-shapes-plant-multifaceted-diversity'
# with multipoint #bounding rectangle was not included with this, should it be included?
#package_id = 'gcos-swe-data'
package = ckan.action.package_show(id=package_id)
dif_pkg = convert_dif(package)

root = ET.Element("root")
child = ET.SubElement(root, "child")
child.text = dif_pkg

xml_str = ET.tostring(root, encoding="utf-8", method="xml", xml_declaration=True)
with open("dif_package.xml", "wb") as f:
    f.write(xml_str)
