import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langsmith import traceable # Uncomment if using LangSmith

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"
MAX_ITERATIONS = 10

# --- Tools with Monitoring Prints ---

@traceable(run_type="tool", name="get_product_price", metadata={"decription": "Look up the price of a product in the catalog", "type": "string", "required": "true"})
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

# --- Tool Schemas (Flattened for Responses API) ---

tools = [
    {
        "type": "function",
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
    {
        "type": "function",
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
    }
]

# --- Wrapped Responses API Call ---

@traceable(name="OpenAI Call", run_type="llm")
def call_openai_responses(messages):
    """Wrapper using the Responses API primitive."""
    return client.responses.create(
        model=MODEL,
        input=messages,
        tools=tools,
        temperature=0 # Keep it 0 for numerical precision
    )

# --- Agent Loop ---
@traceable(name="Shopping Agent Run")
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
                "3. Use the EXACT price returned by tools; never guess or round. "
                "4. ALWAYS call the tools before answering."
            )
        },
        {"role": "user", "content": question}
    ]

    print(f"Question: {question}\n" + "="*40)

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n ----- Iteration {iteration} ------ ")
        
        # 1. Call the API
        response = call_openai_responses(messages)
        
        # 2. Append the model's output items directly to history
        messages += response.output

        # 3. Check for tool calls in the output items
        tool_calls = [item for item in response.output if item.type == "function_call"]
        
        if not tool_calls:
            # If no tool calls, find the text block for the final answer
            final_text = response.output_text
            print(f"\nFinal Answer: {final_text}")
            return final_text

        # 4. Handle Tool Calls
        for tool_call in tool_calls:
            tool_name = tool_call.name
            # In Responses API, arguments are usually already a dict
            args = tool_call.arguments
            
            print(f"  [Tool Selected] {tool_name}({args})")
            print(f"  [Tool Details] ID: {tool_call.call_id} with args: {args}")
            
            tool_to_use = available_functions.get(tool_name)
            if not tool_to_use:
                raise ValueError(f"Tool {tool_name} not found")
            
            # Execute the function
            observation = tool_to_use(**json.loads(args))
            print(f"Tool result: {observation}")

            # 5. Append the result back using 'function_call_output'
            messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(observation),
            })

    print("ERROR: Max iterations reached without a final answer")
    return None

if __name__ == "__main__":
    print("Agent with Responses API and monitoring active...")
    print()
    run_agent("What is the price of laptop after applying a silver discount?")