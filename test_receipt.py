from receipt_renderer import ReceiptRenderer
import os

print("Testing Receipt Renderer...")

settings = {
    1: "Test Store",
    2: "123 Test St",
    3: "555-0199",
    6: "Test Footer"
}

try:
    renderer = ReceiptRenderer(settings)
    # Mock transaction with enough fields
    # id, txn_num, user_id, total, tax, discount, method, tendered, date, cashier_name
    mock_txn = [0, "TEST-001", 1, 100, 0, 0, "Cash", 100, "2025-01-01 12:00:00", "Admin", "Normal"]
    path = renderer.save_receipt(mock_txn, [], folder=".")
    print(f"Success! Saved to {path}")
    
    # Also test preview generation explicitly
    img = renderer.generate_image(None, None, preview=True)
    img.save("preview_test.png", "PNG")
    print("Preview image saved to preview_test.png")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
