from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, CurrentQuotation, HistoryQuotation, PolicyType, QuotationStatus, SubPolicyType, AttachmentM, \
    AttachemntsDetails, MultiRole
from .forms import QuotationInfoForm, AttachmentForm, AttachmentFormset, IssueQuotationForm, SalesQoutationForm, \
    MultiRoleForm, UnderWriterListForm
from django.db.models import Q
import ldap
import datetime
import os
from qoutationTracker.send_report import send_html_table_inside
import mimetypes
import magic
from django.conf import settings

"""

	This is the Login and first Page Viewed by the User. 
	It checked if the user already logged in the log user out 
	Render the login.html

"""


def login(request, context={}):
    if 'username' in request.session:
        del request.session['username']
    if 'multi_role' in request.session:
        del request.session['multi_role']

    return render(request, 'tracker/login.html', context)


# ---------------------------- End login ----------------------------------- #

"""

	This is the Validation Function coming from the login.html. 
	In this function it captured the POSTED username and password using the Basic request.POST 
	It checks for validation (if username or password empty) if username is registered in the System and the status is A=Active
	if no it render the login page with error message. 
	If yes it moves to Authentication with LDAP server manually. 
	IF not Authentcated/server error it render the login page with error message "Username or password incorrect"
	If yes It redirect to Another Function " inbox"
	Then Saving the username in the session. 
"""


