import os
import openai, json, time
import streamlit as st
from tqdm import tqdm
import re
from http import HTTPStatus
import requests
from audiorecorder import audiorecorder
from speech2text import speech2text
import dashscope
from pydub import AudioSegment

dashscope.api_key = "sk-607a763a57f44b4f8b8572c7d1e7d142"


file_path = "audio_len.txt"

# temp_prompt=""""""
#     '你是一位专业的心理助手，由HFUT-MACLab团队开发，你的名字是：小源。你具有丰富的专业心理知识、强烈的同理心、高超的心理引导技能，能够精准识别来访者的情绪，倾听其心理困惑，引导其认知改变，提供专业的咨询建议。'

# Function to read the audio_len value from the file
def read_audio_len(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return int(file.read())
    else:
        return 0


# Function to write the audio_len value to the file
def write_audio_len(file_path, audio_len):
    with open(file_path, "w") as file:
        file.write(str(audio_len))


def decode(res):
    return res.encode("utf-8").decode("utf-8")


def request_KimiChat(message, temperature=0.3) -> str:
    """
    使用requests库调用Moonshot AI的API与Kimi进行聊天。

    :param message: 对话内容
    :param temperature: 用于控制回答的随机性，范围从0到1。
    :return: Kimi的回答。
    """
    url = "https://api.moonshot.cn/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer sk-VZJKcHjsuKSr4dPX8tiyXZvNFXYTcHtfPWUaCMO7TYMr4aTa",
    }
    print(headers, url)
    data = {"model": "moonshot-v1-8k", "messages": message, "temperature": temperature}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        completion = response.json()
        print(completion)
        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {e}"


# def makerequest(prompt, request_sdk="dashscope", stream=False, role="user"):
#     try:
#         print("当前使用的模型", option)
#         history = [{"role": "user", "content": prompt}]
#
#
#         if option == "Baichuan2-13B-Chat":
#             openai.api_base = "http://793b3d41.r9.cpolar.top/v1"
#             openai.api_key = "none"
#             model = "Baichuan2-13B-Chat"
#             response = openai.ChatCompletion.create(
#                 model=model, messages=history, temperature=0.95, stream=stream
#             )
#             if stream:
#                 return response
#         elif option == "Qwen1.5-7B-Chat":
#             openai.api_base = "https://856e9b1.r16.vip.cpolar.cn/v1"
#             openai.api_key = "none"
#             model = "/data/lixubin/MiraAgent-server/temp_full/"
#             response = openai.ChatCompletion.create(
#                 model=model, messages=history, temperature=0.95, stream=stream
#             )
#             if stream:
#                 return response
#         elif option == "default":
#             return request_KimiChat(history)
#         elif option == "Qwen1.5-14B":
#             model = "/data/hujinpeng/workspace/Qwen/qwen1.5-14B-Chat-6-14/Qwen1.5-14B-Chat"
#             from openai import OpenAI
#             client = OpenAI(
#                 api_key="none",
#                 base_url="http://6ddbf7f2.r19.cpolar.top/v1"
#             )
#             response = client.chat.completions.create(
#                 model=model, messages=history, temperature=0.1, stream=False
#             )
#             if stream:
#                 return response
#         elif option == "PsycoLLMv1":
#             # openai.api_base = "https://73840636.r27.cpolar.top/v1/"
#             # openai.api_key = "none"
#
#             # model = "/data/hujinpeng/workspace/v2/v2"
#             # response = openai.ChatCompletion.create(
#             #     model=model, messages=history, temperature=0.95, stream=False
#             # )
#             #
#             # 'https://176ead1a.r19.cpolar.top'
#
#             # base_url = 'http://227b84d9.r26.cpolar.top/v1'
#             # model_name = "/data/hujinpeng/workspace/Qwen-14B-sft/all_data/checkpoint-2589"
#
#             base_url = 'http://72554a24.r5.cpolar.cn/v1'
#             model_name = "/data/hujinpeng/workspace/Qwen-32B-sft/QAs+ds+dialogue/checkpoint-474-merge"
#
#             from openai import OpenAI
#             client = OpenAI(
#                 api_key="none",
#                 base_url=base_url
#             )
#             response = client.chat.completions.create(
#                 model=model_name, messages=history, temperature=0.1, stream=False
#             )
#             print('*'*50)
#             print("PsycoLLMv1 used")
#             if stream:
#                 return response
#         elif option == "PsycoLLMv2":
#             # openai.api_base = "http://llmsapi.vip.cpolar.cn/v1"
#             # openai.api_key = "none"
#             # model = "/data/zonepg/models/Qwen/Qwen1.5-32B-LoRA"
#             # response = openai.ChatCompletion.create(
#             #     model=model, messages=history, temperature=0.95, stream=False
#             # )
#             # if stream:
#             #     return response
#
#             model='/data/hujinpeng/workspace/trained_model/checkpoint-1940'
#             from openai import OpenAI
#             client = OpenAI(
#                 api_key="none",
#                 base_url="https://f35fa83.r16.cpolar.top/v1/"
#             )
#             response = client.chat.completions.create(
#                 model=model, messages=history, temperature=0.1, stream=False
#             )
#             print('*' * 50)
#             print("PsycoLLMv2 used")
#             if stream:
#                 return response
#
#
#         else:
#             return request_KimiChat(history)
#
#         res = decode(response.choices[0].message.content)
#         return res
#     except Exception as e:
#         res = "wrong!"
#         print(e)

