import asyncio
import aiohttp,time
from bs4 import BeautifulSoup

lng=['en','te','ar','bn','fr']


async def translate(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                translation_div = soup.find('div', {'class': 'result-container'})
                translation = translation_div.text.strip() if translation_div else None
                return translation
            else:
                #return "error"
                raise Exception("Error while translation...!")
    except Exception as e:
        #return 'error'
        raise Exception("Error while translation...!")

async def get_tasks(english_words,language):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [translate(
                    session, 
                    f'https://translate.google.com/m?sl=auto&tl={language}&q={word}') 
                    for word in english_words]
            return await asyncio.gather(*tasks)
    except Exception as e:
        raise Exception("Error while translation...!")

async def main(lngu, english_words ):
    dc={}
    try:
        translations_tasks = [ get_tasks(english_words,i) for i in lngu ]
        translated_list = await asyncio.gather(*translations_tasks)
        return translated_list
        #tt = time.time()-start
        # Print the results
    except Exception as e:
        print(e.__dict__)
        raise Exception("Error while translation...!")
    
    
# Run the asynchronous event loop


