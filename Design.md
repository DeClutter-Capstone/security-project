# UI Design Guide — IEA Chat

Follow this exactly. The goal is a clean, modern 
messaging app similar to Messenger and WhatsApp. 
Nothing should look generated or template-like.

---

## Core Rules

- White is the dominant color everywhere
- Blue (#0084ff) is used only for: sent bubbles, 
  active states, the send button, links
- No gradients anywhere
- No heavy shadows — only subtle ones where needed
- No borders on inputs — use background color 
  difference instead
- Generous whitespace, nothing cramped
- Every interactive element has a hover state
- Font: system-ui everywhere, no imports needed

---

## Color Tokens

--white: #ffffff  
--bg-app: #ffffff  
--bg-sidebar: #f0f2f5  
--bg-input: #f0f2f5  
--bg-hover: #f0f2f5  
--bg-active: #e7f3ff  
--blue: #0084ff  
--blue-dark: #0073e6  
--bubble-sent: #0084ff  
--bubble-sent-text: #ffffff  
--bubble-received: #e4e6eb  
--bubble-received-text: #050505  
--text-primary: #050505  
--text-secondary: #65676b  
--text-placeholder: #bcc0c4  
--border: #e4e6eb  
--online-dot: #31a24c  
--error: #e41e3f  

---

## Login Page (index.html)

Layout: full viewport, white background, centered 
single card vertically and horizontally.

Card:
- White background
- Width: 400px
- Padding: 40px
- Border-radius: 12px
- Box-shadow: 0 2px 12px rgba(0,0,0,0.08)

Inside the card top to bottom:
- App name "IEA" in bold 28px --blue, centered, 
  margin-bottom 4px
- Subtitle "Private image messaging" in 14px 
  --text-secondary, centered, margin-bottom 32px
- Input fields: full width, background --bg-input, 
  border: none, border-radius: 10px, padding: 14px 16px, 
  font-size 15px, outline: none. On focus add 
  2px solid --blue border.
- Gap between inputs: 12px
- Login button: full width, background --blue, 
  color white, border: none, border-radius: 10px, 
  padding: 14px, font-size 15px, font-weight 600, 
  cursor pointer. Hover: --blue-dark. 
  Margin-top: 20px.
- Toggle text below button: "Don't have an account? 
  Sign up" — 14px --text-secondary, centered. 
  "Sign up" is --blue, cursor pointer, no underline.
- When toggled to register: same layout, button says 
  "Create Account", toggle says 
  "Already have an account? Log in"
- Error message if login fails: small red text 
  below button, 13px --error

No logo image. No illustrations. Just clean text 
and inputs.

---

## Chat Page (chat.html)

Full viewport. No scrollbars on the outer body. 
Three-column feel but actually two: sidebar + chat.

### Sidebar — 280px wide, fixed height, flex column

Background: --bg-sidebar

Top bar (60px tall):
- Left: "Chats" in bold 20px --text-primary, 
  padding-left 16px
- Right: circular button 36px, background --bg-hover, 
  no border, contains a + icon in --text-secondary. 
  Hover: slightly darker background.
- Vertically centered, padding 0 12px

Search bar below top bar (when + is clicked):
- Slides in smoothly (max-height transition)
- Input same style as login inputs but smaller: 
  padding 10px 14px, font-size 14px
- "Search username" placeholder
- Below input show result inline: 
  if found — green checkmark + username + "Add" 
  button in small blue pill
  if not found — "--text-secondary 13px "No user 
  found"

User list (scrollable, flex-grow 1):
Each user item — padding 8px 12px, border-radius 8px, 
margin 2px 8px, cursor pointer:
  - Left: avatar circle 44px. Background is a color 
    derived from username (use a simple hash of 
    charCode sum mod 6 to pick from 6 pleasant colors: 
    #f4845f #a8c5da #b8a9c9 #92c7a3 #f0c27f #7eb8c9). 
    White letter centered, font-size 18px font-weight 
    600.
  - Right of avatar: two lines. Top line: username, 
    14px font-weight 600 --text-primary. 
    Bottom line: "Tap to chat" in 13px --text-secondary.
  - Far right: green dot 10px if user is online, 
    nothing if offline.
  - Hover: background --bg-hover
  - Active/selected: background --bg-active, 
    username color --blue

No dividers between user items.

---

### Chat Area — flex-grow 1, flex column

#### Header — 60px, white, bottom border 1px --border
- Left: same avatar circle style as sidebar, 36px
- Username bold 16px --text-primary, margin-left 12px
- Online status below username: "Active now" in 13px 
  --online-dot if online, "Offline" in 13px 
  --text-secondary if offline
- All vertically centered, padding 0 16px

#### Messages area — flex-grow 1, overflow-y auto, 
padding 16px

Date separator if needed: 
  centered text, 12px --text-secondary, 
  margin 16px 0

Message group (consecutive messages from same sender 
within 2 minutes share a visual group — only first 
has avatar visible):

Received bubble:
  - Left aligned
  - Background --bubble-received, 
    color --bubble-received-text
  - Border-radius: 18px 18px 18px 4px
  - Padding: 10px 14px
  - Max-width: 65%
  - Font-size: 15px
  - Margin-bottom: 2px (4px for last in group)

Sent bubble:
  - Right aligned
  - Background --bubble-sent, color white
  - Border-radius: 18px 18px 4px 18px
  - Same padding, max-width, font-size

For sent images:
  Show "Image" with a small image icon inside the 
  blue bubble. No technical words. Just "Image".

For received images:
  Show a "View" button — white text, no background, 
  font-weight 600, inside the gray bubble. 
  Padding: 4px 0. Font-size 14px.
  After clicking View and loading, show the actual 
  image inside the bubble, max-width 240px, 
  border-radius 12px. Below image show "✓ Delivered" 
  in 12px --text-secondary if signature valid, 
  nothing if invalid (do not alarm the user).
  W