def validate(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return login(request, {'message': 'Username or Password is Empty'})
    username = username.lower()
    username = username.strip()
    users = User.objects.filter(username=username, status='A')

    if users.exists() is not True:
        return render(request, 'tracker/login.html', {'message': 'You Are Not Authorized to enter This Page'})

    user = users[0]

    request.session['username'] = user.username
    if MultiRole.objects.filter(user=user).exists():
        return redirect(super_inbox)
    else:
        return redirect(inbox)


# ---------------------------- End validate ----------------------------------- #

"""

	This is the Inbox Function coming from the validate function. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	Based on the location of the user and the role and the username it retrive the Current Quotation and pass them to inbox table in templet.

	There are three parameters passed to the templet: 
		list of the quotations (quotations) 
		the user model (user)
		list of policy types  (policytypes)

	It then renders inbox.html

	In here er have used the Queryset API to retrive data from the Database. 
	Reference below website: 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q


"""


def inbox(request, context={}):
    if 'username' in request.session:
        # if request.session.has_key('username'):
        username = request.session['username']
        user = User.objects.filter(username=username)[0]

        location = user.location.location
        department = user.department
        policyTypes = PolicyType.objects.filter(status="A")

        locked_quotation = CurrentQuotation.objects.filter(locked=True)
        today = datetime.datetime.today()
        today = today.replace(tzinfo=None)
        for qout in locked_quotation:
            if qout.locked_by == user:
                qout.locked = False
                qout.locked_by = None
                qout.save()
            locked_date = qout.locked_date
            locked_date = locked_date.replace(tzinfo=None)
            time_locked = today - locked_date
            time_inminutes = time_locked.total_seconds() / 60
            if time_inminutes > 60.00:
                qout.locked = False
                qout.locked_by = None
                qout.locked_date = None
                qout.save()

        if user.role.id == 1:
            quotations = CurrentQuotation.objects.filter(Name_of_Salesman=user).exclude(
                Q(Quotation_Status=2) | Q(Quotation_Status=3) | Q(Quotation_Status=9)).order_by('-Quotation_Date')
            pending_quotations = CurrentQuotation.objects.filter(
                Q(Quotation_Status=2) | Q(Quotation_Status=3) | Q(Quotation_Status=9)).filter(Branch=location).filter(
                Q(Name_of_Salesman=user) | Q(Name_of_Salesman=None)).order_by('Quotation_Date')
        elif user.role.id == 2:

            # quotations = CurrentQuotation.objects.filter(Name_of_Underwriter=user).exclude(
            #     Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(
            #         Quotation_Status=11)).order_by('-Quotation_Date')
            quotations = CurrentQuotation.objects.filter(Policy_Type=department).order_by('-Quotation_Date')

            if department.id == 4 or department.id == 5 or department.id == 8:
                pending_quotations = CurrentQuotation.objects.filter(
                    Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(Quotation_Status=11)) \
                    .filter(Branch=location) \
                    .filter(Q(Policy_Type=4) | Q(Policy_Type=5) | Q(Policy_Type=8)) \
                    .filter(Q(Name_of_Underwriter=user) | Q(Name_of_Underwriter=None)).order_by('Quotation_Date')
            else:
                pending_quotations = CurrentQuotation.objects.filter(
                    Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(Quotation_Status=11)) \
                    .filter(Policy_Type=department) \
                    .filter(Q(Name_of_Underwriter=user) | Q(Name_of_Underwriter=None)).order_by('Quotation_Date')

        else:
            quotations = CurrentQuotation.objects.filter(Policy_Type=department).exclude(
                Q(Quotation_Status=7) | Q(Quotation_Status=11)).order_by('-Quotation_Date')
            pending_quotations = CurrentQuotation.objects.filter(Q(Quotation_Status=7) | Q(Quotation_Status=11)).filter(
                Policy_Type=department).filter(
                Q(Name_of_Policy_Admin=user) | Q(Name_of_Policy_Admin=None)).order_by('Quotation_Date')
        assign_form = ''
        if user.authority:
            if request.method == 'POST':
                assign_form = UnderWriterListForm(request.POST)
                if assign_form.is_valid():
                    Name_Of_Underwriter = assign_form.cleaned_data.get('Underwriter')
                    id_of_quot = request.POST['quot_id']
                    assigned_quot = CurrentQuotation.objects.filter(pk=id_of_quot)[0]
                    assigned_quot.Name_of_Underwriter = Name_Of_Underwriter
                    assigned_quot.save()
                    send_email(assigned_quot, "UTU", user.username)
                    print(user.name)
                    print(Name_Of_Underwriter)
                    print(id_of_quot)
                    return redirect(inbox)
            else:
                assign_form = UnderWriterListForm()
            underwriters = User.objects.filter(Q(role=2)).filter(department=user.department).filter(status='A')
            assign_form.fields["Underwriter"].queryset = underwriters

        context.update(quotations=quotations)
        context.update(pending_quotations=pending_quotations)
        context.update(user=user)
        context.update(policytypes=policyTypes)
        context.update(underwriter=assign_form)
        context.update(roles="")
        context.update(has_roles=False)
        return render(request, 'tracker/inbox.html', context)
    else:
        return redirect(login)


# ---------------------------- End inbox ----------------------------------- #


"""

	This is the Inbox Function coming from the validate function. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	Based on the location of the user and the role and the username it retrive the Current Quotation and pass them to inbox table in templet.

	There are three parameters passed to the templet: 
		list of the quotations (quotations) 
		the user model (user)
		list of policy types  (policytypes)

	It then renders inbox.html

	In here er have used the Queryset API to retrive data from the Database. 
	Reference below website: 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q


"""


def super_inbox(request, context={}):
    if 'username' in request.session:
        # if request.session.has_key('username'):
        username = request.session['username']
        user = User.objects.filter(username=username)[0]
        user_current_role = user
        multi_roles = MultiRole.objects.filter(user=user)
        department = user.department
        if request.method == 'POST':
            roles = MultiRoleForm(request.POST)

            if roles.is_valid():
                user_current_role = roles.cleaned_data.get('role_choosen')
                request.session["multi_role"] = user_current_role.id
                print(f'multi role id :{request.session["multi_role"]}')
                # user = user_current_role.user
                department = user.department

        else:
            roles = MultiRoleForm()

        location = user_current_role.location.location

        policyTypes = PolicyType.objects.filter(status="A")

        locked_quotation = CurrentQuotation.objects.filter(locked=True)
        today = datetime.datetime.today()
        today = today.replace(tzinfo=None)
        for qout in locked_quotation:
            if qout.locked_by == user:
                qout.locked = False
                qout.locked_by = None
                qout.save()
            locked_date = qout.locked_date
            locked_date = locked_date.replace(tzinfo=None)
            time_locked = today - locked_date
            time_inminutes = time_locked.total_seconds() / 60
            if time_inminutes > 60.00:
                qout.locked = False
                qout.locked_by = None
                qout.locked_date = None
                qout.save()

        if user_current_role.role.id == 1:
            quotations = CurrentQuotation.objects.filter(Name_of_Salesman=user).exclude(
                Q(Quotation_Status=2) | Q(Quotation_Status=3) | Q(Quotation_Status=9)).order_by('-Quotation_Date')
            pending_quotations = CurrentQuotation.objects.filter(
                Q(Quotation_Status=2) | Q(Quotation_Status=3) | Q(Quotation_Status=9)).filter(Branch=location).filter(
                Q(Name_of_Salesman=user) | Q(Name_of_Salesman=None)).order_by('Quotation_Date')
        elif user_current_role.role.id == 2:

            # quotations = CurrentQuotation.objects.filter(Name_of_Underwriter=user).exclude(
            #     Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(
            #         Quotation_Status=11)).order_by('-Quotation_Date')
            quotations = CurrentQuotation.objects.filter(Policy_Type=department).order_by('-Quotation_Date')

            if department.id == 4 or department.id == 5 or department.id == 8:
                pending_quotations = CurrentQuotation.objects.filter(
                    Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(Quotation_Status=11)) \
                    .filter(Branch=location) \
                    .filter(Q(Policy_Type=4) | Q(Policy_Type=5) | Q(Policy_Type=8)) \
                    .filter(Q(Name_of_Underwriter=user) | Q(Name_of_Underwriter=None)).order_by('Quotation_Date')
            else:
                pending_quotations = CurrentQuotation.objects.filter(
                    Q(Quotation_Status=1) | Q(Quotation_Status=4) | Q(Quotation_Status=5) | Q(Quotation_Status=11)) \
                    .filter(Policy_Type=department) \
                    .filter(Q(Name_of_Underwriter=user) | Q(Name_of_Underwriter=None)).order_by('Quotation_Date')

        else:
            quotations = CurrentQuotation.objects.filter(Policy_Type=department).exclude(
                Q(Quotation_Status=7) | Q(Quotation_Status=11)).order_by('-Quotation_Date')
            pending_quotations = CurrentQuotation.objects.filter(Q(Quotation_Status=7) | Q(Quotation_Status=11)).filter(
                Policy_Type=department).filter(
                Q(Name_of_Policy_Admin=user) | Q(Name_of_Policy_Admin=None)).order_by('Quotation_Date')

        assign_form = ''
        if user.authority:
            if request.method == 'POST':
                assign_form = UnderWriterListForm(request.POST)
                if assign_form.is_valid():
                    Name_Of_Underwriter = assign_form.cleaned_data.get('Underwriter')
                    id_of_quot = request.POST['quot_id']
                    assigned_quot = CurrentQuotation.objects.filter(pk=id_of_quot)[0]
                    assigned_quot.Name_of_Underwriter = Name_Of_Underwriter
                    assigned_quot.save()
                    send_email(assigned_quot, "UTU",user.username)
                    print(user.name)
                    print(Name_Of_Underwriter)
                    print(id_of_quot)
                    return redirect(super_inbox)
            else:
                assign_form = UnderWriterListForm()
            underwriters = User.objects.filter(Q(role=2)).filter(department=user.department).filter(status='A')
            assign_form.fields["Underwriter"].queryset = underwriters

        roles.fields['role_choosen'].queryset = multi_roles

        context.update(quotations=quotations)
        context.update(pending_quotations=pending_quotations)
        context.update(user=user_current_role)
        context.update(policytypes=policyTypes)
        context.update(underwriter=assign_form)
        context.update(roles=roles)
        context.update(has_roles=True)
        return render(request, 'tracker/inbox.html', context)
    else:
        return redirect(login)


# ---------------------------- End super_inbox ----------------------------------- #


"""

	This is the new_quotation Function coming from the inbox.html templet after the salesperson choose to create new quotation. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	It retrive sevaral data from Master tables Such as: 
		Policy Types using the passed policy type from get request. 
		Quotation status (Submitted Only) Since this is the only status can be entered in this step
		AttachmentsM 
		SubPolicy Type related to the selected Policy Type

	Following the correct way to treat Django ModelForm And ModelFormset to fill out the Models. 
	The Quotation Format will be combnation of {policy_type.short_description}/{user.location.short_location}/{year}
	 and if the quoation was submitted the quotation ID will be added at the end.

	There are three parameters passed to the templet: 
		context.update(user = user)
		context.update(policy_type = policy_type)
		context.update(status = 'new')
		context.update(form = quotation_info)
		context.update(q_date = "")
		context.update(attachemnts=attachemnt)
		context.update(attachmentsform = attachments)
		context.update(history = {})

	   if the request type is Get it renders this page salesquotation.html
	   if the request type is post but the forms is not vaild it will render the salesquotation.html with the errors
	   if the request type is POST and the Form Validate correctly the CurrentQoutation model attachemntsDeteils Models will be created and then redirct to submitted.html with Quotaiont No

	In here er have used the Queryset API to retrive data from the Database. 
	Reference below website: 
	Visit the links in the form.py for more information regarding Forms. 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q


"""


def new_quotation(request, policytype):
    if 'username' in request.session:
        context = {}
        username = request.session['username']
        user = User.objects.filter(username=username)[0]
        user_current_role = user
        has_roles = False
        if 'multi_role' in request.session:
            multi_role_id = request.session['multi_role']
            user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
            has_roles = True
        # print(f'multi role id :{request.session["multi_role"]} and Current Role: {user_current_role}')

        # user = user_current_role.user

        policy_type = PolicyType.objects.filter(id=policytype)[0]
        status = QuotationStatus.objects.filter(id=1)[0]
        attachemntsName = AttachmentM.objects.all()
        year = datetime.datetime.today().year
        if has_roles:
            qout_no = f'{policy_type.short_description}/{user_current_role.location.short_location}/{year}'
            type_of_producer = user_current_role.Type_of_Producer
            user_location = user_current_role.location.location
        else:
            qout_no = f'{policy_type.short_description}/{user.location.short_location}/{year}'
            type_of_producer = user.Type_of_Producer
            user_location = user.location.location

        if request.method == 'POST':

            quotation_info = SalesQoutationForm(request.POST, initial={'Name_of_Salesman': user,
                                                                       'Type_of_Producer': type_of_producer})
            attachments = AttachmentFormset(request.POST, request.FILES, prefix='attachment')

            quotation_info.fields['Quotation_Status'].required = False
            quotation_info.fields['Commission'].required = True
            quotation_info.fields['Name_of_Salesman'].required = False
            quotation_info.fields['Type_of_Producer'].required = False

            if policy_type.id == 1 or policy_type.id == 2:
                quotation_info.fields['No_of_Lives_or_vehicle'].required = True

            if quotation_info.is_valid() and attachments.is_valid():
                qoutation = quotation_info.save(commit=False)

                qoutation.Quot_No = qout_no
                qoutation.Name_of_Salesman = user
                qoutation.Max_Rev_No = '0'
                qoutation.Policy_Type = policy_type
                qoutation.Quotation_Status = status
                qoutation.Branch = user_location
                qoutation.Type_of_Producer = type_of_producer
                qoutation.last_modified_date = datetime.datetime.today()

                qoutation.save()
                count = 0
                for form in attachments:
                    attachment = form.save(commit=False)

                    attachment.Quot_No = qoutation
                    attachment.attachment = attachemntsName[count]
                    attachment.save()
                    count = count + 1

                create_history(qoutation, user)
                send_email(qoutation, "Underwriter")
                qout_no = f'{qoutation.Quot_No}/{qoutation.id}'
                return render(request, 'tracker/submitted.html', {
                    'message': f"The Qoutation has been Submitted Perfectly and the qoutation Number is {qout_no}",
                    'has_roles': has_roles})
        else:
            quotation_info = SalesQoutationForm(
                initial={'Name_of_Salesman': user, 'Type_of_Producer': type_of_producer})
            attachments = AttachmentFormset(queryset=AttachemntsDetails.objects.none(), prefix='attachment')

        quotation_info.fields['Commission'].required = True
        combined_attach = zip(attachemntsName, attachments.forms)
        quotation_info.fields['Sub_Policy_Type'].queryset = SubPolicyType.objects.filter(policyType=policy_type)

        context.update(user=user)
        context.update(policy_type=policy_type)
        context.update(status='new')
        context.update(form=quotation_info)
        context.update(q_date="")
        context.update(user_current_role=user_current_role)
        context.update(has_roles=has_roles)
        context.update(attachemnts=combined_attach)
        context.update(attachmentsform=attachments)
        context.update(history={})
        return render(request, 'tracker/salesquotation.html', context)
    else:
        return redirect(login)


# ---------------------------- End new_quotation ----------------------------------- #


submitted_status = QuotationStatus.objects.filter(pk=1)
incomp_status = QuotationStatus.objects.filter(pk=2)
processed_status = QuotationStatus.objects.filter(pk=3)
accept_status = QuotationStatus.objects.filter(pk=4)
revised_status = QuotationStatus.objects.filter(pk=5)
rejectedUW_status = QuotationStatus.objects.filter(pk=9)
approved_status = QuotationStatus.objects.filter(pk=7)
underprocess_status = QuotationStatus.objects.filter(pk=11)

"""
	This is the sales_qoutation Function coming from the inbox.html templet after the salesperson click on Exisiting quotation from the inbox table. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	It retrive sevaral data from Master tables Such as: 
		Quotation status related to the current status in the chosen quotation. 
		AttachmentsM 
		SubPolicy Type related to the selected Policy Type

	Using the id passed to the function parameter, we retrive the CurrentQuotation from database
	Also we retrive the attachments details and history quotaion using the qout_no. 
	initializing the forms with the correct instance and quesryset. 
	Note: for attachemnts formset you need to pass the id of the attachemnts that you need to change to the formset. Check "else" clause for "if request.method == 'POST':" 
	Following the correct way to treat Django ModelForm And ModelFormset to fill out the Models. 

	There are parameters passed to the templet: 
		context.update(user = user)
		context.update(form = quotation_info)
		context.update(q_date = qout.Quotation_Date)
		context.update(policy_type=qout.Policy_Type)
		context.update(qout = qout)
		context.update(attachemnts = attachemnt)
		context.update(attachmentsform = attachments)
		context.update(status='')
		context.update(history=history)

	   if the request type is Get it renders this page salesquotation.html
	   if the request type is post but the forms is not vaild it will render the salesquotation.html with the errors
	   if the request type is POST and the Form Validate correctly 
			if the posted qoutationStatus is revised or the revision number >0 then the revision number will increase and HistoryQuotation object will be created. 
			the CurrentQoutation model attachemntsDeteils Models will be updated.
			then redirct to submitted.html with Quotaiont No

	In here er have used the Queryset API to retrive data from the Database. 

	Reference below website: 
	Visit the links in the form.py for more information regarding Forms. 
	https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q


"""


def sales_qoutation(request, id):
    if request.session.has_key('username') is not True:
        return redirect(login)
    context = {}
    username = request.session['username']
    user = User.objects.filter(username=username)[0]
    attachemntsName = AttachmentM.objects.all()
    qout = CurrentQuotation.objects.get(pk=id)
    Type_of_Producer = qout.Type_of_Producer
    Name_of_Salesman = qout.Name_of_Salesman

    has_roles = False
    if 'multi_role' in request.session:
        multi_role_id = request.session['multi_role']
        user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
        has_roles = True
    # print(f'multi role id :{request.session["multi_role"]} and Current Role: {user_current_role}')

    attachemnt = AttachemntsDetails.objects.filter(Quot_No=qout)
    if request.method == 'POST':
        quotation_info = SalesQoutationForm(request.POST, instance=qout)
        # quotation_info = SalesQoutationForm(request.POST,  initial={'Type_of_Producer': Type_of_Producer}, instance=qout)
        attachments = AttachmentFormset(request.POST, request.FILES, initial=[{'id': x.id} for x in reversed(attachemnt)],
                                        queryset=AttachemntsDetails.objects.filter(Quot_No=qout), prefix='attachment')
        quotation_info.fields['Commission'].required = True
        quotation_info.fields['Name_of_Salesman'].required = False
        quotation_info.fields['Type_of_Producer'].required = False
        quotation_info.fields["Type_of_Producer"].initial = Type_of_Producer
        print(f' type of prudcer filed {quotation_info.fields["Type_of_Producer"].initial}')
        if quotation_info.is_valid() and attachments.is_valid():
            qoutation = quotation_info.save(commit=False)

            if qoutation.Quotation_Status.id == 5:
                qoutation.Max_Rev_No = qoutation.Max_Rev_No + 1
            create_history(qout, user)
            qoutation.last_modified_date = datetime.datetime.today()
            qoutation.save()

            count = 0
            for attach in attachments:
                obj = attach.save(commit=False)
                if obj.attachment_path:
                    attachemnt[count].attachment_path = obj.attachment_path
                    attachemnt[count].save()
                    print(attachemnt[count].attachment)

                count = count + 1

            qout_no = f'{qoutation.Quot_No}/{qoutation.id}'
            send_email(qoutation, "Underwriter")
            return render(request, 'tracker/submitted.html', {
                'message': f"The Qoutation has been Submitted Perfectly and the qoutation Number is {qout_no}",
                'has_roles': has_roles})

    else:
        quotation_info = SalesQoutationForm(instance=qout)
        # quotation_info = SalesQoutationForm(initial={'Type_of_Producer': Type_of_Producer, 'Name_of_Salesman': Name_of_Salesman}, instance=qout)
        attachments = AttachmentFormset(initial=[{'id': x.id} for x in reversed(attachemnt)],
                                        queryset=AttachemntsDetails.objects.filter(Quot_No=qout), prefix='attachment')

    history = HistoryQuotation.objects.filter(Quot_No=qout)
    cr_exists_message = ''

    if len(CurrentQuotation.objects.filter(CR_No=qout.CR_No)) > 1:
        cr_exists_message = 'The CR Number already exist'

    policy_type = qout.Policy_Type
    status = QuotationStatus.objects.filter(role=user.role)

    if qout.Quotation_Status == incomp_status[0]:
        quotation_info.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(id=1)
    elif qout.Quotation_Status == processed_status[0] or qout.Quotation_Status == rejectedUW_status[0]:
        quotation_info.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(pk__in=[4, 5, 6, 10])

    quotation_info.fields['Sub_Policy_Type'].queryset = SubPolicyType.objects.filter(policyType=policy_type)
    quotation_info.fields['Commission'].required = True
    quotation_info.fields['Name_of_Salesman'].required = False
    quotation_info.fields['Type_of_Producer'].required = False
    quotation_info.fields["Type_of_Producer"].initial = Type_of_Producer

    quotation_info.initial['Comments_Remarks'] = ''
    combined_attach = zip(attachemntsName, attachments.forms)

    context.update(user=user)
    context.update(form=quotation_info)
    context.update(q_date=qout.Quotation_Date)
    context.update(policy_type=qout.Policy_Type)
    context.update(qout=qout)
    context.update(cr_exists=cr_exists_message)
    context.update(attachemnts=combined_attach)
    context.update(attachmentsform=attachments)
    context.update(has_roles=has_roles)
    context.update(status='')
    context.update(history=history)
    return render(request, 'tracker/salesquotation.html', context)


# ---------------------------- End sales_quotation ----------------------------------- #

"""

	This is the underwriter_qoutation Function coming from the inbox.html templet after the Underwriter click on Exisiting quotation from the inbox table. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	It retrive data from Master tables Such as: 
		Quotation status related to the current status in the chosen quotation. 

	Using the id passed to the function parameter, we retrive the CurrentQuotation from database
	Also we retrive the attachments details and history quotaion using the qout_no. 
	initializing the form with the correct instance.
	Since the underwriter doesn't upload any files, we don't use any formset in this function.
	from the attachments details we passed the information to templet to be used for download attachments. 
	Following the correct way to treat Django ModelForm And ModelFormset to fill out the Models. 

	There are parameters passed to the templet: 
		context.update(user = user)
		context.update(form = quotation_info)
		context.update(q_date = qout.Quotation_Date)
		context.update(qout = qout)
		context.update(attachemnts = attachemnt)
		context.update(policy_type=qout.Policy_Type)
		context.update(status='')
		context.update(history=history)
		render underwriterquotation.html

	   if the request type is Get it renders this page underwriterquotation.html
	   if the request type is post but the forms is not vaild it will render the underwriterquotation.html with the errors
	   if the request type is POST and the Form Validate correctly 
			if the posted qoutationStatus is the revision number >0 then the revision number will increase and HistoryQuotation object will be created. 
			the CurrentQoutation model will be updated
			then redirct to submitted.html with Quotaiont No

	In here er have used the Queryset API to retrive data from the Database. 

	Reference below website: 
	Visit the links in the form.py for more information regarding Forms. 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q

"""


def underwriter_qoutation(request, id):
    if request.session.has_key('username') is not True:
        return redirect(login)
    context = {}
    username = request.session['username']
    user = User.objects.filter(username=username)[0]

    has_roles = False
    if 'multi_role' in request.session:
        # multi_role_id = request.session['multi_role']
        # user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
        has_roles = True
    # user = user_current_role.user

    qout = CurrentQuotation.objects.get(id=id)
    old_status = qout.Quotation_Status
    print(f' last modified date {qout.last_modified_date}')

    if qout.locked and qout.locked_by != user:
        return render(request, 'tracker/submitted.html',
                      {'message': f"This Quotation is locked by {qout.locked_by} since {qout.locked_date}"})
    # qout.locked = True
    # qout.locked_by = user
    # qout.locked_date = datetime.datetime.today()
    # qout.save()

    attachemnt = AttachemntsDetails.objects.filter(Quot_No=qout)
    if request.method == 'POST':
        quotation_info = QuotationInfoForm(request.POST, instance=qout)

        quotation_info.fields['Commission'].required = False
        quotation_info.fields['Loading'].required = False
        quotation_info.fields['Loading_Discount'].required = False
        quotation_info.fields['Claim_Discount'].required = False
        quotation_info.fields['Credibility_Factor'].required = False
        # quotation_info.fields['Sub_Policy_Type'].required = False
        # quotation_info.fields['Inception_Date'].required = False
        # quotation_info.fields['CR_No'].required = False
        # quotation_info.fields['Client_Name'].required = False
        # quotation_info.fields['Client_Contact_Person'].required = False
        # quotation_info.fields['Client_Contact_Email'].required = False
        # quotation_info.fields['Client_Contact_Phone'].required = False
        # quotation_info.fields['Company_size'].required = False

        if qout.Policy_Type.id != 1 and qout.Policy_Type.id != 2:
            quotation_info.fields['Loading_Discount'].required = False
            quotation_info.fields['Credibility_Factor'].required = False

        if quotation_info.is_valid():
            qoutation = quotation_info.save(commit=False)

            qoutation.Name_of_Underwriter = user

            if qoutation.Documents_Received:
                qoutation.Date_of_receipt_of_complete_documents = datetime.datetime.today()

            # if qoutation.Quotation_Status.id == 3:
            uw_submission_date = datetime.date.today()
            sales_submission_date = qout.last_modified_date
            print(f'sales_submission_date is {sales_submission_date} and last modified date {qout.last_modified_date}')

            tat = tat_days(sales_submission_date, uw_submission_date)
            qoutation.Quote_to_Client_Date = uw_submission_date
            print(f'old Status is {old_status} with id of {old_status.id}')
            if old_status.id == 1:
                qoutation.TAT = tat
                print('coming from Status 1 which is submitted')
            elif old_status.id == 5 or old_status.id == 4:
                qoutation.Rev_TAT = tat
            print(
                f'uw_submission_date is {uw_submission_date} and last modified date {sales_submission_date} tat is {qoutation.TAT} orignal TAT is {tat}')

            create_history(qout, user)
            qoutation.locked = False
            qoutation.locked_by = None
            qoutation.locked_date = None
            if qoutation.Quotation_Status.id is not 11:
                qoutation.last_modified_date = datetime.datetime.today()
            qoutation.save()
            if qoutation.Quotation_Status.id == 7:
                send_email(qoutation, "Policy admin")
            else:
                send_email(qoutation, "Sales Person")
            qout_no = f'{qoutation.Quot_No}/{qoutation.id}'
            return render(request, 'tracker/submitted.html', {
                'message': f"The Qoutation has been Submitted Perfectly and the qoutation Number is {qout_no}",
                'has_roles': has_roles})
    else:
        quotation_info = QuotationInfoForm(instance=qout)

    history = HistoryQuotation.objects.filter(Quot_No=qout)
    cr_exists_message = ''

    if len(CurrentQuotation.objects.filter(CR_No=qout.CR_No)) > 1:
        cr_exists_message = 'The CR Number already exist'
    policy_type = qout.Policy_Type

    status = QuotationStatus.objects.filter(role=user.role)

    if qout.Quotation_Status == submitted_status[0] or qout.Quotation_Status == underprocess_status[0]:
        quotation_info.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(pk__in=[2, 3, 9, 11])
    elif qout.Quotation_Status == revised_status[0]:
        quotation_info.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(pk__in=[3, 9])
    elif qout.Quotation_Status == accept_status[0]:
        quotation_info.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(pk__in=[7, 9])

    quotation_info.fields['Commission'].required = False
    quotation_info.fields['Loading'].required = False
    quotation_info.fields['Loading_Discount'].required = False
    quotation_info.fields['Claim_Discount'].required = False
    quotation_info.fields['Credibility_Factor'].required = False

    # quotation_info.fields['Sub_Policy_Type'].queryset = SubPolicyType.objects.filter(policyType=policy_type)
    quotation_info.initial['Comments_Remarks'] = ''

    context.update(user=user)
    context.update(form=quotation_info)
    context.update(q_date=qout.Quotation_Date)
    context.update(qout=qout)
    context.update(cr_exists=cr_exists_message)
    context.update(attachemnts=attachemnt)
    context.update(policy_type=qout.Policy_Type)
    context.update(has_roles=has_roles)
    context.update(status='')
    context.update(history=history)
    return render(request, 'tracker/underwriterquotation.html', context)


# ---------------------------- End underwriter_quotation ----------------------------------- #

"""
	This is history function coming from either the underwriterquotaion.html or slaesquotaion.html when user click on revision
	This function is only for viewing the information. 

	we will retrive the history quotation using the id passed from the function parameter. 
	Also we retrive the attachment using the qout_no 

	There are parameters passed to the templet: 
		context.update(qout = history_qout)
		context.update(attachment = attachment)

	render viewqoutaion.html 

"""


def history(request, id):
    if request.session.has_key('username') is not True:
        return redirect(login)
    context = {}
    has_roles = False
    if 'multi_role' in request.session:
        # multi_role_id = request.session['multi_role']
        # user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
        has_roles = True
    # user = user_current_role.user
    username = request.session['username']
    user = User.objects.filter(username=username)[0]
    history_qout = HistoryQuotation.objects.filter(id=id)[0]
    qout = history_qout.Quot_No
    attachment = AttachemntsDetails.objects.filter(Quot_No=qout)
    context.update(qout=history_qout)
    context.update(attachment=attachment)
    context.update(has_roles=has_roles)

    if user.role.id == 1:
        return render(request, 'tracker/viewqoutationsales.html', context)
    else:
        return render(request, 'tracker/viewqoutation.html', context)


# ---------------------------- End history ----------------------------------- #


"""
	This is history function coming from either the underwriterquotaion.html or slaesquotaion.html when user click on revision
	This function is only for viewing the information. 

	we will retrive the history quotation using the id passed from the function parameter. 
	Also we retrive the attachment using the qout_no 

	There are parameters passed to the templet: 
		context.update(qout = history_qout)
		context.update(attachment = attachment)

	render viewqoutaion.html 

"""


def view_quotation(request, id):
    if request.session.has_key('username') is not True:
        return redirect(login)
    context = {}
    username = request.session['username']
    user = User.objects.filter(username=username)[0]
    has_roles = False
    if 'multi_role' in request.session:
        # multi_role_id = request.session['multi_role']
        # user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
        has_roles = True
    # user = user_current_role.user
    current_qout = CurrentQuotation.objects.filter(id=id)[0]
    qout = current_qout.id
    attachment = AttachemntsDetails.objects.filter(Quot_No=qout)
    context.update(qout=current_qout)
    context.update(attachment=attachment)
    context.update(has_roles=has_roles)

    if user.role.id == 1:
        return render(request, 'tracker/viewqoutationsales.html', context)
    else:
        return render(request, 'tracker/viewqoutation.html', context)


# ---------------------------- End View ----------------------------------- #


"""

	This is the issue_qoutation Function coming from the inbox.html templet after the Policy Admin click on Existing quotation from the inbox table. 

	first Check if there is a user in the session. 
	If No it return to login page. 
	If yes It retrieve the user from the Database 
	It retrive data from Master tables Such as: 
		Quotation status related to the current status in the chosen quotation. 

	Using the id passed to the function parameter, we retrive the CurrentQuotation from database
	Also we retrive the attachments details and history quotaion using the qout_no. 
	initializing the form with the correct instance.
	Since the policy admin doesn't upload any files, we don't use any formset in this function.
	from the attachments details we passed the information to templet to be used for download attachments. 
	The policy Admin only Change the Qoutation status to issue if he issued the policy in AIMS.

	There are parameters passed to the templet: 
	context.update(form = form)
	context.update(qout = qout)
	context.update(attachment = attachemnt)
		render issueqoutation.html

	   if the request type is Get it renders this page issueqoutation.html
	   if the request type is post but the forms is not vaild it will render the issueqoutation.html with the errors
	   if the request type is POST and the Form Validate correctly 
			the CurrentQoutation model will be updated
			then redirct to submitted.html with Quotaiont No

	In here er have used the Queryset API to retrive data from the Database. 

	Reference below website: 
	Visit the links in the form.py for more information regarding Forms. 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://docs.djangoproject.com/en/3.0/topics/db/queries/#complex-lookups-with-q


"""


def issue_qoutation(request, id):
    if request.session.has_key('username') is not True:
        return redirect(login)
    context = {}
    username = request.session['username']
    user = User.objects.filter(username=username)[0]

    has_roles = False
    if 'multi_role' in request.session:
        # multi_role_id = request.session['multi_role']
        # user_current_role = MultiRole.objects.filter(id=multi_role_id)[0]
        has_roles = True
    # user = user_current_role.user

    qout = CurrentQuotation.objects.get(id=id)
    # qout.locked = True
    # qout.locked_by = user
    # qout.save()

    attachemnt = AttachemntsDetails.objects.filter(Quot_No=qout)

    if request.method == 'POST':
        form = IssueQuotationForm(request.POST, instance=qout)
        if form.is_valid():
            qoutation = form.save(commit=False)
            qoutation.Name_of_Policy_Admin = user

            if qoutation.Quotation_Status.id == 8:
                qoutation.PPPY = qoutation.Final_Premium / qoutation.No_of_Member

            qoutation.locked = False
            qoutation.locked_by = None
            qoutation.last_modified_date = datetime.datetime.today()
            qoutation.save()
            send_email(qoutation, "policy admin")
            qout_no = f'{qoutation.Quot_No}/{qoutation.id}'
            return render(request, 'tracker/submitted.html', {
                'message': f"The Qoutation has been Submitted Perfectly and the qoutation Number is {qout_no}",
                'has_roles': has_roles})
    else:
        form = IssueQuotationForm(instance=qout)

    form.fields['Quotation_Status'].queryset = QuotationStatus.objects.filter(pk__in=[8, 11])
    context.update(form=form)
    context.update(qout=qout)
    context.update(attachment=attachemnt)
    context.update(has_roles=has_roles)

    return render(request, 'tracker/issueqoutation.html', context)


# ---------------------------- End issue_quotation ----------------------------------- #

"""
	This is the function to download the attachments upoloaded by the saleperson. 

	it doesn't render anything it only download the file using the attahcmnet Id passed as parameter. 

	Currently we are allowing all kind of files to be uploaded and downloaded. 

	 Reference below website: 
	Visit the links in the form.py for more information regarding Forms. 
	https://docs.djangoproject.com/en/3.0/ref/models/querysets/ 
	https://medium.com/@ajrbyers/file-mime-types-in-django-ee9531f3035b
	https://stackoverflow.com/questions/47843129/get-absolute-file-path-of-filefield-of-a-model-instance-in-django
	https://stackoverflow.com/questions/36392510/django-download-a-file

"""


def download(request, id):
    attachemnt = AttachemntsDetails.objects.filter(id=id)[0]
    path = attachemnt.attachment_path.path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    mime = magic.from_file(file_path, mime=True)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=mime)
            response['Content-Disposition'] = f'inline; filename= {attachemnt.attachment_path}'
            return response
    raise Http404


