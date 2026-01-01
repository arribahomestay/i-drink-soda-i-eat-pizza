# Cashier View Modular Structure

## Overview
The cashier view has been refactored into a modular structure for better maintainability. Each component is now a separate module.

## Directory Structure

```
views/
├── cashier/
│   ├── __init__.py                 # Module initializer
│   ├── product_grid.py             # Product display and search
│   ├── shopping_cart.py            # Cart management
│   ├── variant_selector.py         # Product customization dialog
│   └── payment_dialog.py           # Payment processing
├── cashier_view.py                 # Main coordinator (imports all components)
└── ...
```

## Component Modules

### 1. **product_grid.py** (ProductGrid)
**Responsibility:** Display products and handle search

**Features:**
- 3-column grid layout
- Real-time search by name or barcode
- Product cards with name, category, price, stock
- "Add to Cart" button for each product

**Key Methods:**
- `create()` - Creates the UI
- `load_products(search_term)` - Loads/filters products
- `create_product_card(product)` - Creates individual product card
- `on_search(event)` - Handles search input

### 2. **shopping_cart.py** (ShoppingCart)
**Responsibility:** Manage cart items and display

**Features:**
- Cart item list with scrolling
- Quantity controls (+/-)
- Remove item button
- Price summary (Subtotal, Total)
- Clear cart and checkout buttons

**Key Methods:**
- `create(checkout_callback, clear_callback)` - Creates the UI
- `add_item(item)` - Adds item to cart
- `remove_item(item)` - Removes item from cart
- `clear_cart()` - Clears all items
- `get_items()` - Returns all cart items
- `update_cart_display()` - Refreshes cart UI
- `increase_quantity(item)` - Increases item quantity
- `decrease_quantity(item)` - Decreases item quantity
- `get_total()` - Returns cart total

### 3. **variant_selector.py** (VariantSelector)
**Responsibility:** Handle product customization

**Features:**
- Modal dialog for selecting variants and modifiers
- Radio buttons for variants (Size, Color, etc.)
- Checkboxes for modifiers (Add-ons)
- Live price calculation
- "Standard" option (no variant)

**Key Methods:**
- `show()` - Displays the dialog
- `center_window(window, width, height)` - Centers dialog

**Callback:**
- Calls `add_callback(item)` when user confirms selection

### 4. **payment_dialog.py** (PaymentDialog)
**Responsibility:** Process payment and complete transaction

**Features:**
- Payment method selection (Cash/GCash)
- Amount tendered input
- Live change calculation
- Transaction creation
- Receipt generation
- Activity logging

**Key Methods:**
- `show(on_success_callback)` - Displays the dialog
- `center_window(window, width, height)` - Centers dialog

**Process:**
1. Validates payment amount
2. Creates transaction in database
3. Generates receipt
4. Logs activity
5. Calls success callback

## Main Coordinator (cashier_view.py)

The main `CashierView` class:
- Creates header with logout button
- Initializes all components
- Coordinates interactions between components
- Handles add to cart logic (simple vs customized)
- Manages checkout flow

## Component Interaction Flow

```
User Action → CashierView → Component → Callback → CashierView → Update UI

Example: Add Product to Cart
1. User clicks "Add to Cart" on product card (ProductGrid)
2. ProductGrid calls add_to_cart_callback (CashierView.add_to_cart)
3. CashierView checks for variants/modifiers
4. If variants exist: Shows VariantSelector
5. VariantSelector calls add_callback (CashierView.add_customized_item_to_cart)
6. CashierView calls ShoppingCart.add_item()
7. ShoppingCart updates display

Example: Checkout
1. User clicks "Checkout" button (ShoppingCart)
2. ShoppingCart calls checkout_callback (CashierView.checkout)
3. CashierView creates PaymentDialog
4. PaymentDialog processes payment
5. PaymentDialog calls on_success_callback (CashierView.on_checkout_success)
6. CashierView clears cart and reloads products
```

## Benefits of This Structure

1. **Separation of Concerns**: Each component has a single responsibility
2. **Reusability**: Components can be reused or tested independently
3. **Maintainability**: Easy to find and modify specific features
4. **Scalability**: Easy to add new features or components
5. **Testability**: Individual components can be unit tested
6. **Readability**: Smaller, focused files (~150-300 lines each)

## File Size Comparison

**Before:**
- `cashier_view.py`: 923 lines

**After:**
- `cashier_view.py`: 170 lines (coordinator)
- `product_grid.py`: 165 lines
- `shopping_cart.py`: 250 lines
- `variant_selector.py`: 210 lines
- `payment_dialog.py`: 280 lines

**Total**: Same functionality, better organized!

## How to Extend

### Adding a New Feature

**Example: Add a "Favorites" quick access panel**

1. Create `views/cashier/favorites_panel.py`:
```python
class FavoritesPanel:
    def __init__(self, parent, database, add_to_cart_callback):
        self.parent = parent
        self.database = database
        self.add_to_cart_callback = add_to_cart_callback
    
    def create(self):
        # Create favorites UI
        pass
```

2. In `cashier_view.py`, import and initialize:
```python
from views.cashier.favorites_panel import FavoritesPanel

# In setup_ui():
self.favorites_panel = FavoritesPanel(content, self.database, self.add_to_cart)
self.favorites_panel.create()
```

### Modifying a Component

To change how products are displayed:
1. Open `views/cashier/product_grid.py`
2. Modify `create_product_card()` method
3. No need to touch other files!

## Key Design Patterns

1. **Component Pattern**: Each UI section is a separate component
2. **Callback Pattern**: Components communicate via callbacks
3. **Coordinator Pattern**: Main view coordinates component interactions
4. **Single Responsibility**: Each component has one clear purpose

## Testing Strategy

Each component can be tested independently:

```python
# Test ProductGrid
def test_product_grid():
    mock_database = MockDatabase()
    mock_callback = lambda p: print(f"Added {p[1]}")
    
    grid = ProductGrid(parent, mock_database, mock_callback)
    grid.create()
    grid.load_products()
    # Assert products are displayed correctly
```

## Notes

- All components use the same color scheme from `config.py`
- Components are stateless where possible (state in main view)
- Dialogs are modal and centered on screen
- All price calculations exclude tax (tax set to 0)
- Receipt generation uses `ReceiptRenderer` from main codebase

## Migration Status

✅ Product Grid - Complete
✅ Shopping Cart - Complete
✅ Variant Selector - Complete
✅ Payment Dialog - Complete
✅ Main Coordinator - Complete

## Next Steps

Potential enhancements:
1. Add keyboard shortcuts for common actions
2. Add barcode scanner support
3. Add customer display screen
4. Add order history quick view
5. Add favorites/quick access panel
6. Add discount/coupon support
