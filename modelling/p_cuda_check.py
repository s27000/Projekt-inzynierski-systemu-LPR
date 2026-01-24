import torch

# Prosty skrypt sprawdzjący obecność GPU w środowisku
print("---=== SPRZAWDZANIE PODŁĄCZENIA GPU ===---")
print("TORCH:")
print(f"- CUDA dostępne: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"- urządzenie: {torch.cuda.get_device_name(0)}")