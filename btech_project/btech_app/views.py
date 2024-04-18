from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import base64, json, time as t
import asyncio
from btech_project.settings import REDIS_CLIENT
from btech_project.settings import mongo_db, mongo_db_cred
import os
from btech_app import process
from django.http import FileResponse
import os
import aiofiles
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.utils.encoding import escape_uri_path
from asgiref.sync import async_to_sync
import shutil

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def valid_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username,password)
    exists = mongo_db_cred.count_documents({'$and':[{'username':username}, {'password':password}]})
    if(exists == 1):
        books = mongo_db.find({'username':username})
        request.session['user_id'] = username 
        return redirect(home)
    else:
        return render(request,'login.html',{'status':'Invalid credentials'})

def valid_signup(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    exists = mongo_db_cred.count_documents({'username':username})
    if(exists == 1):
        return render(request,'signup.html',{'status':'User Already Existed...!'})
    else:
        mongo_db_cred.insert_one({'username':username,'password':password})
        return render(request, 'login.html')

def home(request):
    #print(mongo_db.collection.find())
    books = mongo_db.find({'username':request.session['user_id']})
    return render(request,'home.html',{'books':books,'user_name':request.session['user_id']})


@api_view(['POST'])
def insert_data(request):
    #data=request.POST['name']
    csrf=request.POST['csrfmiddlewaretoken']
    file = request.FILES['file_data']
    # file_content = base64.b64encode(file.read()).decode('utf-8')
    print("---",csrf,"----",file.name,'-----',type(file))
    print(request.session['user_id'])
    username = request.session['user_id']
    #type of file
    file_name = file.name
    if file_name[-3:] == 'pdf':
        file_name = str(file_name.lower())[:-4]
        file_type = 'pdf'
    else:
        file_name = str(file.name.lower())[:-5]
        file_type = 'docx'
    result = mongo_db.count_documents({  '$and':[  {'name': file_name },{'username':username}  ]  })
    #book_exists = REDIS_CLIENT.smembers('books')
    if result:
        print("already exists")
        return Response({0})
    try:
        process.start(file_name,file,file_type, username ) 
        # mongo_db.insert_one({'name':file_name})
        return Response({1})
    except Exception as e:
        print(e)
        print(e.__dict__)
        return Response({2})
    

@require_GET
@async_to_sync
async def download(request, path, name, language):
    file_path = f"{path}/{name}_{language}.pdf"
    
    async with aiofiles.open(file_path, 'rb') as file:
        content = await file.read()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(os.path.basename(file_path))}"'
        response.write(content)

    return response

def time(request):
    t.sleep(20)
    return render(request,'home.html')

@api_view(['GET'])
def translate(request,username,name,language):
    path = mongo_db.find_one({'$and':[{'name':name},{'username':username}]})
    path = path['path']
    print(path,'========>yes')
    try:
        process.start_translate_one(name,language,path,request.session['user_id'])
        print("===========================trans")
        translated_text = mongo_db.find_one({'name':name})
        translated_text = translated_text['translated']
        translated_text = translated_text[language]
        print(translated_text)
        return Response({'status':translated_text})
    except Exception as e:
        print(e)
        return Response({'status':'failed'})
    
@api_view(['GET'])
def delete(request, name, lang):
    path = mongo_db.find_one({'name':name})
    path = path['path']
    mongo_db.update_one({  '$and':[  {'name': name },{'username': request.session['user_id']}  ]  },{"$set":{f"translated.{lang}":"!t"}})
    file_to_delete = path + "\\" + name + "_" + lang + '.pdf'
    print(file_to_delete)
    os.remove(path + "\\" + name + "_" + lang + '.pdf')
    return Response({'status':'deleted'})

@api_view(['GET'])
def delete_original(request,name):
    path = mongo_db.find_one({'name':name})
    path = path['path']
    shutil.rmtree(path) 
    mongo_db.delete_one({  '$and':[  {'name': name },{'username': request.session['user_id']}  ]  })
    return Response({'status':'deleted original'})


def logout(request):
    request.session.flush()
    #print(request.session['user_id'])
    return render(request,'login.html')