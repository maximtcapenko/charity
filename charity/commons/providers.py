import os

import uuid

from charity.settings import STORAGE_PATH


def save_file_to_storage(*args, **kwargs):
    uid = uuid.uuid4().hex
    file_extension = kwargs['file_extension']
    file = kwargs['file']

    file_name = '%s.%s' % (uid, file_extension)
    file_path = '%s/%s' % (STORAGE_PATH, file_name)

    try:
        with open(file_path, 'wb') as fs:
            fs.write(file.read())
    except Exception as e:
        return {'error': {'description': 'Failed save file to storage',
                          'reason': e.message}}

    return {'name': file_name, 'path': file_path, 'extension': file_extension,
            'size': 0}


def delete_file_from_storage(*args, **kwargs):
    file_path = kwargs['file_path']
    try:
        os.remove(file_path)
    except Exception as e:
        return {'error': {'description': 'Failed remove file from storage',
                          'reason': e.strerror}}
    return {'result': 'success'}
