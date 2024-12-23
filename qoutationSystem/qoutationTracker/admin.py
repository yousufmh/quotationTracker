from django.contrib import admin
from .models import User, HistoryQuotation, CurrentQuotation, AttachemntsDetails, QuotationStatus, PolicyType, UserRole, \
    SubPolicyType, ProducerType, AttachmentM, Branch, UserStatus, InsurerM, BrokerList, POSList, MultiRole, POSLocation

# Register your models here to be Viewed in the Admin Page.

admin.site.register(User)
admin.site.register(HistoryQuotation)
admin.site.register(CurrentQuotation)
admin.site.register(AttachemntsDetails)
admin.site.register(QuotationStatus)
admin.site.register(PolicyType)
admin.site.register(UserRole)
admin.site.register(SubPolicyType)
admin.site.register(ProducerType)
admin.site.register(AttachmentM)
admin.site.register(Branch)
admin.site.register(UserStatus)
admin.site.register(InsurerM)
admin.site.register(BrokerList)
admin.site.register(POSList)
admin.site.register(POSLocation)
admin.site.register(MultiRole)
