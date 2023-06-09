import os
import random
import anthropic
from dotenv import load_dotenv
import io
import streamlit as st
from streamlit_chat import message
from pdfminer.converter import TextConverter 
from pdfminer.pdfinterp import PDFPageInterpreter 
from pdfminer.pdfinterp import PDFResourceManager 
from pdfminer.pdfpage import PDFPage

load_dotenv()
# Set org ID and API key
if 'api_key' not in st.session_state : 
    st.session_state['api_key'] = os.getenv("ANTHROPIC_API_KEY")
    if not st.session_state['api_key'] : 
        st.session_state['api_key'] = st.secrets['ANTHROPIC_API_KEY']
    anthropic_client = anthropic.Client(st.session_state['api_key'])


#Initialise debug logs
logfile = 'logs.txt'
#User variable for number of questions it should ask
msg_limit = 7

def add_log(log) : 
    #print(log)
    with open(logfile, "w") :
        pass
    with open(logfile, 'w', encoding="utf8") as f : 
        f.write(log + "\n")
        
# Setting page title and header
st.set_page_config(page_title="AIIA", page_icon=":man-lifting-weights:")
st.markdown("<h1 style='text-align: center;'>AIIA - Interview Assistant 👩‍🏭</h1>", unsafe_allow_html=True)
st.markdown("[Github](https://github.com/te-ch/AIIA)")

greeting = "Welcome. I'm here to help you practice your interview skills! To start, can you tell me a bit about the job you would like to interview for?"
# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ""
if 'interview_phase' not in st.session_state:
    st.session_state['interview_phase'] = 0
if 'msg_count' not in st.session_state:
    st.session_state['msg_count'] = 0
if 'confirmed' not in st.session_state:
    st.session_state['confirmed'] = 0
if 'job_desc' not in st.session_state:
    st.session_state['job_desc'] = ""
if 'personality' not in st.session_state:
    st.session_state['personality'] = ""
if 'name' not in st.session_state:
    st.session_state['name'] = ""
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
if "personality" not in st.session_state : 
    st.session_state['personality'] = ""
if "submitted" not in st.session_state : 
    st.session_state['submitted'] = ""
if "resume" not in st.session_state : 
    st.session_state['resume'] = ""
if "resume_uploaded" not in st.session_state : 
    st.session_state['resume_uploaded'] = False

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("AIIA Settings")
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation 📛", key="clear")
api_key_field = st.sidebar.form(key="API Key Field")
debug_mode = st.sidebar.checkbox("Enable debug mode")

with api_key_field : 
    api_key = st.text_input(label="Enter Claude API key	🔐")
    submit = st.form_submit_button(label="Submit")
    if submit :
        st.session_state['api_key'] = api_key
        st.text("API key updated! 💎")
welcome_text = (
    "To start, please enter your API key or use a .env file (for local installation)\n" + 
    "To use the bot, enter your name and choose a personality for the interviewer to take on. You never know what the person who interviews you for that dream job might be like, so with this tool, you can prepare for all circumstances! If you are feeling adventurous, you can select a random personality or have the AI generated a mystery one for you!\n" + 
    "Once the AI assistant has determined what job you are applying for, the assistant will switch to that personality.\n" + 
    "The interview will consist of a set number of messages (default = 7) that can be changed in settings.\n After you are finished, it will give you back feedback as the AI which you can use to improve your game.\n" +
    "Please enjoy the bot and let us know what you think!"
)
st.sidebar.header("Welcome to AIIA, a personal AI assistant for practicing tricky job interviews! \n")
with st.sidebar.expander("Instructions 📝") : 
    st.markdown(welcome_text, unsafe_allow_html=True)

#constantly check if api_key has changed
anthropic_client = anthropic.Client(st.session_state['api_key'])

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['chat_history'] = ""
    st.session_state['msg_count'] = 0
    st.session_state['interview_phase'] = 0
    st.session_state['confirmed'] = 0
    st.session_state['job_desc'] = ""
    st.session_state['submitted'] = ""
    st.session_state['resume'] = ""
    st.session_state['resume_uploaded'] = ""
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

#load UI elements
# container for chat history

cv_container = st.container()
response_container = st.container()
# container for text box
container = st.container()
print("This is the start of the script")

