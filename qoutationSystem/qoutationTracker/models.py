from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

"""
    This is the Main Models Files for this App 
    We have 7 Master Models/Tables and 4 Normal Models/Tables. 

    For More information regarding Models Please Visit Below Links: 
    https://docs.djangoproject.com/en/3.0/topics/db/models/#module-django.db.models
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#field-api-reference   

"""

# ---------------------------------------------------------------------------------------#
# ------------------------------- Master Tables --------------------------------------- #


"""
    The UserRole Model is responsible to specify what is the Role of the user (Salesperson, Underwriter, Policy Admin)   
    In the Class Meta we changed the Table Name. 

"""


class UserRole(models.Model):
    class Meta:
        db_table = 'QT_Role_M'

    role = models.CharField(max_length=100)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.role


"""The QuotationStatus Model is responsible to specify what is the Status/(current step) of the Quotation in relation 
to the user role. In the Class Meta we changed the Table Name. 

"""


class QuotationStatus(models.Model):
    class Meta:
        db_table = 'QT_Quotation_Status_M'

    status = models.CharField(max_length=100)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.status


"""The PolicyType Model is responsible to specify what is the policy type of the Quotation with short description to 
be included in the quotation number. In the Class Meta we changed the Table Name. """


class PolicyType(models.Model):
    class Meta:
        db_table = 'QT_Policy_Type_M'

    description = models.CharField(max_length=20)
    short_description = models.CharField(max_length=2)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.description


"""The PolicyType Model is responsible to specify what is the sub policy type of the Quotation in relation to the 
each Policy Type. In the Class Meta we changed the Table Name. """


