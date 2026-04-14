To Implement:

### Products section
- add Warehouse/Store and Category (changes what each store has) + some metadata (confirm the term) that allows individually setting the low stock level alerts. Change the CRUD components to a popover frame.

Transfer the stock in / stock out functionally to here.

### Transactions section 
- add Warehouse/Store transaction logs (scoped and global), History logs search and picker. Expiry data, manufactured data, batch data, category data (automatically moves product if it has expired.)

Remove stock in / stock out, migrate it to Products section.

Date history picker (selects a day and checks its history transaction logs)

### UI 
- Overhaul to a more modern and user-friendly interface. Initiate visually-pleasing designs with intuitive animation (no visually cluttered animations and effects) and Icons. Pop over panel frames for most CRUD actions.

### Warehouse/Store & Categories component
Component granted to Admin and Manager, also uses a popover form. List overview for both.

Hierarchy:
Warehouse/Store - Parent, since its where we add the products.
Categories - Based on the product type (food, drinks, tech, etc.) - Child.

This also means we need to update the SQL schema since warehouse/store is also a primary key.

### Export functionality:

Export csv option, and other export necessities.

### Project structure

Rename the files in a more literal name, app_shell is too vague when its basically the root of the system.
