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

    def form_valid(self, form):
        receiver_account_no = form.cleaned_data['receiver_account_no']
        amount = form.cleaned_data['amount']

        sender_account = UserBankAccount.objects.get(user=self.request.user)

        result = sender_account.transfer_amount(receiver_account_no, amount)

        if result['status'] == 'success':
            messages.success(self.request, result['message'])
            return super().form_valid(form)  
        else:
            messages.error(self.request, result['message'])
            return self.form_invalid(form)  