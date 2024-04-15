from aiogram.filters import BaseFilter

class DeepLinkFilter(BaseFilter):
    
    async def __call__(self, message):
        
        return len(message.text.split()) > 1
        