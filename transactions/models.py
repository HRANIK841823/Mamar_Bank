from django.db import models
from .constans import TRANSACTION_TYPE
from accounts.models import UserBankAccount
# Create your models here.
class Transaction(models.Model):
    account=models.ForeignKey(UserBankAccount,related_name='transaction',on_delete=models.CASCADE)
    #ekjon user er multiple transition hoite pare
    amount=models.DecimalField(decimal_places=2,max_digits=12)
    balance_after_transaction=models.DecimalField(decimal_places=2,max_digits=12)
    transaction_type=models.IntegerField(choices=TRANSACTION_TYPE,null=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    loan_approve=models.BooleanField(default=False)

    #receiver account 
    receiver_account = models.ForeignKey( UserBankAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='received_transactions'
    )

    class Meta:
        ordering =['timestamp']

    
