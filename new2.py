You're thinking in exactly the right direction—**local, lightweight, open-source vision-language models (VLMs)** are becoming incredibly capable, and perfect for tasks like image filtering without sending data to the cloud.

Here are some top contenders that check all your boxes:

---

## 🧠 Recommended Lightweight VLMs for Local Use

| Model Name       | Size      | Highlights                                      | License       |
|------------------|-----------|--------------------------------------------------|----------------|
| **nanoVLM**       | 222M–450M | Ultra-light, PyTorch-native, easy to customize | Apache 2.0     |
| **Moondream2**    | 1.6B      | Fast, edge-friendly, strong VQA & captioning   | Open Source    |
| **SmolVLM**       | 2B        | Efficient memory use, great scene understanding| Apache 2.0     |
| **MiniCPM-V 2.0** | ~2B       | OCR, captioning, fast inference                | Open Source    |
| **PaliGemma**     | 3B        | Strong image-text reasoning, multilingual      | Open Weights   |

These models are designed to run **entirely offline**, and many can operate on consumer-grade GPUs (even 8–12 GB VRAM). Some, like `nanoVLM`, are so compact they can be trained or fine-tuned on a single machine.

---

## 🛠️ What You Can Do With Them

- 🔍 Ask: “Does this image contain a person and a dog?”
- 🧹 Filter: Keep only images that match your semantic criteria
- 🧠 Describe: Generate captions or tags for sorting
- 🧪 Score: Rank images by relevance or clarity

You can batch-process folders of images, use structured prompts, and even integrate with local apps or scripts.

---

## 🚀 Getting Started

If you want a minimal setup:
- Clone [nanoVLM on GitHub](https://github.com/huggingface/nanoVLM) for a readable, PyTorch-native codebase
- Or try [Moondream2](https://scifilogic.com/best-local-multimodal-llm/) or [SmolVLM](https://huggingface.co/blog/smolvlm) via Hugging Face Transformers for plug-and-play inference

Let me know your hardware specs and filtering goals—I can help you pick the best model and write a starter script to get things rolling.