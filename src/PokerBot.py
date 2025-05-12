import time
import math
import random
import itertools
from collections import Counter

RANK_CHAR_TO_INT = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                    '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11,
                    'Q': 12, 'K': 13, 'A': 14}
SUITS = ['H', 'D', 'C', 'S']


def parse_card(card_str):
    rank_char = card_str[0]
    suit_char = card_str[1]
    return (RANK_CHAR_TO_INT[rank_char], suit_char)


class Deck:
    def __init__(self):
        self.cards = [(rank, suit) for rank in range(2, 15) for suit in SUITS]

    def remove(self, cards):
        remove_set = set(cards)
        self.cards = [c for c in self.cards if c not in remove_set]

    def draw(self, n):
        drawn = random.sample(self.cards, n)
        for c in drawn:
            self.cards.remove(c)
        return drawn

    def clone(self):
        new_deck = Deck()
        new_deck.cards = self.cards.copy()
        return new_deck


def evaluate_5cards(cards):
    ranks = sorted([r for (r, _) in cards], reverse=True)
    suits = [s for (_, s) in cards]
    count = Counter(ranks)

    is_flush = len(set(suits)) == 1
    unique_ranks = sorted(set(ranks), reverse=True)
    is_straight = False
    high_straight = None
    if len(unique_ranks) >= 5:
        for i in range(len(unique_ranks) - 4):
            window = unique_ranks[i:i+5]
            if window[0] - window[4] == 4:
                is_straight = True
                high_straight = window[0]
                break
        if not is_straight and set([14, 5, 4, 3, 2]).issubset(unique_ranks):
            is_straight = True
            high_straight = 5

    if is_flush and is_straight:
        return (9, high_straight)

    counts = sorted(count.items(), key=lambda x: (-x[1], -x[0]))

    if counts[0][1] == 4:
        four = counts[0][0]
        kicker = max(r for r in ranks if r != four)
        return (8, four, kicker)
    if counts[0][1] == 3 and counts[1][1] >= 2:
        return (7, counts[0][0], counts[1][0])
    if is_flush:
        return (6,) + tuple(ranks)
    if is_straight:
        return (5, high_straight)
    if counts[0][1] == 3:
        three = counts[0][0]
        kickers = [r for r in ranks if r != three][:2]
        return (4, three) + tuple(kickers)
    if counts[0][1] == 2 and counts[1][1] == 2:
        high_p, low_p = counts[0][0], counts[1][0]
        kicker = max(r for r in ranks if r not in (high_p, low_p))
        return (3, high_p, low_p, kicker)
    if counts[0][1] == 2:
        pair = counts[0][0]
        kickers = [r for r in ranks if r != pair][:3]
        return (2, pair) + tuple(kickers)
    return (1,) + tuple(ranks)


def best_hand_score(seven_cards):
    best = None
    for combo in itertools.combinations(seven_cards, 5):
        score = evaluate_5cards(combo)
        if not best or score > best:
            best = score
    return best


def evaluate_win(hole, opp_hole, board):
    our = best_hand_score(hole + board)
    opp = best_hand_score(opp_hole + board)
    if our > opp:
        return 1
    if our == opp:
        return 0.5
    return 0


def simulate(hole_cards, simulations=20000, time_limit=10.0):
    hole = [parse_card(c) for c in hole_cards]
    deck = Deck()
    deck.remove(hole)

    opp_combos = list(itertools.combinations(deck.cards, 2))
    n = len(opp_combos)
    wins_list = [0.0] * n
    visits = [0] * n

    wins = ties = losses = 0
    total = 0
    C = math.sqrt(2)
    start = time.perf_counter()

    while total < simulations and time.perf_counter() - start < time_limit:
        if total < n:
            idx = total
        else:
            ucb_scores = [
                (wins_list[i]/visits[i]) + C * math.sqrt(math.log(total) / visits[i])
                for i in range(n)
            ]
            idx = max(range(n), key=lambda i: ucb_scores[i])

        visits[idx] += 1
        total += 1

        opp = opp_combos[idx]
        sim_deck = deck.clone()
        sim_deck.remove(opp)

        board = sim_deck.draw(5)

        result = evaluate_win(hole, list(opp), board)
        wins_list[idx] += result

        if result == 1:
            wins += 1
        elif result == 0.5:
            ties += 1
        else:
            losses += 1

    sims_run = total
    win_rate = wins / sims_run if sims_run else 0
    tie_rate = ties / sims_run if sims_run else 0
    loss_rate = losses / sims_run if sims_run else 0
    decision = 'stay' if win_rate >= 0.5 else 'fold'

    print(f"Simulations run: {sims_run}")
    print(f"Win rate: {win_rate:.2%}")
    print(f"Tie rate: {tie_rate:.2%}")
    print(f"Loss rate: {loss_rate:.2%}")
    print(f"Times stayed (wins): {wins}")
    print(f"Times folded (losses): {losses}")
    print(f"Decision: {decision}")

if __name__ == '__main__':
    hand_input = input("Enter your starting hand (e.g. 'AH KD'): ")
    hole_cards = hand_input.upper().split()
    simulate(hole_cards)
