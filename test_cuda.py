import torch

print("=== VÉRIFICATION CUDA ===")
print(f"1. PyTorch version: {torch.__version__}")
print(f"2. CUDA available: {torch.cuda.is_available()}")
print(f"3. CUDA version: {torch.version.cuda}")
print(f"4. GPUs: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"5. GPU name: {torch.cuda.get_device_name(0)}")
else:
    print("5. ❌ CUDA non disponible")
