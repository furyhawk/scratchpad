# make sure you're logged in with `huggingface-cli login`
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

model_id = "stabilityai/stable-diffusion-2-1"

# Use the DPMSolverMultistepScheduler (DPM-Solver++) scheduler here instead
pipe = StableDiffusionPipeline.from_pretrained(model_id)

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("mps")

# Recommended if your computer has < 64 GB of RAM
pipe.enable_attention_slicing()

prompt = "a photo of an lion with sunset and jungle in the background in inkpunk style"
# First-time "warmup" pass (see explanation above)
_ = pipe(prompt, num_inference_steps=1)
# Results match those from the CPU device after the warmup pass.
image = pipe(prompt).images[0]

image.save("lion_inkpunk.png")
