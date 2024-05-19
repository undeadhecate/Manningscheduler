from flask import Flask, render_template, request,redirect,url_for
import pymongo
from bson import ObjectId
from dateutil import relativedelta
from datetime import datetime,timedelta
import uuid
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

@app.route('/ViewManning/<id>',methods=["POST","GET"])
def ViewManning(id):
    mycol = mydb["Manning"]


    if request.method=="POST":
        x = mycol.find_one({"_id":ObjectId(str(id))})
        templist= {"DP": request.form['DP'],"StartDate": request.form['StartDate'],"StartTime": request.form['StartTime'],"EndDate": request.form['EndDate'],"EndTime": request.form['EndTime'],'uid':str(uuid.uuid4())}
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
    for i in range(hours):
        timestamps[((date1+timedelta(hours=i)).strftime("%d%m%y %H%M") )]={}

    mycol = mydb["DutyPosts"]
    dutyposts=mycol.find()
    dutypostsnames=[]
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

        olddata[i['DP']]=[hours,i['uid'],i['StartDate'],i["StartTime"],i['EndDate'],i["EndTime"],]
        print(olddata)
        timestamps[selector]=olddata

    print(timestamps)
    return render_template('ViewManning.html',data=data,dutypostsnames=dutypostsnames,timestamps=timestamps,id=id)

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



if __name__ == '__main__':

    app.run(debug=True, host='127.0.0.1', port=5000)
