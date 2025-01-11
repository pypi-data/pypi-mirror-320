#****************************************************************************
#* task_data.py
#*
#* Copyright 2023 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import pydantic.dataclasses as dc
from pydantic import BaseModel
from typing import Any, Dict, Set, List, Tuple
from .fileset import FileSet

class TaskData(BaseModel):
    task_id : int = -1
    params : Dict[str,Any] = dc.Field(default_factory=dict)
    deps : List['TaskData'] = dc.Field(default_factory=list)
    changed : bool = False

    def hasParam(self, name: str) -> bool:
        return name in self.params
    
    def getParam(self, name: str) -> Any:
        return self.params[name]
    
    def setParam(self, name: str, value: Any):
        self.params[name] = value

    def addFileSet(self, fs : FileSet):
        if "filesets" not in self.params:
            self.params["filesets"] = []
        self.params["filesets"].append(fs)

    def getFileSets(self, type : (str|Set[str])=None) -> List[FileSet]:
        ret = []

        if "filesets" in self.params:
            for fs in self.params["filesets"]:
                if type is None or fs.type in type:
                    ret.append(fs)
        
        return ret

    def copy(self) -> 'TaskData':
        ret = TaskData()
        ret.task_id = self.task_id
        ret.params = self.params.copy()
        for d in self.deps:
            ret.deps.append(d.clone())
        ret.changed = self.changed
        return ret
    
    def merge(self, other):
        for k,v in other.params.items():
            if k not in self.params:
                if hasattr(v, "copy"):
                    self.params[k] = v.copy()
                else:
                    self.params[k] = v
            elif hasattr(self.params[k], "merge"):
                self.params[k].merge(v)
            elif self.params[k] != v:
                raise Exception("Parameter %s has conflicting values" % k)

