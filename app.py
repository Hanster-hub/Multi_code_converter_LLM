import gradio as gr
from styles import CSS
from converter import MODELS, LANG_CONFIG, port, run_code, compile_and_run

LANG_OPTIONS = [("Python", "py"), ("C++", "cpp"), ("Rust", "rs")]

EXAMPLE_CODE = """# Be careful to support large numbers

def lcg(seed, a=1664525, c=1013904223, m=2**32):
    value = seed
    while True:
        value = (a * value + c) % m
        yield value

def max_subarray_sum(n, seed, min_val, max_val):
    lcg_gen = lcg(seed)
    random_numbers = [next(lcg_gen) % (max_val - min_val + 1) + min_val for _ in range(n)]
    max_sum = float('-inf')
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += random_numbers[j]
            if current_sum > max_sum:
                max_sum = current_sum
    return max_sum

def total_max_subarray_sum(n, initial_seed, min_val, max_val):
    total_sum = 0
    lcg_gen = lcg(initial_seed)
    for _ in range(20):
        seed = next(lcg_gen)
        total_sum += max_subarray_sum(n, seed, min_val, max_val)
    return total_sum

import time
start_time = time.time()
result = total_max_subarray_sum(10000, 42, -10, 10)
end_time = time.time()

print("Total Maximum Subarray Sum (20 runs):", result)
print("Execution Time: {:.6f} seconds".format(end_time - start_time))
"""


def convert_wrapper(model, code, lang_from_val, lang_to_val):
    return port(model, code, lang_from_val, lang_to_val)


def run_input_wrapper(code, lang_from_val):
    return run_code(code, lang_from_val)


def run_output_wrapper(code, lang_to_val):
    return compile_and_run(code, lang_to_val)


def main():
    with gr.Blocks(css=CSS, theme=gr.themes.Monochrome(), title="Programming Language Converter") as ui:
        gr.Markdown(
            """
            <h1 style='text-align: center; margin-bottom: 10px;'>
                Programming Language Converter
            </h1>
            <p style='text-align: center; color: gray;'>
                Convert, optimize and run code across Python, C++, and Rust
            </p>
            """
        )

        with gr.Row():
            lang_from = gr.Dropdown(choices=LANG_OPTIONS, value="py", label="From Language")
            lang_to = gr.Dropdown(choices=LANG_OPTIONS, value="rs", label="To Language")

        with gr.Row(equal_height=True):
            with gr.Column(scale=6):
                input_code = gr.Code(
                    label="Input Code", value=EXAMPLE_CODE, language="python", lines=26
                )
            with gr.Column(scale=6):
                output_code = gr.Code(
                    label="Generated Code", value="", language="cpp", lines=26
                )

        with gr.Row(elem_classes=["controls"]):
            run_input = gr.Button("Run Input", elem_classes=["run-btn"])
            model = gr.Dropdown(MODELS, value=MODELS[0], show_label=False)
            convert = gr.Button("Convert", elem_classes=["convert-btn"])
            run_output = gr.Button("Run Output", elem_classes=["run-btn"])

        with gr.Row(equal_height=True):
            with gr.Column(scale=6):
                input_out = gr.TextArea(label="Input Result", lines=8)
            with gr.Column(scale=6):
                output_out = gr.TextArea(label="Output Result", lines=8)

        convert.click(
            fn=convert_wrapper,
            inputs=[model, input_code, lang_from, lang_to],
            outputs=[output_code],
        )
        run_input.click(
            fn=run_input_wrapper,
            inputs=[input_code, lang_from],
            outputs=[input_out],
        )
        run_output.click(
            fn=run_output_wrapper,
            inputs=[output_code, lang_to],
            outputs=[output_out],
        )

    ui.launch(inbrowser=True, share=True)


if __name__ == "__main__":
    main()
