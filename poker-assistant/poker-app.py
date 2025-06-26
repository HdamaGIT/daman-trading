import streamlit as st
from treys import Card, Evaluator, Deck
import random
import os
import sys
from collections import Counter

# --- Title ---
st.title("♠️ Poker Hand Assistant")

# --- Sidebar Inputs ---
with st.sidebar:
    if st.button("🔄 Next Hand"):
        st.session_state.clear()
        st.session_state.active_opponents = st.session_state.get("total_players", 6)
        st.rerun()

    total_players = st.number_input("Total number of players at the table:", min_value=2, step=1, value=6)
    pot_size = st.number_input("Pot size (in BB):", min_value=0.0, step=0.5)
    bet_to_call = st.number_input("Amount to call (in BB):", min_value=0.0, step=0.5)
    active_opponents = st.number_input("Number of opponents still in the hand:", min_value=1, step=1, value=1)
    position = st.selectbox("Your table position:", options=["Early", "Middle", "Late", "Small Blind", "Big Blind"])

# --- Input Section ---
hole_cards = st.text_input("Enter your hole cards (e.g., Ah Ks):")
flop = st.text_input("Flop (optional, e.g., Qd Jc 9h):")
turn = st.text_input("Turn (optional, e.g., 2s):")
river = st.text_input("River (optional, e.g., 7h):")

# --- Utility: Hand Strength Ranking ---
def get_hand_strength_rank(card1, card2):
    ranks = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8,
             '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

    def rank(card): return card[0].upper()
    def suit(card): return card[1].lower()

    r1 = rank(card1)
    r2 = rank(card2)
    s1 = suit(card1)
    s2 = suit(card2)

    suited = s1 == s2
    r1v = ranks.get(r1, 0)
    r2v = ranks.get(r2, 0)

    pair = r1 == r2

    if pair and r1v >= 12:
        return 1
    if {r1 + r2, r2 + r1} & {'AK', 'KA'} and suited:
        return 1
    if {r1 + r2, r2 + r1} & {'AK', 'KA'}:
        return 1
    if pair and r1v >= 9:
        return 2
    if {r1 + r2, r2 + r1} & {'AQ', 'AJ', 'KQ'} and suited:
        return 2
    if {r1 + r2, r2 + r1} & {'AJ', 'KQ', 'QJ'}:
        return 2

    return 3

# --- Pot Odds Calculator ---
def calculate_pot_odds(pot, call):
    if call == 0:
        return 0
    return round((call / (pot + call)) * 100, 2)

# --- Expected Value ---
def calculate_ev(win_pct, pot, call):
    win_fraction = win_pct / 100
    return round((win_fraction * pot) - ((1 - win_fraction) * call), 2)

# --- Draw Detection ---
def detect_draws(board):
    draw_msgs = []
    if len(board) < 3:
        return draw_msgs

    suits = [Card.int_to_str(card)[1] for card in board]
    suit_counts = Counter(suits)
    if max(suit_counts.values()) == 4:
        draw_msgs.append("You have a flush draw.")

    ranks = sorted([Card.get_rank_int(card) for card in board])
    for i in range(len(ranks) - 2):
        window = ranks[i:i+3]
        if max(window) - min(window) == 3:
            draw_msgs.append("You may have a straight draw.")
            break

    return draw_msgs

# --- Win Probability Simulator ---
def run_win_simulation(hole_cards, community_cards, num_opponents=1, num_simulations=500):
    evaluator = Evaluator()
    deck = Deck()

    seen = set()
    for card in hole_cards + community_cards:
        if card in seen:
            continue
        seen.add(card)
        if card in deck.cards:
            deck.cards.remove(card)

    wins = 0
    ties = 0
    for _ in range(num_simulations):
        deck.shuffle()
        opponent_hands = [[deck.draw(1)[0], deck.draw(1)[0]] for _ in range(num_opponents)]
        remaining_board = community_cards[:]

        while len(remaining_board) < 5:
            remaining_board.append(deck.draw(1)[0])

        hero_score = evaluator.evaluate(remaining_board, hole_cards)
        opponent_scores = [evaluator.evaluate(remaining_board, hand) for hand in opponent_hands]

        if all(hero_score < score for score in opponent_scores):
            wins += 1
        elif any(hero_score == score for score in opponent_scores):
            ties += 1

    win_pct = round(100 * wins / num_simulations, 2)
    tie_pct = round(100 * ties / num_simulations, 2)
    return win_pct, tie_pct

