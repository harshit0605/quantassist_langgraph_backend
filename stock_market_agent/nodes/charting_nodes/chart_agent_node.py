from stock_market_agent.config.state import ChartBuilderState


def chart_agent_node(state: ChartBuilderState) -> Dict:
    messages = state['messages']
    llm = ChatOpenAI(model="gpt-4")
    
    chain = create_openai_fn_chain(
        [t.args_schema for t in tools],
        llm,
        verbose=True
    )
    
    response = chain.invoke({"input": messages[-1].content})
    state['messages'].append(AIMessage(content=response))
    
    if "FINISH" in response:
        return {"next_node": END}
    
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        return {
            "next_node": "call_tool",
            "tool_name": function_call["name"],
            "tool_input": function_call["arguments"],
        }
    
    return {"next_node": "human"}