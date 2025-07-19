

#%%

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

#%% Load images
image1 = load_image("https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg")
image2 = load_image("https://huggingface.co/spaces/merve/chameleon-7b/resolve/main/bee.jpg")
# %%
processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Instruct")
# %%
model = AutoModelForVision2Seq.from_pretrained(pretrained_model_name_or_path="HuggingFaceTB/SmolVLM-Instruct",
                                               torch_dtype=torch.bfloat16,
                                               #_attn_implementation="flash_attention_2" if DEVICE == "cuda" else "eager",
                                               ).to(DEVICE)
# %%
imgdir = "/home/lin/codebase/stock_analysis/images/2024"

from glob import glob
imgpaths = glob(f"{imgdir}/*")

image1 = load_image(imgpaths[0])
image2 = load_image(imgpaths[1])

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "image"},
            {"type": "text", "text": "describe the image shows bull market. True or False"}
        ]
    }
]
# %%
prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(text=prompt, images=[image1, # The code is using the `image2` variable to load an
# image of a bee from a specific URL.
image2], return_tensors="pt")
inputs = inputs.to(DEVICE)
# %%
generated_ids = model.generate(**inputs, max_new_tokens=50)
generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)

#%%
print(generated_texts[0])
# %%
from tqdm import tqdm

def create_messages(queries: list[str]):
    messages = []
    for query in queries:
        message = [{"role": "user",
                    "content": [{"type": "image"},
                        {"type": "text", 
                         "text": query}
                    ]
                    }
                    ]
        messages.append(message)
    return messages


def describe_images(imgpath, messages,
                    pretrained_modelname="HuggingFaceTB/SmolVLM-Instruct"
                    ):
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    DEVICE = "cpu"
    print(f"DEVICE. {DEVICE}")
    processor = AutoProcessor.from_pretrained(pretrained_modelname)
    model = AutoModelForVision2Seq.from_pretrained(pretrained_model_name_or_path=pretrained_modelname,
                                                torch_dtype=torch.bfloat16,
                                                #_attn_implementation="flash_attention_2" if DEVICE == "cuda" else "eager",
                                                ).to(DEVICE)

    img = load_image(imgpath)
    for message in messages:
        prompt = processor.apply_chat_template(message, add_generation_prompt=True)
        inputs = processor(text=prompt, images=[img], return_tensors="pt")
        inputs = inputs.to(DEVICE)
        generated_ids = model.generate(**inputs, max_new_tokens=50)
        generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
        return generated_texts[0]

#%%
import dask.bag as db   


#%%
imgpaths = sorted(glob(f"{imgdir}/*"))
messages = create_messages(queries=["Is the image a bull trend? True or False"])

b = db.from_sequence(seq=imgpaths)     
        
# %%
res = b.map(describe_images, messages).compute()
# %%
