from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegistrationFrom,UserUpdateForm
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic.edit import FormView
from django.views import View
from .models import UserBankAccount
from django.contrib import messages
from .forms import TransferAmountForm
#Email sending headers
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
#Email sending Function
def send_transaction_email(user, amount, sender_subject,receiver_subject, sender_template, receiver_template, receiver=None, sender=None):
    # Create the initial context
    context = {
        'user': user,
        'amount': amount,
    }

    # Add receiver and receiver account number if provided
    if receiver:
        context['receiver'] = receiver
        context['receiver_account_no'] = receiver.account.account_no  # Access the account number correctly

    # Add sender if provided
    if sender:
        context['sender'] = sender

    # Render the email for the sender using the sender_template
    sender_message = render_to_string(sender_template, context)
    
    # Create the email and send it to the sender
    send_email_to_sender = EmailMultiAlternatives(sender_subject, '', to=[user.user.email])
    send_email_to_sender.attach_alternative(sender_message, "text/html")
    send_email_to_sender.send()

    # If there is a receiver, render and send the email using the receiver_template
    if receiver:
        # Render the email for the receiver using the receiver_template
        receiver_message = render_to_string(receiver_template, context)
        
        # Send email to the receiver
        send_email_to_receiver = EmailMultiAlternatives(receiver_subject, '', to=[receiver.email])
        send_email_to_receiver.attach_alternative(receiver_message, "text/html")
        send_email_to_receiver.send()



# Create your views here.
class UserRegistrationView(FormView):
    template_name='accounts/user_registration.html'
    form_class=UserRegistrationFrom
    success_url=reverse_lazy('register')
    def form_valid(self,form):
        # print(form.cleaned_data)
        user=form.save()
        login(self.request,user) #request kortechi ,k korteche user
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name='accounts/user_login.html'
    def get_success_url(self) -> str:
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')
    
class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
#Transfer Amount From Another Account 
class TransferAmountView(FormView):
    template_name = 'accounts/transfer.html'
    form_class = TransferAmountForm
    success_url = reverse_lazy('transfer_success')  

    # def form_valid(self, form):
    #     receiver_account_no = form.cleaned_data['receiver_account_no']
    #     amount = form.cleaned_data['amount']

    #     sender_account = UserBankAccount.objects.get(user=self.request.user)

    #     result = sender_account.transfer_amount(receiver_account_no, amount)
    #     receiver=receiver_account_no.user
    #     if result['status'] == 'success':
    #         messages.success(self.request, result['message'])
    #         send_transaction_email(sender_account, amount, "Transfer Money", "accounts/send_money.html")
    #         send_transaction_email(receiver, amount, "Transfer Money", "accounts/Receive_money.html")
    #         return super().form_valid(form)  
    #     else:
    #         messages.error(self.request, result['message'])
    #         return self.form_invalid(form) 
    def form_valid(self, form):
        receiver_account_no = form.cleaned_data['receiver_account_no']
        amount = form.cleaned_data['amount']

        sender_account = UserBankAccount.objects.get(user=self.request.user)

    
        try:
           receiver_account = UserBankAccount.objects.get(account_no=receiver_account_no)
           receiver = receiver_account.user  
        except UserBankAccount.DoesNotExist:
            messages.error(self.request, "Receiver account number is invalid.")
            return self.form_invalid(form)

    # Transfer the money
        result = sender_account.transfer_amount(receiver_account_no, amount)

        if result['status'] == 'success':
            messages.success(self.request, result['message'])
            send_transaction_email(sender_account, amount, "Send Money","Receive Money", "accounts/send_money.html","accounts/receive_money.html", receiver=receiver)
            return super().form_valid(form)  
        else:
            messages.error(self.request, result['message'])
            return self.form_invalid(form) 