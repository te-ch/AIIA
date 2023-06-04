import os
import random
import anthropic
from dotenv import load_dotenv
import io
import datetime
from colorama import init, Fore
import streamlit as st
from streamlit_chat import message

load_dotenv()
# Set org ID and API key
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

#Initialise debug logs
logfile = 'logs.txt'
msg_limit = 7

def add_log(log) : 
    #print(log)
    with open(logfile, "w") :
        pass
    with open(logfile, 'w', encoding="utf8") as f : 
        f.write(log + "\n")
        
# Setting page title and header
st.set_page_config(page_title="AIIA", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>AVA - a totally harmless chatbot 😬</h1>", unsafe_allow_html=True)

# Set org ID and API key
apikey = "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"
anthropic_client = anthropic.Client(api_key=apikey)

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ""
if 'interview_phase' not in st.session_state:
    st.session_state['interview_phase'] = 1
if 'msg_count' not in st.session_state:
    st.session_state['msg_count'] = 0
if 'confirmed' not in st.session_state:
    st.session_state['confirmed'] = 0
if 'job_desc' not in st.session_state:
    st.session_state['job_desc'] = ""
if 'personality' not in st.session_state:
    st.session_state['personality'] = ""
    
# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['chat_history'] = ""

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

print("This is the start of the script")
greeting = "Welcome. I'm here to help you practice your interview skills. To start, can you tell me a bit about the job you would like to interview for? It can be a general description or you can even provide me the URL for the job application."

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            instruction = anthropic.HUMAN_PROMPT + " In this scenario we will roleplay a job interview. Your task is to help me improve my interviewing skills. You will act as the interviewer and will remain in character throughout the entire session."
            if st.session_state['interview_phase'] == 1:  
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + greeting #adds the greeting to the chat history
            st.session_state['chat_history'] += anthropic.HUMAN_PROMPT + " " + user_input #add user input to chat history
            st.session_state['past'].append(user_input)
            if st.session_state['interview_phase'] == 6:
           # ================ PHASE 6 =====================
                print("Phase 6")
                #Begin the interview and ask questions
                sysmes_start = (    # Removes the interviewer persona from the start prompt. Keeps the job description for review.
                    "\nJob description:\n" + st.session_state['job_desc']
                )
                sysmes_end = "\n\nSystem: End of interview. Summarize the interview based on the applicant's replies. Provide constructive criticsm and feedback. Point out what they did well, what their weaknesses were, and how they can improve. At the end, rate their interview and state if they would have got the job. Be completely transparent and honest."
                prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                #AI sends a new "greeting" message sort of thing
                print("Completion 6a")  #completion
                completion = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]     
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                st.session_state["generated"].append(completion)
                add_log(
                    "===================DEBUG=================="+
                    "\n<prompt>" + prompt + "\n</prompt>" +
                    "\n<completion>\n" + completion + "\n</completion>"
                    )
            if st.session_state['interview_phase'] == 5:
           # ================ PHASE 5 =====================
                print("Phase 5")
                sysmes_start = (    # Start prompt to keep the interviewer in character.
                    "\n\nSystem: Roleplay as the interviewer in a fictional dialogue between an interviewer and an applicant." +
                    "\nJob description:\n" + st.session_state['job_desc'] + "\nInterviewer's persona:\n" + st.session_state['personality'] +
                    "\n\nAsk the applicant a series of questions based on the job and the interviewer's personality. The questions should be a mix of general questions to determine the applicant's ability to perform the a job in that field and more specific questions pertaining to the job itself. Don't be afraid to ask creative questions or throw curveballs to gauge the applicant's personality." +
                    "\nExample questions for a job in accounting:\nHow did you learn about our organization and this job opportunity?\nWhy do you think this role is appropriate for you?\nCan you give a few examples of other similar work that you have done?\nHow do you learn best?\nWhat would your past coworkers or peers say if I were to call them to ask about your qualifications for this position?\nHave you ever been terminated for cause by an employer?\nConvince me that I am sitting across from the best candidate for this position."
                )
                sysmes_end = "\n\nSystem: Time's up. Wrap up the conversation and end the interview. Ask the applicant how they think it went."
                prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                print("Completion 5a")  #completion
                completion = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]     
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                st.session_state["generated"].append(completion)
                if st.session_state['msg_count'] == 2:
                    st.session_state['interview_phase'] == 6
                add_log(
                    "===================DEBUG=================="+
                    "\n<prompt>" + prompt + "\n</prompt>" +
                    "\n<completion>\n" + completion + "\n</completion>"
                    )
            if st.session_state['interview_phase'] == 4:
            # ================ PHASE 4 =====================
                print("Phase 4")
                st.session_state['msg_count'] += 1
                #Begin the interview and ask questions
                sysmes_start = (    # Start prompt to keep the interviewer in character.
                    "\n\nSystem: Roleplay as the interviewer in a fictional dialogue between an interviewer and an applicant." +
                    "\nJob description:\n" + st.session_state['job_desc'] + "\nInterviewer's persona:\n" + st.session_state['personality'] +
                    "\n\nAsk the applicant a series of questions based on the job and the interviewer's personality. The questions should be a mix of general questions to determine the applicant's ability to perform the a job in that field and more specific questions pertaining to the job itself. Don't be afraid to ask creative questions or throw curveballs to gauge the applicant's personality." +
                    "\nExample questions for a job in accounting:\nHow did you learn about our organization and this job opportunity?\nWhy do you think this role is appropriate for you?\nCan you give a few examples of other similar work that you have done?\nHow do you learn best?\nWhat would your past coworkers or peers say if I were to call them to ask about your qualifications for this position?\nHave you ever been terminated for cause by an employer?\nConvince me that I am sitting across from the best candidate for this position."
                )
                sysmes_end = "\n\nSystem: Conduct a realistic interview with the applicant. Ask one question at a time. Act according to your personality."
                prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                print("Completion 4a")  #completion
                completion = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]     
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                st.session_state["generated"].append(completion)
                if st.session_state['msg_count'] == msg_limit:
                    st.session_state['interview_phase'] = 5
                    st.session_state['msg_count'] = 0
                add_log(
                    "===================DEBUG=================="+
                    "\n<prompt>" + prompt + "\n</prompt>" +
                    "\n<completion>\n" + completion + "\n</completion>"
                    )
            if st.session_state['interview_phase'] == 1:            
            # ================ PHASE 1 =====================
                print("Phase 1")
                #instruction = anthropic.HUMAN_PROMPT + " In this scenario we will roleplay a job interview. Your task is to help me improve my interviewing skills. You will act as the interviewer and will remain in character throughout the entire session."
                sysmes_start = instruction + "\n\nSystem: The user will tell you what job they are applying for. The user might give you a general description or provide a website URL for the specific job they want to apply to."
                sysmes_end = "\n\nSystem: Do not proceed until the user has provided sufficient information on the job they are applying for. If there is not enough information, ask additional questions to determine what job they're applying for, how much experience the role needs and anything else to clarify more specific information on the job. If they provide adequate information, confirm that you are going to prepare for the interview. Do not start the interview yet."
                #st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + greeting #adds the greeting to the chat history
                #st.session_state['chat_history'] += anthropic.HUMAN_PROMPT + " " + user_input #add user input to chat history
                #user_output = "Applicant: " + user_input
                
                prompt = sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT       
                
                add_log("<prompt>\n" + prompt + "\n<\prompt>")
                print("Completion 1a") #completion
                completion1 = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion1
                #st.session_state['past'].append(user_input)
                #st.session_state["generated"].append(completion1)
                #st.session_state['interview_phase'] = 2
                print("Setting phase to 2")
            #if st.session_state['interview_phase'] == 2:
                print("Phase 2")
                #VALIDATION STEP - Does not add to chat history
                sysmes_validate = "\n\nSystem: Read the previous conversation. Has the applicant provided information about their job? Answer \"YES\" or \"NO\"."
                prompt = instruction + st.session_state['chat_history'] + sysmes_validate + anthropic.AI_PROMPT
                add_log("<prompt>\n" + prompt + "\n<\prompt>")
                print("completion 2a") #completion
                completion = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]
                if "YES" in completion:
                    if st.session_state['confirmed'] == 1:
                        print("Confirmed")
                        add_log(
                            "===================DEBUG=================="+
                            "\n<prompt>" + prompt + "\n</prompt>" +
                            "\n<completion>\n" + completion + "\n</completion>" +
                            "\n<Moving on to summary...>"
                            )
                        sysmes_end = "\n\nSystem: Summarize the job description using the provided information. Write a simple and concise description. \nEXAMPLE OUTPUT:\n{Entry-level position as a cashier at Walmart. Core responsibilities include serving customers and handling any payment transactions. Other responsibilities include stocking shelves, cleaning the shop, and closing down the register at the end of the shift. The ideal candidate will have strong communication skills, enjoy interacting with customers, and be detail-oriented. Basic math and cash-handling skills are important.}\nWrite the job description and nothing else."
                        prompt = instruction + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                        add_log(
                            "===================DEBUG=================="+
                            "\n<prompt>" + prompt + "\n</prompt>"
                            )
                        print("completion 2b")  #completion
                        completion = anthropic_client.completion(
                            prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                        )["completion"]
                        add_log(
                            "===================DEBUG=================="+
                            "\n<prompt>" + prompt + "\n</prompt>" +
                            "\n<completion>\n" + completion + "\n</completion>" +
                            "\n<Set job_desc as response. Moving on to next step...>"
                            )
                        st.session_state['job_desc'] = completion #Sets the AI's response as the Job Description
                        st.session_state['interview_phase'] = 3
                    if st.session_state['confirmed'] == 0:
                        print("Not confirmed, setting confirmed to 1")
                        st.session_state["generated"].append(completion1)
                        st.session_state['confirmed'] = 1
                else:
                    add_log(
                        "===================DEBUG=================="+
                        "\n<prompt>" + prompt + "\n</prompt>" +
                        "\n<completion>\n" + completion + "\n</completion>" +
                        "\n<Not enough information...>"
                        )
                    st.session_state["generated"].append(completion1)
                    st.session_state['interview_phase'] = 1                    
            if st.session_state['interview_phase'] == 3:
            # ================ PHASE 3 =====================
                print("Phase 3")
                personalities = {}
                personalities["friendly"] = "Friendly and helpful. Asks follow up questions and prompts the user for additional information if their answers are not specific or lacking specificity."
                personalities["stoic"] = "Stoic and blunt. Remains impartial and will ask questions and move things along without follow up questions."
                personalities["adversarial"] = "Adversarial. They have many good candidates and are trying to be highly selective in the interview process. Remains professional, but does not help the applicant in any way in their responses. Challenges the applicant to fully prove and demonstrate their capabilities through their answers."
                personalities["hostile"] = "Hostile. They've had a horrible start to their day. Their spouse was mean to them before coming in to work and their dog shit on the floor right before they were about to walk out the door. Once they got to work they realized they forgot their lunch. The applicant is the last candidate that they have to interview before getting to go home for the day."
                personalities["casual"] = "Casual and laid-back. They want the interview to feel informal and relaxing. Their work environment is a fun place to be and they want an applicant that will fit in well with their team dynamic. Considers the applicant's personality to be far more important than boring qualifications. They ask unusual questions to test the applicant's character."
                personalities["mystery"] = "Surprise me! Come up with a random personality for the interviewer."
                personality = ""
                def choose_personality(personality) :
                    print("checkpoint personality")
                    if personality == "random":
                        personality = random.choice(list(personalities.values()))
                    elif personality == "mystery":
                        prompt = (
                            anthropic.HUMAN_PROMPT + "Think of some random personality traits for the character of an interviewer. Write a one-word summary of their personality, followed by a simple and concise description of their defining traits. Be creative and imaginative; surprise me!" +
                            "\nEXAMPLE OUTPUTS:" + "\n{Friendly and helpful. Asks follow up questions and prompts the user for additional information if their answers are not specific or lacking specificity.}" + 
                            "{Casual and laid-back. They want the interview to feel informal and relaxing. Their work environment is a fun place to be and they want an applicant that will fit in well with their team dynamic. Considers the applicant's personality to be far more important than boring qualifications. They ask unusual questions to test the applicant's character.}" + 
                            "{Adversarial. They have many good candidates and are trying to be highly selective in the interview process. Remains professional, but does not help the applicant in any way in their responses. Challenges the applicant to fully prove and demonstrate their capabilities through their answers.}" + "Write the description of the character's personality and nothing else." +
                            anthropic.AI_PROMPT
                        )
                        add_log(
                            "===================DEBUG==================" +
                            "\n<prompt>" + prompt + "\n</prompt>"
                            )
                        print("completion 3a")  #completion
                        completion = anthropic_client.completion(
                            prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                        )["completion"]
                        personality = completion
                    else : personality = personalities[personality]
                    return personality

                    #add_log(
                    #    "===================DEBUG==================" +
                    #    "\n<prompt>" + prompt + "\n</prompt>" +
                    #    "\n<personality>\n" + personality + "\n</personality>"
                    #   )
                st.session_state['personality'] = choose_personality("mystery")
                print("checkpoint 1")
                sysmes_start = (    # Start prompt to keep the interviewer on track.
                    "\n\nSystem: Roleplay as the interviewer in a fictional dialogue between an interviewer and an applicant." +
                    "\nJob description:\n" + st.session_state['job_desc'] + "\nInterviewer's persona:\n" + st.session_state['personality'] +
                    "\n\nAsk the applicant a series of questions based on the job and the interviewer's personality. The questions should be a mix of general questions to determine the applicant's ability to perform the a job in that field and more specific questions pertaining to the job itself. Don't be afraid to ask creative questions or throw curveballs to gauge the applicant's personality." +
                    "\nExample questions for a job in accounting:\nHow did you learn about our organization and this job opportunity?\nWhy do you think this role is appropriate for you?\nCan you give a few examples of other similar work that you have done?\nHow do you learn best?\nWhat would your past coworkers or peers say if I were to call them to ask about your qualifications for this position?\nHave you ever been terminated for cause by an employer?\nConvince me that I am sitting across from the best candidate for this position."
                )
                sysmes_end = "\n\nSystem: Start the interview. Think of a name, introduce yourself and greet the applicant. Act according to your personality."
                st.session_state['chat_history'] = "" #Wipes the chat history
                prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                add_log("\n<prompt>" + prompt + "\n</prompt>")
                #AI sends a new "greeting" message sort of thing
                print("Completion 3b")  #completion
                completion2 = anthropic_client.completion(
                    prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
                )["completion"]
                print("new greeting = " + completion2)
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion2
                st.session_state["generated"].append(completion2)
                print("appended new greeting")
                st.session_state['interview_phase'] = 4
                             


with response_container:
    message(greeting)
    #st.session_state["generated"].append(greeting) ##TODO - This isn't in the prompt nyergh
    if st.session_state["generated"]:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
