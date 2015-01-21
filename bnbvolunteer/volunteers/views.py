from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from random import randint
from django.utils.safestring import mark_safe

from volunteers import userManagement
from volunteers.models import *
from volunteers.userManagement import *

from datetime import date
from datetime import datetime

import csv

@login_required
def volunteerHome(request):
    try:
        user = request.user #authenticate(username='admin', password='adMIN')
        context = getVolunteerPageContext(request,user)
    except:
        print "Not logged in"
        context = {'query_results': [],'total_credits':0,'type_choices':[]}
    return render(request,'volunteers/volunteerHome.html',context)

@login_required
def volunteerSubmit(request):
    try:
        user = request.user #authenticate(username='admin', password='adMIN')
    except:
        print "ERROR UGHHH"
    date = request.POST['date']
    print request.POST['activityType']
    try:
        activityType = ActivityType.objects.filter(name=request.POST['activityType'])[0]
    except:
        activityType1 = ActivityType(name="Edit me out later")
        activityType2 = ActivityType(name="Views.py somewhere")
        activityType1.save()
        activityType2.save()
        activityType = ActivityType.objects.filter(name=request.POST['activityType'])[0]
    # activityType.save()
    description = request.POST['description']
    earned = request.POST.getlist('myInputs')
    print earned
    totalearned = 0
    invalid = []
    invalid_boolean = "False"
    valid_vouchers = Voucher.objects.exclude(redemptionActivity__isnull=False)
    # print Voucher.objects.all()[1].redemptionActivity.description
    print "valid: " + str(valid_vouchers)
    vouchers_used = []
    for voucher_code in earned: #input
        voucher_set = valid_vouchers.filter(code = voucher_code.encode('utf8'))
        print voucher_code.encode('utf8')
        if len(voucher_set)==1:
            # print voucher
            voucher = voucher_set[0]
            totalearned+=voucher.credits
            vouchers_used.append(voucher)
            print "VALID!"
        elif len(voucher_set)==0:
            invalid.append((voucher_code.encode('utf8')))
            invalid_boolean = "True"
        else: 
            return HttpResponse("Error: Multiple vouchers exist for that code")
    storedate = date[6:10]+'-'+date[0:2]+'-'+date[3:5] #reformat the date :/
    activity = Activity(user=user,dateDone=storedate,activityType = activityType, description=description,credits=totalearned) #request.user
    # try: 
    if len(invalid) == 0:
        activity.save()
    # except:
    #     print "ERROR"
    for voucher in vouchers_used:
        voucher.redemptionActivity = activity
        voucher.save()

    context = getVolunteerPageContext(request,user)
    # return HttpResponse("Hi there!")
    context['invalid_vouchers']=mark_safe(invalid)
    context['invalid_boolean']=invalid_boolean
    print invalid_boolean
    return render(request,'volunteers/volunteerHome.html',context)

def getVolunteerPageContext(request,user):
    query_results = Activity.objects.filter(user=user)
    total_credits = 0
    for log in query_results:
        total_credits += log.credits
    type_choices = ActivityType.objects.values_list('name', flat=True)
    # jq = ActivityType.objects.exclude(id__in=activities)
    # type_choices = jq.values_list('name', flat=True)
    if len(type_choices) == 0:
        type_choices = ["Edit me out later","Views.py somewhere"]
    context = {'query_results': query_results,'total_credits':total_credits,'type_choices':type_choices}
    return context

@user_passes_test(lambda user: user.is_staff)
def volunteerStaffHome(request):
    Logs = Activity.objects.all()
    try:
        user = request.user #authenticate(username='admin', password='adMIN')
    except:
        print "Not logged in"
    context = {'Logs': Logs}
    return render(request,'volunteers/volunteerStaffHome.html',context)

    # try:
    #     user = request.user #authenticate(username='admin', password='adMIN')
    #     context = getVolunteerPageContext(request,user)
    # except:
    #     print "Not logged in"
    #     context = {'query_results': [],'total_credits':0,'type_choices':[]}
    # return render(request,'volunteers/volunteerHome.html',context)

