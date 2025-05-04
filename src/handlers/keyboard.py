from PyQt5.QtCore import Qt
from handlers.display import update_main_display

def handle_key_press(main_window, event):
    if event.key() == Qt.Key_1:
        main_window.show_combined = False
        main_window.current_channel = 0
        update_main_display(main_window)
        event.accept()
        return True
    elif event.key() == Qt.Key_2:
        main_window.show_combined = False
        main_window.current_channel = 1
        update_main_display(main_window)
        event.accept()
        return True
    elif event.key() == Qt.Key_3:
        main_window.show_combined = False
        main_window.current_channel = 2
        update_main_display(main_window)
        event.accept()
        return True
    elif event.key() == Qt.Key_A:
        main_window.show_combined = True
        update_main_display(main_window)
        event.accept()
        return True
    return False
