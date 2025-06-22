import time
import random
import curses
import json
import os
from datetime import datetime
import sys

letter_shown = {}
n_letter_shown = {}
letter_correct = {}
n_letter_correct = {}
letter_accuracy = {}
n_letter_accuracy = {}
inverse_letter_accuracy = {}
letter_weight = {}
letter_time_total = {}
letter_time_count = {}
letter_wpm = {}
last_keystroke_time = 0.0

for i in range(32, 127):
    char = chr(i)
    letter_shown[char] = 0
    n_letter_shown[char] = 0
    letter_correct[char] = 0
    n_letter_correct[char] = 0
    letter_accuracy[char] = 0.0
    n_letter_accuracy[char] = 0.0
    inverse_letter_accuracy[char] = 1.0
    letter_weight[char] = 0.0
    letter_time_total[char] = 0.0
    letter_time_count[char] = 0
    letter_wpm[char] = 0.0

letter_frequency = {
    "e": 	12.02,
    "t": 	9.10,
    "a": 	8.12,
    "o": 	7.68,
    "i": 	7.31,
    "n": 	6.95,
    "s": 	6.28,
    "r": 	6.02,
    "h": 	5.92,
    "d": 	4.32,
    "l": 	3.98,
    "u": 	2.88,
    "c": 	2.71,
    "m": 	2.61,
    "f": 	2.30,
    "y": 	2.11,
    "w": 	2.09,
    "g": 	2.03,
    "p": 	1.82,
    "b": 	1.49,
    "v": 	1.11,
    "k": 	0.69,
    "x": 	0.17,
    "q": 	0.11,
    "j": 	0.10,
    "z": 	0.07,
}

def load_user_data():
    global letter_shown, letter_correct, letter_accuracy, letter_time_total, letter_time_count, letter_wpm
    
    try:
        if os.path.exists("userdata.json"):
            with open("userdata.json", "r") as f:
                data = json.load(f)
                
            if "letter_shown" in data:
                letter_shown.update(data["letter_shown"])
            if "letter_correct" in data:
                letter_correct.update(data["letter_correct"])
            if "letter_accuracy" in data:
                letter_accuracy.update(data["letter_accuracy"])
            if "letter_time_total" in data:
                letter_time_total.update(data["letter_time_total"])
            if "letter_time_count" in data:
                letter_time_count.update(data["letter_time_count"])
            if "letter_wpm" in data:
                letter_wpm.update(data["letter_wpm"])
                
            return data.get("test_history", [])
    except (json.JSONDecodeError, IOError) as e:
        pass
    
    return []

def save_user_data(test_results):
    try:
        test_history = []
        if os.path.exists("userdata.json"):
            try:
                with open("userdata.json", "r") as f:
                    existing_data = json.load(f)
                    test_history = existing_data.get("test_history", [])
            except:
                pass
        
        test_history.append(test_results)
        
        if len(test_history) > 50:
            test_history = test_history[-50:]
        
        data = {
            "letter_shown": letter_shown,
            "letter_correct": letter_correct,
            "letter_accuracy": letter_accuracy,
            "letter_time_total": letter_time_total,
            "letter_time_count": letter_time_count,
            "letter_wpm": letter_wpm,
            "test_history": test_history,
            "last_updated": datetime.now().isoformat()
        }
        
        with open("userdata.json", "w") as f:
            json.dump(data, f, indent=2)
            
    except IOError as e:
        pass

def calculate_letter_stats():
    """Calculate average timing and WPM for each letter"""
    global letter_wpm
    
    for letter in letter_time_total:
        if letter_time_count[letter] > 0:
            avg_time = letter_time_total[letter] / letter_time_count[letter]
            # Convert to WPM: (characters per minute) / 5 (avg word length)
            if avg_time > 0:
                letter_wpm[letter] = (12 / avg_time)  # WPM
            else:
                letter_wpm[letter] = 0.0

