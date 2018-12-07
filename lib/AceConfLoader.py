#!/usr/bin/python3
#coding: utf-8
#fanghuizhi@sogou-inc.com

import os

class AceConfLoader:

    filepath = ""

    def __init__(self, in_filepath):
        self.filepath = in_filepath
    
    def loadconf(self, section, key, turnBoolean = False):
        if(not turnBoolean):
            return self._loadconf(self.filepath, section, key)
        else:
            getstr = self._loadconf(self.filepath, section, key)
            if(not isinstance(getstr, str)):
                return False
            if(getstr == "1"):
                return True
            else:
                return False
        
    def loadconfBySector(self, section):
        return self._loadconf_sec(self.filepath, section)
        
    def _loadconf(self, file, section, key):
        dic = self._loadconf_sec(file, section)
        if(len(dic) > 0):
            if(key in dic.keys()):
                #print(dic[key])
                return dic[key]
                
    def _loadconf_sec(self, file, section):
        dic = {}
        if(not os.path.exists(file)):
            return dic
        f = open(file)
        try:
            line = f.readline()
            while line:
                line = line.replace('\n', '')
                if(len(line) > 0 and line[1:len(line)-1] == section):
                    line = f.readline().replace('\n', '')
                    while line:
                        if(line.startswith('[') and line.endswith(']')):
                            break
                        else:
                            dic[line[:line.find('=')].strip()] = line[line.find('=')+1:]
                            line = f.readline().replace('\n', '')
                    break
                else:
                    line = f.readline()
        finally:
            f.close()
        return dic