from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('inbox', views.inbox, name='inbox'),
    path('superinbox', views.super_inbox, name='superinbox'),
    path('newquotation/<policytype>/', views.new_quotation, name='newquotation'),
    path('salesqoutation/<id>/', views.sales_qoutation, name = 'salesqoutation'),
    path('underwriterqoutation/<id>/', views.underwriter_qoutation, name='underwriterqoutation'),
    path('issueqoutation/<id>/', views.issue_qoutation, name='issueqoutation'),
    path('validate', views.validate, name = 'validate'),
    path('download/<id>', views.download, name = 'download'),
    path('history/<id>', views.history, name = 'history'),
    path('viewqoutation/<id>', views.view_quotation, name = 'view_qoutation'),
    path('unlockqoutation/<id>', views.unlock_quotation, name='unlock_qoutation')



]