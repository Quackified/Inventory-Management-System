## UI Improvements
### Fresh Color Experience
Color Scheme to use:
- #696B45
- #E0D5C9
- #C59D50
- #A37C40
- #392007

Task: Experiment and find a pleasing color mix with the given color values. Assign each color and have fun with it making more professional and aesthetically pleasing with Modern UI.

Critical: Don't forget to add Error, Warning, and Success popups/dialogs.

### Icons
Use Material Design Icons for a modern and consistent look.

### Fonts
Use a modern and consistent font for the UI.

Note: You can use tighter font spacing if needed.

### Specific UI Layouts
Dashboard_Screen:
- Image Example: @/reference images/dashboard_example.png

What I want there:
- My tasks UI > Transactions (To Do) (Make sure the UI is fit till the bottom)
- The nice cards there (Total Products, Total Stock, Low Stock Items, etc), exclude the view all button.
- Right of the Transactions is the Warehouse/Store, it indicates the total products, stock, expired stocks, etc. (Make it compact and just summarizes/tallies the data, no need to show the full list)
- Analytics UI (Graph of something? Help me find the right target to visualize, with a mini)

Another Dashboard Image Example: @/reference images/dashboard_example.png

- Grab the Card UI Example there, of course ignore the $ sign and the percentage difference
- Analystics UI button of weekly/monthly there.

Color Scheme: Find the freshest scheme, it will apply universally anyway.

Product Management Screen:
- Image Example: @/reference images/products_example.png

What I want there:
- The Formal table design of rows and columns + context menu button at the right side. (Remove the word "Actions" on the table header). Instead of having a "Delete" and "Edit" button on the old UI, we add the context menu button at the right side of the table, and when clicked, it will show the "Edit" and "Delete" button.

- The search button, grab the parent design of it too.
- Status tag icons (Low Stock, Expired, etc.) with colored of it being green as normal, yellow as low stock, red as expired. (Wait, is this supposed to be expiry status or literally stock alert.)

- Pagination (Uses limits of MySQL with a selection of 10, 25, 50, 100 per page), of course next page and previous page in icons if possible.

- Since I talked about grabbing the parent design from search button. We're adding the export option (dropdown of as CSV and as Excel), stock in, stock out, and a color highlighted of add product.

Transaction Screen:
- Image Example: @/reference images/transactions_example.png

What I want there:
- Date Picker that actually shows the calendar. (From and To)
- A color aware that distinguishes the stock-in and stock-out.
- A pagination
- Many more, as long as it fits with the project design, and UI.

Warehouse/Store:
- Overhauled to a more modern and user-friendly interface. Similar to Products.

Accounts:
- Overhauled to a more modern and user-friendly interface. Similar to Products.

Vertical Sidebar:
- similar philosophy design.
- placeholder for icons (actually can you grab the icons for me? or download the icons?)

### Popover/Dialogs
- Error, Warning, and Success popups/dialogs. This is needed for the thesis for trappings and other user interactions that could lead to errors.

### Animations:
- Soft animations when switching tabs, popups, etc. (Don't overdo it)

PHILOSOPHY:
BE A GOOD SYSTEM DESIGNER THAT REFUSES TO BE GENERIC AI SLOP.