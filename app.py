from gc import collect
from pathlib import Path

import gradio as gr
import pandas as pd
import spaces
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_REPO = "mradermacher/Spreadsheet-RL-4B-GGUF"
QUANT_FILES = {
    "Q2_K · 1.9 GB": "Spreadsheet-RL-4B.Q2_K.gguf",
    "Q3_K_S · 2.2 GB": "Spreadsheet-RL-4B.Q3_K_S.gguf",
    "Q3_K_M · 2.3 GB · lower quality": "Spreadsheet-RL-4B.Q3_K_M.gguf",
    "Q3_K_L · 2.5 GB": "Spreadsheet-RL-4B.Q3_K_L.gguf",
    "IQ4_XS · 2.6 GB": "Spreadsheet-RL-4B.IQ4_XS.gguf",
    "Q4_K_S · 2.7 GB · recommended": "Spreadsheet-RL-4B.Q4_K_S.gguf",
    "Q4_K_M · 2.8 GB · recommended": "Spreadsheet-RL-4B.Q4_K_M.gguf",
    "Q5_K_S · 3.2 GB": "Spreadsheet-RL-4B.Q5_K_S.gguf",
    "Q5_K_M · 3.3 GB": "Spreadsheet-RL-4B.Q5_K_M.gguf",
    "Q6_K · 3.7 GB · very good quality": "Spreadsheet-RL-4B.Q6_K.gguf",
    "Q8_0 · 4.8 GB · best quality": "Spreadsheet-RL-4B.Q8_0.gguf",
    "f16 · 8.9 GB": "Spreadsheet-RL-4B.f16.gguf",
}

model = None
tokenizer = None
active_quant = None


def download_quant(quantization: str) -> None:
    hf_hub_download(repo_id=MODEL_REPO, filename=QUANT_FILES[quantization])


def file_to_text(file_path: str | None) -> str:
    if file_path is None:
        return ""

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        sheets = pd.read_excel(path, sheet_name=None)
        return "\n\n".join(
            f"## Sheet: {sheet_name}\n{frame.to_csv(index=False)}"
            for sheet_name, frame in sheets.items()
        )

    if suffix == ".csv":
        return pd.read_csv(path).to_csv(index=False)

    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t").to_csv(index=False)

    return path.read_text(encoding="utf-8")


@spaces.GPU(duration=120)
def generate(
    system_prompt: str,
    user_prompt: str,
    attachment: str | None,
    quantization: str,
) -> str:
    global active_quant, model, tokenizer

    quant_file = QUANT_FILES[quantization]
    if active_quant != quantization:
        model = None
        tokenizer = None
        active_quant = None
        collect()
        torch.cuda.empty_cache()

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_REPO,
            gguf_file=quant_file,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_REPO,
            gguf_file=quant_file,
            dtype=torch.bfloat16,
            device_map="cuda",
        )
        active_quant = quantization

    attachment_text = file_to_text(attachment)
    user_content = user_prompt
    if attachment_text:
        user_content = f"{user_prompt}\n\n<attachment>\n{attachment_text}\n</attachment>"

    messages = [
        {
            "role": "system",
            "content": (
                f"{system_prompt}\n\nAfter private reasoning, answer once with only the "
                "requested deliverable. Follow the user's output format exactly. Do not "
                "restate analysis, reasoning, or self-correction in the final answer."
            ),
        },
        {"role": "user", "content": user_content},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    think_end_token = tokenizer.convert_tokens_to_ids("</think>")
    with torch.inference_mode():
        reasoning_ids = model.generate(
            **inputs,
            max_new_tokens=2048,
            do_sample=True,
            temperature=0.6,
            top_p=0.95,
            top_k=20,
            eos_token_id=think_end_token,
        )
        if reasoning_ids[0, -1].item() != think_end_token:
            reasoning_ids = torch.cat(
                [
                    reasoning_ids,
                    torch.tensor([[think_end_token]], device=model.device),
                ],
                dim=-1,
            )
        reasoning_ids = torch.cat(
            [
                reasoning_ids,
                tokenizer.encode(
                    "\n\n",
                    add_special_tokens=False,
                    return_tensors="pt",
                ).to(model.device),
            ],
            dim=-1,
        )

        answer_ids = model.generate(
            input_ids=reasoning_ids,
            attention_mask=torch.ones_like(reasoning_ids),
            max_new_tokens=512,
        )

    return tokenizer.decode(
        answer_ids[0, reasoning_ids.shape[-1] :],
        skip_special_tokens=True,
    ).strip()


CSS = """
.gradio-container { max-width: 1180px !important; }
.agent-panel { border: 2px dashed #79b5ce; border-radius: 18px; padding: 8px; }
.output-panel { border: 2px dashed #f0aeb7; border-radius: 18px; padding: 8px; }
"""

with gr.Blocks(css=CSS, title="Spreadsheet Data Agent") as demo:
    gr.Markdown(
        """
        # Spreadsheet Data Agent
        Send instructions and optional file context to Spreadsheet-RL-4B. This first
        inference surface implements the prompt-and-file entry point from the agent diagram.
        """
    )

    with gr.Row():
        with gr.Column(scale=1, elem_classes="agent-panel"):
            gr.Markdown("### RL data input")
            system_prompt = gr.Textbox(
                label="System prompt",
                value=(
                    "You are a spreadsheet reasoning assistant. Inspect the supplied "
                    "spreadsheet or text context and answer the user's request precisely."
                ),
                lines=5,
            )
            user_prompt = gr.Textbox(
                label="User prompt",
                placeholder="Describe the spreadsheet task or ask a question…",
                lines=8,
            )
            attachment = gr.File(
                label="Optional file context",
                file_types=[".txt", ".md", ".json", ".csv", ".tsv", ".xlsx", ".xls"],
                type="filepath",
            )
            quantization = gr.Dropdown(
                choices=list(QUANT_FILES),
                value="Q4_K_M · 2.8 GB · recommended",
                label="Spreadsheet-RL-4B quantization",
                info="Static GGUF quants published by mradermacher; Q4_K_M is the reference recommendation.",
            )
            run = gr.Button("Run inference", variant="primary")

        with gr.Column(scale=1, elem_classes="output-panel"):
            gr.Markdown("### Agent response")
            response = gr.Textbox(
                label="Generated text",
                lines=28,
                buttons=["copy"],
            )

    run.click(
        fn=download_quant,
        inputs=quantization,
        outputs=None,
        show_progress="full",
    ).then(
        fn=generate,
        inputs=[system_prompt, user_prompt, attachment, quantization],
        outputs=response,
        api_name="generate",
        show_progress="full",
    )

demo.queue().launch()
