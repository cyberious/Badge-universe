# Contact Preferences App

A badge app that displays your contact preferences with three interaction modes: handshake, fist bump, and no contact. Each mode has a visual indicator showing whether it's OK or not OK for others to engage with you in that way.

## Features

- **Three Contact Modes**: Handshake, Fist Bump, and No Contact
- **Visual Indicators**: Green circle with checkmark (OK) or red circle with X (Not OK)
- **Interactive Buttons**: Toggle each preference using the A, B, and C buttons
- **Status Display**: Shows which contact methods are currently acceptable

## How to Use

### Button Controls

- **Button A**: Toggle Handshake preference (OK/Not OK)
- **Button B**: Toggle Fist Bump preference (OK/Not OK)
- **Button C**: Toggle No Contact preference (OK/Not OK)

### Default Settings

The app starts with these default preferences:
- Handshake: ✓ OK (Green)
- Fist Bump: ✓ OK (Green)
- No Contact: ✗ Not OK (Red)

Press any button to toggle that specific contact preference.

## Display

The app shows:
1. **Title**: "Contact Prefs" at the top
2. **Three Icons**: Visual representations of each contact type
   - Left icon: Handshake (Button A)
   - Middle icon: Fist Bump (Button B)
   - Right icon: No Contact/Stop Hand (Button C)
3. **Indicators**: Green circles with checkmarks (OK) or red circles with X marks (Not OK)
4. **Button Labels**: A, B, C labels at the bottom showing which button controls which icon
5. **Status Message**: Current acceptable contact methods

## Installation

1. Enter USB Mass Storage mode on your badge (double-press Reset button)
2. Copy the `/apps/contact/` folder to the badge's `/apps/` directory
3. Restart your badge or return to the menu
4. Select "contact" from the app menu

## Use Cases

- **Conferences**: Let people know your preferred greeting style
- **Networking Events**: Display your contact comfort level
- **Social Settings**: Communicate boundaries clearly and visibly
- **Personal Space**: Show when you prefer minimal or no physical contact

## Technical Details

- Built for Tufty Badge (GitHub Universe 2025 Edition)
- Uses badgeware library for graphics and input
- Implements simple icon drawing with shapes
- Real-time button input handling
