from email._header_value_parser import get_value

from flask import render_template, flash, redirect, request, url_for
from werkzeug.debug import console
from werkzeug.urls import url_parse
from app import app
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from app import db

import sqlite3

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc!='':
            next_page=url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    # Logout to index page
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form =RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,\
                  fullname=form.fullname.data,\
                  position=form.position.data,\
                  teamId=form.teamId.data)
        user.set_password(form.password.data)
        db.session.add(user)
        team=Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam=Team(id=user.teamId,\
                         teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash('Registered with a new team created')
            return redirect(url_for('login'))
        else:
            db.session.commit()
            flash('Registered to an existing team')
            return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/adduser', methods=['GET','POST'])
@login_required
def adduser():
    # if not current_user.is_authenticated:
    #     flash('Please Log in as admin to add user')
    #     return redirect(url_for('login'))
    # if current_user.username!='admin':
    #     flash('Please Log in as admin to add user')
    #     return redirect(url_for('index'))
    form =AdduserForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,\
                  fullname=form.fullname.data,\
                  position=form.position.data,\
                  teamId=form.teamId.data)
        user.set_password(form.password.data)
        db.session.add(user)
        team=Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam=Team(id=user.teamId,\
                         teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash(f'Added user {form.username.data} with a new team created')
            return redirect(url_for('adduser'))
        else:
            db.session.commit()
            flash(f'Added user {form.username.data} to an existing team')
            return redirect(url_for('adduser'))
    return render_template('adduser.html',title='Add User',form=form)

@app.route('/addteam',methods=['GET','POST'])
@login_required
def addteam():
    # if not current_user.is_authenticated:
    #     flash('Please Log in as admin to add team')
    #     return redirect(url_for('login'))
    # if current_user.username!='admin':
    #     flash('Please Log in as admin to add team')
    #     return redirect(url_for('index'))


    form=AddteamForm()
    if form.validate_on_submit():
        team=Team(id=form.id.data,\
                  teamName=form.teamName.data)
        db.session.add(team)
        db.session.commit()
        flash(f'Team {form.teamName.data} successfully added!')
        return redirect(url_for('addteam'))
    return render_template('addteam.html',title='Add Team',form=form)
        
@app.route('/deleteteam',methods=['GET','POST'])
@login_required
def deleteteam():
    # if not current_user.is_authenticated:
    #     flash('Please Log in as admin to delete team')
    #     return redirect(url_for('login'))
    # if current_user.username!='admin':
    #     flash('Please Log in as admin to delete team')
    #     return redirect(url_for('index'))

    form=DeleteteamForm()
    
    if form.validate_on_submit():
        team=Team.query.filter_by(id=form.ids.data).first()

        meetings = Reservation.query.filter_by(teamId=team.id).all()
        hasFutureBooking=False
        for meeting in meetings:
            if meeting.date>datetime.now():
                hasFutureBooking=True
                break
        if hasFutureBooking:
            flash('You cannot delete a team that holds future bookings!')
            return redirect(url_for('deleteteam'))

        # delete all users in a deleted team
        userInTeam=User.query.filter_by(teamId=form.ids.data).all()
        for user in userInTeam:
            db.session.delete(user)
        db.session.delete(team)
        db.session.commit()
        flash(f'Team {team.teamName} and team members successfully deleted! Please register member again to other team')
        return redirect(url_for('index'))
    form=DeleteteamForm()
    return render_template('deleteteam.html',title='Delete Team',form=form)

@app.route('/deleteuser',methods=['GET','POST'])
@login_required
def deleteuser():
    # if not current_user.is_authenticated:
    #     flash('Please Log in as admin to delete user')
    #     return redirect(url_for('login'))
    # if current_user.username!='admin':
    #     flash('Please Log in as admin to delete user')
    #     return redirect(url_for('index'))

    
    form=DeleteuserForm()
    if form.validate_on_submit():
        user=User.query.filter_by(id=form.ids.data).first()

        meetings=Reservation.query.filter_by(bookerId=user.id).all()
        hasFutureBooking=False
        for meeting in meetings:
            if meeting.date>datetime.now():
                hasFutureBooking=True
                break
        if hasFutureBooking:
            flash('You cannot delete a user that holds future bookings!')
            return redirect(url_for('deleteuser'))

        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} successfully deleted! ')
        return redirect(url_for('index'))
    return render_template('deleteuser.html',title='Delete User',form=form)


