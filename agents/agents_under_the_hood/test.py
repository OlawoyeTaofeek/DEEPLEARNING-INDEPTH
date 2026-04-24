import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langsmith import traceable, Client

# Initialize 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"

# --- Tools with @traceable ---

@traceable(run_type="tool")
def get_product_price(product: str) -> float:
    """Look up the price of a product in the catalog."""
    print(f"    >> Executing get_product_price(product='{product}')")
    prices = {"laptop": 1299.99, "headphones": 149.95, "keyboard": 89.50}
    return prices.get(product.lower(), 0.0)

@traceable(run_type="tool")
def apply_discount(price: float, discount_tier: str) -> float:
    """Apply a discount tier to a price."""
    print(f"    >> Executing apply_discount(price={price}, discount_tier='{discount_tier}')")
    discount_percentages = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentages.get(discount_tier.lower(), 0)
    return round(price * (1 - discount / 100), 2)

# --- Tool Schemas ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "Look up the price of a product in the catalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                },
                "required": ["product"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_discount",
            "description": "Apply a discount tier to a price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "discount_tier": {"type": "string", "enum": ["bronze", "silver", "gold"]},
                },
                "required": ["price", "discount_tier"],
            },
        },
    }
]

# --- Wrapped LLM Call ---

@traceable(name="OpenAI Call", run_type="llm")
def call_openai(messages):
    """Wrapper to specifically trace the raw API call."""
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

# --- Agent Loop ---

@traceable(name="OpenAI Agent Loop", run_type="chain")
def run_agent(question: str):
    available_functions = {
        "get_product_price": get_product_price,
        "apply_discount": apply_discount,
    }
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a shopping assistant. "
                "1. Use 'get_product_price' to find the base price of a product. "
                "2. Use 'apply_discount' to calculate the final price. "
                "3. If a user mentions a product like 'laptop', use that exact string in the tool. "
                "4. NEVER ask for more details if the product is likely in your catalog. "
                "5. ALWAYS call the tools before answering."
            )
        },
        {"role": "user", "content": question}
    ]

    print(f"Question: {question}\n" + "="*40)

    # Use a loop to handle the multi-step reasoning
    for _ in range(5): 
        # Call the LLM (Traced via call_openai)
        response = call_openai(messages)
        
        response_message = response.choices[0].message
        messages.append(response_message)

        tool_calls = response_message.tool_calls
        
        if not tool_calls:
            print(f"\nFinal Answer: {response_message.content}")
            return response_message.content

        # Handle tool calls
        for tool_call in tool_calls:
            f_name = tool_call.function.name
            f_to_call = available_functions[f_name]
            f_args = json.loads(tool_call.function.arguments)
            
            print(f"  [Tool Selected] {f_name}({f_args})")
            
            # The tool call itself is traced via the @traceable decorator on the function
            f_result = f_to_call(**f_args)
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": f_name,
                "content": str(f_result),
            })

if __name__ == "__main__":
    print("Langchain agent with Binding tools working already")
    print()
    run_agent("What is the price of a laptop after applying a gold discount?")