class account:
    def __init__(self,bal,acc):
        self.balance=bal
        self.account=acc

    def debit(self,amount):
        self.balance-= amount
        print(amount,"debited")
        print("total balance", self.balance)


    def credit(self,amount):
        self.balance+= amount
        print(amount,"credited")
        print("total balance", self.balance)

    def balance(self):
        return self.balance
        
acc1= account(100,1234)
acc1.debit(1000)
acc1.credit(500)
