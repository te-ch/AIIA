import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initial setup, interview type, and personality parameters
# Initial Model Card - invisible to user
context = "\n\nHuman: In this scenario we will roleplay a job interview.  The goal is to help the user improve their interviewing skills.  You will act as the interviewer and will remain in character throughout the entire session."

#user_inp = "You: Hello, I'm here for a job interview."

# Display a starting message to the user
startmsg = "Welcome.  I am AIIA, the artificial inteligence interview assistant.  I was created with the goal of assisting you in practicing interview skills.  To start, can you tell me a bit about the job you would like to interview for?  It can be a general description or you can even provide me the URL for the job application.  Once I've processed that information, we can move on to the next step." 
print(startmsg)

# Update context
context += startmsg

#initialize message counter to prevent infinite interview
msg_count = 1

#Define a function to track used tokens
def count_used_tokens(prompt, completion):
    prompt_token_count = anthropic.count_tokens(prompt)
    completion_token_count = anthropic.count_tokens(completion)

    return (
        "🟡 Used tokens this round: "
        + f"Prompt: {prompt_token_count} tokens, "
        + f"Completion: {completion_token_count} tokens."
           )

#Begin the interview and ask questions

while msg_count < 3:
    user_inp = input("You: ")

    current_inp = anthropic.HUMAN_PROMPT + user_inp + anthropic.AI_PROMPT
    context += current_inp

    prompt = context

    completion = anthropic_client.completion(
        prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
    )["completion"]

    context += completion
    msg_count += 1

    print("AIIA: " + completion)
    print(count_used_tokens(prompt, completion))

#End the interview, summarize, and provide feedback to user

endmsg = "That completes the interview questions.  I am able to summarize and provide feedback on your performance if you'd like."
print(endmsg)
context += endmsg

while True:
    user_inp = input("You: ")

    current_inp = anthropic.HUMAN_PROMPT + user_inp + anthropic.AI_PROMPT
    context += current_inp

    prompt = context

    completion = anthropic_client.completion(
        prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
    )["completion"]

    context += completion
    msg_count += 1

    print("AIIA: " + completion)
    print(count_used_tokens(prompt, completion))

        
