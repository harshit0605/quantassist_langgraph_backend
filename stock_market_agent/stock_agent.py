# from workflows.main_workflow import create_workflow_graph
from stock_market_agent.models.schemas import StockQuery
from stock_market_agent.workflows.personas_workflow import create_workflow_graph
from PIL import Image
import json
import os

workflow = create_workflow_graph()
# def create_workflow(dry_run=False):
#     workflow = create_workflow_graph()
    
#     # Define a custom invoke method that includes the dry_run flag
#     original_invoke = workflow.invoke
    
#     def invoke_with_dry_run(inputs):
#         # Add dry_run flag to the inputs
#         if isinstance(inputs, dict):
#             inputs["dry_run"] = dry_run
#         return original_invoke(inputs)
    
#     # Replace the invoke method
#     workflow.invoke = invoke_with_dry_run
    
#     return workflow

# Create the default workflow instance
# workflow = create_workflow()
# def main():
# result = workflow.invoke({"query": "Analyze Apple stock"})
# print("Agent State:")

# temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tempData'))
# output_file_path = os.path.join(temp_data_folder, "agent_state.json")

# filtered_result = {key: value for key, value in result.items() if key not in ["messages", "ticker"]}

# with open(output_file_path, "w") as file:
#     json.dump(filtered_result, file, indent=4)

# print(f"Agent state written to {output_file_path}")
    # for key, value in result.items():
    #     print(f"{key}: {value}")


# def main():
#     workflow = create_workflow_graph()
#     workflow.get_graph().draw_mermaid_png()
#     image = Image.open(io.BytesIO(workflow.get_graph().draw_mermaid_png()))
    
#     # Display the image
#     image.show()


# if __name__ == "__main__":
#     main()