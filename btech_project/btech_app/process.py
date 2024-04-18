import asyncio, os, pdf2docx, zipfile
import aiohttp,time, shutil
from bs4 import BeautifulSoup
from btech_project.settings import BASE_DIR
import win32com.client, pythoncom
from lxml import etree
from btech_app.async_io_translation import *
from collections import OrderedDict
from docx2pdf import convert
from btech_project.settings import mongo_db

def start(file_name,file,file_type,username ):

    temp_path = str(BASE_DIR) + "\\media\\" + file_name
    temp_path_file = temp_path+'\\'+file_name
    try:
        
        pythoncom.CoInitialize()
        temp_path = str(BASE_DIR) + "\\media\\" + file_name
        temp_path_file = temp_path+'\\'+file_name
        print(temp_path)
        
        os.mkdir(temp_path)
        
        with open(temp_path_file+"."+file_type, 'wb+') as destination_file:
            for chunk in file.chunks():
                destination_file.write(chunk)
        
        if file_type == 'pdf':
            
            print("yes pdf")
            convert_pdf_to_word(temp_path_file+'.pdf',temp_path_file+'.docx')
            #temp_path_file = temp_path_file+'.docx'
            # file_name=file_name+'.docx'

        print("----opened-------   1")

        list_of_languages = OrderedDict()
        list_of_languages = {
            'english': 'en',
        }

        all_languages = OrderedDict({
            'afrikaans': 'af',
            'albanian': 'sq',
'amharic': 'am',
'arabic': 'ar',
'armenian': 'hy',
'azerbaijani': 'az',
'basque': 'eu',
'belarusian': 'be',
'bengali': 'bn',
'bosnian': 'bs',
'bulgarian': 'bg',
'catalan': 'ca',
'cebuano': 'ceb',
'chichewa': 'ny',
'chinese (simplified)': 'zh-CN',
'chinese (traditional)': 'zh-TW',
'corsican': 'co',
'croatian': 'hr',
'czech': 'cs',
'danish': 'da',
'dutch': 'nl',
'english': 'en',
'esperanto': 'eo',
'estonian': 'et',
'filipino': 'tl',
'finnish': 'fi',
'french': 'fr',
'frisian': 'fy',
'galician': 'gl',
'georgian': 'ka',
'german': 'de',
'greek': 'el',
'gujarati': 'gu',
'haitian creole': 'ht',
'hausa': 'ha',
'hawaiian': 'haw',
'hebrew': 'iw',
'hindi': 'hi',
'hmong': 'hmn',
'hungarian': 'hu',
'icelandic': 'is',
'igbo': 'ig',
'indonesian': 'id',
'irish': 'ga',
'italian': 'it',
'japanese': 'ja',
'javanese': 'jw',
'kannada': 'kn',
'kazakh': 'kk',
'khmer': 'km',
'kinyarwanda': 'rw',
'korean': 'ko',
'kurdish (kurmanji)': 'ku',

'kyrgyz': 'ky',
'lao': 'lo',
'latin': 'la',
'latvian': 'lv',
'lithuanian': 'lt',
'luxembourgish': 'lb',
'macedonian': 'mk',
'malagasy': 'mg',
'malay': 'ms',
'malayalam': 'ml',
'maltese': 'mt',
'maori': 'mi',
'marathi': 'mr',
'mongolian': 'mn',
'myanmar (burmese)': 'my',
'nepali': 'ne',
'norwegian': 'no',
'odia': 'or',
'pashto': 'ps',
'persian': 'fa',
'polish': 'pl',
'portuguese': 'pt',
'punjabi': 'pa',
'romanian': 'ro',
'russian': 'ru',
'samoan': 'sm',
'scots gaelic': 'gd',
'serbian': 'sr',
'sesotho': 'st',
'shona': 'sn',
'sindhi': 'sd',
'sinhala': 'si',
'slovak': 'sk',
'slovenian': 'sl',
'somali': 'so',
'spanish': 'es',
'sundanese': 'su',
'swahili': 'sw',
'swedish': 'sv',
'tajik': 'tg',
'tamil': 'ta',
'telugu': 'te',
'thai': 'th',
'turkish': 'tr',
'ukrainian': 'uk',
'urdu': 'ur',
'uzbek': 'uz',
'vietnamese': 'vi',
'welsh': 'cy',
'xhosa': 'xh',
'yiddish': 'yi',
'yoruba': 'yo',
'zulu': 'zu'
        })
        #translate_docx(temp_path,temp_path_file,list_of_languages)

        unzip_docx(temp_path_file+'.docx', temp_path+'\\unzip')
        
        print("----opened-------   2")
        document_xml_path = os.path.join(temp_path+'\\unzip'+'\\word', 'document.xml')
        root = etree.parse(document_xml_path).getroot()
        namespace_uri = root.nsmap.get('w')
        namespace = {'w': namespace_uri}
        wt_elements = root.xpath(".//w:t", namespaces=namespace)
        xml_text_tags = []
        original_text_mongo_db = ''
        for wt_element in wt_elements:
            original_len = len(wt_element.text)
            original_text = wt_element.text
            if ' '*original_len == original_text:
                xml_text_tags.append(['only_space',wt_element.text,original_text])
                original_text_mongo_db += ' '*original_len
            else:
                left_space = ( original_len-len(original_text.lstrip()) )*" "
                right_space = ( original_len-len(original_text.rstrip()) )*" "
                xml_text_tags.append([left_space,wt_element.text,right_space])
                print(left_space,"|",wt_element.text,"|",right_space,sep="")
                original_text_mongo_db += ( left_space + wt_element.text + right_space )

        only_text = [ i[1] for i in xml_text_tags ]

        

        languages_to_translate_code = [ list_of_languages[i] for i in list_of_languages ]
        languages_to_translate = [ i for i in list_of_languages ]
    
        translated_data = asyncio.run(main(languages_to_translate_code,only_text))

        # if translated_data == 0:
        #     print("error")
        #     shutil.rmtree(temp_path)
        #     return 

        # for lang,data in zip(languages_to_translate,translated_data):
        #     print(lang,"--------->",data)

        mongo_db.insert_one({'username':username,'name':file_name,'path':str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name})

        for i in all_languages:
            mongo_db.update_one({'$and':[{"name":file_name},{"username":username}]},{"$set":{f"translated.{i}":"!t"}})
        mongo_db.update_one({'$and':[{"name":file_name},{"username":username}]},{"$set":{f"translated.original":original_text_mongo_db}})
        for i in translated_data:
            print(len(i))

        print("________0________________")
        time.sleep(3)
        if not os.path.exists(str(BASE_DIR)+"\\media\\pdf\\"+username):
            os.mkdir(str(BASE_DIR)+"\\media\\pdf\\"+username)
        os.mkdir(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name)
        print("________1________________")
        time.sleep(3)
        shutil.copy(temp_path+'\\unzip\\word\\document.xml', str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name)
        print("________2________________")
        time.sleep(3)
        for i in translated_data:
            print(i)

        word_app = win32com.client.Dispatch("Word.Application")

        zip_docx(str(BASE_DIR)+"\\media\\"+ file_name+"\\"+"unzip", str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
        word_app.Visible = False
        doc = word_app.Documents.Open(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
        doc.SaveAs(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+"_original"+".pdf", FileFormat=17)
        doc.Close()
        os.remove(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')

        for lng, each_lang in zip(languages_to_translate,translated_data):
            translated_text_to_insert = ''
            for xml, text, wt_element in zip(xml_text_tags, each_lang, wt_elements ):
                if xml[0]=='only_space':
                    wt_element.text = xml[2]
                elif len(xml[0]) == 0 and len(xml[2]) > 0:
                    wt_element.text = text.ljust(len(xml[1])+len(xml[2])," ")
                elif len(xml[2]) == 0 and len(xml[0]) > 0:
                    wt_element.text = text.rjust(len(xml[1])+len(xml[0])," ")
                elif len(xml[0]) > 0 and len(xml[2]) > 0:
                    sti = ' '*len(xml[0]) + text.ljust( len(xml[1]) + len(xml[2]), ' ' )
                    wt_element.text = sti 
                elif len(xml[0])==0 and len(xml[2])==0:
                    wt_element.text = text

                translated_text_to_insert += wt_element.text
            criteria = {"name":file_name}
            mongo_db.update_one({'$and':[{"name":file_name},{"username":username}]},{"$set":{f"translated.{lng}":translated_text_to_insert}})

            print('success-------1')
                # if text != None:
                #     wt_element.text = xml[0] + text + xml[2]
                # else:
                #     wt_element.text = xml[0] + xml[2]
            etree.ElementTree(root).write(document_xml_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
            # print(str(BASE_DIR)+"\\media\\"+ file_name+"\\"+"unzip", str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name)
            # print("-"*50)
            # print( str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name,  str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name[:-5]+"_"+lng+".pdf")
            zip_docx(str(BASE_DIR)+"\\media\\"+ file_name+"\\"+"unzip", str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
            # convert( str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name,  str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name[:-5]+"_"+lng+".pdf")
            
            word_app.Visible = False
            doc = word_app.Documents.Open(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
            doc.SaveAs(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+"_"+lng+".pdf", FileFormat=17)
            doc.Close()
            os.remove(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx') #to remove main document (.docx)
            print('success-------2')
        shutil.move(temp_path+"\\unzip", str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name )
        shutil.copy(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\document.xml",str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\unzip\\word")
        shutil.rmtree(temp_path)  #to remove temp_path that contains xml files
        print("-----   removed  ------")   
            #new_content = input(f"Enter new content for {wt_element.text}: ")
            #wt_element.text = new_content
        # etree.ElementTree(root).write(document_xml_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
        # zip_docx(temp_path+'\\unzip', temp_path_file)
        #pythoncom.CoUninitialize()
        word_app.Quit()
        print("-----   removed 1 ------") 
        pythoncom.CoUninitialize()
        print("-----   removed 2 ------")
        
        return 
    except Exception as e:
        mongo_db.delete_one({'$and':[{"name":file_name},{"username":username}]})
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        if os.path.exists(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name):
            shutil.rmtree(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name)
            os.rmdir(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name)
            print(file_name)
        mongo_db.delete_one({'$and':[{"name":file_name},{"username":username}]})

        raise Exception(e)
def unzip_docx(docx_path, extraction_path):
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(extraction_path)

def zip_docx(extraction_path, output_path):
    with zipfile.ZipFile(output_path, 'w') as zip_ref:
        for root, dirs, files in os.walk(extraction_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, extraction_path)
                zip_ref.write(file_path, arc_name)



def convert_pdf_to_word(pdf_path, output_word_path):
    # Create a new instance of Word
    pythoncom.CoInitialize()
    word = win32com.client.Dispatch("Word.Application")

    try:
        # Open the PDF file
        #word.displayAlerts = False
        pdf_document = word.Documents.Open(pdf_path)
        #pdf_document.displayAlerts=False
        # Save the PDF content as a Word document
        pdf_document.SaveAs(output_word_path, FileFormat=16)  # 16 corresponds to Word document format

    finally:
        # Close all documents and quit Word
        pdf_document.Close()
        word.Quit()
        pythoncom.CoUninitialize()
        
    return 
      



##  TRANSLATE TO ONE LANGUAGE ##
def start_translate_one(file_name,language,path,username):

    unzip_path = os.path.join(path,'unzip')
    try:
        pythoncom.CoInitialize()

        all_languages = OrderedDict({
            'afrikaans': 'af',
            'albanian': 'sq',
'amharic': 'am',
'arabic': 'ar',
'armenian': 'hy',
'azerbaijani': 'az',
'basque': 'eu',
'belarusian': 'be',
'bengali': 'bn',
'bosnian': 'bs',
'bulgarian': 'bg',
'catalan': 'ca',
'cebuano': 'ceb',
'chichewa': 'ny',
'chinese (simplified)': 'zh-CN',
'chinese (traditional)': 'zh-TW',
'corsican': 'co',
'croatian': 'hr',
'czech': 'cs',
'danish': 'da',
'dutch': 'nl',
'english': 'en',
'esperanto': 'eo',
'estonian': 'et',
'filipino': 'tl',
'finnish': 'fi',
'french': 'fr',
'frisian': 'fy',
'galician': 'gl',
'georgian': 'ka',
'german': 'de',
'greek': 'el',
'gujarati': 'gu',
'haitian creole': 'ht',
'hausa': 'ha',
'hawaiian': 'haw',
'hebrew': 'iw',
'hindi': 'hi',
'hmong': 'hmn',
'hungarian': 'hu',
'icelandic': 'is',
'igbo': 'ig',
'indonesian': 'id',
'irish': 'ga',
'italian': 'it',
'japanese': 'ja',
'javanese': 'jw',
'kannada': 'kn',
'kazakh': 'kk',
'khmer': 'km',
'kinyarwanda': 'rw',
'korean': 'ko',
'kurdish (kurmanji)': 'ku',

'kyrgyz': 'ky',
'lao': 'lo',
'latin': 'la',
'latvian': 'lv',
'lithuanian': 'lt',
'luxembourgish': 'lb',
'macedonian': 'mk',
'malagasy': 'mg',
'malay': 'ms',
'malayalam': 'ml',
'maltese': 'mt',
'maori': 'mi',
'marathi': 'mr',
'mongolian': 'mn',
'myanmar (burmese)': 'my',
'nepali': 'ne',
'norwegian': 'no',
'odia': 'or',
'pashto': 'ps',
'persian': 'fa',
'polish': 'pl',
'portuguese': 'pt',
'punjabi': 'pa',
'romanian': 'ro',
'russian': 'ru',
'samoan': 'sm',
'scots gaelic': 'gd',
'serbian': 'sr',
'sesotho': 'st',
'shona': 'sn',
'sindhi': 'sd',
'sinhala': 'si',
'slovak': 'sk',
'slovenian': 'sl',
'somali': 'so',
'spanish': 'es',
'sundanese': 'su',
'swahili': 'sw',
'swedish': 'sv',
'tajik': 'tg',
'tamil': 'ta',
'telugu': 'te',
'thai': 'th',
'turkish': 'tr',
'ukrainian': 'uk',
'urdu': 'ur',
'uzbek': 'uz',
'vietnamese': 'vi',
'welsh': 'cy',
'xhosa': 'xh',
'yiddish': 'yi',
'yoruba': 'yo',
'zulu': 'zu'
        })
        list_of_languages = OrderedDict()
        list_of_languages = {
            language:all_languages[language]
        }


        document_xml_path = os.path.join(unzip_path+'\\word', 'document.xml')
        root = etree.parse(document_xml_path).getroot()
        namespace_uri = root.nsmap.get('w')
        namespace = {'w': namespace_uri}
        wt_elements = root.xpath(".//w:t", namespaces=namespace)
        xml_text_tags = []
        original_text_mongo_db = ''
        for wt_element in wt_elements:
            original_len = len(wt_element.text)
            original_text = wt_element.text
            if ' '*original_len == original_text:
                xml_text_tags.append(['only_space',wt_element.text,original_text])
                original_text_mongo_db += ' '*original_len
            else:
                left_space = ( original_len-len(original_text.lstrip()) )*" "
                right_space = ( original_len-len(original_text.rstrip()) )*" "
                xml_text_tags.append([left_space,wt_element.text,right_space])
                print(left_space,"|",wt_element.text,"|",right_space,sep="")
                original_text_mongo_db += ( left_space + wt_element.text + right_space )

        only_text = [ i[1] for i in xml_text_tags ]

        

        languages_to_translate_code = [ list_of_languages[i] for i in list_of_languages ]
        languages_to_translate = [ i for i in list_of_languages ]
    
        translated_data = asyncio.run(main(languages_to_translate_code,only_text))

        # if translated_data == 0:
        #     print("error")
        #     shutil.rmtree(temp_path)
        #     return 

        # for lang,data in zip(languages_to_translate,translated_data):
        #     print(lang,"--------->",data)

        # for i in translated_data:
        #     print(len(i))


        # for i in translated_data:
        #     print(i)

        word_app = win32com.client.Dispatch("Word.Application")
        for lng, each_lang in zip(languages_to_translate,translated_data):
            translated_text_to_insert = ''
            for xml, text, wt_element in zip(xml_text_tags, each_lang, wt_elements ):
                if xml[0]=='only_space':
                    wt_element.text = xml[2]
                elif len(xml[0]) == 0 and len(xml[2]) > 0:
                    wt_element.text = text.ljust(len(xml[1])+len(xml[2])," ")
                elif len(xml[2]) == 0 and len(xml[0]) > 0:
                    wt_element.text = text.rjust(len(xml[1])+len(xml[0])," ")
                elif len(xml[0]) > 0 and len(xml[2]) > 0:
                    sti = ' '*len(xml[0]) + text.ljust( len(xml[1]) + len(xml[2]), ' ' )
                    wt_element.text = sti 
                elif len(xml[0])==0 and len(xml[2])==0:
                    wt_element.text = text

                translated_text_to_insert += wt_element.text
            criteria = {"name":file_name}
            mongo_db.update_one({'$and':[{"name":file_name},{"username":username}]},{"$set":{f"translated.{lng}":translated_text_to_insert}})

            print('success-------1')
                # if text != None:
                #     wt_element.text = xml[0] + text + xml[2]
                # else:
                #     wt_element.text = xml[0] + xml[2]
            etree.ElementTree(root).write(document_xml_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
            # print(str(BASE_DIR)+"\\media\\"+ file_name+"\\"+"unzip", str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name)
            # print("-"*50)
            # print( str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name,  str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name[:-5]+"_"+lng+".pdf")
            zip_docx(unzip_path, str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
            # convert( str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name,  str(BASE_DIR)+"\\media\\pdf\\"+file_name[:-5]+"\\"+file_name[:-5]+"_"+lng+".pdf")
            
            word_app.Visible = False
            doc = word_app.Documents.Open(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
            doc.SaveAs(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+"_"+lng+".pdf", FileFormat=17)
            doc.Close()
            os.remove(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx') #to remove main document (.docx)
            print('success-------2')
        
          #to remove temp_path that contains xml files
            #new_content = input(f"Enter new content for {wt_element.text}: ")
            #wt_element.text = new_content
        # etree.ElementTree(root).write(document_xml_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
        # zip_docx(temp_path+'\\unzip', temp_path_file)
        #pythoncom.CoUninitialize()
        word_app.Quit()
        print("-----   removed 1 ------") 
        pythoncom.CoUninitialize()
        print("-----   removed 2 ------")
        shutil.copy(str(BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\document.xml", unzip_path+'\\word')

        return "OK"
    except Exception as e:
        criteria = {"name":file_name}
        mongo_db.update_one({'$and':[{"name":file_name},{"username":username}]},{"$set":{f"translated.{language}":"!t"}})
        mongo_db.delete_one({'$and':[{"name":file_name},{"username":username}]})
        if os.path.exists(str(BASE_DIR)+"\\media\\pdf\\"+file_name+"\\"+file_name+'.docx'):
            os.remove((BASE_DIR)+"\\media\\pdf\\"+username+"\\"+file_name+"\\"+file_name+'.docx')
        raise Exception(e)
