# **OptimaLab35**
[OptimaLab35](https://gitlab.com/CodeByMrFinchum/OptimaLab35) is a graphical and terminal user interface for [optima35](https://gitlab.com/CodeByMrFinchum/optima35). It is under **heavy development**, and both UI elements and cross-platform compatibility may change.

## **Overview**

**OptimaLab35** extends **OPTIMA35** (**Organizing, Processing, Tweaking Images, and Modifying scanned Analogs from 35mm Film**) by providing an intuitive interface for image and metadata management. While tailored for analog photography, it supports any type of image.


## **Current Status**

### **Versioning and Compatibility**

The preserved version **v0.1.0** ensures stability with the current GUI design. It depends on **optima35==0.6.4**, a version confirmed to work seamlessly with this release. Future updates may introduce breaking changes, especially as the project evolves across platforms.

### **Installation**

Install via pip (dependencies are automatically managed, except for `simple-term-menu` used in TUI mode, which is Linux-only):
```bash
pip install OptimaLab35
```

## **Development and Notes**

**Alpha Stage**
- UI designs (GUI and TUI) are evolving, and breaking changes may occur.
- The [**CHANGELOG**](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/blob/main/CHANGELOG.md) provides detailed updates.
- Some safety checks are still under development.

**Modes:**
- **GUI**: Default if **PySide6** is available.
- **TUI**: Fallback if **PySide6** is missing or can be explicitly started using the `--tui` flag.

### Preview GUI
**PREVIEW** might be out of date.

**Main tab**

![main](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/raw/feature/enhancing/media/main_tab.png){width=40%}

**Preview window**

![main](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/raw/feature/enhancing/media/preview_window.png){width=40%}

**Exif tab**

![main](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/raw/feature/enhancing/media/exif_tab.png){width=40%}

**Exif editor**

![main](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/raw/feature/enhancing/media/exif_editor.png){width=40%}

**Info window**

![main](https://gitlab.com/CodeByMrFinchum/OptimaLab35/-/raw/feature/enhancing/media/info_window.png){width=40%}

## **Features**

### **Image Processing**
- Resizing
- Renaming with custom order
- Grayscale conversion
- Brightness and contrast adjustment

### **EXIF Management**
- Copy or add custom EXIF data
- Add GPS coordinates
- Add or modify EXIF dates
- Remove EXIF metadata

### **Watermarking**
- Add customizable watermarks

## **Dependencies**

**GUI Mode:**
- `optima35`
- `pyside6`

**TUI Mode (Linux only):**
- `simple-term-menu`

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