def makerequest(history, request_sdk="dashscope", stream=False, role="user"):
    try:
        print("当前使用的模型", option)

        if option == "Baichuan2-13B-Chat":
            openai.api_base = "http://793b3d41.r9.cpolar.top/v1"
            openai.api_key = "none"
            model = "Baichuan2-13B-Chat"
            response = openai.ChatCompletion.create(
                model=model, messages=history, temperature=0.95, stream=stream
            )
            if stream:
                return response
        elif option == "Qwen1.5-7B-Chat":
            openai.api_base = "https://856e9b1.r16.vip.cpolar.cn/v1"
            openai.api_key = "none"
            model = "/data/lixubin/MiraAgent-server/temp_full/"
            response = openai.ChatCompletion.create(
                model=model, messages=history, temperature=0.95, stream=stream
            )
            if stream:
                return response
        elif option == "default":
            return request_KimiChat(history)
        elif option == "Qwen1.5-14B":
            model = "/data/hujinpeng/workspace/Qwen/qwen1.5-14B-Chat-6-14/Qwen1.5-14B-Chat"
            from openai import OpenAI
            client = OpenAI(
                api_key="none",
                base_url="http://6ddbf7f2.r19.cpolar.top/v1"
            )
            response = client.chat.completions.create(
                model=model, messages=history, temperature=0.1, stream=False
            )
            if stream:
                return response


        # elif option == "PsycoLLMv1":
        #     # openai.api_base = "https://73840636.r27.cpolar.top/v1/"
        #     # openai.api_key = "none"
        #
        #     # model = "/data/hujinpeng/workspace/v2/v2"
        #     # response = openai.ChatCompletion.create(
        #     #     model=model, messages=history, temperature=0.95, stream=False
        #     # )
        #     #
        #     # 'https://176ead1a.r19.cpolar.top'
        #
        #     # base_url = 'http://227b84d9.r26.cpolar.top/v1'
        #     # model_name = "/data/hujinpeng/workspace/Qwen-14B-sft/all_data/checkpoint-2589"
        #
        #     base_url = 'http://psycollm.vip.cpolar.cn/v1'
        #     model_name = "/data/hujinpeng/workspace/Qwen-32B-sft/QAs+ds+dialogue/checkpoint-474-merge"
        #
        #     from openai import OpenAI
        #     client = OpenAI(
        #         api_key="none",
        #         base_url=base_url
        #     )
        #     response = client.chat.completions.create(
        #         model=model_name, messages=history, temperature=0.1, stream=False
        #     )
        #     print('*'*50)
        #     print("PsycoLLMv1 used")
        #     if stream:
        #         return response

        elif option == "PsycoLLMv1":
            base_url = 'http://psycollm.vip.cpolar.cn/v1'
            model_name = "/data/hujinpeng/workspace/Qwen-32B-sft/QAs+ds+dialogue/checkpoint-474-merge"

            from openai import OpenAI
            client = OpenAI(
                api_key="none",
                base_url=base_url
            )
            response = client.chat.completions.create(
                model=model_name, messages=history, temperature=0.1, stream=False
            )
            print('*' * 50)
            print("PsycoLLMv1 used")
            if stream:
                return response

        elif option == "PsycoLLMv2":
            model = '/data/hujinpeng/workspace/trained_model/checkpoint-1940'
            from openai import OpenAI
            client = OpenAI(
                api_key="none",
                base_url="https://f35fa83.r16.cpolar.top/v1/"
            )
            response = client.chat.completions.create(
                model=model, messages=history, temperature=0.1, stream=False
            )
            print('*' * 50)
            print("PsycoLLMv2 used")
            if stream:
                return response

        else:
            return request_KimiChat(history)

        res = decode(response.choices[0].message.content)
        return res
    except Exception as e:
        res = "wrong!"
        print(e)


