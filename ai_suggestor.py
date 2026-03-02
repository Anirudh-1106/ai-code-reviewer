from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

code_string = """
def calculate_sum(a, b):
    result = a + b
    if result > 10:
        print("Greater than 10")
    else:
        print("Less than or equal to 10")
    return result
"""

prompt = PromptTemplate(
    input_variables=["code_string"],
    template=
        "You are an experienced coding teacher, so generate the suggestions based on the given code for the student.\n"
        "Also, not just give suggestions but explain WHY you are suggesting them.\n"
        "Explain errors like time complexity, space complexity, etc.\n"
        "Code:\n{code_string}"
)

def get_ai_suggestion(code_string):
    final_prompt = prompt.format(code_string=code_string)
    result = model.invoke(final_prompt)
    print(result.content)

get_ai_suggestion(code_string)
