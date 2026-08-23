from __future__ import annotations

from pathlib import Path
import re


MAP_EXPORT_KEYS=('edm','map','sav','png_global','png_current')
STATS_EXPORT_KEYS=('json','csv','png')


def safe_export_basename(value:str)->str:
    """Return a Windows-safe shared basename without silently inventing one."""
    text=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',str(value or '')).strip().rstrip('. ')
    text=re.sub(r'\s+','_',text)
    if not text:raise ValueError('empty export basename')
    if text.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:text='_'+text
    return text


def map_export_capabilities(side:int,source_path:Path|str|None)->dict[str,bool]:
    source=Path(source_path) if source_path else None
    binary=int(side)==768
    return {
        'edm':binary,
        'map':binary,
        'sav':bool(source and source.suffix.lower()=='.sav' and source.is_file()),
        'png_global':True,
        'png_current':True,
    }


def map_export_paths(folder:Path|str,basename:str,selected)->dict[str,Path]:
    folder=Path(folder);base=safe_export_basename(basename);chosen=set(selected)
    names={
        'edm':f'{base}.edm',
        'map':f'1-{base}.map',
        'sav':f'{base}.sav',
        'png_global':f'{base}_global.png',
        'png_current':f'{base}_current_view.png',
    }
    return {key:folder/names[key] for key in MAP_EXPORT_KEYS if key in chosen}


def stats_export_paths(folder:Path|str,basename:str,selected)->dict[str,Path]:
    folder=Path(folder);base=safe_export_basename(basename);chosen=set(selected)
    return {key:folder/f'{base}.{key}' for key in STATS_EXPORT_KEYS if key in chosen}


def existing_export_paths(paths:dict[str,Path])->list[Path]:
    return [path for path in paths.values() if path.exists()]
