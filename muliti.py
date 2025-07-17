You’re speaking my language—this is the kind of high-volume, high-efficiency local VLM project that’s both fun and demanding. With **5 million images**, **two GPUs**, and a goal to filter for **“person or forklift”** using a **lightweight, open-source VLM**, here’s a robust setup with multiprocessing and memory-safe inference.

---

## ⚙️ Overview of the Pipeline

```txt
[Image Folder] → [Multiprocessing Batch Loader] → [Local VLM Inference per GPU] → [Semantic Filtering] → [Save Results]
```

Your requirements:
- ✅ Run locally without sending images online
- ✅ Use a lightweight open-source VLM (e.g. MiniCPM-V 2.0 or Moondream2)
- ✅ Use both GPUs for parallel inference
- ✅ Avoid crashing due to memory overflows

---

## 🧱 1. Setup Environment

```bash
python -m venv vlm-env
source vlm-env/bin/activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers pillow opencv-python tqdm
```

(Replace `cu118` with your CUDA version)

---

## 🧠 2. Load the VLM (Moondream2 Example)

This part runs per image but can be split across GPUs:

```python
from transformers import AutoProcessor, AutoModelForVision2Text
from PIL import Image
import torch

model_name = "scifigpt/moondream2"

device = torch.device("cuda:0")  # use GPU 0 or 1
model = AutoModelForVision2Text.from_pretrained(model_name).to(device)
processor = AutoProcessor.from_pretrained(model_name)

def analyze_image(path, prompt="Does this image contain a person or forklift?"):
    image = Image.open(path).convert("RGB")
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=50)
    return processor.batch_decode(output, skip_special_tokens=True)[0]
```

---

## 🧠 3. Multiprocessing Setup

We’ll divide your image folder across workers, each bound to one GPU:

```python
from multiprocessing import Process, Queue
from glob import glob
import os
from tqdm import tqdm

def worker(image_paths, gpu_id, result_queue):
    device = torch.device(f"cuda:{gpu_id}")
    # Load VLM on assigned GPU
    model = AutoModelForVision2Text.from_pretrained(model_name).to(device)
    processor = AutoProcessor.from_pretrained(model_name)

    for path in tqdm(image_paths):
        try:
            image = Image.open(path).convert("RGB")
            inputs = processor(images=image, text="Does this image contain a person or forklift?", return_tensors="pt").to(device)
            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=50)
            response = processor.batch_decode(output, skip_special_tokens=True)[0]
            result_queue.put((path, response))
        except Exception as e:
            result_queue.put((path, f"error: {str(e)}"))

def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]
```

---

## 🚀 4. Run It Across Two GPUs

```python
if __name__ == "__main__":
    all_images = glob("/your/images/folder/**/*.jpg", recursive=True)
    chunks = chunkify(all_images, 2)

    q = Queue()
    p0 = Process(target=worker, args=(chunks[0], 0, q))
    p1 = Process(target=worker, args=(chunks[1], 1, q))

    p0.start()
    p1.start()

    with open("filtered_results.csv", "w") as f:
        f.write("path,response,keep\n")
        count = 0
        while count < len(all_images):
            path, response = q.get()
            keep = "yes" in response.lower() or "person" in response.lower() or "forklift" in response.lower()
            f.write(f"{path},{response},{keep}\n")
            count += 1

    p0.join()
    p1.join()
```

---

## 🧠 Smart Filtering Function

You can refine the decision logic like:

```python
def should_keep(response):
    response = response.lower()
    return any(x in response for x in ["yes", "person", "forklift"])
```

---

## 🧹 Tips to Prevent Crashes

- ✅ Wrap inference in `torch.no_grad()` and catch exceptions
- ✅ Use batch sizes of 1 (due to image variability)
- ✅ Limit GPU memory with PyTorch’s `torch.cuda.set_per_process_memory_fraction()` if needed
- ✅ Avoid loading all images into memory—stream using paths

---

Would you like help benchmarking runtime or making this resumeable across restarts? You’re already halfway to a production-grade pipeline.