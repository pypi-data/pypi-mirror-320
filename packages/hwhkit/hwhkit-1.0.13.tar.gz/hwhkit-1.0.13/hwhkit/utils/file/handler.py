
import aiofiles

class AsyncFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    async def read_file(self):
        async with aiofiles.open(self.file_path, mode='r') as file:
            content = await file.read()
            return content

    async def write_file(self, content):
        async with aiofiles.open(self.file_path, mode='w') as file:
            await file.write(content)

    async def append_file(self, content):
        async with aiofiles.open(self.file_path, mode='a') as file:
            await file.write(content)

