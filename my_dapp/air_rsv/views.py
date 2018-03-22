# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Create your views here.
    # -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404,render, redirect
from django.http import HttpResponse
from models import *
import json
from django.views.decorators import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.core.exceptions import *
import datetime
from django.core.exceptions import ValidationError
from models import *

def phone_valid(value):
    val = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                 code='invalid_phonenumber')
    try :
        val=val(value)
        return None
    except:
        return "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."


def date_valid(value):
    val = RegexValidator(regex=r'^\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$',
                                message="Enter valid date")
    try:
        val(value)
        return None
    except:
        return "Enter valid date"

@ensure_csrf_cookie
def change_password(request):
    if request.method == "POST":
        if request.session['type'] == 'passenger':
            passenger = Passenger.objects.get(email = request.session['id'])
            oldpassword = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            if passenger.check_password(oldpassword):
                passenger.set_password(passenger.make_password(newpassword))
                passenger.save()
            else:
                messages.error(request,'Old Password Incorrect')
            return redirect('/')
        elif request.session['type'] == 'airline':
            airline = Airline.objects.get(email = request.session['id'])
            oldpassword = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            if airline.check_password(oldpassword):
                airline.set_password(airline.make_password(newpassword))
                airline.save()
            else:
                messages.error(request,'Old Password Incorrect')
            return redirect('/')
    else:
        if request.session['type'] == 'passenger':
            return render(request,"air_rsv/change_password_user.html",{'base':'base_user.html'})
        else :
            return render(request,"air_rsv/change_password_user.html",{'base':'base_airline.html'})

def home(request):
    if 'id' in request.session.keys():
        if request.session['type'] == 'passenger':
            passenger = Passenger.objects.get(email = request.session['id'])
            context = {'object' : passenger,'base':'base_user.html'}
            return render(request,'air_rsv/user_profile.html', context)
        elif request.session['type'] == 'airline':
            airline = Airline.objects.get(email=request.session['id'])
            context = {'object': airline, 'base': 'base_airline.html'}
            return render(request,'air_rsv/user_profile.html',context)
    else:
        return render(request,"air_rsv/home.html")

@ensure_csrf_cookie
def signup(request):
    if 'id' in request.session.keys():
        if request.session['type'] == 'passenger':
            passenger = Passenger.objects.get(email = request.session['id'])
            context = {'object' : passenger,'base':'base_user.html'}
            return render(request,'air_rsv/user_profile.html', context)
        elif request.session['type'] == 'airline':
            airline = Airline.objects.get(email=request.session['id'])
            context = {'object': airline, 'base': 'base_airline.html'}
            return render(request,'air_rsv/user_profile.html',context)

    if request.method == 'POST':
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST.get('password')
        usertype = request.POST.get('usertype')
        print usertype
        phonenumber = request.POST.get('phonenumber')
        if usertype == 'passenger':
            user = Passenger(email = email,firstname=firstname,lastname=lastname, password = password, phonenumber = phonenumber)
            user.set_password(user.make_password(password))
            # checking the regex
            error = phone_valid(user.phonenumber)
            if error is None:
                user.save()
            else:
                messages.error(request, error)
                return redirect('/register')
            request.session['type'] = 'passenger'
            request.session['id'] = email
        elif  usertype == 'airline':
            user = Airline(email = email,firstname=firstname,lastname=lastname, password = password, phonenumber = phonenumber)
            user.set_password(user.make_password(password))
            # checking the regexs
            error = phone_valid(user.phonenumber)
            if error is None:
                user.save()
            else:
                messages.error(request, error)
                return redirect('/register')
            request.session['type'] = 'airline'
            request.session['id'] = email
        return redirect('/')
    if request.method == 'GET':
        return render(request,'air_rsv/register.html')


@ensure_csrf_cookie
def signin(request):

    if 'id' in request.session.keys():
        if request.session['type'] == 'passenger':
            passenger = Passenger.objects.get(email=request.session['id'])
            context = {'object': passenger, 'base': 'base_user.html'}
            return render(request, 'air_rsv/user_profile.html', context)
        elif request.session['type'] == 'airline':
            airline = Airline.objects.get(email=request.session['id'])
            context = {'object': airline, 'base': 'base_airline.html'}
            return render(request, 'air_rsv/user_profile.html', context)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            passenger = Passenger.objects.get(email=email)
            if passenger.check_password(password):
                request.session['id'] = email
                request.session['type'] = 'passenger'
                return redirect('/')
            else:
                messages.error(request,'Password Incorrect')
                return redirect('/signin')
        except:
            try:
                airline = get_object_or_404(Airline, email=email)
                if airline.check_password(password):
                    request.session['id'] = email
                    request.session['type'] = 'airline'
                    return redirect('/')
                else:
                    messages.error(request,'Password Incorrect')
                    return redirect('/signin')
            except:
                messages.error(request,'No Passenger or Airline is registered with this email')
                return redirect('/signin')

    elif request.method == 'GET':
        return render(request,'air_rsv/signin.html')

def logout(request):
    try:
        del request.session['id']
        del request.session['type']
        request.session.modified = True
    except KeyError:
        pass
    return render(request, 'air_rsv/home.html')


@ensure_csrf_cookie
def add_flight(request):
    if request.method=="POST":
        flightid = request.POST['flightid']
        business_fare = request.POST['business_fare']
        economy_fare = request.POST['economy_fare']
        total_seats = request.POST['total_seats']
        airline_email = Airline.objects.get(email= request.POST['airline_id'])
        source_id = Airport.objects.get(airport_id=request.POST['source_id'])
        source_dep = request.POST['source_dep']
        destination_id = Airport.objects.get(airport_id=request.POST['destination_id'])
        destination_arr = request.POST['destination_arr']
        day_offset = request.POST['day_offset']
        intermediate_stops = request.POST['intermediate_stops']
        flight=Flight(flight_id = flightid,	business_classfare = business_fare,economy_classfare = economy_fare,	total_seats =total_seats ,
	            airline_email = airline_email,	daysoffset = day_offset,sourceid = source_id,	departureid = destination_id ,	departure_time = source_dep,arrival_time = destination_arr)
        flight.save()
        key_ar="inter_arrtime"
        key_dest_id="destination_id"
        key_inter_dp="inter_deptime"
        key_id_off="interday_offset"
        print intermediate_stops,"asdfghj"
        for i in range(1,int(intermediate_stops)+1):
            inter_arrtime=request.POST[key_ar+str(i)]
            destination_id=Airport.objects.get(airport_id=request.POST[key_dest_id+str(i)])
            inter_deptime=request.POST[key_inter_dp+str(i)]
            interday_offset=request.POST[key_id_off+str(i)]
            int_med_stop=IntermediateStop(flight_id = flight,stop_id =destination_id ,daysoffset = interday_offset,	departure_time = inter_deptime,
                                          arrival_time = inter_arrtime)
            int_med_stop.save()
        return redirect('/')
    else:
        return render(request,'air_rsv/flightadd.html')


def remove_flight(request):
    if request.method=="POST":
        flight=Flight.objects.get(flight_id=request.POST['flight_id'])
        flight.delete()
        return redirect('/')
    else:
        return render(request,'air_rsv/flightremove.html')

def flight_data(request):
    airline=Airline.objects.get(email=request.session['id'])
    flight_obj=Flight.objects.filter(airline_email=airline)
    return render(request,'air_rsv/flight_data.html',{'flight':flight_obj})
