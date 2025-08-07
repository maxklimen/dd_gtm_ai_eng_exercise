# **DroneDeploy AI Engineering Technical Take-home Coding Exercise**

## **Task:**

We want to generate draft outbound emails to all potential DroneDeploy customers who are speaking at a conference to get them to come to our booth: \#42 for a demo of DroneDeploy and a free gift.

Our customers would fall into two categories: those who are building things (general contractors, specialty contractors, engineering firms etc…), or those getting things built for them (owners). We do not want to email competitors or potential partners.

You can find the speaker list here: [https://www.digitalconstructionweek.com/all-speakers/](https://www.digitalconstructionweek.com/all-speakers/)

## **Notes:**

* This exercise shouldn’t take you more than 2hrs to complete.  
* This conference has already passed, and we’ve already sent our emails \- we won’t be using the outputs.  
* Technologies to use:  
  * Python  
  * Asyncio  
  * LLM of choice (OpenAI, Google, Anthropic etc..)  
  * Frameworks are okay, but not required (LiteLLM, LangChain etc..)  
* Outputs should be a CSV file with columns for:  
  * Speaker Name (just their name is fine)  
  * Speaker Title (their role/title at their company)  
  * Speaker Company (the name of the company they work at)  
  * Company Category (Builder, Owner, Partner, Competitor, Other)  
  * Email Subject (an interesting hook that they’d care about)  
  * Email Body (A few sentences about why they should stop by our booth, with an emphasis on DroneDeploy’s relevance to their business/role)  
* Use a .env file to host API keys (please don’t share them with us\!), but do provide a .env\_sample so we can match the ENV variables to test your solution.  
* Folder structure should follow:

```
dd_gtm_ai_eng_exercise
├── .env_sample (your sample .env file with appropriate env variables)
├── main.py (the main python file to run)
├── README.md (readme file with instructions on how to run and any other details you'd like to add)
├── in (a folder for all inputs you might want to use)
├── out (a folder for all the outputs you'll store)
│   └── email_list.csv (the final output in the above format)
└── utils (a folder for any helper functions you might need/use)
```

Feel free to include `.cursor`, `.claude` or similar folders/files for bonus points if you used them.