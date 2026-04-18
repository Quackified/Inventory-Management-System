Okay, something is clearly wrong with your design objectives.

### UI Critical Issues
Vertical Sidebar:
- Not fully colored, why is the selection categories the only thing that is colored?

Dashboard:
- Scrolling of the recent transactions has a overflow scrolling bug, even though the scrollbar is full, it scrolls upwards vertically. It's also better to remove the scrollbar overall and just replace it with adding a view all button (View All >) on the top right. Same applies to warehouse overview.

- Color design philosophy should change here, I only meant to replicate the UI Layout and design, but colors should be on your own discretion and flavor.

Products:
- ... context menu is too thin and small to be noticed, its popover buttons does not work and instead forcefully blocks outside clicks and inputs.

- you clearly didn't follow @products_example.png, your status icons are unaligned (align it to left and not center), I also said to make it like a tag note just like in the picture where it has a rounded background with color.

- Export dropdown has too much margin of the Export as buttons. Same issue applies to all export buttons of all gui.

Transactions:
- Sigh you didn't follow the @transactions_example.png, the date picker is a popover (this sucks and spawns outside the GUI) and not a dropdown (follow how Google does their date picker), and the table design is not formal. There's no calender icon which @ttkbootstrap_example.png has and it supposed to be one button, not two separate buttons of FROM and TO.

Warehouse and Categories:
- No pagination to be seen, add it on both components.

Account Management:
- again, same as products, add a context menu button instead of "selecting the user and clicking the edit button". It supposed to be a modern one, not a clunky one.


Universal:
- Why does some of the popover gui has a custom X close button? We already have a cancel button, you're conflicting the design and making it redundant.

- There's UI components examples on @ttkbootstrap_example.png.