@app.route('/book',methods=['GET','POST'])
@login_required
def book():
    form=BookmeetingForm()
    if form.validate_on_submit():
        
        # check time collision
        meetingcollisions=Reservation.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=form.rooms.data).all()
        print(len(meetingcollisions))
        for meetingcollision in meetingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (form.startTime.data<meetingcollision.floatendtime and (form.startTime.data+form.duration.data)>meetingcollision.startTime):
                flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().fullname}.')
                return redirect(url_for('book'))

        # make booking
        booker=current_user

        team=Team.query.filter_by(id=current_user.teamId).first()
        room=Service.query.filter_by(id=form.rooms.data).first()
        cost=int(room.cost)
        endTime=form.startTime.data+form.duration.data/60
        hour = int(endTime // 1)
        minute = int((endTime % 1) * 60)
        if minute == 0 :
            new_endtime = str(hour) + ":00"
        else:
            new_endtime=str(hour) + ":" + str(minute)
        participants_user=form.participants_user.data
        participants_partner=form.participants_partner.data

        meeting=Reservation(title=form.title.data,teamId=team.id,roomId=room.id,bookerId=booker.id,date=form.date.data,startTime=form.startTime.data,endTime=new_endtime,floatendtime=endTime,duration=form.duration.data,group=form.group.data,cost=cost*form.duration.data)
        db.session.add(meeting)

        # Add booking log
        log=CostLog(title=form.title.data,teamId=team.id,teamName=team.teamName,date=form.date.data,cost=cost*form.duration.data,group=form.group.data)
        db.session.add(log)

        #Add Group info
        #new_group_name = form.group.data
        #old_group_name = Group.query.filter_by()
        group_name = Group(group=form.group.data)
        db.session.add(group_name)

        # Add participants records
        for participant in participants_user:
            participating=Assistant(meeting=form.title.data,userId=participant)
            db.session.add(participating)
        for participant in participants_partner:
            participating=Participants_partner(meeting=form.title.data,partnerId=participant)
            db.session.add(participating)

        db.session.commit()
        flash('Added new reservation successfully!')
        return redirect(url_for('index'))
    return render_template('book.html',title='Reservation',form=form)

@app.route('/cancelbooking',methods=['GET','POST'])
@login_required
def cancelbooking():

    
    form=CancelbookingForm()
    if form.validate_on_submit():
        meeting=Reservation.query.filter_by(id=form.ids.data).first()

        if meeting.date<=datetime.now():
            flash(f'Past booking cannot be canceled')
            return redirect(url_for('cancelbooking'))

        cancellist = Cancel(title=meeting.title,teamId=meeting.teamId,roomId=meeting.roomId,bookerId=meeting.bookerId,date=meeting.date,startTime=meeting.startTime,endTime=meeting.endTime,floatendtime=meeting.floatendtime,duration=meeting.duration,group=meeting.group,cost=meeting.cost)
        #cancellist  = meeting
        db.session.add(cancellist)

        participants_user=Assistant.query.filter_by(meeting=meeting.title).all()
        for part in participants_user:
            db.session.delete(part)
        participants_partner=Participants_partner.query.filter_by(meeting=meeting.title).all()
        for part in participants_partner:
            db.session.delete(part)
        
        costlog=CostLog.query.filter_by(title=meeting.title).first()
        db.session.delete(costlog)

        db.session.delete(meeting)
        db.session.commit()
        flash(f'Reservation for {meeting.title} successfully deleted! ')
        return redirect(url_for('index'))
    return render_template('cancelbooking.html',title='Cancel Meeting',form=form)

@app.route('/roomavailable',methods=['GET','POST'])
@login_required
def roomavailable():

    form=RoomavailableForm()
    if form.validate_on_submit():
        meetings=Reservation.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        roomsOccupied=set()
        for meeting in meetings:
            if (form.startTime.data<meeting.floatendtime and (form.startTime.data+form.duration.data)>meeting.startTime):
                roomsOccupied.add(Service.query.filter_by(id=meeting.roomId).first())
        rooms=Service.query.all()
        roomsavailable=[]
        for room in rooms:
            if room not in roomsOccupied:
                roomsavailable.append(room)
        return render_template('availablelist.html',title='Room available',rooms=roomsavailable)
    return render_template('available.html',title='Room availability check',form=form)

@app.route('/reservationreport',methods=['GET','POST'])
def reservationreport():
    if not current_user.is_authenticated:
        flash('Please Log in as admin to access to reservation report')
        return redirect(url_for('login'))
    if current_user.username!='admin':
        flash('Please Log in as admin to access to reservation report')
        return redirect(url_for('index'))
    form = ReservationreportForm()
    if form.validate_on_submit():

        room = Service.query.filter_by(id=form.rooms.data).first()

        meetings=Reservation.query.filter_by(roomId=room.id).filter(Reservation.date>=datetime.combine(form.startdate.data,datetime.min.time())).filter(Reservation.date<=datetime.combine(form.enddate.data,datetime.min.time())).all()



        reservationlist =[]

        for meeting in meetings:
            reservationlist.append(meeting)
        return render_template('reservationlist.html',title='Reservation list', meetings=reservationlist)
    return render_template('reservation.html',title='Reservation Report', form=form)

@app.route('/cancellationreport',methods=['GET','POST'])
def cancellationreport():
    if not current_user.is_authenticated:
        flash('Please Log in as admin to access to cancellation report')
        return redirect(url_for('login'))
    if current_user.username!='admin':
        flash('Please Log in as admin to access to cancellation report')
        return redirect(url_for('index'))
    form = CancellationreportForm()
    if form.validate_on_submit():

        room = Service.query.filter_by(id=form.rooms.data).first()

        meetings=Cancel.query.filter_by(roomId=room.id).filter(Cancel.date>=datetime.combine(form.startdate.data,datetime.min.time())).filter(Cancel.date<=datetime.combine(form.enddate.data,datetime.min.time())).all()

        cancellationlist =[]
        for meeting in meetings:
            cancellationlist.append(meeting)
        return render_template('cancellationlist.html',title='Cancellation list', meetings=cancellationlist)
    return render_template('cancellation.html',title='Cancellation Report', form=form)


@app.route('/updateservice', methods=['GET','POST'])
def updateservice():
    if not current_user.is_authenticated:
        flash('Please Log in as admin to update service')
        return redirect(url_for('login'))
    if current_user.username!='admin':
        flash('Please Log in as admin to update service')
        return redirect(url_for('index'))

    form = UpdateserviceForm()

    if form.validate_on_submit():

        service= Service.query.filter_by(id=form.update_rooms.data).first()
        service.cost = form.cost.data

        # db.session.update(service)
        db.session.commit()


        rooms = Service.query.all()
        allrooms = []
        for room in rooms:
            allrooms.append({'roomName': room.roomName, 'cost': room.cost})

        return render_template('updateservicelist.html', title='Update Service List',allrooms=allrooms, form=form )
    return render_template('updateservice.html',title ='Update Service',form =form)




    # return render_template('updateservice.html', title='Update Service',allrooms=allrooms)


@app.route('/roomoccupation',methods=['GET','POST'])
@login_required

def roomoccupation():

    form=RoomoccupationForm()
    if form.validate_on_submit():
        #meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        roomoccus=[]
        hours=range(8,21)
        rooms=Service.query.all()
        allrooms=[]
        for room in rooms:
            roomoccu=dict()
            roomoccu['roomName']=room.roomName
            roomoccu['roomhours']=[False]*13
            for hour in hours:
                meetings=Reservation.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=room.id).all()
                
                for meeting in meetings:
                    if (hour)<meeting.floatendtime and (hour+0.5)>meeting.startTime:
                        roomoccu['roomhours'][hour-8]=True
                        break
            roomoccus.append(roomoccu)

            allrooms.append({'roomName': room.roomName, 'cost': room.cost})
            #allrooms.append({'roomName':room.roomName,'tel':'Yes' if room.telephone else 'No','pro':'Yes' if room.projector else 'No',\
             #               'wb':'Yes' if room.whiteboard else 'No','cost':room.cost})
            #< td > {{room.tel}} < / td >
            #< td > {{room.pro}} < / td >
            #< td > {{room.wb}} < / td >
            #< th > Telephone < / th >
            #< th > Projector < / th >
            #< th > WhiteBoard < / th >

        return render_template('occupationlist.html',title='Room Occupation',roomoccus=roomoccus,date=form.date.data,hours=[str(hour) for hour in hours],allrooms=allrooms)
    return render_template('occupation.html',title='Room Occupation Status',form=form)

