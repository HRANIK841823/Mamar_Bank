from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .constants import ACCOUNT_TYPE,GENDER_TYPE
from django.apps import apps
from transactions.constans import TRANSFER
# Create your models here.
class UserBankAccount(models.Model):
   
    user=models.OneToOneField(User,related_name='account',on_delete=models.CASCADE)
    account_type=models.CharField(max_length=10,choices=ACCOUNT_TYPE)
    account_no=models.IntegerField(unique=True) #account number konodin duijon user er same hobe na
    birth_date=models.DateField(null=True,blank=True) #kao na dite chaile problem nai tai null,blank true
    gender=models.CharField(max_length=10,choices=GENDER_TYPE)
    initial_deposite_date=models.DateField(auto_now_add=True)
    balance=models.DecimalField(default=0,max_digits=12,decimal_places=2) #highest 12 digit and 2 dosomik porjonto rakhte parbe

    def __str__(self):
        return str(self.account_no)
    def transfer_amount(self, target_account_no, amount):
        Transaction = apps.get_model('transactions', 'Transaction')
        try:
            target_account = UserBankAccount.objects.get(account_no=target_account_no)
            if self.balance >= amount:
                # minus amount
                self.balance -= amount
                self.save()
                #get user data 
                Transaction.objects.create(
                    account=self,
                    amount=amount,
                    balance_after_transaction=self.balance,
                    transaction_type=TRANSFER,
                    receiver_account=target_account
                )
                # plus amount
                target_account.balance += amount
                target_account.save()
                #get Receiver Data
                Transaction.objects.create(
                    account=target_account,
                    amount=amount,
                    balance_after_transaction=target_account.balance,
                    transaction_type=TRANSFER,  
                    receiver_account=self
                )


                return {"status": "success", "message": "Transfer successful"}
            else:
                return {"status": "error", "message": "Insufficient balance for transfer"}
        except ObjectDoesNotExist:
            return {"status": "error", "message": "Recipient account not found"}
class UserAddress(models.Model):
    user=models.OneToOneField(User,related_name='address',on_delete=models.CASCADE)
    street_address=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    postal_code=models.IntegerField()
    country=models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.user.email