# **OPTIMA35**
[optima35](https://gitlab.com/CodeByMrFinchum/optima35) is a Python package for managing and editing images, with a focus on analog photography (using pillow and piexif). For a graphical user interface, see [OptimaLab35](https://gitlab.com/CodeByMrFinchum/OptimaLab35).

## **Installation**
Install with pip (dependencies will be installed automatically):
```bash
pip install optima35
```
and the GUI with
```bash
pip install OptimaLab35
```

## **Overview**

**OPTIMA35** (**Organizing, Processing, Tweaking Images, and Modifying scanned Analogs from 35mm Film**) simplifies the editing and management of images and metadata. Though optimized for analog photography, it can handle any type of images.

## **Features**

### **Image Processing**
- Resize images
- Rename with custom order
- Grayscale conversion
- Brightness and contrast adjustment

### **EXIF Management**
- Copy or add custom EXIF data
- Add GPS coordinates
- Add or modify EXIF dates
- Remove EXIF metadata

### **Watermarking**
- Add customizable watermarks to images

## **Current Status**

**Alpha Stage**
- Active development with frequent updates.
- Breaking changes may occur in minor version updates.
- Check the [CHANGELOG](https://gitlab.com/CodeByMrFinchum/optima35/-/blob/main/CHANGELOG.md?ref_type=heads) for details on changes and updates.

## **Contributing and Feedback**

Feedback, bug reports, and contributions are welcome! Please submit them through the [GitLab repository](https://gitlab.com/CodeByMrFinchum/optima35).

# Use of LLMs
In the interest of transparency, I disclose that Generative AI (GAI) large language models (LLMs), including OpenAI’s ChatGPT and Ollama models (e.g., OpenCoder and Qwen2.5-coder), have been used to assist in this project.

## Areas of Assistance:
- Project discussions and planning
- Spelling and grammar corrections
- Suggestions for suitable packages and libraries
- Guidance on code structure and organization

In cases where LLMs contribute directly to code or provide substantial optimizations, such contributions will be disclosed and documented in the relevant sections of the codebase.

**Ollama**
- mradermacher gguf Q4K-M Instruct version of infly/OpenCoder-1.5B
- unsloth gguf Q4K_M Instruct version of both Qwen/QWEN2 1.5B and 3B

### References
1. **Huang, Siming, et al.**
   *OpenCoder: The Open Cookbook for Top-Tier Code Large Language Models.*
   2024. [PDF](https://arxiv.org/pdf/2411.04905)

2. **Hui, Binyuan, et al.**
   *Qwen2.5-Coder Technical Report.*
   *arXiv preprint arXiv:2409.12186*, 2024. [arXiv](https://arxiv.org/abs/2409.12186)

3. **Yang, An, et al.**
   *Qwen2 Technical Report.*
   *arXiv preprint arXiv:2407.10671*, 2024. [arXiv](https://arxiv.org/abs/2407.10671)
