import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
from tqdm import tqdm  
import multiprocessing
from glob import glob
#from transformers import Idefics3ImageProcessor

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
                    pretrained_modelname="HuggingFaceTB/SmolVLM-Instruct",
                    DEVICE = "cpu"
                    ):
    print(f"DEVICE. {DEVICE}")
    #from transformers import Idefics3ImageProcessor
    processor = AutoProcessor.from_pretrained(pretrained_modelname)
    model = AutoModelForVision2Seq.from_pretrained(pretrained_model_name_or_path=pretrained_modelname,
                                                torch_dtype=torch.float32,
                                                #_attn_implementation="flash_attention_2" if DEVICE == "cuda" else "eager",
                                                ).to(DEVICE)

    img = load_image(imgpath)
    res = None
    for message in messages:
        prompt = processor.apply_chat_template(message, add_generation_prompt=True)
        inputs = processor(text=prompt, images=[img], return_tensors="pt")
        inputs = inputs.to(DEVICE)
        generated_ids = model.generate(**inputs, max_new_tokens=50)
        generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
        res = generated_texts[0]
    return res


def describe_images_wrapper(args):
    try:
        res = describe_images(**args)
        return res
    except Exception as e:
        print(f"Error processing {args['imgpath']}: {e}")
        return None

def run_multiprocess(imgdir, 
                     queries=["Is the image a bull trend? True or False"]
                     ):
    messages = create_messages(queries=queries)

    imgpaths = sorted(glob(f"{imgdir}/*"))
    args = [{"imgpath": img_path, "messages": messages,
             "pretrained_modelname": "HuggingFaceTB/SmolVLM-Instruct",
            } for img_path in imgpaths
        ]

    num_processes = multiprocessing.cpu_count()
    chunksize = max(1, len(args) // num_processes)
    print(f"start processing ...")
    with multiprocessing.Pool(num_processes) as p:
        results = list(
                    tqdm(
                        p.imap_unordered(describe_images_wrapper, 
                                         args, chunksize=chunksize
                                        ),
                        total=len(imgpaths),
                    )
                )
    print(f"results: {results}")
    return results




if __name__ == "__main__":
    imgdir = "/home/lin/codebase/stock_analysis/images/2024"

    run_multiprocess(imgdir=imgdir)