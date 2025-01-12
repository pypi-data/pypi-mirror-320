import curses
import math


class TerminalSelector:
    def __init__(self, items, title="Please select an item"):
        self.items = items
        self.title = title
        self.current_position = 0
        self.window_start = 0

    def draw_menu(self, stdscr):
        height, width = stdscr.getmaxyx()
        # Reserve one line for title, one for instructions
        max_display_items = height - 3

        # Clear screen
        stdscr.clear()

        # Display title
        stdscr.addstr(0, 0, self.title, curses.A_BOLD)

        # Display instructions
        stdscr.addstr(
            height - 1,
            0,
            "Use ↑/↓ arrows to navigate, Enter to select, q to quit",
            curses.A_DIM,
        )

        # Adjust window if current position is out of view
        if self.current_position >= self.window_start + max_display_items:
            self.window_start = self.current_position - max_display_items + 1
        elif self.current_position < self.window_start:
            self.window_start = self.current_position

        # Display items
        for idx in range(min(max_display_items, len(self.items) - self.window_start)):
            item_idx = idx + self.window_start
            item = self.items[item_idx]

            # Truncate item if it's too long
            if len(item) > width - 4:
                item = item[: width - 7] + "..."

            # Highlight current selection
            if item_idx == self.current_position:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(idx + 1, 0, f" {item} ")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f" {item} ")

        # Display scrollbar if needed
        if len(self.items) > max_display_items:
            scrollbar_height = math.ceil(
                (max_display_items / len(self.items)) * max_display_items
            )
            scrollbar_pos = math.floor(
                (self.window_start / len(self.items)) * max_display_items
            )
            for i in range(max_display_items):
                if i >= scrollbar_pos and i < scrollbar_pos + scrollbar_height:
                    stdscr.addstr(i + 1, width - 1, "█")
                else:
                    stdscr.addstr(i + 1, width - 1, "│")

        stdscr.refresh()

    def run(self):
        def _inner(stdscr):
            # Setup
            curses.curs_set(0)  # Hide cursor
            stdscr.clear()

            while True:
                self.draw_menu(stdscr)
                key = stdscr.getch()

                if key == curses.KEY_UP and self.current_position > 0:
                    self.current_position -= 1
                elif (
                    key == curses.KEY_DOWN
                    and self.current_position < len(self.items) - 1
                ):
                    self.current_position += 1
                elif key in [curses.KEY_ENTER, ord("\n"), ord("\r")]:
                    return self.items[self.current_position]
                elif key == ord("q"):
                    return None

        return curses.wrapper(_inner)


# Example usage
if __name__ == "__main__":
    # Sample list of items
    items = [f"Item {i}" for i in range(1, 101)]  # Create 100 items

    selector = TerminalSelector(items, "Select an item from the list")
    selected_item = selector.run()

    # Print result after exiting curses window
    if selected_item:
        print(f"You selected: {selected_item}")
    else:
        print("Selection cancelled")
