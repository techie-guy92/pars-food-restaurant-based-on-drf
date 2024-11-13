(function($) {
    $(document).ready(function() {
        const totalAmountField = $(".field-total_amount .readonly");

        async function updateTotals() {
            const foodItems = $(".field-food select");
            const priceFields = $(".field-price p");
            const quantities = $(".field-quantity input");
            const grandTotalFields = $(".field-grand_total p");
            
            let totalAmount = 0;
            for (let index = 0; index < foodItems.length; index++) {
                const foodItem = foodItems[index];
                const quantity = quantities[index].value;
                const grandTotalField = grandTotalFields[index];
                const priceField = priceFields[index];
                
                console.log(`Processing item ${index}:`, foodItem, quantity, grandTotalField, priceField);
                
                if (foodItem.value && quantity) {
                    try {
                        const response = await fetch(`/api/v1/get_food_price/${foodItem.value}/`);
                        // const response = await fetch(`/get_food_price/${foodItem.value}/`);
                        const data = await response.json();
                        const price = data.price;
                        const grandTotal = price * quantity;
                        
                        if (grandTotalField) {
                            grandTotalField.textContent = grandTotal;
                        } else {
                            console.error(`Grand total field not found for item ${index}`);
                        }
                        
                        if (priceField) {
                            priceField.textContent = price;
                            console.log(`Price for item ${index} set to: ${price}`);
                        } else {
                            console.error(`Price field not found for item ${index}`);
                        }
                        
                        totalAmount += grandTotal;
                    } catch (error) {
                        console.error(`Error fetching price for item ${index}:`, error);
                    }
                } else {
                    console.warn(`Food item or quantity not set for item ${index}`);
                }
            }
            totalAmountField.text(totalAmount);
        }

        $(".inline-group").on("change", ".field-food select, .field-quantity input", updateTotals);
        $(".inline-group").on("input", ".field-quantity input", updateTotals);
    });
})(django.jQuery);


// ====================================================================================================

// Let's break down the process step-by-step to understand how the "grand total" and "total amount" fields are updated, 
// and why the `urls.py` sends data to the `get_food_price/<int:food_id>/` URL.

// ### 1. URL Configuration
// In your `urls.py`, you have defined a URL pattern that maps to the `get_food_price` view:
// ```python
// path('get_food_price/<int:food_id>/', get_food_price, name='get_food_price'),
// ```
// This URL is used by the JavaScript code to fetch the price of a food item based on its ID. When the cashier selects a food item, 
// the JavaScript code sends an AJAX request to this URL to get the price of the selected food item.

// ### 2. JavaScript Code Execution
// When the cashier is adding an order at `http://127.0.0.1:8000/admin/main/order/add/`, the following steps occur:

// 1. **Event Listener Setup**: The JavaScript code sets up event listeners for changes in the food item selection and quantity input fields.
//     ```javascript
//     $(".inline-group").on("change", ".field-food select, .field-quantity input", updateTotals);
//     $(".inline-group").on("input", ".field-quantity input", updateTotals);
//     ```

// 2. **Fetching Food Price**: When a food item is selected or the quantity is changed, the `updateTotals` function is called. 
// This function sends an AJAX request to the `get_food_price/<int:food_id>/` URL to fetch the price of the selected food item.
//     ```javascript
//     const response = await fetch(`/get_food_price/${foodItem.value}/`);
//     const data = await response.json();
//     const price = data.price;
//     ```

// 3. **Calculating Grand Total**: The JavaScript code calculates the grand total for each food item by multiplying 
// the price by the quantity and updates the corresponding field in the admin interface.
//     ```javascript
//     const grandTotal = price * quantity;
//     grandTotalField.textContent = grandTotal;
//     ```

// 4. **Updating Total Amount**: The JavaScript code sums up the grand totals of all food items to calculate the total amount and updates the `totalAmountField`.
//     ```javascript
//     totalAmount += grandTotal;
//     totalAmountField.text(totalAmount);
//     ```

// ### 3. Server-Side Logic
// When the order is saved, the server-side logic in your Django models ensures that the totals are correctly calculated and saved to the database:

// 1. **OrderItem Model**: The `save` method of the `OrderItem` model calls the `calculate_orders` method to calculate the `grand_total` for each order item.
//     ```python
//     def save(self, *args, **kwargs):
//         self.calculate_orders()
//         super().save(*args, **kwargs)
//     ```

// 2. **Order Model**: The `save` method of the `Order` model calls the `calculate_order_items` method to calculate the `total_amount` for the order.
//     ```python
//     def save(self, *args, **kwargs):
//         self.completed_payment()
//         if not self.pk:
//             super().save(*args, **kwargs)
//         self.calculate_order_items()
//         super().save(*args, **kwargs)
//     ```

// ### Summary of the Process
// 1. **JavaScript Execution**: When the cashier selects food items and enters quantities, 
// the JavaScript code dynamically updates the "grand total" and "total amount" fields in the admin interface 
// by fetching food prices via AJAX requests to the `get_food_price` URL.
// 2. **Server-Side Calculation**: When the order is saved, the server-side logic in the Django models ensures that 
// the totals are correctly calculated and saved to the database.

// This way, the JavaScript provides real-time feedback to the cashier, 
// while the server-side logic ensures data integrity and correctness.


// ====================================================================================================