with open("chatdemo.json", "rb") as f:
    chatprompt = json.load(f)


def score_prompt_build(text, system_prompt, question):
    """
    text:用户回复的内容
    system_prompt:系统的prompt[optional]
    question:提问
    """
    return f"你是一位专业的心理咨询助手，请依据患者的回答内容，仅输出该项得分结果。用户回答没有，表示无此症状。【提问内容：{question}\n用户回答：{text}。】\n格外注意：根据症状程度分为【0:无、1:轻度、2:中度、3:较重、4:重度】。"


# def question_build(topic, last_topic, last_response, identification):
#     """
#     topic:用户回复的内容
#     system_prompt:系统的prompt[optional]
#     """
#     # print(topic,last_topic,last_response)
#     return f"你是一位专业的心理咨询助手，能够结合汉密尔顿焦虑量表与用户进行访谈。首先对用户的上个问题的回答表示理解与支持，并针对{topic}这一项目进一步访谈提问。格外注意：问题描述符合用户身份：{identification},每次提问不超过150字。上个问题：{last_topic}，用户回答：{last_response}."


def question_build(topic, last_topic, last_response, identification):
    """
    topic:用户回复的内容
    system_prompt:系统的prompt[optional]
    """

    # _prompt = f"你是一位专业的心理咨询助手，能够结合汉密尔顿焦虑量表与用户进行访谈。首先对用户的上个问题的回答表示理解与支持，并针对{topic}这一项目进一步访谈提问。格外注意：问题描述符合用户身份：{identification},每次提问不超过150字。上个问题：{last_topic}，用户回答：{last_response}."

    # _prompt = f"""你是一位专业的心理咨询助手，首先对用户的上个问题的回答表示理解与支持,给出一些共情的回复，
    #            上个问题的主题是{last_topic}，用户的回答为{last_response}.
    #            下一步将针对{topic}这一项目进一步访谈提问。
    #            格外注意：问题描述符合用户身份：{identification},每次提问不超过150字。
    #            下面给几个可以提问的问题：
    #            {chatprompt[topic][0]}
    #            {chatprompt[topic][1]}
    #            {chatprompt[topic][2]}
    #            """

    _prompt = f"""你是专业的心理咨询助手小源，能够共情地与用户沟通。
               上个问题的主题：{last_topic}，用户的回答：{last_response}。
               首先对用户的上个问题的回答给予一定的反馈,给出一些共情的回复。
               下一步将针对{topic}这一项目进一步访谈提问,请提出问题
               格外注意：问题描述符合用户身份：{identification},每次提问不超过150字。
               例如你可以提出以下问题：
                {chatprompt[topic][0]}
                {chatprompt[topic][1]}
               """
    # print(topic,last_topic,last_response)
    return _prompt

def single_question_build(topic):
    """
    topic:用户回复的内容
    system_prompt:系统的prompt[optional]
    """
    return f"你是一位专业的心理咨询助手，能够结合汉密尔顿焦虑量表与用户进行访谈。现在需要你针对{topic}这一项向用户提问一个问题，并提示用户详细描述症状。格外注意：提问不超过150字"

# def single_question_build(topic):
#     """
#     topic:用户回复的内容
#     system_prompt:系统的prompt[optional]
#     """
#     print('topic',topic)
#     # _prompt = f"""
#     #             你是一位专业的心理咨询助手小源，需要了解用户关于{topic}的信息，根据{topic}提问用户一个相关的问题，用于了解用户在{topic}的情况。
#     #             格外注意：你当前不知道用户关于{topic}的信息，提问不超过150字
#     #             下面给几个可以提问的问题：
#     #             {chatprompt[topic][0]}
#     #             {chatprompt[topic][1]}
#     #             {chatprompt[topic][2]}
#     #             """
#
#     _prompt = f"""你是专业的心理咨询助手小源，能够共情地与用户沟通。针对{topic}这一项目进一步访谈提问,请提出问题
#                格外注意：每次提问不超过150字。
#                 例如，你可以向你的用户提出以下问题：
#                 {chatprompt[topic][0]}
#                 {chatprompt[topic][1]}
#                 {chatprompt[topic][2]}
#                 """
#     # _prompt = f"""
#     #             说一个笑话
#     #             """
#     return _prompt


