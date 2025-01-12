import os
import uuid
from fastapi import File, Request, UploadFile
from starlette.datastructures import UploadFile as UploadFileType
import shutil
from collections import defaultdict
from ._settings import CRUD_FILE_ROOT


def savefile(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    filename, file_extension = os.path.splitext(file.filename)
    stored_filename = f"{filename}_{unique_id}{file_extension}"
    
    # 临时
    os.makedirs(CRUD_FILE_ROOT, exist_ok=True)  

    path = CRUD_FILE_ROOT / stored_filename

    with open(path, 'wb+') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return stored_filename



# 提取任意数量和名称的表单字段
async def get_form_data(request: Request):
    form = await request.form()
    data = defaultdict(list)

    for key, value in form.multi_items():
        data[key].append(value)

    # 将单一元素的列表转换回单一值
    return {key: values if len(values) > 1 else values[0] for key, values in data.items()}
