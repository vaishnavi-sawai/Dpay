import smartpy as sp

class UserInfo(sp.Contract):
    def __init__(self, metadata):
        self.init(
            all_users = sp.nat(0),
            all_groups = sp.nat(10),


            users = sp.big_map( tkey = sp.TNat, tvalue = sp.TRecord( 
            user_friends = sp.TSet(sp.TAddress), 
            user_groups = sp.TSet(sp.TNat),
            user_name = sp.TString, 
            user_bio = sp.TString, 
            user_address = sp.TAddress ) ),


            groups = sp.big_map(
            tkey = sp.TNat,
            tvalue = sp.TRecord(
            group_name = sp.TString,
            group_friends = sp.TSet(sp.TAddress),
            balance = sp.TMutez,
            staking_amount = sp.TMutez

            )),


            metadata = metadata,

        )
    

    @sp.entry_point
    def register(self, params):
        self.data.users[self.data.all_users] = sp.record(
            user_friends =sp.set() ,
            user_groups = sp.set(),
            user_name = params.user_name,
            user_bio = params.user_bio,
            user_address = sp.sender,

        )
        self.data.all_users += 1
   
    @sp.entry_point
    def addFriend(self, params):
        self.data.users[params.id].user_friends.add(
        self.data.users[params.friend_id].user_address ) 


    @sp.entry_point
    def make_group(self, params):
        sp.set_type(params,sp.TRecord( 
        group_name = sp.TString, 
        friends = sp.TList(sp.TNat),
        ))

        group_friends = sp.local('group_friends', sp.set())
        sp.for friend in params.friends: 
            group_friends.value.add(self.data.users[friend].user_address) 

        self.data.groups[self.data.all_groups] = sp.record(
            group_name = params.group_name,
            group_friends = group_friends.value,
            balance = sp.mutez(0),
            staking_amount = sp.mutez(0)
        )
        sp.for friend in params.friends: 
            self.data.users[friend].user_groups.add(self.data.all_groups)
        self.data.all_groups += 1  


    @sp.entry_point
    def addAmountToGroup(self, group_id):
        sp.set_type(group_id, sp.TNat)
        
        # sp.send(sp.self_address, sp.amount),
        self.data.groups[group_id].balance += sp.amount
        

    @sp.entry_point
    def withdraw(self, params):
        sp.set_type(params,sp.TRecord( 
        group_id = sp.TNat,
        amount = sp.TMutez 
        
        ))

        sp.send(sp.sender, params.amount),
        self.data.groups[params.group_id].balance -= params.amount

       
                 

if "templates" not in __name__:
    @sp.add_test(name = "StoreValue")
    def test():
        # create test users
        alice = sp.test_account("alice")
        bob = sp.test_account("bob")
        tom = sp.test_account("tom")
        lucy = sp.test_account("lucy")

        # create scenario
        scenario = sp.test_scenario()

        # Add heading
        scenario.h1("DPAY")

        # Add subheading
        scenario.h2("Initialise the contract")

        c1 =  UserInfo(
            metadata = sp.utils.metadata_of_url("ipfs://QmTLTbo1a9pvFf2nPNKoLUNjokyw4An9PSVkx82QzKDCtj")
        )

        # Add c1 to scenario
        scenario += c1
        
        scenario.h2("Register a user")
        # Call register entry point
        c1.register(
            user_name = "alice",
            user_bio = "Heyy there!"
        ).run(sender = alice)


        scenario.h2("Register another user")
        c1.register(
            user_name = "bob",
            user_bio = "Hii I'm new to Tezos"
        ).run(sender = bob)

        c1.register(
            user_name = "tom",
            user_bio = "Hi there!"
        ).run(sender = tom)

        c1.register(
            user_name = "lucy",
            user_bio = "Heyy there!"
        ).run(sender = lucy)

        scenario.h2("Add Friend")

        c1.addFriend(
          id = 1,
          friend_id = 2
        ).run(sender = bob)

        c1.addFriend(
          id = 1,
          friend_id = 0
        ).run(sender = bob)

        c1.addFriend(
          id = 1,
          friend_id = 1
        ).run(sender = bob) 

        scenario.h2("Make group")

        c1.make_group(
        group_name = "GROUP 1",
        friends = [ 0, 3]
        ) 

        c1.make_group(
        group_name = "GROUP 2",
        friends = [ 2, 1]
        )

        scenario.h2("Add Money")

        c1.addAmountToGroup(
        10
        ).run(amount = sp.mutez(100000))     