def total_score(scores):
    total_score = 0
    # print(scores,len(scores))
    for score in scores:
        numbers = re.findall(r"\d+", score)
        if len(numbers) > 0:
            number = int(numbers[0])
        else:
            number = 0
        total_score += number
    return total_score


def get_number(text):
    numbers = re.findall(r"\d+", text)
    if len(numbers) > 0:
        number = int(numbers[0])
    else:
        number = 0
    return number


def build_conclusion_prompt(responses, questions, topics, system_prompt=""):
    """
    responses:用户回复
    questions:问题
    system_prompt:系统prompt
    topics:主题
    scores:评分
    """
    history = ""
    i = 1

    for response, question, topic in tqdm(zip(responses, questions, topics)):
        history += (
            f"对于第{i}个项有关{topic}方面，心理医生提问{question},患者回答{response}"
        )
        i += 1
    return f"你是一位专业的心理咨询助手，请根据心理访谈对话历史{history},输出我的主述症状摘要。"


def build_advice_prompt(responses, questions, topics, system_prompt=""):
    """
    responses:用户回复
    questions:问题
    system_prompt:系统prompt
    topics:主题
    scores:评分
    """
    history = ""
    i = 1

    for response, question, topic in tqdm(zip(responses, questions, topics)):
        history += (
            f"对于第{i}个项有关{topic}方面，心理医生提问{question},患者回答{response}"
        )
        i += 1
    return f"你是一位专业的心理咨询助手，请根据心理访谈对话历史{history},生成个性化针对性的建议。"


def build_table(topics, scores):
    table = "|序号|项目|得分|\n|----|----|----|\n"
    i = 1
    for topic, score in tqdm(zip(topics, scores)):
        table += f"|{i}|{topic}|{get_number(score)}分|\n"
        i += 1
    return table


def build_summary_prompt(
    topics, scores, conclusion, system_prompt="", table="", advice=""
):
    """
    responses:用户回复
    questions:问题
    system_prompt:系统prompt
    topics:主题
    scores:评分
    """
    scorelist = ""
    i = 1
    totalscore = total_score(scores)
    # print("评分列表：",scores)

    for topic, score in tqdm(zip(topics, scores)):
        scorelist += f"{i}.{topic}：{get_number(score)}分；\n"
        i += 1
    zhengzhuang = "没有焦虑"
    if totalscore >= 29:
        zhengzhuang = "严重焦虑"
    elif totalscore >= 21:
        zhengzhuang = "重度焦虑"
    elif totalscore >= 14:
        zhengzhuang = "中度焦虑"
    elif totalscore >= 7:
        zhengzhuang = "轻度焦虑"
    print(table)

    return f"""# 量表

**1. 测评得分表:**

{table}

总得分：{totalscore}

**2. 分析结论：**

您的总分是 {totalscore}，属于 {zhengzhuang}，{conclusion}

**3. 报告建议：**

{advice}
"""


prompt_topics = list(chatprompt.keys())
total_questions = len(prompt_topics)
st.title("💬 Chatbot demo")
# option = st.selectbox(
#     "How would you like to chat with?", ("default", "PsycoLLMv1", "PsycoLLMv2"), index=0
# )

option = st.selectbox(
    "How would you like to chat with?", ("default", "PsycoLLMv1"), index=1
)

if "messages" not in st.session_state:
    question = "您好, 我是您的专属心理助手小源,很高兴在这里与你交流。请注意, 这只是一个初步的筛查, 不能代替正规的精神科诊断和治疗。 首先为了评估的准确性，我想收集您的基本信息：年龄、性别、职业，如果可以，我们开始吧。"


    st.session_state["messages"] = [{"role": "assistant", "content": f"{question}"}]
    st.session_state["questions"] = []
    st.session_state["responses"] = []
    # st.session_state["scores"] = []
    # st.session_state["topics"] = []
    st.session_state["identification"] = ""

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    if st.session_state["identification"] == "":
        st.session_state["identification"] = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
    else:
        st.session_state["responses"].append(prompt)

    history = st.session_state["messages"]
    response = makerequest(history, stream=False, role="assistant")
    st.chat_message("assistant").write(response)
    st.session_state["messages"].append({"role": "assistant", "content": response})

