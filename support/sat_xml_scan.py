#!/usr/bin/env python
#
# Convert XML files from http://satellites-xml.eu/ to scanfile format
#

import os
import sys
import xml.etree.ElementTree as ET
import re, unicodedata

FLAG_NETWORK_SCAN = 1
FLAG_USE_BAT      = 2
FLAG_USE_ONOT     = 4
FLAG_SKIP_NIT     = 8

POLARIZATION = {
  '0': 'H',
  '1': 'V',
  '2': 'L',
  '3': 'R'
}

FEC = {
  '0':  'AUTO',
  '1':  '1/2',
  '2':  '2/3',
  '3':  '3/4',
  '4':  '5/6',
  '5':  '7/8',
  '6':  '8/9',
  '7':  '3/5',
  '8':  '4/5',
  '9':  '9/10',
  '15': 'NONE'
}

MODULATION = {
  '0': 'AUTO',
  '1': 'QPSK',
  '2': '8PSK'
}

SYSTEM = {
  '0': 'S',
  '1': 'S2'
}

def inspect(node):
  print('  tag=%s attrib=%s' % (repr(node.tag), repr(node.attrib)))

def asciize(str):
  if type(str) != type(u''):
    str = unicode(str, 'UTF-8')
  str = unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
  str = re.sub('\s\s+', ' ', str)
  str = str.strip().replace(' ', '-')
  return str

def parse_sat(node):

  position = node.attrib['position']
  flags = node.attrib['flags']
  name = node.attrib['name']

  assert(flags == '0')

  filename = name.replace('(', '').replace(')', '').replace('/', '+')
  filename = DIR + '/' + asciize(filename)

  fp = open(filename, "w+")
  fp.write('# Generated by Tvheadend from satellites.xml\n')

  for child in node:
    if child.tag == 'transponder':
      polarization = POLARIZATION[child.attrib['polarization']]
      fec = FEC[child.attrib['fec_inner']]
      freq = child.attrib['frequency']
      rate = child.attrib['symbol_rate']
      modulation = MODULATION[child.attrib['modulation']]
      system = SYSTEM[child.attrib['system']]
      if system == 'S' and modulation == 'QPSK':
        fp.write('%s %s %s %s %s\n' %
          (system, freq, polarization, rate, fec))
      else:
        fp.write('%s %s %s %s %s %s %s\n' %
          (system, freq, polarization, rate, fec, 'AUTO', modulation))

  fp.close()

if len(sys.argv) < 3:
  if len(sys.argv) != 1:
    usage = 'python sat_xml_scan.py'
  else:
    usage = sys.argv[0]
  print('Usage: %s satellite.xml /output/directory/path' % usage)
  sys.exit(0)

DIR = sys.argv[2]
if not os.path.isdir(DIR):
  raise ValueError, "Second argument must be the output directory"
tree = ET.parse(sys.argv[1])
root = tree.getroot()
if root.tag == 'satellites':
  for child in root:
    if child.tag == 'sat':
      parse_sat(child)
