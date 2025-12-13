wallet_balance = 0 
transactions = [] # List to store history

print("--- Digital Wallet System Started ---")

# --- INFINITE LOOP ---
while True:
    print(f"\nCurrent Balance: Rs. {wallet_balance}\n")
    print("1. Add Money")
    print("2. Make Payment")
    print("3. View History (Last 10)")
    print("4. Withdraw Money")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    # --- LOGIC FOR MENU ---
    if choice == "1":
        amount = int(input("Enter amount to add: "))
        wallet_balance = wallet_balance + amount
        
        # Add record to list
        transactions.append(f"Credit: +{amount}")
        print("Success: Money Added.")

    elif choice == "2":
        amount = int(input("Enter payment amount: "))
        
        if wallet_balance >= amount:
            wallet_balance = wallet_balance - amount
            
            # Add record to list
            transactions.append(f"Debit:  -{amount}")
            print("Success: Payment made.")
        else:
            print("Failed: Insufficient Funds!")

    elif choice == "3":
        print("\n--- Last 10 Transactions ---")
        
        # SLICING: Get the last 10 items from the list
        # format: list[start : end]
        # using negative index [-10:] means "10th from the end, to the end"
        recent_txns = transactions[-10:]
        
        for txn in recent_txns:
            print(txn)
            
        print("----------------------------")

    elif choice == "4":
        amount = int(input("Enter Widthdrawl amount: "))
        
        if wallet_balance >= amount:
            wallet_balance = wallet_balance - amount
            
            # Add record to list
            transactions.append(f"Widthdrawal Debit:  -{amount}")
            print(f"Success: Amount Widthrwal {amount}.")
        else:
            print("Failed: Insufficient Funds!")

    elif choice == "5":
        print("Exiting Wallet. Goodbye!")
        break 
        
    else:
        print("Invalid choice, please try again.")