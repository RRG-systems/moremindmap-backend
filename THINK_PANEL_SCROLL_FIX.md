# THINK Panel Scroll Fix — COMPLETE ✓

## Problem
The THINK panel was expanding with each query instead of scrolling internally. Messages kept pushing the panel bigger.

## Root Cause
- `.think-chat-box` had `flex: 1` (expand to fill space)
- No fixed height or max-height
- `.think-messages` had no scroll constraint
- Container grew infinitely as messages accumulated

## Solution

### CSS Changes (`dashboard.css`)

**Before:**
```css
.think-chat-box {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.think-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
```

**After:**
```css
.think-chat-box {
    height: 300px;           /* FIXED HEIGHT */
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 0;
    background: #0f1419;
    border: 1px solid #1a2847;
    border-radius: 4px;
    margin-top: 8px;
}

.think-messages {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;        /* SCROLL INNER CONTAINER */
}
```

### JavaScript Fix (`think_chat_handler_fixed.js`)

Enhanced auto-scroll to bottom when new messages arrive:
```javascript
addMessage(role, text) {
    // ... create message ...
    this.messagesContainer.appendChild(msgDiv);
    
    // Scroll both containers to bottom
    setTimeout(() => {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        if (this.chatBox) this.chatBox.scrollTop = this.chatBox.scrollHeight;
    }, 0);
}
```

### HTML Cleanup (`dashboard.html`)

Removed conflicting inline styles from chat box div so CSS takes precedence:
```html
<!-- Before: had inline style="background: #0f1419; padding: 12px; ..." -->
<!-- After: clean, CSS-driven -->
<div id="thinkChatBox" class="think-chat-box hidden">
    <div id="thinkMessages" class="think-messages"></div>
</div>
```

## Result

✓ THINK panel maintains fixed height (300px)
✓ Messages scroll internally within that height
✓ Panel no longer expands with each query
✓ Auto-scroll to latest message works smoothly
✓ Clean separation: HTML structure, CSS styling, JS behavior

## Panel Behavior

```
┌─ THINK — DIAGNOSTIC ENGINE ────────────┐
│ How can I help you?                     │
└─────────────────────────────────────────┘

  [as user queries...]

┌─ THINK — DIAGNOSTIC ENGINE ────────────┐
│ [Scrollable area, max 300px height]     │
│ User: Why are we flat?                  │
│ Rocky: Current BRAIN state is FLAT...   │
│ User: What should we do?                │
│ Rocky: I recommend...                   │◄── New messages scroll into view
│ [scroll bar appears when content > 300px]   Auto-scroll to bottom
└─────────────────────────────────────────┘
[Input area]
```

## Files Modified

| File | Change |
|------|--------|
| `dashboard.css` | Fixed `.think-chat-box` to `height: 300px`, enabled scroll on `.think-messages` |
| `think_chat_handler_fixed.js` | Enhanced auto-scroll logic |
| `dashboard.html` | Removed conflicting inline styles |