@login_required
def volunteerStaffLog(request):
    Logs = Activity.objects.all().order_by('-dateEntered')
    if request.method == "POST":
        
        Logs = Activity.objects.exclude(dateDone__gt=request.POST['dateDoneUp']).filter(dateDone__gte=request.POST['dateDoneDown']).order_by('-dateEntered')
        context = {'Logs': Logs, 'dateDoneUp': request.POST['dateDoneUp'], 'dateDoneDown': request.POST['dateDoneDown']}
    else:
        context = {'Logs': Logs, 'dateDoneUp': date.today().isoformat(), 'dateDoneDown': "2000-01-01"}
    return render(request, 'volunteers/volunteerStaffLog.html', context)


@login_required
def volunteerStaffActivity(request):
    if request.method == "POST":
        if not request.POST['activityName'] == "":
            ActivityType(name=request.POST['activityName']).save()
    if 'delete' in request.GET:
        ActivityType.objects.get(id=request.GET['delete']).delete()
        return HttpResponseRedirect(reverse("volunteerStaffActivity"))
    query_results = ActivityType.objects.all()
    context = {'query_results': query_results}
    return render(request, 'volunteers/volunteerStaffActivity.html', context)

@login_required
def volunteerStaffUserSearchResult(request):
    inform = ""
    if request.method == "GET":
        search_results = User.objects.all() 
    else:
        if 'lastname' in request.POST.keys():
            if request.POST['lastname'] != "":    
                search_results = User.objects.filter(last_name=request.POST['lastname'])
            else:
                search_results = User.objects.all()
        else:
            search_results = User.objects.all()
            try:  
                s = 1 + int(request.POST['credits'])
                for user in search_results:
                    if user.username in request.POST.keys():
                        if request.POST[user.username]:
                            addLog = Activity(user=user,  description=request.POST['description'], credits=request.POST['credits'], staff=request.user)
                            if int(request.POST['credits']) + user.profile.credit >= 0:
                                addLog.save();
                                user.profile.credit += int(request.POST['credits'])
                                user.profile.save()
                            else:
                                inform += user.username + ', '
            except:
                inform = "Please type an integer in credits."
    if not inform == "":
        inform = "No enough credits for " + inform[:-2] +"!" 
    context = {'search_results': search_results,  'inform': inform}
    return render(request, 'volunteers/volunteerStaffSearchResults.html', context)

@login_required
def volunteerStaffUser(request):
    inform = ""
    userSearch_result = User.objects.get(username=request.GET['getuser'])
    search_results = Activity.objects.filter(user=userSearch_result)
    creditSum = 0
    for result in search_results:
        creditSum += result.credits
    if request.method == "POST":
        try:
            addLog = Activity(user=userSearch_result,  description=request.POST['description'], credits=request.POST['credits'], staff=request.user)
            if creditSum + int(addLog.credits) < 0:
                inform = "Do not have enough credits"
            else:
                addLog.save()
                search_results = Activity.objects.filter(user=userSearch_result)
                creditSum += int(addLog.credits)
        except:
            inform = "Please type an integer in credits."
    userSearch_result.profile.credit = creditSum
    userSearch_result.profile.save()
    context = {'search_results': search_results, 'getuser':userSearch_result, 'inform': inform}
    return render(request, 'volunteers/volunteerStaffUser.html', context)


def userLogin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.process(request):
            if "next" in request.GET:
                redirect = request.GET["next"]
            else:
                if not request.user.has_perm('staff_status'):
                    redirect = reverse("volunteerHome")
                else: 
                    redirect = reverse("volunteerStaffHome")
            return HttpResponseRedirect(redirect)
        else:
            return render(request, "volunteers/login.html", {"form": form})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse("volunteerHome"))
        else:
            return render(request, "volunteers/login.html", {"form": LoginForm()})