# --- Evaluation Logic ---
if hole_cards:
    try:
        cards = [c[0].upper() + c[1].lower() for c in hole_cards.split() if len(c) == 2]
        if len(cards) != 2:
            st.error("Please enter exactly two hole cards, like 'Ah Ks'.")
        else:
            tier = get_hand_strength_rank(cards[0], cards[1])
            odds = calculate_pot_odds(pot_size, bet_to_call)

            if tier == 1:
                st.success("Preflop Tier: **Premium**\n✅ Recommend: **Call or Raise**")
            elif tier == 2:
                st.info("Preflop Tier: **Playable**\n⚠️ Recommend: **Consider Calling** depending on raise size and players left.")
            else:
                st.warning("Preflop Tier: **Weak**\n❌ Recommend: **Fold** unless pot odds are exceptional.")

            st.write(f"**Pot Odds:** {odds}%")
            if odds < 15 and tier == 3:
                st.info("Pot odds are low and hand is weak. Recommend folding.")
            elif odds >= 20 and tier != 1:
                st.info("Pot odds may justify a call with marginal hands.")

            if position == "Early":
                st.write("📍 Early position: be more cautious, tighter range advised.")
            elif position == "Late":
                st.write("📍 Late position: wider range acceptable, use positional advantage.")
            elif position == "Small Blind":
                st.write("📍 Small Blind: consider implied odds and post-flop disadvantage.")

            hero_hole = [Card.new(c) for c in cards]
            full_board = []

            if flop:
                flop_cards = [card for card in flop.split() if len(card) == 2]
                full_board.extend([Card.new(card[0].upper() + card[1].lower()) for card in flop_cards])

            if turn and len(turn.strip()) == 2:
                full_board.append(Card.new(turn.strip()[0].upper() + turn.strip()[1].lower()))

            if river and len(river.strip()) == 2:
                full_board.append(Card.new(river.strip()[0].upper() + river.strip()[1].lower()))

            win_pct, tie_pct = run_win_simulation(hero_hole, full_board, num_opponents=active_opponents)

            st.write(f"**Win % (vs {active_opponents} opponent{'s' if active_opponents > 1 else ''}):** {win_pct}%")
            st.write(f"**Tie %:** {tie_pct}%")

            evaluator = Evaluator()
            completed_board = full_board + [Card.new(c) for c in ['2h'] * (5 - len(full_board))]
            hand_score = evaluator.evaluate(completed_board, hero_hole)
            hand_class = evaluator.get_rank_class(hand_score)
            hand_name = evaluator.class_to_string(hand_class)
            st.write(f"**Current Best Hand (with simulated board):** {hand_name}")

            ev = calculate_ev(win_pct, pot_size, bet_to_call)
            st.write(f"**Expected Value (EV) of Calling:** {ev} BB")

            # --- Advice Rationales ---
            st.markdown("### 🧠 Advice Rationale")
            st.write(f"Hand Tier: {tier}")
            st.write(f"Pot Odds: {odds}% vs Win %: {win_pct}%")
            if win_pct < odds:
                st.write("⚠️ Your win probability is lower than required by pot odds. Consider folding.")
            else:
                st.write("✅ Win probability exceeds pot odds. Call may be justified.")

            # --- Draw Detection Output ---
            draws = detect_draws(full_board + hero_hole)
            for draw_msg in draws:
                st.info(draw_msg)

    except Exception as e:
        st.error(f"Error evaluating hand: {e}")
else:
    st.info("Enter your hole cards above to get started.")
