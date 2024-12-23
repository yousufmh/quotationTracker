from django import forms
from django.forms import ModelForm, modelformset_factory, DecimalField
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CurrentQuotation, AttachemntsDetails, MultiRole, User, ProducerType

"""
    This The Main Model Form for this app. And it is used in new_qouation and slaes_qoutaion and underwriter_qoutation.

    For Reference regarding ModelForm in Django Please visit below websites: 
    https://docs.djangoproject.com/en/3.0/topics/forms/modelforms/ 

    If you want to use A normal Form in Django, visit below website: 
    https://docs.djangoproject.com/en/3.0/topics/forms/
"""


class QuotationInfoForm(ModelForm):
    """
        For the below Fields, We want to restrict the input to be between 0-100 Because These fields represent percentage values
        Make sure to import it from django.core.validators

        Since our Form should be connected to Current Qoutation Model we need to add it to class Meta
        Also we want Exclude some fields that will never be entered Manually by the user

        You can have more information regarding Validator from the Below Websites:
        https://docs.djangoproject.com/en/3.0/ref/forms/validation/
        https://docs.djangoproject.com/en/3.0/ref/validators/
        https://stackoverflow.com/questions/849142/how-to-limit-the-maximum-value-of-a-numeric-field-in-a-django-model

    """

    Commission = DecimalField(validators=[MinValueValidator(0),
                                          MaxValueValidator(15)], )
    Loading = DecimalField(validators=[MinValueValidator(0),
                                       MaxValueValidator(100)])
    Loading_Discount = DecimalField(validators=[MinValueValidator(0),
                                                MaxValueValidator(100)])
    Claim_Discount = DecimalField(validators=[MinValueValidator(0),
                                              MaxValueValidator(100)])
    Credibility_Factor = DecimalField(validators=[MinValueValidator(0),
                                                  MaxValueValidator(100)])
    error_css_class = "error"

    """

    """

    class Meta:
        model = CurrentQuotation
        exclude = ['Quotation_Date', 'Name_of_Salesman', 'Type_of_Producer', 'Inception_Date',
                   'Sub_Policy_Type', 'Quot_No', 'Max_Rev_No', 'Branch', 'broker', 'pos', 'pos_location', 'Policy_Type',
                   'CR_No', 'Client_Name', 'Client_Contact_Person', 'Client_Contact_Email', 'Client_Contact_Phone',
                   'Company_size', 'Name_of_Policy_Admin', 'last_modified_date',
                   'Quote_to_Client_Date', 'Date_of_receipt_of_complete_documents', 'policy_no', 'TAT', 'Rev_TAT']

    def clean(self):
        super(QuotationInfoForm, self).clean()

        status = self.cleaned_data.get("Quotation_Status")
        fields = [
            'Commission','Loading','Loading_Discount','Claim_Discount','Credibility_Factor','Estimated_Premium'
            ,'Sum_Insured','Risk_Premium','Average_Risk_Rate_per_member','Book_rate','Experience_rate'
        ]
        if status.id == 3:
            # self._errors['CR_No'] = self.error_class(['CR Number Already Exists'])
            for field in fields:
                msg = self.cleaned_data.get(field)
                print(msg)
                if msg is None:
                    self._errors[field] = self.error_class(['This Field is required'])
            # self.fields['Commission'].required = True
            # self.fields['Loading'].required = True
            # self.fields['Loading_Discount'].required = True
            # self.fields['Claim_Discount'].required = True
            # self.fields['Credibility_Factor'].required = True

        return self.cleaned_data
#if msg and not msg.isspace():


"""
        Since our Form should be connected to Current Qoutation Model we need to add it to class Meta
        Also we want to include some fields that will only be entered Manually by the user

        You can have more information regarding Validator from the Below Websites:
        https://www.geeksforgeeks.org/python-form-validation-using-django/
        https://docs.djangoproject.com/en/3.0/ref/forms/validation/
        https://docs.djangoproject.com/en/3.0/ref/validators/
        https://stackoverflow.com/questions/849142/how-to-limit-the-maximum-value-of-a-numeric-field-in-a-django-model

"""


class SalesQoutationForm(ModelForm):
    Commission = DecimalField(validators=[MinValueValidator(0),
                                          MaxValueValidator(15)], )
    Name_of_Salesman = forms.ModelChoiceField(widget=forms.HiddenInput(),queryset=User.objects.all())
    Type_of_Producer = forms.ModelChoiceField(widget=forms.HiddenInput(),queryset=ProducerType.objects.all())


    class Meta:
        model = CurrentQuotation
        fields = ['Sub_Policy_Type', 'Quotation_Status', 'Name_of_Salesman', 'Type_of_Producer', 'Inception_Date', 'CR_No', 'Client_Name',
                  'Client_Contact_Person',
                  'broker', 'pos', 'pos_location',
                  'Client_Contact_Email',
                  'Client_Contact_Phone', 'Company_size', 'Current_Insured', 'Prior_Year_Insured',
                  'Prior_Two_Year_Insured',
                  'No_of_Lives_or_vehicle',
                  'Client_Target', 'Comments_Remarks', 'Commission']

    def clean(self):
        super(SalesQoutationForm, self).clean()
        Commission = self.cleaned_data.get('Commission')
        user = self.cleaned_data.get('Name_of_Salesman')
        producer_type = self.cleaned_data.get('Type_of_Producer')

        if (producer_type.id == 1 or producer_type.id == 4) and Commission > 5:
            self._errors['Commission'] = self.error_class(['For Sales/POS-telesales Commission should not be more than 5%'])

        if (producer_type.id == 2) and Commission > 10:
            self._errors['Commission'] = self.error_class(
                ['For Broker Commission should not be more than 10%'])

        if (producer_type.id == 3) and Commission > 0:
            self._errors['Commission'] = self.error_class(
                ['For Direct Commission should not be more than 0%'])

        return self.cleaned_data


class MultiRoleForm(forms.Form):
    role_choosen = forms.ModelChoiceField(queryset=MultiRole.objects.all())


class UnderWriterListForm(forms.Form):
    Underwriter = forms.ModelChoiceField(queryset=User.objects.all())


"""
    This Model Form is not being used right now maybe will be used later one Because we need a formset not and regular form
"""


class AttachmentForm(ModelForm):
    class Meta:
        model = AttachemntsDetails
        fields = ['attachment_path']


"""
    Here We are creating Formset for the Attachemnts Model and since we have max of 8 attachemnts we specify the extra to be 8 and we also exclude the Qout_No.
    In here we are using the modelformset_factory helper function to create Formset. 

    You can have more information regarding Model Formset from the Below Websites: 
    https://docs.djangoproject.com/en/3.0/topics/forms/modelforms/#modelform-factory-function
    https://docs.djangoproject.com/en/3.0/topics/forms/modelforms/#model-formsets
    https://docs.djangoproject.com/en/3.0/topics/forms/formsets/

"""
AttachmentFormset = modelformset_factory(AttachemntsDetails, exclude=('Quot_No',), max_num=8, extra=8)

"""
    This Form is used only to gather the Qoutation status Hence we used the fields attribute to spicify which fields will be used.  
"""


class IssueQuotationForm(ModelForm):
    class Meta:
        model = CurrentQuotation
        fields = ['Quotation_Status', 'policy_no', 'Final_Premium', 'No_of_Member']
