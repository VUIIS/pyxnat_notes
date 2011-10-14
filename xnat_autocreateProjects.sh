#!/usr/bin/env python

import pyxnat;
import xlrd;
import os;
import random;
from urllib import urlopen
from urllib import quote
print "hello"

def userByEmail(interface,email):
 result = []
 users = interface.manage.users();
 for i in range(0,len(users)) :
  if interface.manage.users.email(users[i]).lower() == email.lower() : 
    result = users[i]
    return result
 return result


wb = xlrd.open_workbook('/home/xnat/projects.xls')
sh = wb.sheet_by_index(0)
# for rownum in range(sh.nrows):
interface = pyxnat.Interface(
         server='http://masi.vuse.vanderbilt.edu/xnat',
         user='admin',
         password='bennett',
         cachedir=os.path.join(os.path.expanduser('~'), '.store')
         )

interface.manage.schemas.add('xnat.xsd')

existingProjects=  interface.select.projects().get();

for rownum in range(1,sh.nrows):
    prjId = sh.cell(rownum,1).value.encode('ascii','ignore')
    prjPI = sh.cell(rownum,2).value.encode('ascii','ignore')
    prjPI = prjPI.replace(',','');
    prjPI = prjPI.replace('.','');
    prjPI = prjPI.replace('Dr ','');
    prjPI = prjPI.replace('Phd','');
    prjPI = prjPI.replace('PhD','');
    prjPI = prjPI.replace('PHD','');
    prjPI = prjPI.replace('MD','');
    piEmail = sh.cell(rownum,3).value.encode('ascii','ignore')
    piPhone = sh.cell(rownum,6).value.encode('ascii','ignore')
    prjTitle = sh.cell(rownum,7).value.encode('ascii','ignore')
    prjDesc = sh.cell(rownum,8).value.encode('ascii','ignore')

    thisPrj = interface.select.project(prjId);
    if not thisPrj.exists() :
       thisPrj.create()
  
    print prjId
    print prjTitle

    nameList = prjPI.split();
    if len(nameList) == 0 :
         firstName = "Missing";
         lastName = "Missing";
    elif len(nameList) == 1 :
         firstName = "Missing";
         lastName = prjPI;
    else :
         firstName = nameList[0]
         lastName = nameList[len(nameList)-1];
    print firstName
    print lastName


    thisPrj.attrs.set('xnat:projectData/description',prjDesc)
#    thisPrj.attrs.set('xnat:projectData/PI/firstname',firstName)
#    thisPrj.attrs.set('xnat:projectData/PI/lastname',lastName)
    thisPrj.attrs.set('xnat:projectData/secondary_ID',prjTitle[0:min(23,len(prjTitle))])
    thisPrj.attrs.set('xnat:projectData/name',prjTitle[0:min(255,len(prjTitle))])
#    thisPrj.add_user(login, role='owner=;adelnrst[\]')

    piUser = userByEmail(interface,piEmail);
    if piUser == [] : 
      userName = firstName + lastName
      while userName in interface.manage.users() : 
        userName += str(random.randint(0,9))
      userPass = userName+"37027"
      print "Need to create user"
      url = "http://masi.vuse.vanderbilt.edu/xnat/app/action/XDATRegisterUser?xdat%3Auser.login="+quote(userName)+"&xdat%3Auser.primary_password="+quote(userPass)+"&xdat%3Auser.primary_password="+quote(userPass)+"&xdat%3Auser.firstname="+quote(firstName)+"&xdat%3Auser.lastname="+quote(lastName)+"&xdat%3Auser.email="+quote(piEmail)+"&lab=NA&comments=NA&xdat%3Auser.primary_password.encrypt=true"
      print url
      print urlopen(url).read()
      piUser = userByEmail(interface,piEmail)
    print piUser   
    print "HAVE: " + piUser
    thisPrj.add_user(piUser,'owner')

