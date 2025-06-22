import time
import difflib
import random
import curses

letter_shown = {}
letter_correct = {}
letter_accuracy = {}
inverse_letter_accuracy = {}
letter_weight = {}
letter_time = {}

for i in range(32, 127):
    char = chr(i)
    letter_shown[char] = 0
    letter_correct[char] = 0
    letter_accuracy[char] = 0.0
    inverse_letter_accuracy[char] = 1.0
    letter_weight[char] = 0.0
    letter_time[char] = 0.0

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

average_time = 0.0

def typing_test(stdscr):
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

    for letter in letter_accuracy:
        inverse_letter_accuracy[letter] = 1 / letter_accuracy[letter] if letter_accuracy[letter] > 0 else 1.0

    if letter_time:
        average_time = sum(letter_time.values()) / len(letter_time)
    else:
        average_time = 1.0
    
    for letter in letter_accuracy:
        if letter in letter_time:
            letter_time[letter] = letter_time[letter] / average_time if average_time > 0 else 1.0
        else:
            letter_time[letter] = 1.0

    for letter in letter_accuracy:
        if letter in letter_time and letter in letter_frequency:
            letter_weight[letter] = (inverse_letter_accuracy[letter] * 
                                   letter_frequency[letter] * 
                                   letter_time[letter] / average_time if average_time > 0 else 1.0)
        else:
            letter_weight[letter] = letter_weight[letter]

    word_weight = {word: 1 for word in possible_words}
    for word in possible_words:
        for letter in word:
            if letter_accuracy[letter] > 0:
                word_weight[word] = word_weight[word] + letter_weight[letter]
            else:
                word_weight[word] = word_weight[word] + 2
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
    safe_addstr(start_row, 0, words_to_type, curses.color_pair(1))
    
    safe_addstr(6, 0, "Start typing:")
    stdscr.refresh()
    
    user_input = ""
    start_time = time.time()
    current_pos = 0
    
    while current_pos < len(words_to_type):
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break
        
        if key == 27:  # ESC to quit
            break
        elif key == curses.KEY_BACKSPACE or key == 8 or key == 127:  # Backspace
            if user_input:
                user_input = user_input[:-1]
                current_pos = len(user_input)
                
                try:
                    stdscr.move(start_row, 0)
                    stdscr.clrtoeol()
                except curses.error:
                    pass
                
                # Redraw text
                for i, char in enumerate(user_input):
                    if i < max_x - 1:
                        if char == words_to_type[i]:
                            safe_addstr(start_row, i, char, curses.color_pair(2))  # Correct - green
                        else:
                            safe_addstr(start_row, i, char, curses.color_pair(3))  # Incorrect - red
                
                remaining = words_to_type[len(user_input):]
                if len(user_input) < max_x - 1:
                    safe_addstr(start_row, len(user_input), remaining, curses.color_pair(1))  # Grey
                
        elif 32 <= key <= 126:  # Printable characters
            char = chr(key)
            user_input += char
            
            try:
                stdscr.move(start_row, 0)
                stdscr.clrtoeol()
            except curses.error:
                pass
            
            # Redraw text
            for i, typed_char in enumerate(user_input):
                if i < len(words_to_type) and i < max_x - 1:
                    letter_shown[words_to_type[i]] += 1
                    if typed_char == words_to_type[i]:
                        letter_time[typed_char] = time.time() - start_time
                        safe_addstr(start_row, i, typed_char, curses.color_pair(2))  # Correct - green
                        letter_correct[typed_char] += 1
                        letter_accuracy[typed_char] = letter_correct[typed_char] / letter_shown[typed_char]
                    else:
                        safe_addstr(start_row, i, typed_char, curses.color_pair(3))  # Incorrect - red
                        letter_accuracy[words_to_type[i]] = letter_correct[words_to_type[i]] / letter_shown[words_to_type[i]]
                        
            
            remaining = words_to_type[len(user_input):]
            if len(user_input) < max_x - 1:
                safe_addstr(start_row, len(user_input), remaining, curses.color_pair(1))  # Grey
            
            current_pos = len(user_input)
        
        try:
            stdscr.refresh()
        except curses.error:
            pass
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    accuracy = difflib.SequenceMatcher(None, words_to_type, user_input).ratio()
    wpm = (len(words_to_type.split()) / time_taken) * 60 if time_taken > 0 else 0
    
    safe_addstr(8, 0, f"Time taken: {time_taken:.2f} seconds")
    safe_addstr(9, 0, f"Words per minute: {wpm:.2f}")
    safe_addstr(10, 0, f"Accuracy: {accuracy * 100:.2f}%")
    letter_stats = [f"{letter}: {letter_accuracy[letter] * 100:.2f}%" for letter in letter_accuracy if letter_accuracy[letter] > 0]
    safe_addstr(11, 0, f"Letter accuracy: {', '.join(letter_stats)}")
    safe_addstr(12, 0, "Press esc to exit... Press any other key to continue")
    
    try:
        stdscr.refresh()
        key = stdscr.getch()
        if key == 27:
            return
        else:
            typing_test(stdscr)
    except curses.error:
        pass

def main():
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Correct
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Incorrect
        
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