def typing_test(stdscr):
    global last_keystroke_time
    
    curses.curs_set(0)
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    
    if max_y < 15 or max_x < 50:
        stdscr.addstr(0, 0, "Terminal too small!")
        stdscr.addstr(1, 0, f"Need at least 15x50, got {max_y}x{max_x}")
        stdscr.addstr(2, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        return
    
    with open("words.txt", "r") as f:
        possible_words = [word.strip() for word in f.readlines()]
    
    calculate_letter_stats()

    for i in range(32, 127):
        char = chr(i)
        n_letter_shown[char] = 0
        n_letter_correct[char] = 0
        n_letter_accuracy[char] = 0.0
    
    for letter in letter_accuracy:
        inverse_letter_accuracy[letter] = 1 / letter_accuracy[letter] if letter_accuracy[letter] > 0 else 1.0
    
    for letter in letter_accuracy:
        if letter in letter_frequency:
            wpm_weight = 1.0 / (letter_wpm[letter] + 0.1)
            letter_weight[letter] = (inverse_letter_accuracy[letter] * 
                                   letter_frequency[letter] * 
                                   wpm_weight)
        else:
            letter_weight[letter] = 1.0

    word_weight = {word: 1 for word in possible_words}
    for word in possible_words:
        for letter in word:
            if letter_accuracy[letter] > 0:
                word_weight[word] = word_weight[word] + letter_weight[letter]
            else:
                word_weight[word] = word_weight[word] + letter_weight[letter] * 2
        word_weight[word] = word_weight[word] / len(word)
    
    words_to_type = ""
    word_count = 0
    target_words = words_limit if test_type == "words" else 50
    
    for _ in range(target_words):
        word = random.choices(possible_words, weights=word_weight.values(), k=1)[0]
        test_text = words_to_type + (" " if words_to_type else "") + word
        words_to_type = test_text
        word_count += 1
        if test_type == "words" and word_count >= target_words:
            break
    
    if not words_to_type:
        words_to_type = "hello world test"
    
    def safe_addstr(y, x, text, attr=0):
        try:
            if y < max_y and x < max_x and x >= 0:
                available_width = max_x - x - 1
                if len(text) > available_width:
                    text = text[:available_width]
                if text:
                    stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    center_y = max_y // 2
    center_x = max_x // 2
    row_width = min(80, max_x - 4)
    
    title = "Welcome to typr!"
    title_x = center_x - len(title) // 2
    
    if test_type == "time":
        status_text = f"Time limit: {time_limit} seconds - Press any key to start"
    elif test_type == "forever":
        status_text = "Forever mode - Press ESC to quit, any key to start"
    else:
        status_text = f"Words to type: {words_limit}"
    status_x = center_x - len(status_text) // 2
    
    instruction = "Type the text below:"
    instruction_x = center_x - len(instruction) // 2
    
    safe_addstr(center_y - 6, title_x, title)
    safe_addstr(center_y - 4, status_x, status_text)
    safe_addstr(center_y - 3, instruction_x, instruction)
    
    start_row = center_y - 1
    text_start_x = center_x - row_width // 2
    
    stdscr.refresh()
    
    user_input = ""
    start_time = None
    last_keystroke_time = 0.0
    current_pos = 0
    test_finished = False
    typing_started = False
    
    def update_display():
        """Update the 3-row text display"""
        for row in range(3):
            try:
                stdscr.move(start_row + row, 0)
                stdscr.clrtoeol()
            except curses.error:
                pass
        
        chars_per_row = row_width
        
        current_row = len(user_input) // chars_per_row
        display_start_row = max(0, current_row - 1) if current_row > 0 else 0
        display_start = display_start_row * chars_per_row
        
        remaining_text = words_to_type[display_start:]
        typed_text = user_input[display_start:]
        
        for row in range(3):
            row_start = row * chars_per_row
            row_end = (row + 1) * chars_per_row
            
            row_target = remaining_text[row_start:row_end] if row_start < len(remaining_text) else ""
            row_typed = typed_text[row_start:row_end] if row_start < len(typed_text) else ""
            
            if not row_target:
                continue
                
            for i, char in enumerate(row_typed):
                if i < len(row_target):
                    color = curses.color_pair(2) if char == row_target[i] else curses.color_pair(3)
                    safe_addstr(start_row + row, text_start_x + i, char, color)
            
            remaining = row_target[len(row_typed):]
            if remaining:
                absolute_pos = display_start + row_start + len(row_typed)
                
                if absolute_pos == len(user_input) and len(user_input) < len(words_to_type):
                    next_char = remaining[0]
                    safe_addstr(start_row + row, text_start_x + len(row_typed), next_char, 
                              curses.color_pair(5) | curses.A_UNDERLINE | curses.A_BOLD)
                    rest = remaining[1:]
                    if rest:
                        safe_addstr(start_row + row, text_start_x + len(row_typed) + 1, rest, curses.color_pair(4))
                else:
                    safe_addstr(start_row + row, text_start_x + len(row_typed), remaining, curses.color_pair(4))
    
    update_display()
    
    while not test_finished:
        current_time = time.time()
        
        if test_type == "time" or test_type == "forever":
            if typing_started and start_time:
                elapsed_time = current_time - start_time
                if test_type == "time":
                    remaining_time = max(0, time_limit - elapsed_time)
                    if elapsed_time > 0:
                        current_wpm = (len(user_input) / elapsed_time) * 12
                    else:
                        current_wpm = 0
                    status_text = f"Time: {remaining_time:.1f}s | WPM: {current_wpm:.1f}"
                else:
                    if elapsed_time > 0:
                        current_wpm = (len(user_input) / elapsed_time) * 12
                    else:
                        current_wpm = 0
                    status_text = f"Time: {elapsed_time:.1f}s | WPM: {current_wpm:.1f} | ESC to quit"
                
                status_x = center_x - len(status_text) // 2
                try:
                    stdscr.move(center_y - 4, 0)
                    stdscr.clrtoeol()
                    safe_addstr(center_y - 4, status_x, status_text)
                except curses.error:
                    pass
        
        if test_type == "time" and typing_started and start_time and (current_time - start_time) >= time_limit:
            test_finished = True
            break
        
        if (test_type == "time" or test_type == "forever") and current_pos >= len(words_to_type) - 50:
            additional_words = ""
            for _ in range(20):
                word = random.choices(possible_words, weights=word_weight.values(), k=1)[0]
                additional_words += " " + word
            words_to_type += additional_words
        
        if test_type == "words" and current_pos >= len(words_to_type):
            test_finished = True
            break
        
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            exit()
        
        if key == 27 or key == 3:  # ESC or Ctrl+C to quit
            if test_type == "forever":
                test_finished = True
                break
            else:
                exit()
        elif key == curses.KEY_BACKSPACE or key == 8 or key == 127:
            if user_input and len(user_input) > 0:
                last_char_pos = len(user_input) - 1
                if last_char_pos < len(words_to_type):
                    if forgive_errors:
                        letter_shown[words_to_type[last_char_pos]] -= 1
                        n_letter_shown[words_to_type[last_char_pos]] -= 1

                    if user_input[last_char_pos] == words_to_type[last_char_pos]:
                        if not forgive_errors:
                            letter_shown[words_to_type[last_char_pos]] -= 1
                            n_letter_shown[words_to_type[last_char_pos]] -= 1
                        letter_correct[words_to_type[last_char_pos]] -= 1
                        n_letter_correct[words_to_type[last_char_pos]] -= 1
                
                user_input = user_input[:-1]
                current_pos = len(user_input)
                update_display()
                
        elif 32 <= key <= 126:  # Printable characters
            char = chr(key)
            
            if not typing_started:
                typing_started = True
                start_time = time.time()
                last_keystroke_time = start_time
            
            current_time = time.time()
            
            if forgive_errors and current_pos < len(words_to_type) and char != words_to_type[current_pos]:
                continue
            
            if last_keystroke_time > 0:
                keystroke_time = current_time - last_keystroke_time
            else:
                keystroke_time = 0.0
            
            user_input += char
            position = len(user_input) - 1
            
            if position < len(words_to_type):
                expected_char = words_to_type[position]
                letter_shown[expected_char] += 1
                n_letter_shown[expected_char] += 1
                
                if char == expected_char:
                    letter_time_total[expected_char] += keystroke_time
                    letter_time_count[expected_char] += 1
                    
                    letter_correct[expected_char] += 1
                    n_letter_correct[expected_char] += 1
                    letter_accuracy[expected_char] = letter_correct[expected_char] / letter_shown[expected_char]
                    n_letter_accuracy[expected_char] = n_letter_correct[expected_char] / n_letter_shown[expected_char]
                else:
                    letter_accuracy[expected_char] = letter_correct[expected_char] / letter_shown[expected_char]
                    n_letter_accuracy[expected_char] = n_letter_correct[expected_char] / n_letter_shown[expected_char]
            
            last_keystroke_time = current_time
            current_pos = len(user_input)
            update_display()
        
        try:
            stdscr.refresh()
        except curses.error:
            pass
    
    end_time = time.time()
    time_taken = end_time - start_time if start_time else 0
    accuracy = 0.0
    letter_count = 0

    for letter in letter_accuracy:
        if letter_accuracy[letter] > 0:
            accuracy += letter_accuracy[letter]
            letter_count += 1
    accuracy = accuracy / letter_count

    new_accuracy = 0.0
    letter_count = 0
    for letter in n_letter_accuracy:
        if n_letter_accuracy[letter] > 0:
            new_accuracy += n_letter_accuracy[letter]
            letter_count += 1
    new_accuracy = new_accuracy / letter_count

    raw_wpm = (len(words_to_type) / time_taken) * 10 if time_taken > 0 else 0
    wpm = raw_wpm * new_accuracy

    test_results = {
        "timestamp": datetime.now().isoformat(),
        "raw_wpm": round(raw_wpm, 2),
        "wpm": round(wpm, 2),
        "accuracy": round(new_accuracy * 100, 2),
        "time_taken": round(time_taken, 2),
        "text_length": len(words_to_type),
        "words_typed": len(words_to_type.split()),
        "characters_typed": len(user_input)
    }
    
    stdscr.clear()
    
    results_title = "Results"
    results_title_x = center_x - len(results_title) // 2
    safe_addstr(center_y - 6, results_title_x, results_title, curses.A_BOLD)
    
    wpm_text = f"WPM: {wpm:.2f}"
    wpm_x = center_x - len(wpm_text) // 2
    safe_addstr(center_y - 4, wpm_x, wpm_text)
    
    accuracy_text = f"Accuracy: {new_accuracy * 100:.2f}%"
    accuracy_x = center_x - len(accuracy_text) // 2
    safe_addstr(center_y - 3, accuracy_x, accuracy_text)
    
    time_text = f"Time taken: {time_taken:.2f} seconds"
    time_x = center_x - len(time_text) // 2
    safe_addstr(center_y - 2, time_x, time_text)
    
    avg_accuracy_text = f"Avg. Accuracy: {accuracy * 100:.2f}%"
    avg_accuracy_x = center_x - len(avg_accuracy_text) // 2
    safe_addstr(center_y - 1, avg_accuracy_x, avg_accuracy_text)
    
    if new_accuracy > 0.5:
        save_user_data(test_results)
        saved_text = "Test results saved"
        saved_x = center_x - len(saved_text) // 2
        safe_addstr(center_y + 1, saved_x, saved_text, curses.color_pair(2))
    else:
        not_saved_text = "Results not saved - accuracy too low"
        not_saved_x = center_x - len(not_saved_text) // 2
        safe_addstr(center_y + 1, not_saved_x, not_saved_text, curses.color_pair(3))
    
    continue_text = "Press ESC to exit... Press Enter to continue"
    continue_x = center_x - len(continue_text) // 2
    safe_addstr(center_y + 3, continue_x, continue_text)
    
    calculate_letter_stats()
    
    try:
        stdscr.refresh()
        key = stdscr.getch()
        while True:
            if key == 27 or key == 3:
                exit()
            elif key == 10:
                break
            key = stdscr.getch()
        typing_test(stdscr)

    except curses.error:
        pass

def show_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    
    menu_items = [
        ("Words Test (10 words)", "words"),
        ("Time Test (60s)", "time"),
        ("Forever Mode (no time limit)", "forever"),
        ("Exit", "exit")
    ]
    
    current_selection = 0
    
    while True:
        stdscr.clear()
        
        center_y = max_y // 2
        center_x = max_x // 2

        title = "typr"
        title_x = center_x - len(title) // 2
        stdscr.addstr(center_y - 4, title_x, title, curses.A_BOLD)
        
        for i, (display_text, mode) in enumerate(menu_items):
            y_pos = center_y - 2 + i
            x_pos = center_x - len(display_text) // 2
            
            if i == current_selection:
                stdscr.addstr(y_pos, x_pos - 2, "> ", curses.A_BOLD)
                stdscr.addstr(y_pos, x_pos, display_text, curses.A_BOLD | curses.A_REVERSE)
                stdscr.addstr(y_pos, x_pos + len(display_text), " <", curses.A_BOLD)
            else:
                stdscr.addstr(y_pos, x_pos, display_text)
        
        instructions = "Use ↑/↓ arrows to navigate, Enter to select"
        instr_x = center_x - len(instructions) // 2
        stdscr.addstr(center_y + 4, instr_x, instructions, curses.color_pair(4))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            current_selection = (current_selection - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % len(menu_items)
        elif key == 10 or key == 13:  # Enter
            selected_mode = menu_items[current_selection][1]
            if selected_mode == "exit":
                exit()
            return selected_mode
        elif key == 27 or key == 3:  # ESC or Ctrl+C
            exit()

def main():
    load_user_data()
    
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Correct
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Incorrect
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)    # Black on white

            if curses.can_change_color():
                GREY_INDEX = 8
                curses.init_color(GREY_INDEX, 500, 500, 500)  # 50% red, green, blue
                curses.init_pair(4, GREY_INDEX, curses.COLOR_BLACK)  # Grey text on black
            else:
                curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        typing_test(stdscr)
    except Exception as e:
        try:
            curses.endwin()
        except:
            pass
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            curses.endwin()
        except:
            pass

if __name__ == "__main__":
    global forgive_errors, test_type, time_limit, words_limit
    forgive_errors = False
    test_type = "words"
    time_limit = 60
    words_limit = 10
    
    if len(sys.argv) == 1:
        try:
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
            if curses.has_colors():
                curses.start_color()
                curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
                
                if curses.can_change_color():
                    GREY_INDEX = 8
                    curses.init_color(GREY_INDEX, 500, 500, 500)
                    curses.init_pair(4, GREY_INDEX, curses.COLOR_BLACK)
                else:
                    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
            
            selected_mode = show_menu(stdscr)
            test_type = selected_mode
            
            if test_type == "time":
                time_limit = 60
            
            curses.endwin()
            
        except Exception as e:
            try:
                curses.endwin()
            except:
                pass
            print(f"Menu Error: {e}")
            exit()
    else:
        if "--forgive-errors" in sys.argv:
            forgive_errors = True
        if "--time" in sys.argv:
            test_type = "time"
            time_limit = int(sys.argv[sys.argv.index("--time") + 1])
        if "--words" in sys.argv and test_type == "words":
            words_limit = int(sys.argv[sys.argv.index("--words") + 1])
        if "--forever" in sys.argv:
            test_type = "forever"
    
    main()