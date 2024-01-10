#!/usr/bin/env python3
import os
import argparse

from huggingface_hub import hf_hub_download, snapshot_download

from chatBot.paths import models_path, models_cache_path
from chatBot.settings.settings import settings

resume_download = True

parser = argparse.ArgumentParser(prog='Setup: Download models from BridgeSkillz')
parser.add_argument('--resume', default=True, action=argparse.BooleanOptionalAction, help='Enable/Disable resume_download options to restart the download progress interrupted')
args = parser.parse_args()
resume_download = args.resume

os.makedirs(models_path, exist_ok=True)
embedding_path = models_path / "embedding"

print(f"Downloading embedding {settings().local.embedding_hf_model_name}")
snapshot_download(
    repo_id=settings().local.embedding_hf_model_name,
    cache_dir=models_cache_path,
    local_dir=embedding_path,
)
print("Embedding model downloaded! BridgeSkillz 😊")
print("Downloading models for local execution...")

# Download LLM and create a symlink to the model file
hf_hub_download(
    repo_id=settings().local.llm_hf_repo_id,
    filename=settings().local.llm_hf_model_file,
    cache_dir=models_cache_path,
    local_dir=models_path,
    resume_download=resume_download,
)

print("LLM model downloaded!  BridgeSkillz 😊")
print("Setup done")
