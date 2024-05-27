from flask import Flask, render_template, request,redirect,url_for
import pymongo
from bson import ObjectId
from dateutil import relativedelta
from datetime import datetime,timedelta
import uuid,random,copy,json
import numpy as np
app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ManningScheduler"]

# todo
# names enforce to have no spacing
# Add restrictions to roles

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/ManageRestriction',methods=["GET","POST"])
def managerestriction():
    global mydb

    if request.method=="POST":
        restrictions=[]
        counter=0
        mydict={'name':request.form['RestrictionName'],'FromTime':request.form['Restriction1-1'],'ToTime':request.form['Restriction1-2'],'inverse':request.form['inverse']}
        daysaffected=[]
        dutypostsaffected=[]
        for i in request.form.items():
            counter+=1
            if counter<=4:
                pass
            elif str(i[0]).startswith("day"):
                daysaffected.append(str(i[0]))
            elif str(i[0]).startswith("DP"):
                dutypostsaffected.append(str(i[0]))

        mydict['daysaffected']=daysaffected
        mydict['dutypostsaffected']=dutypostsaffected

        mycol = mydb["Restriction"]

        x = mycol.insert_one(mydict)


        return redirect(url_for('managerestriction'))
    if request.method=="GET":
        mycol = mydb["Restriction"]

        restrictions={}
        for x in mycol.find():
            restrictions[(x['name'].replace(' ',''))]=x

        mycol = mydb["DutyPosts"]
        DutyPosts=[]
        for x in mycol.find():
            DutyPosts.append(x['name'])
        print(restrictions)

    return render_template('ManageRestriction.html',restrictions=restrictions,DutyPosts=DutyPosts)

@app.route('/EditRestrictions',methods=["POST"])
def editrestriction():
    global mydb


    restrictions=[]
    counter=0
    mydict={'name':request.form['NewRestrictionName'],'FromTime':request.form['Restriction1-1'],'ToTime':request.form['Restriction1-2'],'inverse':request.form['inverse']}
    daysaffected=[]
    dutypostsaffected=[]
    for i in request.form.items():
        counter+=1
        if counter<=4:
            pass
        elif str(i[0]).startswith("day"):
            daysaffected.append(str(i[0]))
        elif str(i[0]).startswith("DP"):
            dutypostsaffected.append(str(i[0]))

    mydict['daysaffected']=daysaffected
    mydict['dutypostsaffected']=dutypostsaffected

    mycol = mydb["Restriction"]

    myquery = {"name": request.form['OldRestrictionName']}
    newvalues = {"$set": mydict}
    print('123',mydict)
    mycol.update_one(myquery, newvalues)




    return redirect(url_for('managerestriction'))

@app.route('/ManageRole',methods=["GET","POST"])
def managerole():
    global mydb

    if request.method=="POST":
        restrictions=[]
        for i in request.form.items():
            restrictions.append(i[0])
        restrictions.pop(0)

        mycol = mydb["Roles"]

        mydict = {"name": request.form['RoleName'], "Restrictions": restrictions}

        x = mycol.insert_one(mydict)
        return redirect(url_for('managerole'))
    if request.method=="GET":
        mycol = mydb["Roles"]

        roles={}
        for x in mycol.find():
            roles[x['name']]=x['Restrictions']

        RestrictionsAvailable={}
        mycol = mydb["Restriction"]
        for x in mycol.find():
            RestrictionsAvailable[x['name']]=x['_id']
        print(roles)



    return render_template('ManageRole.html',roles=roles,RestrictionsAvailable=RestrictionsAvailable)

@app.route('/EditRoles',methods=["POST"])
def EditRoles():
    global mydb

    mycol = mydb["Roles"]

    restrictions = []
    for i in request.form.items():
        restrictions.append(i[0])
    restrictions.pop(0)
    restrictions.pop(0)

    myquery = {"name": str(request.form["OldRoleName"])}
    newvalues = {"$set": {"name": str(request.form["RoleName"]),"Restrictions": restrictions}}
    mycol.update_one(myquery, newvalues)





    return redirect(url_for('managerole'))

@app.route('/ManageUsers', methods=["GET","POST"])
def manageuser():

    if request.method=="POST":
        mycol = mydb["Users"]
        userdetails = {}
        restrictions=[]
        counter=0
        for i in request.form.items():
            if counter==0:
                userdetails['name']=i[1]
            elif counter==1:
                userdetails['role']=i[1]
            elif counter==2:
                userdetails['contact']=i[1]
            elif counter == 3:
                userdetails['standgatepri'] = i[1]
            else:
                restrictions.append(i[0])
            counter+=1
        userdetails['restrictions']=restrictions
        x = mycol.insert_one(userdetails)
        return redirect(url_for('manageuser'))

    elif request.method=="GET":
        mycol = mydb["Roles"]

        roles={}
        for x in mycol.find():
            roles[x['name']]=[x['Restrictions'],str(x['_id'])]

        RestrictionsAvailable={}
        mycol = mydb["Restriction"]
        for x in mycol.find():
            RestrictionsAvailable[x['name']]=str(x['_id'])

        users=[]
        mycol = mydb["Users"]
        for x in mycol.find():
            users.append(x)
        print(users)



    return render_template('ManageUsers.html',RestrictionsAvailable=RestrictionsAvailable,roles=roles,users=users)

