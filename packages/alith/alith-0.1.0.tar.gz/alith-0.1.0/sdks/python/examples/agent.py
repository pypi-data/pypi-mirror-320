from alith import Agent

agent = Agent(
    name="A dummy Agent",
    model="gpt-4o-mini",
    preamble="You are a comedian here to entertain the user using humour and jokes.",
)
print(agent.prompt("Entertain me!"))
