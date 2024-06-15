from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import *
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
import requests
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
import random
import json
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.utils.safestring import mark_safe
import secrets
import string
from itertools import chain
from operator import attrgetter
from django.db.models import F, Value, CharField
from django.db.models import Sum

def landing(request):
    return render(request, 'landing.html')


#home page - dashboard
@login_required
def home(request):
    user = request.user
    UserInfo = CustomUser.objects.get(pk=user.pk)
    UserDetails = UserProfile.objects.get(user=user)
    notifications = Notifications.objects.filter(user=user, seen=False).order_by('-created_at')
    notifications_count = Notifications.objects.filter(user=user, seen=False).count()
    cards = CryptoCards.objects.filter(user=user)
    payment_details = PaymentDetails.objects.get_or_create(user=user, defaults={
        'bitcoin_address': 'None',
        'ethereum_address': 'None',
        'usdt_TRC20_address': 'None',
        'usdt_ERC20_address': 'None',
        })
    address = WalletAddress.objects.all()

    coin_gecko_api_key = 'CG-ijyB17U95TbbzxurdFzBKi6H'

    coin_gecko_endpoint = 'https://api.coingecko.com/api/v3/coins/markets'
    
    crypto_ids = ['bitcoin', 'ethereum', 'litecoin', 'ripple', 'cardano', 'tether', 'polygon', 'solana', 'polkadot', 'dogecoin', 'chainlink', 'avalanche', 'uniswap', 'monero', 'tron', 'stellar', 'eos']

    coin_gecko_params = {
        'vs_currency': 'GBP',
        'ids': ','.join(crypto_ids),
        'order': 'market_cap_desc',
        'sparkline': 'false',
        'price_change_percentage': '24h',
        'key': coin_gecko_api_key,
    }
    try:
        coin_gecko_response = requests.get(coin_gecko_endpoint, params=coin_gecko_params)
    except requests.exceptions.ConnectionError:
        coin_gecko_response = None

    if coin_gecko_response and coin_gecko_response.status_code == 200:
        coins_data = coin_gecko_response.json()
    else:
        coins_data = []

    context = {
        'UserInfo': UserInfo, 
        'UserDetails': UserDetails,
        'profile_image': UserDetails.Profile_image,
        'notifications': notifications,
        'coins_data': coins_data,
        'notifications_count': notifications_count,
        'cards': cards,
        'payment_details': payment_details,
        'address': address,

        }
    return render(request, 'index-dashboard.html', context)

 
@login_required
def addHome(request):
    return render(request, 'component-add-to-home.html')


def index_crypto(request):
    return render(request, 'index-crypto.html')

def index_secondary(request):
    return render(request, 'index-secondary.html')

def index_waves(request):
    return render(request, 'index-waves.html')

def menu_add_card(request):
    return render(request,'menu-add-card.html')

def menu_set_card(request):
    return render(request, 'menu-card-settings.html')


def menu_exchange(request):
    return render(request, 'menu-exchange.html')

def menu_friends(request):
    return render(request, 'menu-friends-transfer.html')

def menu_highlights(request):
    return render(request,'menu-highlights.html')

def actions(request):
    return render(request, 'component-actions.html')

def alerts(request):
    return render(request, 'component-alerts.html')




@login_required
def menu_notifications(request):
    user = request.user
    notifications = Notifications.objects.filter(user=user, seen=False).order_by('-created_at')
    return render(request, 'menu-notifications.html',{
            'notifications':notifications})

@login_required
def mark_as_seen(request):
    user = request.user
    notifications = Notifications.objects.filter(user=user, seen=False).order_by('-created_at')
    for notification in notifications:
        notification.seen = True
        notification.save()
    return JsonResponse({'success': True})

@login_required
def menu_sidebar(request):
    user = request.user
    UserInfo = CustomUser.objects.get(pk=user.pk)
    UserDetails = UserProfile.objects.get(user=user)
    profile_image = UserDetails.Profile_image

    context = {
        'UserInfo': UserInfo, 
        'UserDetails': UserDetails,
        'profile_image': profile_image,
        }
    return render(request,'menu-sidebar.html', context)

def menu_transfer(request):
    return render(request,'menu-transfer.html')



