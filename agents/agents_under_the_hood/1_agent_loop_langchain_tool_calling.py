from dotenv import load_dotenv
import os

load_dotenv("C:/Users/user/Documents/DeepLearning-Indepth/agents/agents_under_the_hood/.env")
from langchain.chat_models import init_chat_model
from langchain.tools import tool 
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langsmith import traceable

MAX_ITERATIONS = 10
MODEL = "gpt-5"

prices = {"laptop": 1299.99, "headphones": 149.95, "keyboard": 89.99}



# -- Tools (Langchain @tool decorator) ----
@tool
def get_product_price(product: str) -> float:
    """Lookup the price of a product in the catalog"""
    print(f"   > Execution get_product_price(product='{product})")
    global prices
    return prices.get(product, 0)

@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price and return the final price.
    Available tiers: bronze, silver, gold."""
    print(f"    >> Executing apply_discount(price={price}, discount_tier='{discount_tier}')")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)

@traceable(name="Langchain Agent Loop")
def run_agent(question: str):
    tools = [get_product_price, apply_discount]
    tools_dict = {t.name: t for t in tools}

    llm = init_chat_model(model=MODEL)
    llm_with_tools = llm.bind_tools(tools)
    print(f"Question: {question}")
    print("=" * 60)
    messages = [
        SystemMessage(
            content=(
                "You are a helpful shopping assistant. "
                "You have access to a product catalog tool "
                "and a discount tool.\n\n"
                "STRICT RULES — you must follow these exactly:\n"
                "1. NEVER guess or assume any product price. "
                "You MUST call get_product_price first to get the real price.\n"
                "2. Only call apply_discount AFTER you have received "
                "a price from get_product_price. Pass the exact price "
                "returned by get_product_price — do NOT pass a made-up number.\n"
                "3. NEVER calculate discounts yourself using math. "
                "Always use the apply_discount tool.\n"
                "4. If the user does not specify a discount tier, "
                "ask them which tier to use — do NOT assume one."
            )
        ),
        HumanMessage(content=question),
    ]
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(F"\n ----- Iteration {iteration} ------ ")
        ai_message = llm_with_tools.invoke(messages)
    
        tool_calls = ai_message.tool_calls
        if not tool_calls:
            print(f"\nFinal Answer: {ai_message.content}")
            return ai_message.content
        tool_call = tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")

        print(f"  [Tool selected] {tool_name} with args: {tool_args}")

        tool_to_use = tools_dict.get(tool_name)
        if not tool_to_use:
            raise ValueError(f"Tool {tool_name} not found")
        observation = tool_to_use.invoke(tool_args)
        print(f"Tool result: {observation}")

        messages.append(ai_message)
        messages.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call_id)
        )

    print("ERROR: Max iterations reached without a final answer")
    return None


if __name__ == "__main__":
    print("Langchain agent with Binding tools working already")
    print()
    result = run_agent("What is the price of laptop after applying a gold discount?")