# if prompt := st.chat_input():
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     st.chat_message("user").write(prompt)
#
#     if (
#         st.session_state["identification"] == ""
#         and len(st.session_state["questions"]) == 0
#     ):
#         st.session_state["identification"] = prompt
#     else:
#         st.session_state["responses"].append(prompt)
#
#     history = st.session_state["messages"]
#     question = makerequest(history, stream=False, role="assistant")
#     st.chat_message("assistant").write(question)
#     st.session_state["questions"].append(question)
#     st.session_state["topics"].append(prompt_topics[len(st.session_state["questions"]) - 1])
#     st.session_state.messages.append({"role": "assistant", "content": f"{question}"})
#
#     if len(st.session_state["questions"]) >= len(prompt_topics):
#         st.chat_message("assistant").write(
#             "感谢你的真诚配合，接下来我将为您输出一份心理初筛报告。结果仅供参考，不作为医学诊断依据。生成报告可能需要较长时间，请稍等。"
#         )
#         history = st.session_state["messages"]
#         summary_response = makerequest(history, stream=False, role="assistant")
#
#         st.session_state.messages.append(
#             {"role": "assistant", "content": f"{summary_response}"}
#         )
#         st.chat_message("assistant").write(summary_response)

        # table = build_table(st.session_state["topics"], st.session_state["scores"])
        # st.session_state.messages.append(
        #     {"role": "assistant", "content": f"{summary_response}"}
        # )
        # st.session_state.messages.append(
        #     {"role": "assistant", "content": table}
        # )
        # st.chat_message("assistant").write(summary_response)
        # st.chat_message("assistant").write(table)



# if prompt := st.chat_input():
#     if (
#         st.session_state["identification"] == ""
#         and len(st.session_state["questions"]) == 0
#     ):
#         st.session_state["identification"] = prompt
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.chat_message("user").write(prompt)
#         question_prompt = single_question_build(prompt_topics[0])
#         print('question_prompt',len(st.session_state["questions"]), question_prompt)
#         question = makerequest(question_prompt, stream=False, role="assistant")
#         st.chat_message("assistant").write(question)
#         st.session_state["questions"].append(question)
#         st.session_state["topics"].append(prompt_topics[0])
#         st.session_state.messages.append(
#             {"role": "assistant", "content": f"{question}"}
#         )
#     else:
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.chat_message("user").write(prompt)

#         now_index = len(st.session_state["questions"])
#         score_prompt = score_prompt_build(
#             prompt, "", st.session_state["questions"][-1]
#         )  # 用户回复以及最后一个问题
#         score = makerequest(score_prompt)
#         # print("score:",score,"score prompt:",score_prompt)
#         st.session_state["scores"].append(score)
#         st.session_state["responses"].append(prompt)
#
#         if len(st.session_state["questions"]) >= len(prompt_topics):
#             # 进行总结
#             st.chat_message("assistant").write(
#                 "感谢你的真诚配合，接下来我将为您输出一份心理初筛报告。结果仅供参考，不作为医学诊断依据。生成报告可能需要较长时间，请稍等。"
#             )
#             conculsion_prompt = build_conclusion_prompt(
#                 st.session_state["responses"],
#                 st.session_state["questions"],
#                 st.session_state["topics"],
#             )
#             conclusion = makerequest(conculsion_prompt)
#             table = build_table(st.session_state["topics"], st.session_state["scores"])
#             advice_prompt = build_advice_prompt(
#                 st.session_state["responses"],
#                 st.session_state["questions"],
#                 st.session_state["topics"],
#             )
#             advice = makerequest(advice_prompt)
#             summary_prompt = build_summary_prompt(
#                 st.session_state["topics"],
#                 st.session_state["scores"],
#                 conclusion,
#                 "",
#                 advice=advice,
#                 table=table,
#             )
#             # query_res = makerequest(summary_prompt,stream=False,role="assistant")
#             # print(summary_prompt)
#             query_res = summary_prompt
#             st.session_state.messages.append(
#                 {"role": "assistant", "content": f"{query_res}"}
#             )
#             st.chat_message("assistant").write(query_res)
#             # print(st.session_state["messages"])
#         else:
#
#             question_prompt = question_build(
#                 prompt_topics[now_index],
#                 st.session_state["topics"][-1],
#                 st.session_state["responses"][-1],
#                 st.session_state["identification"],
#             )
#             print('question_prompt', len(st.session_state["questions"]), question_prompt)
#             question = makerequest(question_prompt, stream=False, role="assistant")
#             st.chat_message("assistant").write(question)
#             st.session_state["questions"].append(question)
#             st.session_state["topics"].append(prompt_topics[now_index])  # 这里更新topic
#             st.session_state.messages.append(
#                 {"role": "assistant", "content": f"{question}"}
#             )