@app.route('/EditUser', methods=["POST"])
def edituser():
    global mydb

    mycol = mydb["Users"]
    userdetails = {}
    restrictions = []
    counter = 0
    for i in request.form.items() :
        if counter==0:
            pass
        elif counter == 1 :
            userdetails['name'] = i[1]
        elif counter == 2 :
            userdetails['role'] = i[1]
        elif counter == 3 :
            userdetails['contact'] = i[1]
        elif counter == 4 :
            userdetails['standgatepri'] = i[1]
        else :
            restrictions.append(i[0])
        counter += 1
    userdetails['restrictions'] = restrictions

    myquery = {"_id": ObjectId(str(request.form["OldUserName"]))}
    newvalues = {"$set": userdetails}
    print(userdetails)
    print(mycol.update_one(myquery, newvalues))
    return redirect(url_for('manageuser'))






@app.route('/CreateManning',methods=["GET","POST"])
def createmanning():
    global mydb

    if request.method=="POST":


        mycol = mydb["Manning"]

        mydict = {"name": request.form['Name'],"StartDate": request.form['StartDate'],"StartTime": request.form['StartTime'],"EndDate": request.form['EndDate'],"EndTime": request.form['EndTime'],"Data":[]}

        x = mycol.insert_one(mydict)
        return redirect(url_for('ManageManning'))

    return render_template('CreateManning.html')

@app.route('/CreateShiftTemplate',methods=["GET","POST"])
def createshifttemplate():
    global mydb

    if request.method=="POST":


        mycol = mydb["Manning"]

        mydict = {"name": request.form['Name'],"StartDate": request.form['StartDate'],"StartTime": request.form['StartTime'],"EndDate": request.form['EndDate'],"EndTime": request.form['EndTime'],"Data":[]}

        x = mycol.insert_one(mydict)
        return redirect(url_for('ManageManning'))

    return render_template('CreateShiftTemplate.html')

@app.route('/ManageDutyPost', methods=["GET","POST"])
def ManageDutyPost():
    global mydb

    if request.method=="POST":


        mycol = mydb["DutyPosts"]

        mydict = {"name": request.form['DutyPostName']}

        x = mycol.insert_one(mydict)
        return redirect(url_for('ManageDutyPost'))
    if request.method=="GET":
        mycol = mydb["DutyPosts"]

        DutyPosts=[]
        for x in mycol.find():
            DutyPosts.append(x['name'])

    return render_template('ManageDutyPost.html',DutyPosts=DutyPosts)

@app.route('/EditDutyPost',methods=["POST"])
def EditDutyPost():
    global mydb

    mycol = mydb["DutyPosts"]

    restrictions = []
    for i in request.form.items():
        restrictions.append(i[0])
    restrictions.pop(0)
    restrictions.pop(0)

    myquery = {"name": str(request.form["OldDutyPostName"])}
    newvalues = {"$set": {"name": str(request.form["DutyPostName"])}}
    mycol.update_one(myquery, newvalues)





    return redirect(url_for('ManageDutyPost'))

@app.route('/ManageManning')
def ManageManning():
    global mydb

    mycol = mydb["Manning"]
    manning=[]
    for x in mycol.find():
        manning.append(x)
    print(manning)


    return render_template('ManageManning.html',manningdata=manning)

