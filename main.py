import time
import random
import curses
import json
import os
from datetime import datetime

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
forgive_errors = False

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
    
    with open("words_i_like.txt", "r") as f:
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
    for _ in range(10):
        word = random.choices(possible_words, weights=word_weight.values(), k=1)[0]
        test_text = words_to_type + (" " if words_to_type else "") + word
        if len(test_text) < max_x - 5:
            words_to_type = test_text
            word_count += 1
            if word_count >= 10:
                break
        else:
            break
    
    if not words_to_type:
        words_to_type = "hello world test"
    
    def safe_addstr(y, x, text, attr=0):
        try:
            if y < max_y and x < max_x:
                available_width = max_x - x - 1
                if len(text) > available_width:
                    text = text[:available_width]
                stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    safe_addstr(0, 0, "Welcome to the typing test!")
    safe_addstr(2, 0, "Type the text below:")
    
    start_row = 4
    safe_addstr(start_row, 0, words_to_type, curses.color_pair(4))
    
    stdscr.refresh()
    
    user_input = ""
    start_time = time.time()
    last_keystroke_time = start_time
    current_pos = 0
    
    while current_pos < len(words_to_type):
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break
        
        if key == 27 or key == 3:  # ESC or Ctrl+C to quit
            break
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
                
                try:
                    stdscr.move(start_row, 0)
                    stdscr.clrtoeol()
                except curses.error:
                    pass
                
                for i, char in enumerate(user_input):
                    if i < max_x - 1:
                        if char == words_to_type[i]:
                            safe_addstr(start_row, i, char, curses.color_pair(2))  # Correct - green
                        else:
                            safe_addstr(start_row, i, char, curses.color_pair(3))  # Incorrect - red
                
                remaining = words_to_type[len(user_input):]
                if len(user_input) < max_x - 1:
                    safe_addstr(start_row, len(user_input) + 1, remaining[1:], curses.color_pair(4))  # Grey
                    safe_addstr(start_row, len(user_input), remaining[:1], curses.color_pair(4) | curses.A_UNDERLINE | curses.A_BOLD)  # Grey
                
        elif 32 <= key <= 126:  # Printable characters
            char = chr(key)
            current_time = time.time()
            
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
            
            try:
                stdscr.move(start_row, 0)
                stdscr.clrtoeol()
            except curses.error:
                pass
            
            for i, typed_char in enumerate(user_input):
                if i < len(words_to_type) and i < max_x - 1:
                    if typed_char == words_to_type[i]:
                        safe_addstr(start_row, i, typed_char, curses.color_pair(2))  # Correct - green
                    else:
                        safe_addstr(start_row, i, typed_char, curses.color_pair(3))  # Incorrect - red
            
            remaining = words_to_type[len(user_input):]
            if len(user_input) < max_x - 1:
                safe_addstr(start_row, len(user_input) + 1, remaining[1:], curses.color_pair(4))  # Grey
                safe_addstr(start_row, len(user_input), remaining[:1], curses.color_pair(4) | curses.A_UNDERLINE | curses.A_BOLD)  # Grey
            
        try:
            stdscr.refresh()
        except curses.error:
            pass
    
    end_time = time.time()
    time_taken = end_time - start_time
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
    if new_accuracy > 0.5:
        save_user_data(test_results)
        safe_addstr(11, 0, "Test results saved", curses.color_pair(2))
    else:
        safe_addstr(11, 0, "The test results are not saved because the accuracy is too low", curses.color_pair(3))


    safe_addstr(7, 0, f"WPM: {wpm:.2f}")
    safe_addstr(8, 0, f"Accuracy: {new_accuracy * 100:.2f}%")
    # 9
    # 10
    # 11 (test results saved)
    safe_addstr(12, 0, f"Time taken: {time_taken:.2f} seconds")
    safe_addstr(13, 0, f"Avg. Accuracy: {accuracy * 100:.2f}%")
    safe_addstr(15, 0, "Press esc to exit... Press any other key to continue")
    
    calculate_letter_stats()
    
    try:
        stdscr.refresh()
        key = stdscr.getch()
        if key == 27 or key == 3:
            exit()
        else:
            typing_test(stdscr)
    except curses.error:
        pass

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
    main()