import tomllib
import tomli_w
import os
class ConfigManager():
    def __init__(self,path='./config/config.toml'):
        self.path=path
        self.data={}
        if not os.path.exists(self.path):
            self._create()
        self._load()

    def _ensure_dir(self):
        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    def _create(self):
        self.data={}
        self._save()
    def _load(self):
        with open(self.path,'rb') as f:
            self.data=tomllib.load(f)
    def _save(self):
        self._ensure_dir()
        with open(self.path,'wb') as f:
            tomli_w.dump(self.data,f)
    def has(self,section,key=None):
        if key is None:
            return section in self.data
        return section in self.data and key in self.data[section]
    def get(self,section,key,default=None):
        return self.data.get(section,{}).get(key,default)
    def get_key(self,section):
        return list(self.data.get(section,{}).keys())
    def set(self,section,key,value):
        self.data.setdefault(section,{})
        self.data[section][key]=value
        self._save()