class SubPolicyType(models.Model):
    class Meta:
        db_table = 'QT_Sub_Policy_Type_M'

    policyType = models.ForeignKey(PolicyType, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.description


"""
    The Producer Type Model is responsible to specify what is the type of quotation producer (Sales, Broker, Direct).    
    In the Class Meta we changed the Table Name. 
"""


class ProducerType(models.Model):
    class Meta:
        db_table = 'QT_Producer_Type_M'

    description = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.description


"""
    The AttachemntM Model is responsible to specify what is the Attachemnt Type.    
    In the Class Meta we changed the Table Name. 
"""


class AttachmentM(models.Model):
    class Meta:
        db_table = 'QT_Attachment_M'

    document_name = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.document_name


"""
    The InsurerM Model is responsible to specify what is the Insurer  Type.    
    In the Class Meta we changed the Table Name. 
"""


class InsurerM(models.Model):
    class Meta:
        db_table = 'QT_Insurer_M'

    name = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.name


"""
    The BrokerList Model is responsible to specify which broker is issuing the quotation.    
    In the Class Meta we changed the Table Name. 
"""


class BrokerList(models.Model):
    class Meta:
        db_table = 'QT_Broker_List_M'

    name = models.CharField(max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.name


"""
    The POSList Model is responsible to specify The list of POS employee with their emails .    
    In the Class Meta we changed the Table Name. 
"""


class POSList(models.Model):
    class Meta:
        db_table = 'QT_POS_List_M'

    name = models.CharField(max_length=100)
    username = models.CharField(blank=True, null=True, max_length=100)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.name


"""
    The Branch Model is responsible to specify what is the branch of the User.    
    In the Class Meta we changed the Table Name. 

"""


class Branch(models.Model):
    class Meta:
        db_table = 'QT_Branch_M'

    location = models.CharField(max_length=100)
    short_location = models.CharField(max_length=2)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.location


"""
    The Branch Model is responsible to specify what is the branch of the User.    
    In the Class Meta we changed the Table Name. 

"""


class POSLocation(models.Model):
    class Meta:
        db_table = 'QT_POS_Location_M'

    location = models.CharField(max_length=100)
    # short_location = models.CharField(max_length=2)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.location


"""
    The UserStatus Model is not being Used right Now.    
    In the Class Meta we changed the Table Name. 
"""


class UserStatus(models.Model):
    class Meta:
        db_table = 'QT_User_Status_M'

    status = models.CharField(max_length=100)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.status


# ------------------------------------------------------------------------------------------------#
# ----------------------- App Tables ----------------------------------------------------------- #


"""
    The User Model is responsible to Hold The information of the user Which is explained Below.

    username: is the Active Directory username and used for authentication with LDAP 
    Name: is the Display Name 
    Role:The role of the user foreign key of the Master table (UserRole) 
    location: the branch of the user foreign key of the master table(Branch) 
    department: The Department the user in, it is foreign key of the master (PolicyType)  
    Only For U/W authority: specify if the user has spacial features such as reports and activate users and so on. 
    Note: this has not been used yet. 
    status: The status of the user if he is Active 'A' if not 'X' 
    In the Class Meta we changed the Table Name. """


class User(models.Model):
    class Meta:
        db_table = 'QT_User_T'

    username = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    location = models.ForeignKey(Branch, on_delete=models.CASCADE)
    department = models.ForeignKey(PolicyType, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name='User_PolicyType')
    Type_of_Producer = models.ForeignKey(ProducerType, blank=True, null=True, on_delete=models.CASCADE)
    authority = models.BooleanField()
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.name


"""
    The MultiRole Model is responsible to Hold The Multi Role information of the user Which is explained Below.

    user: is the foreign key that links to the user table.  
    Role: The role of the user foreign key of the Master table (UserRole) 
    location: the branch of the user foreign key of the master table(Branch) 
    status: The status of the user if he is Active 'A' if not 'X' 
    In the Class Meta we changed the Table Name. 
    """


class MultiRole(models.Model):
    class Meta:
        db_table = 'QT_Multi_Role_T'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, blank=True, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Branch, blank=True, null=True, on_delete=models.CASCADE)
    Type_of_Producer = models.ForeignKey(ProducerType, blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=1)
    create_date = models.DateField(auto_now_add=True)
    create_name = models.CharField(max_length=100)
    update_date = models.DateField(blank=True, auto_now=True)
    update_name = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.user.__str__() + " " + self.location.__str__() + " " + self.role.__str__() + " " + self.Type_of_Producer.__str__()


"""
    The CurrentQuotation Model is responsible to Hold The information of the Current Quotation (Most updated Quotation)

    Note: For The Foregin Key Fields you need to add the related_name if you going to use more then one field with 
    the same Model. 

    In the Class Meta we changed the Table Name. 
"""


class CurrentQuotation(models.Model):
    class Meta:
        db_table = 'QT_Current_Quotation_T'

    Quot_No = models.CharField(max_length=200)
    Max_Rev_No = models.PositiveIntegerField(blank=True)
    Policy_Type = models.ForeignKey(PolicyType, on_delete=models.CASCADE)
    Sub_Policy_Type = models.ForeignKey(SubPolicyType, on_delete=models.CASCADE)
    Branch = models.CharField(max_length=100)
    Quotation_Date = models.DateField(auto_now_add=True)  # auto_now_add = True
    Inception_Date = models.DateField()
    Name_of_Salesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_salesperson')
    Type_of_Producer = models.ForeignKey(ProducerType, blank=True, null=True, on_delete=models.CASCADE)

    broker = models.ForeignKey(BrokerList, blank=True, null=True, on_delete=models.CASCADE)
    pos = models.ForeignKey(POSList, blank=True, null=True, on_delete=models.CASCADE)
    pos_location = models.ForeignKey(POSLocation, blank=True, null=True, on_delete=models.CASCADE)

    CR_No = models.CharField(max_length=100)
    Client_Name = models.CharField(max_length=100)
    Client_Contact_Person = models.CharField(max_length=100)
    Client_Contact_Email = models.EmailField(max_length=100)
    Client_Contact_Phone = models.CharField(max_length=16)
    Company_size = models.PositiveIntegerField()
    Current_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                        related_name='current_Current_Insured')
    Prior_Year_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                           related_name='current_Prior_Year')
    Prior_Two_Year_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                               related_name='current_Prior_Two_Year')
    No_of_Lives_or_vehicle = models.PositiveIntegerField(blank=True, null=True)
    Client_Target = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Data_completion_date = models.DateField(blank=True, null=True)
    Name_of_Underwriter = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                            related_name='current_underwiter')
    Documents_Received = models.BooleanField(blank=True, null=True)
    Name_of_pending_documents = models.CharField(blank=True, max_length=100)
    Date_of_receipt_of_complete_documents = models.DateField(blank=True, null=True)
    Reinsurance_Approval_Request = models.BooleanField(blank=True, null=True)
    Reinsurance_Request_Date = models.DateField(blank=True, null=True)
    Reinsurance_Received_Approval_Date = models.DateField(blank=True, null=True)
    Commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Loading = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Loading_Discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Claim_Discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Credibility_Factor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Estimated_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Final_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    No_of_Member = models.PositiveIntegerField(blank=True, null=True)
    PPPY = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Sum_Insured = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Risk_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Average_Rate_per_vehicle_member = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Average_Risk_Rate_per_member = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Book_rate = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Experience_rate = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Deductible = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Aggregate_Limit = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Anyone_Occurrence = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)

    Average_claims_per_person_per_months = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Average_claims_per_person_per_year = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Extrapolated_claims = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Provider_discount = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Trend = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Additional_factor = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Admin_Loading = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Commission_Claim = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Total_Loading = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Recommended_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)

    Quote_to_Client_Date = models.DateField(blank=True, null=True)
    TAT = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Rev_TAT = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Comments_Remarks = models.TextField(max_length=500, blank=True)
    Quotation_Status = models.ForeignKey(QuotationStatus, on_delete=models.CASCADE)
    Name_of_Policy_Admin = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                             related_name='current_policy_admin')
    policy_no = models.CharField(blank=True, null=True, max_length=100)
    last_modified_date = models.DateField(blank=True, null=True)
    locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='locked_by')
    locked_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.Quot_No}/{self.id}'


