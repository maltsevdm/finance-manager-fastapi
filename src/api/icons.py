import os
from os import walk

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix='/icons', tags=['icons'])


@router.get('/all')
def get_icons():
    path = '../icons'

    f = []
    for (_, _, filenames) in walk(path):
        for filename in filenames:
            if not filename.startswith('.'):
                f.append(filename)
    return f


@router.get('/{icon_name}')
def get_icon(icon_name: str):
    path = os.path.join('../icons', icon_name)
    return FileResponse(path)
