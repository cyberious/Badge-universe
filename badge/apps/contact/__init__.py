from badgeware import screen, PixelFont, shapes, brushes, run, io

# Load a font
font = PixelFont.load("/system/assets/fonts/ark.ppf")

# Contact preference states: 0 = handshake, 1 = fist bump, 2 = no contact
contact_modes = ["Handshake", "Fist Bump", "No Contact"]
current_mode = 0

# State for each icon (True = OK/Green, False = Not OK/Red)
icon_states = [True, True, False]  # Default: handshake OK, fist bump OK, no contact not OK

def draw_icon(x, y, icon_type, is_active):
    """Draw a contact icon with OK/Not OK indicator"""
    
    # Icon background box
    if is_active:
        screen.brush = brushes.color(100, 100, 255)  # Blue highlight for active
    else:
        screen.brush = brushes.color(60, 60, 60)  # Gray background
    screen.draw(shapes.rounded_rectangle(x, y, 40, 50, 4))
    
    # Draw the icon symbol
    screen.brush = brushes.color(255, 255, 255)
    
    if icon_type == 0:  # Handshake
        # Draw a simplified handshake icon
        screen.draw(shapes.rectangle(x + 8, y + 20, 8, 12))  # Left hand
        screen.draw(shapes.rectangle(x + 24, y + 20, 8, 12))  # Right hand
        screen.draw(shapes.rectangle(x + 12, y + 25, 16, 3))  # Connecting clasp
        # Thumbs
        screen.draw(shapes.rectangle(x + 8, y + 18, 3, 4))
        screen.draw(shapes.rectangle(x + 29, y + 18, 3, 4))
    
    elif icon_type == 1:  # Fist bump
        # Draw two fists bumping
        screen.draw(shapes.rounded_rectangle(x + 8, y + 22, 10, 12, 2))  # Left fist
        screen.draw(shapes.rounded_rectangle(x + 22, y + 22, 10, 12, 2))  # Right fist
        # Impact lines
        screen.draw(shapes.line(x + 18, y + 20, x + 22, y + 16))
        screen.draw(shapes.line(x + 18, y + 35, x + 22, y + 39))
    
    elif icon_type == 2:  # No contact
        # Draw a hand with "stop" gesture
        screen.draw(shapes.rounded_rectangle(x + 12, y + 18, 16, 18, 2))  # Palm
        # Fingers
        screen.draw(shapes.rectangle(x + 14, y + 12, 3, 8))
        screen.draw(shapes.rectangle(x + 18, y + 10, 3, 10))
        screen.draw(shapes.rectangle(x + 22, y + 11, 3, 9))
        screen.draw(shapes.rectangle(x + 26, y + 13, 3, 7))
    
    # Draw OK/Not OK indicator
    indicator_y = y + 38
    indicator_x = x + 20
    
    if icon_states[icon_type]:
        # Green OK circle with checkmark
        screen.brush = brushes.color(0, 200, 0)  # Green
        screen.draw(shapes.circle(indicator_x, indicator_y, 6))
        # Simple checkmark
        screen.brush = brushes.color(255, 255, 255)
        screen.draw(shapes.line(indicator_x - 2, indicator_y, indicator_x - 1, indicator_y + 2))
        screen.draw(shapes.line(indicator_x - 1, indicator_y + 2, indicator_x + 2, indicator_y - 2))
    else:
        # Red Not OK circle with X
        screen.brush = brushes.color(200, 0, 0)  # Red
        screen.draw(shapes.circle(indicator_x, indicator_y, 6))
        # X mark
        screen.brush = brushes.color(255, 255, 255)
        screen.draw(shapes.line(indicator_x - 3, indicator_y - 3, indicator_x + 3, indicator_y + 3))
        screen.draw(shapes.line(indicator_x - 3, indicator_y + 3, indicator_x + 3, indicator_y - 3))
    
    # Draw label below icon
    screen.brush = brushes.color(255, 255, 255)
    screen.font = PixelFont.load("/system/assets/fonts/memo.ppf")  # Smaller font for labels
    label_text = ["Shake", "Bump", "No"][icon_type]
    w, _ = screen.measure_text(label_text)
    screen.text(label_text, x + 20 - w // 2, y + 48)

def update():
    global current_mode, icon_states
    
    # Handle button presses to toggle icon states
    # Button A toggles handshake
    if io.BUTTON_A in io.pressed:
        icon_states[0] = not icon_states[0]
    
    # Button B toggles fist bump
    if io.BUTTON_B in io.pressed:
        icon_states[1] = not icon_states[1]
    
    # Button C toggles no contact
    if io.BUTTON_C in io.pressed:
        icon_states[2] = not icon_states[2]
    
    # Clear screen with black background
    screen.brush = brushes.color(0, 0, 0)
    screen.draw(shapes.rectangle(0, 0, 160, 120))
    
    # Draw title
    screen.brush = brushes.color(211, 250, 55)  # Yellow
    screen.font = font
    title = "Contact Prefs"
    w, h = screen.measure_text(title)
    screen.text(title, 80 - w // 2, 8)
    
    # Draw the three icons
    draw_icon(10, 25, 0, False)   # Handshake (Button A)
    draw_icon(60, 25, 1, False)   # Fist Bump (Button B)
    draw_icon(110, 25, 2, False)  # No Contact (Button C)
    
    # Draw button labels at bottom
    screen.brush = brushes.color(150, 150, 150)
    screen.font = PixelFont.load("/system/assets/fonts/memo.ppf")
    screen.text("A", 25, 108)
    screen.text("B", 75, 108)
    screen.text("C", 125, 108)
    
    # Draw current status message
    screen.brush = brushes.color(255, 255, 255)
    active_prefs = []
    if icon_states[0]:
        active_prefs.append("Shake")
    if icon_states[1]:
        active_prefs.append("Bump")
    if not icon_states[2] and not icon_states[0] and not icon_states[1]:
        active_prefs.append("No Contact")
    
    if active_prefs:
        status = "OK: " + ", ".join(active_prefs)
    else:
        status = "No contact OK"
    
    w, _ = screen.measure_text(status)
    if w < 160:
        screen.text(status, 80 - w // 2, 95)
    
    return None

if __name__ == "__main__":
    run(update)
