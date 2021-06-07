# cowin-vaccination-check
This source code is a simple easy to use solution developed in python for booking and getting real time updates for vaccination slots. 
The main program to run is get-vaccination-slots-session.py.

Some things to do before to make sure it's good and easy usage. There are some placeholders in the code which you need to fill -
- The program uses a dictionary of list **receivers**(line - 114). One needs to complete the dictionary as needed using {Username: [pincodes]}
- This program uses telegram developer api to send notifications. I would suggest you to look into getting the required API keys and fill in the placeholders as mentioned in the code.
- You need to mention the list of pincodes to look out for. This can be put in the placeholder **pincodes**(line - 119)
- It sends notifications for both 18+ and 45+, to make sure to send notification to only 45+ a user list is present in line - 155. Fill in accordingly if needed.
- From line 171 - 181, it does automated booking of the beneficiary present in the current registered mobile number.
The format is {"dose": 1, "center_id": center_id, "session_id": session_id, "slot": preffered_slot, "beneficiaries": [""]}. It will parse the captcha(which was present before) decode it and send the request for booking. Currently the captcha is removed so you can comment out the portion where parsing is done.
- The program reads the otp automatically using the software called airmore. Have a read [here]([https://pyairmore.readthedocs.io/) on how to set that up.

Do feel free to ask questions if there are any more doubts. 
