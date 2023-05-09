import os
import torch
import pygame as pg
from transformers import CodeGenForCausalLM, AutoTokenizer


def generate_prompt(input_text, root_dir):
    prompts = []
    for file in os.listdir(root_dir):
        if file.endswith(".py") and not file.startswith("dynamic_edit"):
            file_name = file
            with open(os.path.join(root_dir, file), 'r') as f:
                code = f.read()
            prompt = f'<NME> {file_name}\n'f'<BEF> {code}\n'f'<MSG> {input_text}\n'
            prompts.append(prompt)
    return prompts


class InputBox:
    def __init__(self, x, y, w, h, text='', color_inactive=pg.Color('lightskyblue3'),
                 color_active=pg.Color('dodgerblue2'), font=pg.font.Font(None, 32)):
        self.rect = pg.Rect(x, y, w, h)
        self.color = color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.font = font
        self.tokenizer = AutoTokenizer.from_pretrained('CarperAI/diff-codegen-350m-v2')
        self.tokenizer.padding_side = 'left'
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = CodeGenForCausalLM.from_pretrained('CarperAI/diff-codegen-350m-v2').to(self.device)
        self.root_dir = os.path.dirname(os.path.realpath(__file__))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.generate_code(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

    def edit_files(self, model_output):
        # read files and edit them
        for filename in os.listdir(self.root_dir):
            if filename.endswith(".py") and filename != "dynamic_edit_diff.py":
                self.edit_file(filename, model_output)

    def generate_code(self, text):
        prompts = generate_prompt(text, root_dir=self.root_dir)
        inputs = self.tokenizer(prompts, return_tensors='pt', padding=True).to(self.device)
        self.model.config.use_cache = True
        model_output = self.model.generate(**inputs, temperature=0.0, max_length=1000)
        decoded = self.tokenizer.decode(model_output[0])
        self.edit_files(decoded)

    def edit_file(self, filename, model_output):
        model_output = model_output.split('\n')
        new_file = []
        # start reading from the <DFF> tag
        start = False
        for line in model_output:
            if '<DFF>' in line:
                start = True
                continue
            if start:
                # keep lines that starts with '+' and remove lines that starts with '-' or '@' or '\'
                if line.startswith('+') or line.startswith(' '):
                    new_file.append(line[1:] + '\n')
                elif line.startswith('-') or line.startswith('@') or line.startswith('\\'):
                    continue
                else:
                    new_file.append(line + '\n')
        # write new file
        with open(os.path.join(self.root_dir, "edited_" + filename), 'w') as f:
            f.writelines(new_file)



