"""
THINK Entrance Messages — Random cool startup lines when ROCKY enters THINK.

Each trading session gets a fresh, random announcement.
"""

import random


ENTRANCE_MESSAGES = [
    # Classic hype
    "🎙️ LET'S GET READY TO RUMBLE",
    "🚀 ROCKY IS IN THE BUILDING",
    "⚡ BUCKLE UP, THIS IS GONNA BE FUN",
    "🏎️ ENGINES IGNITED. LET'S MAKE MONEY.",
    "🎬 IT'S SHOWTIME.",
    
    # Movie references
    "🎭 Here's looking at you, markets.",
    "🔥 May the odds be ever in our favor.",
    "💥 This is gonna be LEGENDARY.",
    "🌟 Winter is coming. Profits too.",
    "⚔️ For Frodo! (And tendies.)",
    
    # Trading vibes
    "📈 Green day incoming.",
    "💰 The printer goes brrrrr.",
    "🎰 Let's roll the dice.",
    "🧠 Big brain trading time.",
    "💎 Diamonds are formed under pressure.",
    
    # Sci-fi cool
    "🛸 Initiating profit sequence.",
    "🤖 AI operators online.",
    "👽 Your mission, should you choose to accept it...",
    "⏰ Time to make history.",
    "🔮 The future is now.",
    
    # Chaotic energy
    "🌪️ Hold onto your hats.",
    "🎪 The circus is open.",
    "🎸 TURN IT UP TO 11",
    "🍕 Let's make some dough.",
    "🎯 TARGET LOCKED.",
    
    # Subtle flex
    "😎 Cool guys don't look at volatility.",
    "🏆 This is what winning looks like.",
    "👑 King of the hill, baby.",
    "🌈 Rainbow after the storm.",
    "🎊 Party's starting.",
    
    # Random chaos
    "🐉 Here be dragons (and gains).",
    "🚁 Incoming hot drop.",
    "🍷 Let's wine and grind.",
    "🎺 Trumpet sounds intensify.",
    "🦆 Quack quack, here comes the stack.",
    
    # Operator style
    "🤫 We're going dark. Into profit.",
    "⏳ Time to print.",
    "🎓 School is in session.",
    "🧬 Evolution in progress.",
    "🔬 Running the experiment.",
    
    # Aggressive
    "💪 SHOW THESE MARKETS WHO'S BOSS",
    "🥊 READY TO FIGHT",
    "⚡ MAXIMUM OVERDRIVE",
    "🌪️ UNLEASH THE KRAKEN",
    "🎯 ZERO MERCY MODE",
    
    # Chill
    "☕ Coffee's brewing. Profits too.",
    "🌅 Another day, another dollar.",
    "🎵 And the beat goes on.",
    "🌊 Riding the wave.",
    "🧘 Zen mode activated.",
]

EXIT_MESSAGES = [
    "🎸 ROCKY has left the building!",
    "👋 See you next time, champ.",
    "🌅 Trading day complete. Go rest.",
    "💤 ROCKY's logged off.",
    "🚪 Heading out. Profits in tow.",
    "✌️ Peace out, traders.",
    "🎬 That's a wrap, folks.",
    "🏁 Session closed. GG.",
    "🌙 Until next time...",
    "📺 Switching to standby.",
]


def get_random_entrance():
    """Get a random entrance message."""
    return random.choice(ENTRANCE_MESSAGES)


def get_random_exit():
    """Get a random exit message."""
    return random.choice(EXIT_MESSAGES)
