from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class AccountInfoInline(admin.StackedInline):
    model = UserProfile
    can_delete = True
    extra = 0

class CryptoCardsInline(admin.StackedInline):
    model = CryptoCards
    extra = 0

class PaymentDetailsInline(admin.StackedInline):
    model = PaymentDetails
    extra = 0
    can_delete = True
    

class NotificationsInline(admin.StackedInline):
    model = Notifications
    can_delete = True
    extra = 0

class WithdrawalRequestInline(admin.StackedInline):
    model = WithdrawalRequest
    can_delete = True
    extra = 0

class DepositsInline(admin.StackedInline):
    model = Deposit
    can_delete = True
    extra = 0
class IDMEInline(admin.StackedInline):
    model = IDME
    can_delete = True
    extra = 0

class ChartsInline(admin.StackedInline):
    model = Charts
    can_delete = True
    extra = 0


class EmailMessageInline(admin.StackedInline):
    model = email_message
    can_delete = True
    extra = 0

class LimitInline(admin.StackedInline):
    model = MinimumDeposit
    can_delete = True
    extra = 0

class PaymentInline(admin.StackedInline):
    model = PaymentDetails
    can_delete = True
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [
        AccountInfoInline, 
        CryptoCardsInline, 
        WithdrawalRequestInline, 
        NotificationsInline, 
        PaymentDetailsInline,
        DepositsInline,
        IDMEInline,
        ChartsInline,
        EmailMessageInline,
        LimitInline,
        PaymentInline,
        ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(
    [WalletAddress, 
     ExchangeRates, 
     MinimumDeposit, 
     Investments, 
     CardRequest])

# Register your models here.