# ---------------------------- End download ----------------------------------- #


def unlock_quotation(request, id):
    qout = CurrentQuotation.objects.get(id=id)
    qout.locked = False
    qout.locked_by = None
    qout.save()
    return redirect(inbox)


def tat_days(sales_time, uw_time):
    from_weekday = sales_time.weekday()
    to_weekday = uw_time.weekday()
    if from_weekday > 4:
        from_weekday = 0
    day_diff = to_weekday - from_weekday
    whole_week = ((uw_time - sales_time).days - day_diff) / 7
    workdays_in_whole_weeks = whole_week * 5
    beginning_end_correction = min(day_diff, 5) - (max(to_weekday - 4, 0) % 5)
    working_days = workdays_in_whole_weeks + beginning_end_correction
    tat_in_days = max(0, working_days)
    tat_in_days = round(tat_in_days)
    return tat_in_days


def disablefileds(quotation_info):
    quotation_info.fields['Sub_Policy_Type'].disabled = True
    quotation_info.fields['Inception_Date'].disabled = True
    quotation_info.fields['Type_of_Producer'].disabled = True
    quotation_info.fields['Client_Name'].disabled = True
    quotation_info.fields['Client_Contact_Person'].disabled = True
    quotation_info.fields['Client_Contact_Email'].disabled = True
    quotation_info.fields['Client_Contact_Phone'].disabled = True
    quotation_info.fields['Current_Insured'].disabled = True
    quotation_info.fields['Prior_Year_Insured'].disabled = True
    quotation_info.fields['Prior_Two_Year_Insured'].disabled = True
    quotation_info.fields['No_of_Lives_or_vehicle'].disabled = True
    quotation_info.fields['Current_Insured'].disabled = True