@app.route('/ViewManning/ManageDuties/<id>',methods=["POST","GET"])
def ViewManning(id):
    mycol = mydb["Manning"]

    hoursrequired=0
    if request.method=="POST":
        x = mycol.find_one({"_id":ObjectId(str(id))})
        templist= {"DP": request.form['DP'],"StartDate": request.form['StartDate'],"StartTime": request.form['StartTime'],"EndDate": request.form['EndDate'],"EndTime": request.form['EndTime'],'uid':str(uuid.uuid4()),"person":""}
        x['Data'].append(templist)
        myquery = {"_id":ObjectId(str(id))}
        newvalues = {"$set" : x}

        mycol.update_one(myquery, newvalues)
        return redirect(url_for("ViewManning",id=id))


    data=mycol.find_one({"_id": ObjectId(str(id))})


    # Parse the dates from strings into datetime objects
    date1 = datetime.strptime(data['StartDate']+" "+data["StartTime"], "%d%m%y %H%M")
    date2 = datetime.strptime(data['EndDate']+" "+data["EndTime"], "%d%m%y %H%M")
    # Calculate the difference between the two dates
    difference = relativedelta.relativedelta(date2, date1)

    hours=difference.days*24
    hours+=difference.hours+1

    timestamps={}
    odddatetimes=[]
    for i in data['Data']:
        if i['StartTime'][2:]!='00' and (i['StartDate']+" "+i['StartTime']) not in odddatetimes:
            odddatetimes.append( (i['StartDate']+" "+i['StartTime']))
        if i['EndTime'][2:]!='00'and (i['EndDate']+" "+i['EndTime']) not in odddatetimes:
            odddatetimes.append( (i['EndDate']+" "+i['EndTime']))

    updatedodddatetimes=[]
    odddatetimes.sort()
    for i in odddatetimes:
        updatedodddatetimes.append(datetime.strptime(i, "%d%m%y %H%M"))


    for i in range(hours):

        if len(updatedodddatetimes)>0:
            while 1:
                if len(updatedodddatetimes)==0:
                    break
                diff=relativedelta.relativedelta( (date1+timedelta(hours=i)),updatedodddatetimes[0])
                if diff.minutes + (diff.hours*60)>0:
                    timestamps[(updatedodddatetimes[0].strftime("%d%m%y %H%M") )] = {}
                    updatedodddatetimes.pop(0)
                else:
                    break

        timestamps[((date1+timedelta(hours=i)).strftime("%d%m%y %H%M") )]={}


    mycol = mydb["DutyPosts"]
    dutyposts=mycol.find()
    dutypostsnames=[]
    listoftimestamps=timestamps.keys()
    listoftimestamps=list(listoftimestamps)
    for i in dutyposts:
        dutypostsnames.append(i['name'])
    for i in data['Data']:
        selector=((datetime.strptime(i['StartDate']+" "+i["StartTime"], "%d%m%y %H%M")).strftime("%d%m%y %H%M") )
        olddata=timestamps[selector]
        date1 = datetime.strptime(i['StartDate'] + " " + i["StartTime"], "%d%m%y %H%M")
        date2 = datetime.strptime(i['EndDate'] + " " + i["EndTime"], "%d%m%y %H%M")
        # Calculate the difference between the two dates
        difference = relativedelta.relativedelta(date2, date1)
        hours = difference.days * 24
        hours += difference.hours
        hours +=difference.minutes/60
        hoursrequired+=hours
        hours=listoftimestamps.index(i['EndDate'] + " " + i["EndTime"]) - listoftimestamps.index(
            i['StartDate'] + " " + i["StartTime"])
        if hours==0:
            hours=1
        startindex=listoftimestamps.index(selector)
        for z in range(hours):
            newdata=timestamps[listoftimestamps[startindex+z]]
            newdata[i['DP']] = ["voiditem"]
            timestamps[listoftimestamps[startindex+z]] = newdata

        olddata[i['DP']]=[listoftimestamps.index(i['EndDate']+" "+i["EndTime"])-listoftimestamps.index(i['StartDate']+" "+i["StartTime"]),i['uid'],i['StartDate'],i["StartTime"],i['EndDate'],i["EndTime"],i['person']]
        timestamps[selector]=olddata



    print(data['cannotstand'])

    mycol=mydb['Users']
    userdata=[]
    for x in mycol.find() :
        userdata.append(x)




    return render_template('ViewManning.html',cannotstandlist=data['cannotstand'],data=data,dutypostsnames=dutypostsnames,timestamps=timestamps,id=id,userdata=userdata,hoursrequired=hoursrequired)

@app.route('/UpdateChunk/<manningid>',methods=["POST"])
def UpdateChunk(manningid):
    save=False
    delete=False
    try:
        request.form['Save']
        save=True
    except:
        try:
            request.form['Delete']
            delete=True

        except:
            pass



    mycol = mydb["Manning"]

    x = mycol.find_one({"_id":ObjectId(str(manningid))})
    counter=0
    if save==True or delete==True:
        for i in x['Data']:

            if i['uid']==request.form['ChunkId']:
                templist=i
                x['Data'].pop(counter)
                break
            counter+=1
    if save==True:
        templist["StartDate"]=request.form['StartDate']
        templist["StartTime"]=request.form['StartTime']
        templist["EndDate"]=request.form['EndDate']
        templist["EndTime"]=request.form['EndTime']
        x['Data'].append(templist)

    if save==True or delete==True:
        myquery = {"_id":ObjectId(str(manningid))}
        newvalues = {"$set" : x}
        mycol.update_one(myquery, newvalues)

    return redirect(url_for("ViewManning",id=manningid))


