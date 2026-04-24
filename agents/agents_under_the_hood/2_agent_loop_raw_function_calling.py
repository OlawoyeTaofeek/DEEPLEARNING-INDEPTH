from dotenv import load_dotenv

load_dotenv("C:/Users/user/Documents/DeepLearning-Indepth/agents/agents_under_the_hood/.env")

import openai
from langsmith import traceable
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_ITERATIONS = 10
MODEL = "gpt-5"
import json 

@traceable(run_type="tool")
def get_product_price(product: str) -> float:
    """Look up the price of a product in the catalog."""
    print(f"    >> Executing get_product_price(product='{product}')")
    prices = {"laptop": 1299.99, "headphones": 149.95, "keyboard": 89.50}
    return prices.get(product, 0)


@traceable(run_type="tool")
def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price and return the final price.
    Available tiers: bronze, silver, gold."""
    print(f"    >> Executing apply_discount(price={price}, discount_tier='{discount_tier}')")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)

tools = [
    {
        "type": "function",
        "name": "get_product_price",
        "description": "Look up the price of a product in the catalog.",
        "parameters": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "The product name, e.g. 'laptop', 'headphones', 'keyboard'",
                },
            },
            "required": ["product"],
        },
    },
    {
        "type": "function",
        "name": "apply_discount",
        "description": "Apply a discount tier to a price and return the final price. Available tiers: bronze, silver, gold.",
        "parameters": {
            "type": "object",
            "properties": {
                "price": {
                    "type": "number",
                    "description": "The original price",
                },
                "discount_tier":{
                    "type": "string",
                    "description": "The discount tier: 'bronze', 'silver', or 'gold'",                    
                }
            },
            "required": ["price", "discount_tier"],
        },
    },
]

@traceable(name="OpenAI Chat", run_type="llm")
def openai_chat_traced(messages):
    return client.responses.create(
        model="gpt-4",
        tools=tools,
        input=messages,
    )

@traceable(name="OpenAI Agent Loop")
def run_agent(question: str):

    messages = [
        {
            "role": "system",
            "content": (
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
            ),
        },
        {"role": "user", "content": question},
    ]

    response = openai_chat_traced(messages)

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")

        tool_call = next(
            (item for item in response.output if item.type == "function_call"),
            None
        )

        if not tool_call:
            # final answer
            for item in response.output:
                if item.type == "message":
                    return item.content[0].text

        name = tool_call.name
        args = json.loads(tool_call.arguments)

        print(f"[Tool Call] {name} -> {args}")

        if name == "get_product_price":
            result = get_product_price(**args)
        if name == "apply_discount":
            result = apply_discount(**args)

        print(f"[Tool Result] {result}")

        # 🔥 CRITICAL: chain with previous_response_id
        messages.append(
            {
              "type": "function_call_output",
              "call_id": tool_call.call_id,
              "output": str(result)
            }
        )

    raise RuntimeError("Max iterations reached")
        


if __name__ == "__main__":
    print("Langchain agent with Binding tools working already")
    print()
    result = run_agent("What is the price of laptop after applying a gold discount?")