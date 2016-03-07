__author__ = 'dhana013'


import sys, yaml, json
stream_input = open("/home/dhana013/config.yaml")

dataMap = yaml.load(stream_input)

print dataMap