def userRegistration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.process(request):
            return HttpResponseRedirect(reverse('userLogin'))
        else:
            return render(request, "volunteers/register.html", {"form": form})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse("volunteerHome"))
        else:
            return render(request, "volunteers/register.html", {"form": RegistrationForm()})

@login_required
def editProfile(request):
    if request.method == "POST":
        infoForm = EditProfileForm(request.POST)
        infoForm.process(request)
        pwForm = PasswordChangeForm(request.POST)
        if pwForm.isFilled(request):
            pwForm.process(request)
    else:
        infoForm = EditProfileForm(createUserContext(request.user))
        pwForm = PasswordChangeForm()
    returnPage = "volunteerHome"
    if request.user.has_perm("staff_status"):
        returnPage = "volunteerStaffHome"
    return render(request, "volunteers/profile.html", {"infoForm": infoForm, "pwForm": pwForm, "returnPage": returnPage})

def verify(request, code):
    verificationRequests = VerificationRequest.objects.filter(code=code)
    if verificationRequests:
        message = verificationRequests[0].verify()
        return HttpResponse(message)
    else:
        return HttpResponse("Invalid code.")

@login_required
def deleteAccount(request):
    userManagement.deleteAccount(request)
    return HttpResponseRedirect(reverse("editProfile"))

@login_required
def search(request):
    context = {}
    return render(request,'volunteers/search.html',context)

@login_required
def updateProfile(request):
    context = {}
    return render(request,'volunteers/updateProfile.html',context)

@user_passes_test(lambda user: user.is_staff)
def codeGenerator(request):
    context = {}
    return render(request,'volunteers/codeGenerator.html',context)

#Generates an 8-digit-long random code that alternates between capital letters and numbers 1-9
def generateCode():
    
    #Returns a string of a single random capitalized letter of the alphabet 
    def getRandomLetter():
        return chr(65+randint(0,25))
    
    code = ""
    for i in range(0,8):
        if (i%2 == 0):
            letter = getRandomLetter()
            code += str(letter)
        else:
            integer = randint(1,9)
            code += str(integer)
    return code

@user_passes_test(lambda user: user.is_staff)
def generateCodes(request):
    generatedVouchers = []
    for counter in range(1,16):
        voucherInfo = request.POST.getlist("myInputs"+str(counter))
        print "Let's a go! For the "+str(counter)+"th time!"
        print "voucherInfo:"+str(voucherInfo)
        if voucherInfo == []:
            print "We've reached the endddddd"
            break
        points = voucherInfo[0]
        quantity = voucherInfo[1]
        if (points == "" or quantity == ""):
            print "You left a field blank yo.."
            #TODO: redirect them to the same page with an error message telling the user to try again TODO

        for i in range(int(quantity)):
            newCode = generateCode()
            while (Voucher.objects.filter(code=newCode).exists()):
                newCode = generateCode()

            voucher = Voucher(code=newCode, credits=int(points))
            voucher.save()
            generatedVouchers.append(voucher)
    context = {'generatedVouchers': generatedVouchers}
    return render(request,'volunteers/viewGeneratedCodes.html',context)

@user_passes_test(lambda user: user.is_staff)
def viewGeneratedCodes(request):
    generatedVouchers = request.generatedVouchers
    context = {'generatedVouchers': generatedVouchers}
    return render(request,'volunteers/viewGeneratedCodes.html',context)

def exportCodes(request):
    generatedVouchers = Voucher.objects.all()
    now = datetime.now().strftime('%d-%b-%Y-%H-%M-%S')

    if len(generatedVouchers) == 0:
        print "THERE ARE NO VOUCHERS TO EXPORT?!?"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voucherCodes-'+now+'.csv"'

    writer = csv.writer(response)
    writer.writerow(['Codes', 'Credits'])

    for voucher in generatedVouchers:
        writer.writerow([str(voucher.code), str(voucher.credits)])

    return response