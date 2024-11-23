from openai import OpenAI
import gradio as gr
import pyperclip
import time


client = OpenAI(
    api_key="OPENAI_API_KEY",
    base_url='BASE_URL',
)

META_PROMPT = """
Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions**: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

# Notes [optional]

[optional: edge cases, details, and an area to call or repeat out specific important considerations]
""".strip()

def generate_prompt(task_or_prompt: str):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": META_PROMPT,
            },
            {
                "role": "user",
                "content": "Task, Goal, or Current Prompt:\n" + task_or_prompt,
            },
        ],
    )

    return f"✨ 生成结果：{completion.choices[0].message.content}"


def copy_to_clipboard(output_text):
    pyperclip.copy(output_text)
    return gr.update(value="✔ 已复制到剪贴板！", visible=True)


def clear_message():
    time.sleep(2)
    return gr.update(visible=False)


with gr.Blocks(css="""
    #input-box, #output-box {
        height: 600px !important;
        width: 100% !important;
        overflow: auto;
    }
    .output-box {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 10px;
    }
""") as demo:
    gr.Markdown(
        """
        <h1 style="text-align: center; color: #4CAF50;">基于Meta-Prompt的prompt生成工具</h1>
        <p style="text-align: center;">输入一段prompt，点击 <strong>生成</strong>，然后可以将生成结果一键拷贝！</p>
        """
    )
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            input_box = gr.Textbox(
                label="输入prompt",
                placeholder="请输入prompt...", 
                elem_id="input-box", 
            )
            generate_button = gr.Button(
                "生成 🛠️", 
                elem_id="generate-button", 
                variant="primary",
            )

        with gr.Column(scale=2):
            output_box = gr.Textbox(
                label="输出prompt",
                interactive=False, 
                placeholder="生成的prompt将显示在此处...", 
                elem_id="output-box",
            )
            copy_button = gr.Button(
                "拷贝 📋", 
                elem_id="copy-button", 
                variant="secondary",
            )
            message = gr.Textbox(
                value="", 
                visible=False, 
                interactive=False, 
                show_label=False, 
                elem_id="message-box",
            )
    
    generate_button.click(fn=generate_prompt, inputs=input_box, outputs=output_box)
    copy_button.click(fn=copy_to_clipboard, inputs=output_box, outputs=message).then(
        fn=clear_message, inputs=None, outputs=message
    )


if __name__ == "__main__":
    demo.launch()
