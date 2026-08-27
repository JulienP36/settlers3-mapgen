from __future__ import annotations
from pathlib import Path
import json

def load_profile(path:Path|str)->dict:
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)
