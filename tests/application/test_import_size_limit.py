from types import SimpleNamespace

import pytest

from s3mapgen.application.imports import controller
from s3mapgen.map_data.model import MapState


@pytest.mark.parametrize('extension',['.map','.edm','.sav'])
def test_oversized_import_preserves_current_session(monkeypatch,extension):
    previous=object()
    host=SimpleNamespace(current=previous,import_source='previous.map')
    host._task_begin=lambda *args:None
    host._task_error=lambda *args:None
    errors=[]
    monkeypatch.setattr(controller.filedialog,'askopenfilename',lambda **kwargs:'oversized'+extension)
    monkeypatch.setattr(controller,'read_area',lambda path:MapState.empty(832))
    monkeypatch.setattr(controller,'read_sav_state',lambda path:MapState.empty(832))
    monkeypatch.setattr(controller,'read_starts',lambda path:[])
    monkeypatch.setattr(controller,'show_message',lambda *args,**kwargs:errors.append(kwargs['exception']))
    controller.ImportController.import_file(host)
    assert len(errors)==1 and '768' in str(errors[0])
    assert host.current is previous
    assert host.import_source=='previous.map'