#Function to get response from Anthropic Claude
def get_response(prompt) : 
    completion_ = anthropic_client.completion(
            prompt=prompt, model="claude-v1.3-100k", max_tokens_to_sample=1000
            )["completion"]
    return completion_

#Define a function to extract text from pdfs by page
def extract_text_by_page(pdf_path): 

    with io.BytesIO(pdf_path) as fh: 
        
        for page in PDFPage.get_pages(fh, 
                                    caching=True, 
                                    check_extractable=True): 
            
            resource_manager = PDFResourceManager() 
            fake_file_handle = io.StringIO() 
            
            converter = TextConverter(resource_manager, 
                                    fake_file_handle) 
            
            page_interpreter = PDFPageInterpreter(resource_manager, 
                                                converter) 
            
            page_interpreter.process_page(page) 
            text = fake_file_handle.getvalue() 
            
            yield text 
            
            # close open handles 
            converter.close() 
            fake_file_handle.close() 
#Define a fuction to extract text from entire pdf

def extract_text(pdf_path): 
    for page in extract_text_by_page(pdf_path): 
        resume = ""
        resume += (page + "\n")
        return resume 

if st.session_state.api_key :
    with cv_container :    
        #===============Upload CV box==================#
        uploaded_file = st.file_uploader("Upload your resume (optional) :", disabled=st.session_state.resume_uploaded)
        if uploaded_file is not None:
            resumebytes = uploaded_file.getvalue()
            st.write(st.session_state.resume + "Uploaded!")
            st.session_state.resume = extract_text(resumebytes)
            st.session_state.resume_uploaded = True

    with container:
        personalities = {}
        #personalities["Meg"] = {"Name": "Meg", "Personality": "Friendly, helpful", "Description": "Asks follow up questions and prompts the user for additional information if their answers are not specific or lacking specificity."}
        personalities["Friendly"] = "[Name: Meg;\nPersonality: Friendly, helpful;\nDescription: Asks follow up questions and prompts the user for additional information if their answers are not specific or lacking specificity.]"
        personalities["Stoic"] = "[Name: Elizabeth;\nPersonality: Stoic, blunt;\nDescription: Remains impartial and will ask questions and move things along without follow up questions.]"
        personalities["Adversarial"] = "[Name: Hamilton;\nPersonality: Adversarial;\nDescription: He has good candidates and is trying to be highly selective in the interview process. Remains professional, but does not help the applicant in any way in their responses. Challenges the applicant to fully prove and demonstrate their capabilities through their answers.]"
        personalities["Hostile"] = "[Name: Greg;\nPersonality: Hostile;\nDescription: Greg has had a horrible start to his day. His wife was mean to him before coming in to work and his dog shit on the floor right before he was about to walk out the door. Once he got to work he realized he forgot his lunch. The applicant is the last candidate that he has to interview before getting to go home for the day.]"
        personalities["Casual"] = "[Name: Barney;\nPersonality: Casual and laid-back;\nDescription: He wants the interview to feel informal and relaxing. Their work environment is a fun place to be and they want an applicant that will fit in well with their team dynamic. Considers the applicant's personality to be far more important than boring qualifications. They ask unusual questions to test the applicant's character.]"
        personalities["Mystery"] = "Surprise me! Come up with a random personality for the interviewer."
        personalities["Random 🎲"] = "Choose random" 
        def choose_personality(personality_, personalities) :
            del personalities["Random 🎲"]
            if personality_ == "Random 🎲":
                personality_ = random.choice(list(personalities.values()))
            elif personality_ == "Mystery":
                prompt_ = (
                    anthropic.HUMAN_PROMPT + "Create a random character persona for a job interviewer. Format your message as follows, including square brackets:\n[Name: (Character's name);\nPersonality: (One-two word summary of their personality);\nDescription: (Further details on their defining traits)]\nBe creative and imaginative; surprise me!" +
                    "\nEXAMPLE OUTPUTS:" + "\n[Name: Meg;\nPersonality: Friendly, helpful;\nDescription: Asks follow up questions and prompts the user for additional information if their answers are not specific or lacking specificity.]" + 
                    "\n[Name: Barney;\nPersonality:\nCasual and laid-back;\nDescription: He wants the interview to feel informal and relaxing. His work environment is a fun place to be and he wants an applicant that will fit in well with their team dynamic. Considers the applicant's personality to be far more important than boring qualifications. He asks unusual questions to test the applicant's character.]" + 
                    "\n[Name: Hamilton;\nPersonality: Adversarial;\nDescription: Hamilton has many good candidates and is trying to be highly selective in the interview process. Remains professional, but does not help the applicant in any way in their responses. Challenges the applicant to fully prove and demonstrate their capabilities through their answers.]" + "\nWrite the description of the character's personality and nothing else." +
                    anthropic.AI_PROMPT
                )
                add_log(
                    "===================DEBUG==================" +
                    "\n<prompt>" + prompt_ + "\n</prompt>" +
                    "\n<personality>\n" + personality_ + "\n</personality>"
                )
                #Create a mystery personality using completion
                completion = get_response(prompt_)
                message(completion, is_user=False)
                personality_ = completion
            else : personality_ = personalities[personality_]
            return personality_

        #Name and personality field
        if st.session_state.disabled == False :
            with st.form("start_form") :
                st.session_state.name = st.text_input('Please enter your name.', key="enter_name", disabled=st.session_state.disabled) 
                personality = st.selectbox('Choose interviewer personality:', list(personalities.keys()), disabled=st.session_state.disabled)
                submit_button = st.form_submit_button(label='Submit') 
                if submit_button: 
                    st.write(f'Name: {st.session_state.name}')
                    st.write(f'Personality: {personality}')
                    #write personality to session state
                    st.session_state.personality = choose_personality(personality, personalities)
                    st.session_state.resume_uploaded = True #Disable uploading resume

                    message(f"Ok, {st.session_state.name}, for this practice interview, I will take on a {personality} personality!\n I will be {st.session_state.personality}")#{st.session_state.personality}") 
                    st.session_state.submitted = True
                    print(st.session_state.submitted)
                    st.session_state.disabled = True

        with st.form(key='my_form', clear_on_submit=True):
            if st.session_state.submitted :
                user_input = st.text_area("You:", key='input', height=100)
                submit_button = st.form_submit_button(label='Send')

            def phase_1() : 
                # ================ PHASE 1 =====================
                    print("Phase 1")
                    sysmes_start = instruction ##TODO assignment
                    #instruction = anthropic.HUMAN_PROMPT + " In this scenario we will roleplay a job interview. Your task is to help me improve my interviewing skills. You will act as the interviewer and will remain in character throughout the entire session."
                    sysmes_end = "\n\nSystem: From the provided information, confirm the details of the job that the applicant is applying to. If they have not provided enough information about the job, ask additional questions to determine the job details. Do not start the interview yet."

                    prompt = sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT       
                    
                    add_log("<prompt>\n" + prompt + "\n<\prompt>")
                    print("Completion 1a") #completion
                    completion1 = get_response(prompt)
                    st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion1

                    print("Setting phase to 2")
                #if st.session_state['interview_phase'] == 2:
                    print("Phase 2")
                    #VALIDATION STEP - Does not add to chat history
                    sysmes_validate = "\n\nSystem: Has the applicant provided information about their job? Answer 'YES' or 'NO'."
                    prompt = instruction + st.session_state['chat_history'] + sysmes_validate + anthropic.AI_PROMPT
                    add_log("<prompt>\n" + prompt + "\n<\prompt>")
                    print("completion 2a") #completion
                    completion = get_response(prompt)
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
                            completion = get_response(prompt)
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
                        #st.session_state['interview_phase'] = 1

            def phase_3() : 
                # ================ PHASE 3 =====================
                print("Phase 3")
                #Add resume to prompt if needed
                if st.session_state.resume != "" : 
                    resume = f"The applicant has provided their resume. Please make sure it corresponds to the job description. Resume: \n[{st.session_state.resume}]"
                else : 
                    resume = ""
                sysmes_start = (    # Start prompt to keep the interviewer on track.
                    f"\n\nSystem: Write the next reply as the interviewer in a fictional dialogue between an interviewer and an applicant. Avoid writing internet-style roleplay actions." +
                    f"\nJob description:\n {st.session_state['job_desc']}" + 
                    f"\n {resume}"
                    f"\nInterviewer's persona:\n {st.session_state['personality']}" +
                    f"\n\nAsk the applicant a series of questions based on the job and the interviewer's personality. The questions should be a mix of general questions to determine the applicant's ability to perform the a job in that field and more specific questions pertaining to the job itself. Don't be afraid to ask creative questions or throw curveballs to gauge the applicant's personality." +
                    f"\nExample questions for a job in accounting:\nHow did you learn about our organization and this job opportunity?\nWhy do you think this role is appropriate for you?\nCan you give a few examples of other similar work that you have done?\nHow do you learn best?\nWhat would your past coworkers or peers say if I were to call them to ask about your qualifications for this position?\nHave you ever been terminated for cause by an employer?\nConvince me that I am sitting across from the best candidate for this position."
                )
                sysmes_end = "\n\nSystem: Start the interview. Introduce yourself and greet the applicant. Act according to your personality."
                st.session_state['chat_history'] = "" #Wipes the chat history
                prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                add_log("\n<prompt>" + prompt + "\n</prompt>")
                #AI sends a new "greeting" message sort of thing
                print("Completion 3b")  #completion
                completion = get_response(prompt)
                print("new greeting = " + completion)
                st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                st.session_state["generated"].append(completion)
                print("appended new greeting")
                st.session_state['interview_phase'] = 4

            def phase_4() : 
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
                    sysmes_end = "\n\nSystem: Conduct a realistic interview with the applicant. Ask a total of " + str(st.session_state['msg_count']) + "questions, one question per message. Do not end the interview yet. Stay in character as the interviewer."
                    prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                    print("Completion 4a")  #completion
                    completion = get_response(prompt)
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
            
            def phase_5() : 
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
                    completion = get_response(prompt)
                    st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                    st.session_state["generated"].append(completion)
                    st.session_state['interview_phase'] = 6
                    add_log(
                        "===================DEBUG=================="+
                        "\n<prompt>" + prompt + "\n</prompt>" +
                        "\n<completion>\n" + completion + "\n</completion>"
                        )

            def phase_6() : 
                # ================ PHASE 6 =====================
                    print("Phase 6")
                    #Begin the interview and ask questions
                    sysmes_start = (    # Removes the interviewer persona from the start prompt. Keeps the job description for review.
                        "\nJob description:\n" + st.session_state['job_desc']
                    )
                    sysmes_end = "\n\nSystem: End of interview. Summarize the interview based on the applicant's replies. Provide constructive criticism and feedback. Point out what they did well, what their weaknesses were, and how they can improve. At the end, rate their interview out of 10 and state if they would have got the job. Be completely transparent and honest."
                    prompt = instruction + sysmes_start + st.session_state['chat_history'] + sysmes_end + anthropic.AI_PROMPT
                    #AI sends a new "greeting" message sort of thing
                    print("Completion 6a")  #completion
                    completion = get_response(prompt)
                    st.session_state['chat_history'] += anthropic.AI_PROMPT + " " + completion
                    st.session_state["generated"].append(completion)
                    add_log(
                        "===================DEBUG=================="+
                        "\n<prompt>" + prompt + "\n</prompt>" +
                        "\n<completion>\n" + completion + "\n</completion>"
                        )

            if submit_button and user_input:
                instruction = anthropic.HUMAN_PROMPT + " In this scenario we will roleplay a job interview. Your task is to help me improve my interviewing skills. You will act as the interviewer and will remain in character throughout the entire session."
                if st.session_state['interview_phase'] == 0:  
                    st.session_state['chat_history'] += (anthropic.AI_PROMPT + " " + greeting) #adds the greeting to the chat history
                    if st.session_state.resume : 
                        st.session_state['chat_history'] += (anthropic.HUMAN_PROMPT + "Here is my resume: " + "[" + st.session_state.resume + "\n" + "]" )
                        st.write(st.session_state.chat_history)
                    st.session_state['interview_phase'] = 1
                st.session_state['chat_history'] += anthropic.HUMAN_PROMPT + " " + user_input #add user input to chat history
                st.session_state['past'].append(user_input)
                
                if st.session_state['interview_phase'] == 6: 
                    phase_6()
                if st.session_state['interview_phase'] == 5: 
                    phase_5()
                if st.session_state['interview_phase'] == 4: 
                    phase_4()
                if st.session_state['interview_phase'] == 3: 
                    phase_3()
                if st.session_state['interview_phase'] == 1: 
                    phase_1()

if debug_mode :
    st.text("message count: " + str(st.session_state.msg_count))
    st.text("interview phase: " + str(st.session_state.interview_phase))                       

with response_container:
    message(greeting) #initial greeting added
    if st.session_state["generated"]:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))