@login_required
def page_activity(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    profile_picture = profile.Profile_image
    withdrawals = WithdrawalRequest.objects.filter(user=user).order_by('-created_at')
    deposits = Deposit.objects.filter(user=user).order_by('-created_at')
    investments = Investments.objects.filter(investor=user).order_by('-date')
    card_requests = CardRequest.objects.filter(user=user).order_by('-date')
    all_activities = sorted(
        chain(
            withdrawals.annotate(activity_date=F('created_at'), activity_type=Value('Withdrawal', output_field=CharField())),
            deposits.annotate(activity_date=F('created_at'), activity_type=Value('Deposit', output_field=CharField())),
            investments.annotate(activity_date=F('date'), activity_type=Value('Investment', output_field=CharField())),
            card_requests.annotate(activity_date=F('date'), activity_type=Value('Card Request', output_field=CharField()))
        ),
        key=attrgetter('activity_date'),
        reverse=True
    )

    context = {
        'investments': investments,
        'withdrawals': withdrawals,
        'deposits': deposits,
        'profile': profile,
        'profile_picture': profile_picture,
        'all_activities': all_activities,
    }
    
    return render(request, 'page-activity.html', context)


@login_required
def page_crypto_report(request):
    user = request.user
    notifications = Notifications.objects.filter(user=user).count()
    UserDetails = UserProfile.objects.get(user=user)
    exchange_rate = ExchangeRates.objects.all()
    cards = CryptoCards.objects.filter(user=user)
    payment_details = PaymentDetails.objects.filter(user=user)
    address = WalletAddress.objects.all()

    try:
        balance = CryptoBalances.objects.get(user=user)
    except CryptoBalances.DoesNotExist:
        balance = None
    except CryptoBalances.MultipleObjectsReturned:
        balance = None
    crypto_balance = None
    if balance is not None:
        crypto_balance = balance
    profile_image = UserDetails.Profile_image

    context = {
        'notifications':notifications,
        'UserDetails': UserDetails,
        'crypto_balance': crypto_balance,
        'profile_image': profile_image,
        'exchange_rate': exchange_rate,
        'cards': cards,
        'payment_details': payment_details,
        'address': address,
    }
    return render(request, 'page-crypto-report.html', context)




@login_required
def page_payments(request):
    user = request.user
    user_info = UserProfile.objects.get(user=user)
    notifications_count = Notifications.objects.filter(user=user).count()
    payment_details = PaymentDetails.objects.filter(user=user)
    address = WalletAddress.objects.all()
    profile_image = UserProfile.objects.get(user=user).Profile_image
    cards = CryptoCards.objects.filter(user=user)
    investments = Investments.objects.filter(investor=user)
    
    context = {
        'cards': cards,
        'user_info': user_info,
        'notifications_count': notifications_count,
        'payment_details': payment_details,
        'address': address,
        'profile_image': profile_image,
        'investments': investments,

        }
    return render(request, 'page-payments.html', context)



@login_required
def page_profile(request):
    user = request.user
    UserInfo = CustomUser.objects.get(pk=user.pk)
    UserDetails = UserProfile.objects.get(user=user)
    notifications_count = Notifications.objects.filter(user=user, seen=False).count()
    profile_image = UserProfile.objects.get(user=user).Profile_image
    cards = CryptoCards.objects.filter(user=user)
    addresses, created = PaymentDetails.objects.get_or_create(user=user, defaults={
        'bitcoin_address': 'None',
        'ethereum_address': 'None',
        'usdt_TRC20_address': 'None',
        'usdt_ERC20_address': 'None',
        })

    context = {
        'notifications_count': notifications_count,
        'UserDetails': UserDetails,
        'profile_image': profile_image,
        'cards': cards,
        'addresses': addresses,
        'created': created
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        tether_usdt = request.POST.get('tether_usdt')
        ethereum_usdt = request.POST.get('ethereum_usdt')
        ethereum = request.POST.get('ethereum')
        bitcoin = request.POST.get('bitcoin')
        oldpassword = request.POST.get('oldpassword')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if username:
            if len(username) < 6:
                messages.error(request, 'Username must be at least 6 characters long', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            UserInfo.username = username
        
        if tether_usdt:
            if len(tether_usdt) < 20:
                messages.error(request, 'Please enter a USDT wallet address', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            addresses.usdt_TRC20_address = tether_usdt

        if ethereum_usdt:
            if len(ethereum_usdt) < 20:
                messages.error(request, 'Please enter a tether USDT wallet address', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            addresses.usdt_ERC20_address = ethereum_usdt

        if ethereum:
            if len(ethereum) < 20:
                messages.error(request, 'Please enter an ethereum ETH wallet address', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            addresses.ethereum_address = ethereum

        if bitcoin:
            if len(bitcoin) < 20:
                messages.error(request, 'Please enter a bitcoin BTC wallet address', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            addresses.bitcoin_address = bitcoin

        if password1 and password2:
            if not oldpassword:
                messages.error(request, 'To update your password, enter your old password')
                return render(request, 'page-profile.html', context)
            
            if password1!= password2:
                messages.error(request, 'New passwords do not match', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            
            request.session.setdefault('update_password', True)
            request.session.setdefault('password_attempt', 0)

            if not UserInfo.check_password(oldpassword):
                request.session['password_attempt'] += 1
                if request.session['password_attempt'] >= 5:
                    request.session['update_password'] = False
                    messages.error(request, 'You can no longer change your password. please try again later', extra_tags='profile')
                    return render(request, 'page-profile.html', context)
                
                messages.error(request, 'Old password is incorrect', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            
            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters long', extra_tags='profile')
                return render(request, 'page-profile.html', context)
            
            
            if not request.session['update_password']:
                messages.error(request, 'You cannot change your password because of multiple failed attempts. Please try again later', extra_tags='profile')
                return render(request, 'page-profile.html', context)

            UserInfo.set_password(password1)
            UserInfo.save()
            messages.success(request, 'Password changed successfully', extra_tags='profile')
            request.session['password_attempt'] = 0
        
        UserInfo.save()
        addresses.save()
        messages.success(request, 'Profile updated successfully', extra_tags='profile')

        return render(request, 'page-profile.html', context)         
    return render(request, 'page-profile.html', context)



# USER TRADE REPORT VIEW
@login_required
def page_report(request):
    user = request.user
    notifications_count = Notifications.objects.filter(user=user, seen=False).count()
    profile_image = UserProfile.objects.get(user=user).Profile_image
    user_details = UserProfile.objects.get(user=user)
    charts = Charts.objects.filter(user=user)
    investment = Investments.objects.filter(investor=user)
    total_invested = investment.aggregate(total_amount=Sum('amount'))['total_amount']
    if total_invested is None:
        total_invested = 0.00
    context = {
        'notifications_count': notifications_count,
        'user_details': user_details,
        'profile_image': profile_image,
        'charts': charts,
        'investment':investment,
        'total_invested': total_invested,
        }
    return render(request, 'page-reports.html', context)




# AUTHENTICATION SECTION

def page_signin(request):
    if request.method == 'POST':
        request.session.setdefault('attempts', 0)
        request.session.setdefault('counter', 4)

        load = request.body.decode('utf-8')
        data = json.loads(load)
        username = data['username']
        password = data['password']
        if not username or not password:
            return JsonResponse({'error': 'Cannot authenticate ghost requests'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                v_obj = is_verified.objects.get(user=user)
            except is_verified.DoesNotExist:
                email = user.email
                return JsonResponse({'verify': 'There was a problem authenticating you. perhaps, you have not verified your account email', 'email':email}, status=404)
            if not v_obj.verified:
                email = v_obj.email
                request.session.setdefault('email', email)
                return JsonResponse({'verify': f'Looks like you have not verified your email {email}. Please verify it now to ensure you are a legitimate user.', 'email':email}, status=400)
            else:
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.can_login:
                    return JsonResponse({'error': 'You currently do not have permission to log in or you have been restricted. No worries! you can contact support team for help.'})
                else:
                    request.session.clear()
                    login(request, user)
                    return JsonResponse({'success': 'You have been successfully logged in.'}, status=200)
        else:
            request.session['attempts'] += 1
            request.session['counter'] -= 1
            if request.session['attempts'] >= 4:
                try:
                    user = CustomUser.objects.get(username=username)
                    profile = UserProfile.objects.get(user=user)
                    profile.can_login = False
                    profile.save()
                    return JsonResponse({'error': 'Maximum attempts exceeded, your account has been disabled. Please contact support for help.'}, status=400)
                except CustomUser.DoesNotExist:
                    request.session.setdefault('risky', True)
                    return JsonResponse({'error': f'Invalid username or password. Further requests will no longer be processed until after an unspecified period of time.', 'disable': 'true'}, status=403)
                except UserProfile.DoesNotExist:
                    return JsonResponse({'error': 'You do not have a profile instance. Perhaps, you\'re partially not a regisered user?'}, status=403)
                
            else: 
                counter = request.session['counter']
                return JsonResponse({'error': f'Incorrect username or password. You have {counter} more attempts left.'}, status=400)
            
    risky = request.session.get('risky', None)
    if risky:
        request.session.setdefault('clear_session', 0)
        request.session['clear_session'] += 1
        if request.session['clear_session'] >= 5:
            request.session.clear()
            return render(request, 'sign-in.html')
        return render(request, 'sign-in.html', {'risk': True})

    return render(request, 'sign-in.html')



def login_user(request):
    if request.method == 'POST':
        request.session.setdefault('attempts', 0)
        request.session.setdefault('counter', 4)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if not username or not password:
            return JsonResponse({'error': 'Cannot authenticate ghost user'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                v_obj = is_verified.objects.get(user=user)
            except is_verified.DoesNotExist:
                email = user.email
                return JsonResponse({'verify': 'There was a problem authenticating you. perhaps, you have not verified your account email', 'email':email}, status=404)
            if not v_obj.verified:
                email = v_obj.email
                request.session.setdefault('email', email)
                return JsonResponse({'verify': f'Looks like you have not verified your email: {email}. Please verify it now to ensure you are a legitimate user.', 'email':email}, status=400)
            else:
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.can_login:
                    return JsonResponse({'error': 'You currently do not have permission to log in or you have been restricted. Contact support team for help.'})
                else:
                    request.session.clear()
                    login(request, user)
                    return JsonResponse({'success': 'Fetching your account, please wait...'}, status=200)
        else:
            request.session['attempts'] += 1
            request.session['counter'] -= 1
            if request.session['attempts'] >= 4:
                try:
                    user = CustomUser.objects.get(username=username)
                    profile = UserProfile.objects.get(user=user)
                    profile.can_login = False
                    profile.save()
                    request.session.setdefault('risky', True)
                    return JsonResponse({'error': 'Maximum attempts exceeded, your account has been disabled. Please contact support for help.', 'disable': 'true'}, status=400)
                except CustomUser.DoesNotExist:
                    request.session.setdefault('risky', True)
                    return JsonResponse({'error': f'Invalid username or password. Further requests will no longer be processed until after an unspecified period of time.', 'disable': 'true'}, status=403)
                except UserProfile.DoesNotExist:
                    user.delete()
                    return JsonResponse({'error': 'You do not have a profile instance. Perhaps, you\'re not a regisered user, Please restart your registration'}, status=403)
                
            else: 
                counter = request.session['counter']
                return JsonResponse({'error': f'Incorrect username or password. You have {counter} more attempts left.'}, status=400)
            
    risky = request.session.get('risky', None)
    if risky:
        request.session.setdefault('clear_session', 0)
        request.session['clear_session'] += 1
        if request.session['clear_session'] >= 5:
            request.session.clear()
            return render(request, 'log-in.html')
        return render(request, 'log-in.html', {'disable': True})
    return render(request, 'log-in.html')
""" 
EMAIL VERIFICATION SECTION
"""

def get_global_code(email, message): 
    try:
        user = CustomUser.objects.get(email=email)
        verification_code = random.randint(100000, 999999)
        object, created = is_verified.objects.get_or_create(user=user, defaults={
            'email': email,
            'verified': False,
            'verification_code': verification_code
        })
        
        object.verified = False
        object.verification_code = verification_code
        object.email = email
        object.creation_time = timezone.now()
        object.save()

        subject = 'myPurse verification code!'
        body = message
        from_email = 'alerts@myprofitpurse.com'
        recipient_list = [email]
        email_message = EmailMultiAlternatives(subject, body, from_email, recipient_list)
        email_message.content_subtype = 'html'
        email_message.send()
        return JsonResponse({'success': f"verification code has been sent to {email}"})
    except CustomUser.DoesNotExist:
       return JsonResponse({'success': "You will get a verification code if your email is registered"})



def get_code(request, email): 
    request.session.setdefault('trials', 0)
    request.session['trials'] += 1
    if request.session['trials'] >= 3:
        return JsonResponse({'error': 'Too many attempts, please try again later.', 'disable': True})
    try:
        user = CustomUser.objects.get(email=email)
        verification_code = random.randint(100000, 999999)
        object, created = is_verified.objects.get_or_create(user=user, defaults={
            'email': email,
            'verified': False,
            'verification_code': verification_code
        })
        
        object.verified = False
        object.verification_code = verification_code
        object.email = email
        object.creation_time = timezone.now()
        object.save()
        subject = 'Please verify your email!'
        body = f'You just requested for a purse account email verification code to your Email address: {email}. please enter this code <h3><strong> {verification_code} </strong></h3> in the verification page to access your account.'
        from_email = 'alerts@myprofitpurse.com'
        recipient_list = [email]
        email_message = EmailMultiAlternatives(subject, body, from_email, recipient_list)
        email_message.content_subtype = 'html'
        email_message.send()
        return JsonResponse({'success': f"verification code has been sent to {email}"})
    except CustomUser.DoesNotExist:
       return JsonResponse({'success': "You will get a verification code if your email is registered"})
        



def verify_email(request):
    request.session.setdefault('verification_trials', 0)
    if request.method == 'POST':
        request.session['verification_trials'] +=1
        if request.session['verification_trials'] == 4:
            return JsonResponse({'error': "Multiple verification requests received within a short period of time, please slow down. ", 'disable': True})
        
        loads = request.body.decode('utf-8')
        data = json.loads(loads)
        email = data['email']
        code = data['code']
        if not code:
            return JsonResponse({'error': 'Please submit the verification code sent to your registered account email.'})
        
        try:
            verified_object = is_verified.objects.get(email=email, verification_code=code)
        except is_verified.DoesNotExist:
            return JsonResponse({'error': 'Invalid verification code'})

        currentTime = timezone.now()
        timeoutDuration = timedelta(minutes=15)
        if currentTime - verified_object.creation_time > timeoutDuration:
            return JsonResponse({'error': 'Verification code expired. Please get a new code'})

        verified_object.verified = True
        verified_object.verification_code = 0
        verified_object.save()

        user = verified_object.user
        login(request, user)
        request.session['email'] = ''
        return JsonResponse({'success': 'Email verified successfully, fetching your account...'})
    return JsonResponse({'error': 'Invalid request method'}, status=403)

"""
ENDS HERE
"""



# REGISTRATION
def page_signup(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        picture = request.FILES.get('picture', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        consent = request.POST.get('consent', None)
        nationality = request.POST.get('nationality', None)
        if not (firstname and lastname and username and email and password1 and password2 and picture and consent and nationality):
            return JsonResponse({'error': 'Required field is missing'}, status=400)
        
        if password1 != password2:
            return JsonResponse({'error': 'Password mismatch'}, status=400)
        
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username used. perhaps you want to log in?'}, status=400)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': ' email already used, perhaps you want to log in?'}, status=400)
        
        user = CustomUser.objects.create_user(username=username, email=email, password=password1, first_name=firstname, last_name=lastname)
        user.save()
        UserProfile.objects.create(user=user, Nationality=nationality, Profile_image=picture,)
        MinimumDeposit.objects.create(user=user, amount=500)
        request.session.setdefault('email', email)
        return JsonResponse({'verify':f'Now, simply verify {email} to continue to your account.', 'email':email})
    
    return render(request, 'sign-up.html')

def email_verify_page(request, email):
    request.session.setdefault('email', email)
    trials = request.session.get('verification_trials', None)
    if trials and trials >= 4:
        disabled = True
        request.session.setdefault('reset', 0)
        request.session['reset'] += 1
        if request.session['reset'] >= 3:
            trials = 0
            disabled = False

    else:
        disabled = False
    return render(request, 'verify-email.html', {'disabled': disabled, 'email': email})


def signout(request):
    logout(request)
    request.session.flush()
    return render(request, 'logged-out.html')

def logged_out(request):
    return render(request, 'logged-out.html')




def page_terms(request):

    if request.method == 'POST':
        cookie = HttpResponse('Consent initialized!')
        
        cookie.set_cookie('consent', False)
        request.session.setdefault('consent', False)

        consent = request.POST.get('consent')
        if not consent:
            messages.error(request, 'Please accept these terms by checking the box below.', extra_tags='consent')
            return render(request, 'page-terms-of-service.html',)
        if consent == 'accepted':          
            accepted = True
            cookie.set_cookie('consent', accepted, max_age=31536000)
            request.session['consent'] = accepted
            messages.success(request, 'Consent choice saved to your device successfully. If you clear your browser cache, you will need to accept these terms again. Periodically, you may be prompted to accept these terms again. You can now use any of our products and services in compliance to the terms and conditions outlined here.', extra_tags='consent')
            return render(request, 'page-terms-of-service.html', {'cookie': cookie})
        
    messages.success(request, 'Welcome !', extra_tags='consent')
    return render(request, 'page-terms-of-service.html')

#      WALLET SECTION --

@login_required
def page_wallet(request):
    user = request.user
    UserInfo = CustomUser.objects.get(pk=user.pk)
    UserDetails = UserProfile.objects.get(user=user)
    notifications_count = Notifications.objects.filter(user=user, seen=False).count()
    cards = CryptoCards.objects.filter(user=user)
    payment_details = PaymentDetails.objects.filter(user=user)
    external_messages = messages.get_messages(request)
    address = WalletAddress.objects.all()
    withdrawals = WithdrawalRequest.objects.filter(user=user)
    deposits =  Deposit.objects.filter(user=user)
    withdrawal_count = withdrawals.count()
    deposit_count = deposits.count()

    context = {
        'UserInfo': UserInfo, 
        'UserDetails': UserDetails,
        'profile_image': UserDetails.Profile_image,
        'notifications_count': notifications_count,
        'profile_image': UserDetails.Profile_image,
        'cards': cards,
        'payment_details': payment_details,
        'messages': external_messages,
        'address': address,
        'withdrawals': withdrawals,
        'deposits': deposits,
        'withdrawal_count': withdrawal_count,
        'deposit_count': deposit_count,
        }
    return render(request, 'page-wallet.html', context)



def pages(request):
    return render(request, 'pages.html')

def walkthrough_slide(request):
    return render(request, 'walkthrough-slide.html')

def walkthrough(request):
    return render(request, 'walkthrough.html')


    # GET REQUEST IDs
def generate_reference(length):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

    # WITHDRAWAL FUNCTIONS

@login_required
def withdrawal(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'})
    user = request.user
    request.session.setdefault('withdrawal_attempts', 0)
    request.session.setdefault('withdrawal_counter', 3)
    UserDetails = UserProfile.objects.get(user=user)
    UserInfo = CustomUser.objects.get(pk=user.pk)
    cards = CryptoCards.objects.filter(user=user)
    cards_count = cards.count()
    card_status = CryptoCards.objects.filter(user=user).first()

    if request.method == 'POST':
        source = request.POST.get('Source')
        payfrom = request.POST.get('payfrom')
        network = request.POST.get('network')
        address = ''
        amount = request.POST.get('amount')
        pin = request.POST.get('pin')
        request_id = generate_reference(25)
        if not(source and payfrom and network and amount and pin):
            return JsonResponse({'error':'Some required details are missing. please fill in all the details to process this request'})
        
        pin = int(pin)
        amount = Decimal(amount)

        
        if pin != UserDetails.card_pin:
            request.session['withdrawal_attempts'] += 1
            request.session['withdrawal_counter'] -= 1
            counter = request.session['withdrawal_counter']
            if request.session['withdrawal_attempts'] >= 3:
                UserDetails.CanWithraw =  False
                UserDetails.save()
                request.session['withdrawal_attempts'] = 0
                request.session['withdrawal_counter'] = 3
                return JsonResponse({'error': 'You can no longer access this function. Please contact support.'})
            return JsonResponse({'error': f'Incorrect authorization pin. You have {counter} attempts left. Please try again.'})
        
        
        if UserDetails.TradeIsActive:
            return JsonResponse({'error': "You cannot make withdrawals while your trade is active. Please wait until your trade is completed."})

        if not UserDetails.CanWithraw:
            return JsonResponse({'error': "You cannot make withdrawals at this time. Try again later."})
        
        
        if cards_count == 0:
            return JsonResponse({'error': 'Please activate at least one cryptographically secured card through your wallet. It is required to process refundable withdrawals from your account. Refundable here means that transactions can be reversed within 20 minutes after submitting the transaction request. This is especiallly useful in cases where the recipient address is entered incorrectly. Withrawals are relayed through your activated card as direct blockchain transactions are irrecoverable and irreversible'})
        
        if card_status.card_status == 'Blocked':
            return JsonResponse({'error': 'Your transaction card has been blocked. Please contact your administrator'})
        
        if card_status.card_status == 'Not activated':
            return JsonResponse({'error': 'Your transaction card is not activated. Thus, withdrawal cannot be processed'})
    

        if source == 'Profits':
            amount = Decimal(amount)
            if amount > UserDetails.Profits:
                return JsonResponse({'error': 'Insufficient profits for withdrawal.'})
            UserDetails.Profits -= amount

        elif source == 'Bonus':
            amount = Decimal(amount)
            if amount > UserDetails.Bonus:
                return JsonResponse({'error': 'Insufficient bonus for withdrawal.'})
            UserDetails.Bonus -= amount

        elif source == 'Deposit':
            amount = Decimal(amount)
            if amount > UserDetails.Deposits:
                return JsonResponse({'error': 'Insufficient deposits for withdrawal'})
            UserDetails.Deposits -= amount

        elif source == 'everything':
            amount = Decimal(amount)
            if amount > UserDetails.total_balance:
                return JsonResponse({'error': 'Insuffient balance'})
            UserDetails.Deposits = 0.00
            UserDetails.Bonus = 0.00
            UserDetails.Profits = 0.00


        withdrawal_limit = Decimal(UserDetails.Withdrawal_limit)
        amount = Decimal(amount)
        if amount < withdrawal_limit:
            return JsonResponse({'error': f"Withdrawal amount is less than your withdrawal limit. Currently, you can withdraw a minimum of £{UserDetails.Withdrawal_limit}. Consider topping up your account or accumulate more profits then trying again."})
        


        if UserDetails.Nationality == "united-states":
            if  UserDetails.VerificationStatus == "Under review":
               return JsonResponse({'error': 'Your verification is still under review. please try again later'})
            
        if UserDetails.Nationality == "united-states":
            if UserDetails.VerificationStatus == "Awaiting" or UserDetails.VerificationStatus == "Failed":     
                status = 'Verification Required'
                subject = 'Please verify your account!'
                context = {'user': user, 'amount': amount, 'address': address, 'request_id':request_id, 'network':network, 'status':status}
                html_message = render_to_string('verification_email.html', context)
                plain_message = strip_tags(html_message)
                from_email = 'alerts@myprofitpurse.com' 
                recipient_list = [user.email]

                email = EmailMultiAlternatives(subject, plain_message, from_email,  recipient_list)
                email.attach_alternative(html_message, "text/html")
                email.send()
                return JsonResponse({'verify': 'Withdrawals are restricted to verified users only. Please verify your account to continue'})      
        UserDetails.save()

        try:
            Payment = PaymentDetails.objects.get(user=user)
        except PaymentDetails.DoesNotExist:
            Payment = None
        except PaymentDetails.MultipleObjectsReturned:
            Payment = None
        if Payment:
            bitcoin_address = Payment.bitcoin_address
            ethereum_address = Payment.ethereum_address
            usdt_trc20_address = Payment.usdt_TRC20_address
            usdt_erc20_address = Payment.usdt_ERC20_address
        else:
            bitcoin_address = 'null'
            ethereum_address = 'null'
            usdt_trc20_address = 'null'
            usdt_erc20_address = 'null'

        if  network == 'bitcoin':    
            withdrawal_request = WithdrawalRequest(
                user=user,
                network=network,
                address=bitcoin_address,
                amount=amount,
                status='Under review',
                RequestID=request_id
            )
        elif network == 'ethereum':
            withdrawal_request = WithdrawalRequest(
                user=user,
                network=network,
                address=ethereum_address,
                amount=amount,
                status='Under review',
                RequestID=request_id
            )
        elif network == 'usdt_trc20':
            withdrawal_request = WithdrawalRequest(
                user=user,
                network=network,
                address=usdt_trc20_address,
                amount=amount,
                status='Under review',
                RequestID=request_id
            )
        elif network == 'usdt_erc20':
            withdrawal_request = WithdrawalRequest(
                user=user,
                network=network,
                address=usdt_erc20_address,
                amount=amount,
                status='Under review',
                RequestID=request_id
            )
        withdrawal_request.save()

        status = 'Reviewing for compliance.'
        subject = 'Withdrawal Request Submitted'
        context = {'user': user, 'amount': amount, 'address': address, 'request_id':request_id, 'network':network, 'status':status}
        html_message = render_to_string('withdrawal_email.html', context)
        plain_message = strip_tags(html_message)
        from_email = 'alerts@myprofitpurse.com' 
        recipient_list = [user.email]
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            from_email,
            recipient_list,
            )
        email.attach_alternative(html_message, "text/html")
        try:
            email.send()
        except Exception as e:
            pass
        subject = f' {UserInfo.username} Just requested to withdraw funds!'
        email_message = f'One of your users "{UserInfo.first_name}, {UserInfo.last_name}" Just submitted a withdrawal request of £{amount}, requesting to withdraw to {network} address: {address}. Request ID: SPK{request_id}. Log into your administrator account to check details'
        from_email = 'alerts@myprofitpurse.com' 
        recipient_list = ['support@myprofitpurse.com']
        email = EmailMultiAlternatives(subject, email_message, from_email, recipient_list)
        try:
            email.send()
        except Exception as e:     
            return JsonResponse({'success': f'Withdrawal is being processed. Due to poor user network, we\'ve suspended email alert for this transaction:'})
        request.session.clear()
        return JsonResponse({'success': f'Withdrawal request submitted successfully. Check your email for updates. Note: {e}'})


@login_required
def deposit(request):
    user = request.user
    user_info = CustomUser.objects.get(pk=user.pk)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        network = request.POST.get('network')
        proof = request.FILES.get('slip')
        

        if not (amount and network and proof):
            return JsonResponse({'error': 'Complete the requested details about your transaction'})
        amount = float(amount)
        min, created = MinimumDeposit.objects.get_or_create(user=user, defaults={'amount': 500})
        minimum = float(min.amount)
        if amount < minimum:
            return JsonResponse({'error': f'The minimum amount you can deposit at the moment is £ {minimum}' })

        deposit = Deposit(
            user=user,
            DepositAmount=amount,
            Network=network,
            Proof=proof,
            status='Under review',
        )
        deposit.save()

        try:
            subject = 'Confirming Deposit'
            from_email = 'alerts@myprofitpurse.com'
            to_email = [user.email]

            context = {'user': user, 'deposit': deposit}
            html_message = render_to_string('deposit_email.html', context)
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message, fail_silently=False)

            subject = f' {user_info.first_name} Just submitted a Deposit!'
            email_message = f'{user_info.first_name} {user_info.last_name} Just submitted a deposit on your website. The user submitted a request of £{amount}. paid through {network} address. Log in to your account and verify the user\'s payment.'
            from_email = 'alerts@myprofitpurse.com' 
            recipient_list = ['support@myprofitpurse.com']
            email = EmailMultiAlternatives(subject, email_message, from_email, recipient_list)
            email.send()
        except Exception as e:
            return JsonResponse({'success': 'Your account will be automatically credited upon successful confirmation. Due to network congestion, we may not be able to send you email notifications on this. Instead, check your account for updates.'})

        return JsonResponse({'success': 'Your account will be automatically credited upon successful confirmation'})
    
    return JsonResponse({'error': 'Invalid request method'})


def invest(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'})
    
    user = request.user
    user_info = UserProfile.objects.get(user=user)
    plan = request.POST.get('plan', None)
    amount = request.POST.get('amount', None)
    duration = request.POST.get('duration', None)
    account = request.POST.get('account', None)

    if not (plan and amount and duration and account):
        return JsonResponse({'error': 'you must specify the plan, amount and investment duration'}, status=400)
    
    amount = Decimal(amount)
    if account == 'profits':
        user_balance = Decimal(user_info.Profits)
    elif account == 'deposit':
        user_balance = Decimal(user_info.Deposits)
    amount = Decimal(amount)
    if amount > user_balance:
        return JsonResponse({'error': 'Insufficient funds for investment'}, status=400)
    
    if plan == 'micro-plan' and (amount < 499 or amount > 999):
        return JsonResponse({'error': 'For Micro plan, you can only invest a minimum of £499.99 and a maximum of £999.99'})
    
    elif plan == 'standard-plan' and (amount < 999 or amount > 4999):
        return JsonResponse({'error': 'For Standard plan, you can only investment a minimum of £999.99 and a maximum of £4,999.99'}, status=400)
    
    elif plan == 'premium-plan' and (amount < 4999 or amount > 9999):
        return JsonResponse({'error': 'For Premium plan, you can only investment a minimum of £4,999.99 and a maximum of £9,999.99'}, status=400)
    
    elif plan == 'elite-plan' and (amount < 9999 or amount > 19999):
        return JsonResponse({'error': 'For Elite plan, you can only investment a minimum of £10,999.99 and a maximum of £9,999.99'}, status=400)
    
    elif plan == 'premium-yield-plan' and (amount < 19999 or amount > 39999):
        return JsonResponse({'error': 'For Premium+ , you can only investment a minimum of £19,999.99 and a maximum of £39,999.99'}, status=400)
    
    elif plan == 'signatory-plan' and amount < 39999:
        return JsonResponse({'error': 'This plan requires a minimum capital of £39,999.99'}, status=400)
    
    elif plan == 'signatory-plan' and amount > 100000:
        return JsonResponse({'error': 'Please select the waiver plan to invest above £100,000 or below £400' }, status=400)
    
    if plan == 'signatory-plan' and duration != '30-days':
        return JsonResponse({'error': 'The minimum duration for the selected plan must be 30 days'}, status=400)
    
    # checked passed.
    if account == 'deposit':
        user_info.Deposits -= amount
    elif account == 'profits':
        user_info.Profits -= amount
    user_info.save()
    if plan == 'waiver':
        waiver = True
    else:
        waiver = False

    investment = Investments.objects.create(
        investor=user,
        plan=plan,
        amount=amount,
        duration=duration,
        waiver=waiver,
    )
    investment.save()
    title = "Congratulations!"
    message = f"You have just activated a trade under {plan} on your account with a capital of £{amount}, debited from your {account} account. Your trade is set to span the duration of {duration}. During the wait, you can frequently check the performance of your investment. You can request to cancel your trade at any time through your administrator."
    Notifications.objects.create(
        user=user, 
        title=title,
        message=message,
        )
    return JsonResponse({'success': f'You have just activated a trade under {plan} on your account with a capital of £{amount}, debited from your {account} account. Your trade is set to span the duration of {duration}. During the wait, you can frequently check the performance of your investment. You can request to cancel your trade at any time through your administrator.'})


def get_card(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'})
    
    user = request.user
    user_info = UserProfile.objects.get(user=user)
    load = request.body.decode('utf-8')
    data = json.loads(load)

    name = data['name']
    amount = data['amount']
    user_balance = Decimal(user_info.Deposits)

    if user_balance < Decimal('2000'):
        return JsonResponse({'error': 'You do not have sufficient balance for this action.'}, status=400)


    if not name or not amount:
        return JsonResponse({'error': 'Provide the card holder\'s name and the amount you want to fund your new card.'}, status=400)
    
    amount = Decimal(amount)
    if amount < Decimal('1000'):
        amount_left = Decimal('1000') - amount
        return JsonResponse({'error': f'Minimum card balance must be over £1000. You would also be charged a card creation fee of £1,000. You can continue if you increase the funding amount with: {amount_left} more'}, status=400)
    amount = amount + 1000
    user_info.Deposits -= amount
    if user_info.Deposits < 0:
        return JsonResponse({'error': f'Not enough balance to process your request. top up your deposit account to continue'}, status=400)
    
    user_info.save()  
    card = CardRequest.objects.create(user=user, name_on_card=name, amount=amount)
    card.save()
    title = "New Card request"
    message = "Your account has been debited for card activation, You will be notified when your new card is activated."
    Notifications.objects.create(user=user, title=title, message=message)
    return JsonResponse({'success': 'Your card activation request was successful. you will be notified when your new card is activated'})

    

        
    
    
    

# PASSWORD RESET VIEWS
def custom_password_reset(request):
    return PasswordResetView.as_view(
        template_name='reset-password.html'
    )(request)

def custom_password_reset_done(request):
    return PasswordResetDoneView.as_view(
        template_name='reset-done.html'
    )(request)

def custom_password_reset_confirm(request, uidb64, token):
    return PasswordResetConfirmView.as_view(
        template_name='reset-confirm.html'
    )(request, uidb64=uidb64, token=token)

def custom_password_reset_complete(request):
    return PasswordResetCompleteView.as_view(
        template_name='reset-complete.html'
    )(request)

# PASSWORD RESET VIEW
# PASSWORD RESET VIEW

@login_required
def verification(request):
    user = request.user
    info = CustomUser.objects.get(pk=user.pk)
    account_info = UserProfile.objects.get(user=user)


    if request.method == 'POST':
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        try:
            phone = int(request.POST.get('phone_number'))
        except ValueError:
            messages.error(request, 'Enter a valid and active phone number.', extra_tags='verification')
            return render(request, 'verification.html', {'user':user})
        
        dob = request.POST.get('dob')
        id_front = request.FILES.get('id_front')
        id_back = request.FILES.get('id_back')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')



        if not (email and firstname and lastname and address and dob and id_front and id_back and password1 and password2):
            messages.error(request, 'All fields are required. check for any missing field and fill it accordingly.', extra_tags='verification')
            return render(request, 'verification.html', {'user':user})
        if not phone:
            messages.error(request, 'Phone number is required.', extra_tags='verification')
            return render(request,'verification.html', {'user':user})
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match, please check and try again.', extra_tags='verification')
            return render(request, 'verification.html', {'user':user})
        
        realDate = datetime.strptime(dob, '%Y-%m-%d').date()

        verified_user = IDME(
            user=user,
            email=email,
            firstname=firstname,
            lastname=lastname,
            address=address,
            phone=phone,
            DOB=realDate,
            password=password1,
            id_front=id_front,
            id_back=id_back,
            
        )
        verified_user.save()
        account_info.VerificationStatus = "Under review" 
        account_info.save()

        status = account_info.VerificationStatus

        subject = 'Verification request submitted!'
        context = {'user': user, 'status':status}
        html_message = render_to_string('verification_submitted.html', context)
        plain_message = strip_tags(html_message)
        from_email = 'alerts@myprofitpurse.com' 
        recipient_list = [user.email]
        email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
        email.attach_alternative(html_message, "text/html")
        email.send()

        subject = f' {info.first_name} Just submitted verifications documents!'
        email_message = f'{info.first_name} {info.last_name} from {account_info.Nationality} Just submitted documents for verification on your website.  Log in to your administrator account and verify the user\'s request.'
        from_email = 'alerts@myprofitpurse.com' 
        recipient_list = ['support@myprofitpurse.com']
        email = EmailMultiAlternatives(subject, email_message, from_email, recipient_list)
        email.send()
        messages.success(request, 'Verification details submitted successfully. check email or profile for verification status.', extra_tags='verification')
        return redirect('home')
    return render(request, 'verification.html',{'user':user })