@app.route('/AssignUserToChunk/<manningid>',methods=["POST"])
def AssignUserToChunk(manningid):
    print(request.form['ChunkId'])
    print(request.form['fixedtrooper'])

    mycol = mydb["Manning"]
    x = mycol.find_one({"_id":ObjectId(str(manningid))})
    counter=0
    for i in x['Data']:
        if i['uid']==request.form['ChunkId']:
            newdata=i
            print(newdata)
            newdata['fixedtrooper']=request.form['fixedtrooper']
            break
        counter+=1
    myquery = {"_id" : ObjectId(str(manningid))}
    newvalues = {"$set" : x}
    mycol.update_one(myquery, newvalues)
    return '123'

@app.route('/compute',methods=["POST"])
def Compute():

    premanning={}
    mycol = mydb["Manning"]

    x = mycol.find_one({"_id":ObjectId(str(json.loads(request.data.decode())['id']))})

    mycol = mydb["Users"]
    userlist=[]
    y = mycol.find()
    for i in y:
        userlist.append(i)
    counter=0
    print(x['Data'])

    # for i in x['Data']:
    #     templist=i
    #     tempuserlist=userlist
    #     while 1:
    #         breakout=True
    #         person = tempuserlist[random.randint(0, len(tempuserlist) - 1)]['name']
    #         for k in biggertemplist:
    #             if k['person']==person and (abs(find_time_diff(k['EndDate'],k['EndTime'],i['StartDate'],i['StartTime']))<6 or (i['StartDate'],i['StartTime'])==(k['StartDate'],k['StartTime']) or (abs(find_time_diff(i['EndDate'],i['EndTime'],k['StartDate'],k['StartTime']))<6)):
    #                 print(abs(find_time_diff(k['EndDate'],k['EndTime'],i['StartDate'],i['StartTime'])),'invalid', (i['StartDate'],i['StartTime'])==(k['StartDate'],k['StartTime']))
    #                 breakout=False
    #         if breakout==True:
    #             print(person,i)
    #             break
    #     templist['person'] = person
    #     biggertemplist.append(templist)
    tempuserlist=[]
    for i in userlist:
        if str(i['_id']) not in json.loads(request.data.decode())['cannotstand']:
            tempuserlist.append(i)
    userlist=tempuserlist

    print(userlist)
    while 1:
        Data=computingthing(x, userlist)
        if Data!=False:
            x["Data"] =Data
            break

    x['cannotstand']=json.loads(request.data.decode())['cannotstand']
    myquery = {"_id":ObjectId(str(json.loads(request.data.decode())['id']))}

    mycol = mydb["Manning"]
    mycol.update_one(myquery,{ "$set": x })

    print('done')
    return  redirect(url_for("ViewManning",id=str(json.loads(request.data.decode())['id'])))


def find_time_diff(StartDate,StartTime,EndDate,EndTime):
    date1 = datetime.strptime(StartDate + " " + StartTime, "%d%m%y %H%M")
    date2 = datetime.strptime(EndDate + " " + EndTime, "%d%m%y %H%M")
    # Calculate the difference between the two dates
    difference = relativedelta.relativedelta(date2, date1).hours
    return difference


def computingthing(dataset,userlist):
    print('trying')
    print(dataset)
    tempdict=dataset['Data']

    sortedlist = sorted(tempdict, key=lambda elem : "%46s%24s%02s%04s" % (
    elem['StartDate'], elem['StartDate'], elem['StartDate'], elem['StartTime']))
    dataset['Data']=sortedlist
    x=dataset
    biggertemplist=[]

    backuplist=userlist

    for i in x['Data']:
        templist=i
        tempuserlist=copy.deepcopy(userlist)
        
        while 1:
            breakout=True
            randomnumber=random.randint(0, len(tempuserlist) - 1)
            person = tempuserlist[randomnumber]['name']
            tempuserlist.pop(randomnumber)

            for k in biggertemplist:
                if k['person']==person and (abs(find_time_diff(k['EndDate'],k['EndTime'],i['StartDate'],i['StartTime']))<find_time_diff(k['StartDate'],k['StartTime'],k['EndDate'],k['EndTime']) or (i['StartDate'],i['StartTime'])==(k['StartDate'],k['StartTime']) or (abs(find_time_diff(i['EndDate'],i['EndTime'],k['StartDate'],k['StartTime']))<(abs(find_time_diff(k['StartDate'],k['StartTime'],k['EndDate'],k['EndTime']))))):
                    breakout=False
            if breakout==True:
                break
            if len(tempuserlist)==0:
                return False

        templist['person'] = person
        biggertemplist.append(templist)
    return biggertemplist


if __name__ == '__main__':

    app.run(debug=True, host='127.0.0.1', port=5000)