# ---------------------------- End disablefileds ----------------------------------- #

"""
	This only Create a new model of the History Quotation using the passed qoutaion model 
"""


def create_history(qoutation, user):
    history_temp = HistoryQuotation(Quot_No=qoutation, Rev_No=qoutation.Max_Rev_No, Rev_Name=user.name,
                                    Policy_Type=qoutation.Policy_Type,
                                    Sub_Policy_Type=qoutation.Sub_Policy_Type,
                                    Branch=qoutation.Branch,
                                    Quotation_Date=qoutation.Quotation_Date,
                                    Inception_Date=qoutation.Inception_Date,
                                    Name_of_Salesman=qoutation.Name_of_Salesman,
                                    Type_of_Producer=qoutation.Type_of_Producer,
                                    broker=qoutation.broker,
                                    pos=qoutation.pos,
                                    pos_location=qoutation.pos_location,
                                    CR_No=qoutation.CR_No,
                                    Client_Name=qoutation.Client_Name,
                                    Client_Contact_Person=qoutation.Client_Contact_Person,
                                    Client_Contact_Email=qoutation.Client_Contact_Email,
                                    Client_Contact_Phone=qoutation.Client_Contact_Phone,
                                    Current_Insured=qoutation.Current_Insured,
                                    Prior_Year_Insured=qoutation.Prior_Year_Insured,
                                    Prior_Two_Year_Insured=qoutation.Prior_Two_Year_Insured,
                                    No_of_Lives_or_vehicle=qoutation.No_of_Lives_or_vehicle,
                                    Client_Target=qoutation.Client_Target,
                                    Data_completion_date=qoutation.Data_completion_date,
                                    Name_of_Underwriter=qoutation.Name_of_Underwriter,
                                    Documents_Received=qoutation.Documents_Received,
                                    Name_of_pending_documents=qoutation.Name_of_pending_documents,
                                    Date_of_receipt_of_complete_documents=qoutation.Date_of_receipt_of_complete_documents,
                                    Reinsurance_Approval_Request=qoutation.Reinsurance_Approval_Request,
                                    Reinsurance_Request_Date=qoutation.Reinsurance_Request_Date,
                                    Reinsurance_Received_Approval_Date=qoutation.Reinsurance_Received_Approval_Date,
                                    Company_size=qoutation.Company_size,
                                    Commission=qoutation.Commission,
                                    Loading=qoutation.Loading,
                                    Loading_Discount=qoutation.Loading_Discount,
                                    Claim_Discount=qoutation.Claim_Discount,
                                    Credibility_Factor=qoutation.Credibility_Factor,
                                    Estimated_Premium=qoutation.Estimated_Premium,
                                    Final_Premium=qoutation.Final_Premium,
                                    No_of_Member=qoutation.No_of_Member,
                                    PPPY=qoutation.PPPY,
                                    Deductible=qoutation.Deductible,
                                    Aggregate_Limit=qoutation.Aggregate_Limit,
                                    Anyone_Occurrence=qoutation.Anyone_Occurrence,
                                    Sum_Insured=qoutation.Sum_Insured,
                                    Risk_Premium=qoutation.Risk_Premium,
                                    Average_Rate_per_vehicle_member=qoutation.Average_Rate_per_vehicle_member,
                                    Average_Risk_Rate_per_member=qoutation.Average_Risk_Rate_per_member,
                                    Book_rate=qoutation.Book_rate,
                                    Experience_rate=qoutation.Experience_rate,
                                    Average_claims_per_person_per_months=qoutation.Average_claims_per_person_per_months,
                                    Average_claims_per_person_per_year=qoutation.Average_claims_per_person_per_year,
                                    Extrapolated_claims=qoutation.Extrapolated_claims,
                                    Provider_discount=qoutation.Provider_discount,
                                    Trend=qoutation.Trend,
                                    Additional_factor=qoutation.Additional_factor,
                                    Admin_Loading=qoutation.Admin_Loading,
                                    Commission_Claim=qoutation.Commission_Claim
                                    , Total_Loading=qoutation.Total_Loading,
                                    Recommended_Premium=qoutation.Recommended_Premium,
                                    Quote_to_Client_Date=qoutation.Quote_to_Client_Date,
                                    TAT=qoutation.TAT,
                                    Comments_Remarks=qoutation.Comments_Remarks,
                                    Quotation_Status=qoutation.Quotation_Status)
    history_temp.save()


