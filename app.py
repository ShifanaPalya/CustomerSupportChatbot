import autogen
from autogen import config_list_from_json
from autogen  import AssistantAgent, UserProxyAgent
import groq
import json
import panel as pn
from panel.chat import ChatInterface
import asyncio
# pn.extension("perspective")


config_list = autogen.config_list_from_json("./OAI_CONFIG_LIST")


with open("model_config.json", "r") as file:
        llm_config = json.load(file)

llm_config["config_list"] = config_list

input_future = None

class MyConversableAgent(autogen.ConversableAgent):

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        print('***Inside a_get_human_input function***')  
        chat_interface.send(prompt, user="System", respond=False)
        # Create a new Future object for this input operation if none exists
        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        # Wait for the callback to set a result on the future
        await input_future

        # Once the result is set, extract the value and reset the future for the next input operation
        input_value = input_future.result()
        input_future = None
        return input_value

#Initialize UserProxyAgent
user_proxy_agent = MyConversableAgent(
    name="user_proxy_agent",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    }
)

#Initialize AssistantAgent
assistant_agent = AssistantAgent(
    name="assistant_agent",
    system_message="""You are an intelligent customer service agent. You will be answering the customer queries only if you
    know the answer to it else you will be responding with I am not sure of that, I'll escalate this issue to our support team. If you 
    have any questions to ask the customer, ask only at the end.
    Reply TERMINATE if the task has been solved at full satisfaction.""",
    llm_config=llm_config,
)

# user_proxy_agent.initiate_chat(assistant_agent,
#                                message="My refrigerator is not cooling. I could see only the light. Please help!")


def print_messages(recipient, messages, sender, config):

    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

    content = messages[-1]['content']

    if all(key in messages[-1] for key in ['name']):
        chat_interface.send(content, user=messages[-1]['name'], respond=False)
    else:
        chat_interface.send(content, user=recipient.name, respond=False)
    
    return False, None  # required to ensure the agent communication flow continues

user_proxy_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

assistant_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

pn.extension(design="material")

initiate_chat_task_created = False

async def delayed_initiate_chat(agent, recipient, message):

    global initiate_chat_task_created
    # Indicate that the task has been created
    initiate_chat_task_created = True

    # Wait for 2 seconds
    await asyncio.sleep(2)

    # Now initiate the chat
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    
    global initiate_chat_task_created
    global input_future

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(user_proxy_agent, assistant_agent, contents))

    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("There is currently no input being awaited.")


chat_interface = ChatInterface(callback=callback)
chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()


