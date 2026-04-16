import os
import random
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API KEY is missing in .env file")

sessions = {}
app = FastAPI()

class Message(BaseModel):
    session_id : str
    message : str

    @field_validator("session_id")
    @classmethod
    def session_id_is_missing(cls, v):
        if not v.strip():
            raise ValueError("Session ID is missing")
        return v
    
    @field_validator("message")
    @classmethod
    def message_is_empty(cls, v):
        if not v.strip():
            raise ValueError("Message is Empty")
        return v
    
restaurant = {
    "name": "Bella Italia",
    "opening_hours": "12 PM to 11 PM",
    "location": "Astoria, New York",
    "phone": "123-456-7890",
    "menu": {
        "pizzas": ["Margherita", "Pepperoni", "Vegetarian"],
        "pastas": ["Carbonara", "Bolognese", "Vegan Arrabbiata"],
        "desserts": ["Tiramisu", "Gelato"]
    },
    "dietary_options": ["vegetarian", "vegan", "gluten_free"],
    "prices": {
        "pizzas": "$12-$18",
        "pastas": "$10-$16",
        "desserts": "$6-$10"
    }
}


llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0.2,
    max_tokens = 500,
    api_key = api_key
)

@tool
def check_menu(category: str = None) -> str:
    """Returns the restaurnts menu.
    If category is provided, returns items for that category.
    Categories are: pizza, pastas, desserts.
    Use this for any menu related questions"""
    
    if category is None:
        result = ""
        for cat, items in restaurant["menu"].items():
            result += f"{cat.upper()}: {', '.join(items)}\n"
        return result
    category = category.lower().strip()
    if category in restaurant["menu"]:
        items = restaurant["menu"][category]
        return f"{category.upper()} : {', '.join(items)}"
    return f"Category '{category}' not found. Available: pizza, pastas, desserts"
    
@tool
def check_dietary_options(requirement: str) -> str:
    """Checks if a specific dietary requirement is available.
    Use this when customer asks about vegertarian, vegan or gluten free options.
    Available options: vegertarian, vegan, gluten_free."""

    requirement = requirement.lower()
    if requirement not in restaurant["dietary_options"]:
        return f"Sorry, {requirement} option is not available"
    return f"Yes, we have {requirement} option available"

@tool
def get_restaurant_info() -> str:
    """Returns general restaurant information.
    Use this for questions about opening hours, location or phone number."""

    name = restaurant["name"]
    hours = restaurant["opening_hours"]
    location = restaurant["location"]
    return f"Name: {name}\nOpening hours: {hours}\nLocation: {location}"

@tool
def check_availability(date : str, time : str) -> str:
    """Checks if tables are available at a specific date and time.
    Use this before booking to verify availability.
    """
    return f"yes, we have tables are available on {date} at {time}."


@tool
def book_table(date: str, time: str, people: int, special_requirement: str = None) -> str:
    """Books a table at the restaurants.
    Use this when customer wants to make a reservation.
    Requires date, time and number of people.
    Maximum 8 people per table
    """

    if int(people) > 8:
        return "Sorry, maximum 8 people per table."
    if int(people) < 1:
        return "Please, provide a valid number of people"
    
    ref = random.randint(1000,9999)
    return f"Table booked! Reference number : {ref}. Date: {date}, Time: {time}, People: {people}."


tools = [
    check_menu,
    check_dietary_options,
    get_restaurant_info,
    book_table,
    check_availability
]

menu_str = str(restaurant['menu']).replace('{', '{{').replace('}', '}}')
dietary_str = str(restaurant['dietary_options'])
prices_str = str(restaurant['prices']).replace('{', '{{').replace('}', '}}')


system_prompt = f"""You are Arda, a reliable assistant for Bella Italia restaurant.

REAL RESTAURANT DATA — only use this information:
- Opening hours: {restaurant['opening_hours']}
- Location: {restaurant['location']}
- Phone: {restaurant['phone']}
- Menu: {menu_str}
- Dietary options: {dietary_str}
- Price ranges: {prices_str}

ANTI-HALLUCINATION RULES:
- Only confirm menu items listed above
- Never make up prices, availability or details
- If unsure use the appropriate tool

BOOKING STEPS:
1. UNDERSTAND - identify what customer needs
2. GATHER - collect date, time, people count
3. VALIDATE - check availability
4. EXECUTE - make the booking
5. CONFIRM - give complete confirmation

GUARDRAIL RULES:
- Only answer Bella Italia related questions
- If asked unrelated questions redirect politely
"""

agent = create_react_agent(
    llm, 
    tools,
    prompt=system_prompt
)

@app.post("/chat")
def ai_chat(message: Message):
    session_id = message.session_id
    
    if session_id not in sessions:
        sessions[session_id] = []
  
    sessions[session_id].append(
        HumanMessage(content=message.message)
    )

    result = agent.invoke({
        "messages": sessions[session_id]
    })

    ai_message = result["messages"][-1]
    
    sessions[session_id].append(ai_message)
    
    return {"output": ai_message.content}