@app.route('/meetingbooker')
@login_required
def meetingbooker():


    meetings=Reservation.query.order_by(Reservation.date).all()
    meetingreturns=[]
    for meeting in meetings:
        meetingreturn=dict()
        meetingreturn['title']=meeting.title
        meetingreturn['group']=meeting.group
        meetingreturn['room']=Service.query.filter_by(id=meeting.roomId).first().roomName
        meetingreturn['booker']=User.query.filter_by(id=meeting.bookerId).first().fullname
        meetingreturn['date']=meeting.date.date()
        meetingreturn['time']=f'{meeting.startTime} to {meeting.endTime}'
        meetingreturn['cost']=meeting.cost
        meetingreturns.append(meetingreturn)
    return render_template('booker.html',meetings=meetingreturns)

@app.route('/cancellist')
@login_required
def cancellist():

    cancels = Cancel.query.order_by(Cancel.date).all()
    cancelreturns=[]
    for cancel in cancels:
        cancelreturn=dict()
        cancelreturn['title']=cancel.title
        cancelreturn['group']=cancel.group
        cancelreturn['room']=Service.query.filter_by(id=cancel.roomId).first().roomName
        cancelreturn['booker']=User.query.filter_by(id=cancel.bookerId).first().fullname
        cancelreturn['date']=cancel.date.date()
        cancelreturn['time']=f'{cancel.startTime} to {cancel.endTime}'
        cancelreturn['cost']=cancel.cost
        cancelreturns.append(cancelreturn)
    return render_template('cancellist.html',cancels=cancelreturns)