# ---------------------------- End create_history ----------------------------------- #

"""
	This Function Sends an email Notification to underwriter for the submitted Quotation using the passed quotation model 
"""


def send_email(qoutation, to_role, assignee_user=None):
    if to_role == "Underwriter":
        cc = f'{qoutation.Name_of_Salesman.username}@.com'
        if qoutation.Policy_Type.id == 2:
            if qoutation.Name_of_Underwriter is None:
                to = """"""
            else:
                to = f'{qoutation.Name_of_Underwriter.username}'

        elif qoutation.Policy_Type.id == 1:
            if qoutation.Name_of_Underwriter is None:
                to = ''
            else:
                to = f'{qoutation.Name_of_Underwriter.username}'

            cc = cc + ''
        print(f'location id = {qoutation.Name_of_Salesman.location_id}')
        if qoutation.Name_of_Salesman.location_id == 3:

            if qoutation.Type_of_Producer.id == 1 or qoutation.Type_of_Producer.id == 3:
                cc = cc + ''
            elif qoutation.Type_of_Producer.id == 2:
                cc = cc + ''
        if qoutation.Type_of_Producer.id == 4:
            cc = cc + f',{qoutation.pos.username}'



    elif to_role == "Sales Person":
        to = f'{qoutation.Name_of_Salesman.username}'
        cc = f'{qoutation.Name_of_Underwriter.username}'
        if qoutation.Name_of_Salesman.location_id == 3:
            print(f'producer Type : {qoutation.Type_of_Producer}')
            if qoutation.Type_of_Producer.id == 1 or qoutation.Type_of_Producer.id == 3:
                cc = cc + ''
            elif qoutation.Type_of_Producer.id == 2:
                cc = cc + ''
        if qoutation.Policy_Type.id == 1:
            cc = cc + ''
        if qoutation.Type_of_Producer.id == 4:
            cc = cc + f',{qoutation.pos.username}'

    elif to_role == "UTU":
        to = f'{qoutation.Name_of_Underwriter.username}'
        cc = f'{assignee_user}'

    else:
        if qoutation.Policy_Type.id == 2 and qoutation.Name_of_Policy_Admin is None:
            to = ''

        elif qoutation.Policy_Type.id == 1 and qoutation.Name_of_Policy_Admin is None:
            if qoutation.Name_of_Salesman.location_id == 1:
                to = ''
            else:
                to = ''
        else:
            to = f'{qoutation.Name_of_Policy_Admin.username}'
        cc = f'{qoutation.Name_of_Salesman.username}{qoutation.Name_of_Underwriter.username}'
        if qoutation.Name_of_Salesman.location_id == 3:
            if qoutation.Type_of_Producer.id == 1 or qoutation.Type_of_Producer.id == 3:
                cc = cc + ''
            elif qoutation.Type_of_Producer.id == 2:
                cc = cc + ''
        if qoutation.Policy_Type.id == 1:
            cc = cc + ''
        if qoutation.Type_of_Producer.id == 4:
            cc = cc + f',{qoutation.pos.username}'


    bcc = ''
    if qoutation.Policy_Type.id == 2:
        bcc = bcc + ''

    subject = f'NEW SUBMISSION for M/s. {qoutation.Client_Name}'
    style = """
				<html>
				<head>
					<meta http-equiv="content-type" content="text/html; charset=UTF-8">
					<style>

				tr,td,table {
				  font-family: 'gu_font';
				  border: 1px solid #ddd;
				  border-collapse: collapse;
				  font-size: 11pt;
				  margin:3px;
				}


				thead {
					color: white;
					background-color: #b2b2b2;
					font-family: Calibri, sans-serif;
				}
				</style> </head>
			"""
    message = f"""
			   {style}
			 <body>
				Dear Team, <br><br>
				  This is a new submission received requesting a quotation/revised quotation and below summary of the 
				  account : <br><br> 
				  <table>
				   <tr>
					   <th>Quotation Number:  </th>
					   <td> {qoutation.Quot_No}/{qoutation.id} </td>
				   </tr>
				   <tr>
					   <th>Type of Request :  </th>
					   <td>{qoutation.Quotation_Status}</td>
				   </tr>
				   <tr>
					   <th>Name of client:  </th>
					   <td>{qoutation.Client_Name}  </td>
				   </tr>
					<tr>
					   <th>No. of Insured:  </th>
					   <td>{qoutation.No_of_Lives_or_vehicle}  </td>
				   </tr>
					<tr>
					   <th>Producer Channels:  </th>
					   <td> {qoutation.Type_of_Producer} </td>
				   </tr>
					<tr>
					   <th>Name of Sales/Broker:  </th>
					   <td>{qoutation.Name_of_Salesman}  </td>
				   </tr>

				   <tr>
					   <th>Name of Underwriter:  </th>
					   <td>{qoutation.Name_of_Underwriter}  </td>
				   </tr>

				   <tr>
					   <th>Name of Policy Admin:  </th>
					   <td>{qoutation.Name_of_Policy_Admin}  </td>
				   </tr>

					<tr>
					   <th>Commission %:  </th>
					   <td>{qoutation.Commission}  </td>
				   </tr>
				   <tr>
					   <th>Submission Date :  </th>
					   <td>{qoutation.Quotation_Date}  </td>
				   </tr>
				   <tr>
					   <th>Expected Policy Inception date:  </th>
					   <td>{qoutation.Inception_Date}  </td>
				   </tr>
					<tr>
					   <th>Comments And Remark:  </th>
					   <td>{qoutation.Comments_Remarks}  </td>
				   </tr>
				   </table> <br> <br>
					To Access the quotation, Please visit . <br><br> 
				  Best regards, <br>
				  Quotation Tracker System. 
			   </p>
			 </body>
		   </html>
		   """
    print(f'to = {to}, cc = {cc}, bcc = {bcc}')
    # send_html_table_inside(to=to, cc=cc, bcc=bcc, subject=subject, message=message)