"""
    The HistoryQuotation Model is responsible to Hold The information of the Revised Quotations (Keep track of the changes of the same quotation)

    Note: For The Foregin Key Fields you need to add the related_name if you going to use more then one field with the same Model. 

    In the Class Meta we changed the Table Name. 
"""


class HistoryQuotation(models.Model):
    class Meta:
        db_table = 'QT_Quotation_His_T'

    Quot_No = models.ForeignKey(CurrentQuotation, on_delete=models.CASCADE)
    Rev_No = models.PositiveSmallIntegerField()
    Rev_Date = models.DateField(auto_now_add=True)
    Rev_Name = models.CharField(max_length=100)
    Policy_Type = models.ForeignKey(PolicyType, on_delete=models.CASCADE, blank=True)
    Sub_Policy_Type = models.ForeignKey(SubPolicyType, on_delete=models.CASCADE, blank=True)
    Branch = models.CharField(max_length=100, blank=True)
    Quotation_Date = models.DateField(blank=True)  # auto_now_add = True
    Inception_Date = models.DateField(blank=True)
    Name_of_Salesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hist_salesperson', blank=True)
    Type_of_Producer = models.ForeignKey(ProducerType, blank=True, null=True, on_delete=models.CASCADE)

    broker = models.ForeignKey(BrokerList, blank=True, null=True, on_delete=models.CASCADE)
    pos = models.ForeignKey(POSList, blank=True, null=True, on_delete=models.CASCADE)
    pos_location = models.ForeignKey(POSLocation, blank=True, null=True, on_delete=models.CASCADE)

    CR_No = models.CharField(max_length=100)
    Client_Name = models.CharField(max_length=100)
    Client_Contact_Person = models.CharField(max_length=100)
    Client_Contact_Email = models.EmailField(max_length=100)
    Client_Contact_Phone = models.CharField(max_length=16)
    Company_size = models.PositiveIntegerField()
    Current_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                        related_name='hist_Current_Insured')
    Prior_Year_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                           related_name='hist_Prior_Year')
    Prior_Two_Year_Insured = models.ForeignKey(InsurerM, blank=True, null=True, on_delete=models.CASCADE,
                                               related_name='hist_Prior_Two_Year')
    No_of_Lives_or_vehicle = models.PositiveIntegerField(blank=True, null=True)
    Client_Target = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Data_completion_date = models.DateField(blank=True, null=True)
    Name_of_Underwriter = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                            related_name='hist_underwiter')
    Documents_Received = models.BooleanField(blank=True, null=True)
    Name_of_pending_documents = models.CharField(blank=True, null=True, max_length=100)
    Date_of_receipt_of_complete_documents = models.DateField(blank=True, null=True)
    Reinsurance_Approval_Request = models.BooleanField(blank=True, null=True, )
    Reinsurance_Request_Date = models.DateField(blank=True, null=True)
    Reinsurance_Received_Approval_Date = models.DateField(blank=True, null=True)
    Commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Loading = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Loading_Discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Claim_Discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Credibility_Factor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Estimated_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Final_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    No_of_Member = models.PositiveIntegerField(blank=True, null=True)
    PPPY = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Sum_Insured = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Risk_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Average_Rate_per_vehicle_member = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Average_Risk_Rate_per_member = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Book_rate = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Experience_rate = models.DecimalField(max_digits=1000, decimal_places=5, blank=True, null=True)
    Deductible = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Aggregate_Limit = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Anyone_Occurrence = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)

    Average_claims_per_person_per_months = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Average_claims_per_person_per_year = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Extrapolated_claims = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Provider_discount = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Trend = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Additional_factor = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Admin_Loading = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Commission_Claim = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Total_Loading = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Recommended_Premium = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)

    Quote_to_Client_Date = models.DateField(blank=True, null=True)
    TAT = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Rev_TAT = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    Comments_Remarks = models.TextField(max_length=500, null=True, blank=True)
    Quotation_Status = models.ForeignKey(QuotationStatus, on_delete=models.CASCADE)
    Name_of_Policy_Admin = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                             related_name='hist_policy_admin')
    policy_no = models.CharField(blank=True, null=True, max_length=100)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.Quot_No}/{self.id}'


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'attachemnts/{instance.Quot_No}/{instance.attachment}.{ext}'


"""
    The AttachmentsDetails Model is responsible to Hold The information of Each Attachments for specific Quotation with the specific Attachemnts Type.  

    Note: For The Upload_to we override it with the above function to store the files in the proper format. 

    In the Class Meta we changed the Table Name. 
"""


class AttachemntsDetails(models.Model):
    class Meta:
        db_table = 'QT_Attachment_Details_T'

    Quot_No = models.ForeignKey(CurrentQuotation, on_delete=models.CASCADE, blank=True, null=True)
    attachment_path = models.FileField(upload_to=upload_to, blank=True, null=True)
    attachment = models.ForeignKey(AttachmentM, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.id} / {self.attachment}'