@app.route('/meetingparticipants',methods=['GET','POST'])
@login_required
def meetingparticipants():

    form=MeetingparticipantsForm()

    if form.validate_on_submit():
        meeting=Reservation.query.filter_by(id=form.ids.data).first()
        participants=[]
        participants_user=Assistant.query.filter_by(meeting=meeting.title).all()
        participants_partner=Participants_partner.query.filter_by(meeting=meeting.title).all()


        participants.append(f'Group: {meeting.group}')
        participants.append(f'Date: {meeting.date.date()}')
        participants.append(f'Start Time: {meeting.startTime}')
        participants.append(f'End Time: {meeting.endTime}')
        participants.append(f'Cost: {meeting.cost}')
        for part in participants_user:
            participants.append(f'Assistant: {User.query.filter_by(id=part.userId).first().fullname}')
        for part in participants_partner:
            participants.append(f'Accessory: {Accessory.query.filter_by(id=part.partnerId).first().name} ')

        return render_template('participants.html',title='Meeting Participants',meetingtitle=meeting.title,participants=participants)
    return render_template('participantscheck.html',title='Meeting Participants',form=form)





@app.route('/costs',methods=['GET','POST'])
@login_required

def costs():

    form=CostaccruedForm()
    if form.validate_on_submit():


        costlogs=CostLog.query.all()
        teams=list(set([costlog.group for costlog in costlogs]))
        teamcosts=[]

        # slow implementation, can be optimized
        for team in teams:
            teamcost=dict()
            teamcost['group']=team
            teamcost['total']=0
            teamcost['member']=[]

            for costlog in costlogs:
                if costlog.group==team:
                    teamcost['total']+=costlog.cost
                    teamcost['member'].append(costlog.title)
            teamcosts.append(teamcost)
        return render_template('costs.html',title='Cost Accrued',group=costlog.group,teamcosts=teamcosts)
    return render_template('costcheck.html',title='Cost Accrued check',form=form)