audio = AudioSegment.empty()
audio = audiorecorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    pause_prompt="",
    show_visualizer=True,
    key=None,
)
print("ceshi0.1")
print(type(audio))
print(len(audio))
audio_len = read_audio_len(file_path)
print(audio_len)
if len(audio) > 0 and len(audio) != audio_len:
    print("ceshi1")
    audio.export("audio.wav", format="wav", parameters=["-ar", "16000"])
    print("ceshi1.1")

    result, status = speech2text("audio.wav")
    edited_text = st.text_area(
        "Edit the transcribed text before submitting:",
        result,
        label_visibility="collapsed",
    )

    if st.button("Submit"):
        prompt = edited_text
        edited_text = None
        result = None
        audio_len = len(audio)
        write_audio_len(file_path, audio_len)
        print("ceshi2")
        if (
            st.session_state["identification"] == ""
            and len(st.session_state["questions"]) == 0
        ):
            st.session_state["identification"] = prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            question_prompt = single_question_build(prompt_topics[0])
            # print(question_prompt)
            question = makerequest(question_prompt, stream=False, role="assistant")
            st.chat_message("assistant").write(question)
            st.session_state["questions"].append(question)
            st.session_state["topics"].append(prompt_topics[0])
            st.session_state.messages.append(
                {"role": "assistant", "content": f"{question}"}
            )
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            now_index = len(st.session_state["questions"])
            score_prompt = score_prompt_build(
                prompt, "", st.session_state["questions"][-1]
            )  # 用户回复以及最后一个问题
            score = makerequest(score_prompt)
            # print("score:",score,"score prompt:",score_prompt)
            st.session_state["scores"].append(score)
            st.session_state["responses"].append(prompt)

            if len(st.session_state["questions"]) >= len(prompt_topics):
                # 进行总结
                st.chat_message("assistant").write(
                    "感谢你的真诚配合，接下来我将为您输出一份心理初筛报告。结果仅供参考，不作为医学诊断依据。生成报告可能需要较长时间，请稍等。"
                )
                conculsion_prompt = build_conclusion_prompt(
                    st.session_state["responses"],
                    st.session_state["questions"],
                    st.session_state["topics"],
                )
                conclusion = makerequest(conculsion_prompt)
                table = build_table(
                    st.session_state["topics"], st.session_state["scores"]
                )
                advice_prompt = build_advice_prompt(
                    st.session_state["responses"],
                    st.session_state["questions"],
                    st.session_state["topics"],
                )
                advice = makerequest(advice_prompt)
                summary_prompt = build_summary_prompt(
                    st.session_state["topics"],
                    st.session_state["scores"],
                    conclusion,
                    "",
                    advice=advice,
                    table=table,
                )
                # query_res = makerequest(summary_prompt,stream=False,role="assistant")
                # print(summary_prompt)
                query_res = summary_prompt
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"{query_res}"}
                )
                st.chat_message("assistant").write(query_res)
                # print(st.session_state["messages"])
            else:

                question_prompt = question_build(
                    prompt_topics[now_index],
                    st.session_state["topics"][-1],
                    st.session_state["responses"][-1],
                    st.session_state["identification"],
                )

                question = makerequest(question_prompt, stream=False, role="assistant")
                st.chat_message("assistant").write(question)
                st.session_state["questions"].append(question)
                st.session_state["topics"].append(
                    prompt_topics[now_index]
                )  # 这里更新topic
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"{question}"}
                )
    else:
        st.write(result)


# questions = []
# responses = []
# scores = []
# topics = []

# for key in list(chatprompt.keys()):
#     question_prompt = question_build(key,chatprompt[key])
#     question = makerequest(question_prompt)
#     topics.append(key)
#     print("AI: ",question)
#     response = input("Human: ")
#     score_prompt = score_prompt_build(response,"",question)
#     # print(score_prompt)
#     score = makerequest(score_prompt)
#     print("score:",score)
#     questions.append(question)
#     responses.append(response)
#     scores.append(score)
# summary_prompt = build_summary_prompt(responses,questions,topics,scores,"")
# print(makerequest(summary_prompt))
