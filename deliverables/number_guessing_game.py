"""
Number Guessing Game
A fun game where you try to guess a randomly generated number!
"""

import random
import sys


def get_difficulty():
    """Let the player choose difficulty level."""
    print("\n🎮 Select Difficulty Level:")
    print("  1. Easy   (1-50,   10 attempts)")
    print("  2. Medium (1-100,  7 attempts)")
    print("  3. Hard   (1-500,  10 attempts)")
    print("  4. Expert (1-1000, 10 attempts)")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if choice in [1, 2, 3, 4]:
                difficulties = {
                    1: (50, 10, "Easy"),
                    2: (100, 7, "Medium"),
                    3: (500, 10, "Hard"),
                    4: (1000, 10, "Expert")
                }
                return difficulties[choice]
            else:
                print("❌ Please enter a number between 1 and 4.")
        except ValueError:
            print("❌ Invalid input! Please enter a number.")


def get_hint(secret_number, guess, attempts_left, max_attempts):
    """Provide a helpful hint to the player."""
    hint = ""
    
    # Temperature hint
    difference = abs(secret_number - guess)
    if difference == 0:
        hint = "🎯 Perfect!"
    elif difference <= 5:
        hint = "🔥 Burning hot!"
    elif difference <= 15:
        hint = "🌡️ Warm!"
    elif difference <= 30:
        hint = "❄️ Cold..."
    else:
        hint = "🥶 Freezing cold!"
    
    # Even/Odd hint (only after a few attempts)
    if attempts_left < max_attempts - 2:
        if secret_number % 2 == 0:
            hint += " (Hint: The number is even)"
        else:
            hint += " (Hint: The number is odd)"
    
    return hint


def play_game():
    """Main game logic."""
    print("\n" + "=" * 50)
    print("🎯  NUMBER GUESSING GAME  🎯")
    print("=" * 50)
    print("\nI'm thinking of a secret number...")
    
    # Get difficulty settings
    max_range, max_attempts, difficulty_name = get_difficulty()
    secret_number = random.randint(1, max_range)
    
    print(f"\n📊 Difficulty: {difficulty_name}")
    print(f"🔢 Range: 1 to {max_range}")
    print(f"💰 Attempts: {max_attempts}")
    print("-" * 50)
    
    attempts = 0
    guesses = []
    
    while attempts < max_attempts:
        attempts_left = max_attempts - attempts
        print(f"\n💭 Attempts remaining: {attempts_left}")
        
        # Get player's guess
        try:
            guess_input = input(f"Enter your guess (1-{max_range}): ").strip()
            
            # Check for quit command
            if guess_input.lower() in ['q', 'quit', 'exit']:
                print("\n👋 Game quit. Thanks for playing!")
                return
            
            guess = int(guess_input)
            
            if guess < 1 or guess > max_range:
                print(f"❌ Please enter a number between 1 and {max_range}.")
                continue
                
        except ValueError:
            print("❌ Invalid input! Please enter a valid number.")
            continue
        
        attempts += 1
        guesses.append(guess)
        
        # Check the guess
        if guess == secret_number:
            print("\n" + "🎉" * 20)
            print(f"🎊 CONGRATULATIONS! You guessed it in {attempts} attempts!")
            print("🎉" * 20)
            
            # Score based on attempts
            score = (max_attempts - attempts + 1) * 100
            if difficulty_name == "Medium":
                score *= 2
            elif difficulty_name == "Hard":
                score *= 4
            elif difficulty_name == "Expert":
                score *= 8
            print(f"🏆 Your score: {score} points")
            break
            
        elif guess < secret_number:
            hint = get_hint(secret_number, guess, attempts, max_attempts)
            print(f"📈 Too low! {hint}")
        else:
            hint = get_hint(secret_number, guess, attempts, max_attempts)
            print(f"📉 Too high! {hint}")
        
        # Show previous guesses
        if len(guesses) > 1:
            print(f"📝 Your guesses: {', '.join(map(str, guesses))}")
    
    else:
        # Out of attempts
        print("\n" + "💔" * 20)
        print("😢 GAME OVER! You ran out of attempts.")
        print(f"The secret number was: {secret_number}")
        print("💔" * 20)
    
    # Show game statistics
    print("\n📊 Game Statistics:")
    print(f"   • Total attempts: {attempts}")
    print(f"   • All guesses: {', '.join(map(str, guesses))}")


def main():
    """Main entry point."""
    while True:
        play_game()
        
        # Ask if player wants to play again
        print("\n" + "-" * 50)
        play_again = input("\n🔄 Would you like to play again? (yes/no): ").strip().lower()
        
        if play_again not in ['yes', 'y', 'sure', 'ok']:
            print("\n👋 Thanks for playing! Goodbye! 🎮")
            break
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
        sys.exit(0)