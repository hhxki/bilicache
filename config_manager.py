import tomllib
import tomli_w
import os
import login_cookie
class ConfigManager():
    def __init__(self,path='config.toml'):
        self.path=path
        self.data={}
        if not os.path.exists(self.path):
            self._create()
        self._load()
    def _create(self):
        self.data={}
        self._save()
    def _load(self):
        with open(self.path,'rb') as f:
            self.data=tomllib.load(f)
    def _save(self):
        with open(self.path,'wb') as f:
            tomli_w.dump(self.data,f)
    def has(self,section,key=None):
        if key is None:
            return section in self.data
        return section in self.data and key in self.data[section]
    def get(self,section,key,default=None):
        return self.data.get(section,{}).get(key,default)
    def set(self,section,key,value):
        self.data.setdefault(section,{})
        self.data[section][key]=value
        self._save()