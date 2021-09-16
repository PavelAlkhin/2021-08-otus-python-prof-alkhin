#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    straight_ranks = straight(ranks)
    flush_hand = flush(hand)
    if len(straight_ranks) > 6 and len(flush_hand) > 6:
        return flush_hand, ranks

    kind_4 = kind(4, ranks)
    if len(kind_4):
        return kind_4, ranks

    kind_3 = kind(3, ranks)
    kind_2 = kind(2, ranks, kind_3)
    if len(kind_3) and len(kind_2):
        return kind_3, kind_2

    if len(flush_hand) > 4:
        return flush_hand, ranks

    if len(straight_ranks) > 4:
        return straight_ranks, ranks

    if len(kind_3):
        return kind_3, ranks

    two_pair_hand = two_pair(ranks)
    if len(two_pair_hand) > 1:
        return two_pair(ranks), ranks

    if len(kind_2):
        return kind_2, ranks

    return [], ranks


def card_ranks(hand, limit=0, reverse=True):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    x = sorted(iter(hand),
               key=lambda a: a['rank'],
               reverse=reverse)
    if limit != 0:
        return x[:limit]

    return x


def flush(hand):
    """Возвращает True, если все карты одной масти
    Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
    """
    """переделано на возврат готовой руки"""
    array_hand_c = []
    array_hand_s = []
    array_hand_h = []
    array_hand_d = []
    for xx in (x for x in iter(hand)):
        if xx['suit'] == 'C':
            array_hand_c.append(xx)

        elif xx['suit'] == 'S':
            array_hand_s.append(xx)

        elif xx['suit'] == 'H':
            array_hand_h.append(xx)

        elif xx['suit'] == 'D':
            array_hand_d.append(xx)

    if len(array_hand_c) >= 5:
        array_hand_c = card_ranks(array_hand_c, 5)
        return array_hand_c

    if len(array_hand_s) >= 5:
        array_hand_s = card_ranks(array_hand_s, 5)
        return array_hand_s

    if len(array_hand_h) >= 5:
        array_hand_h = card_ranks(array_hand_h, 5)
        return array_hand_h

    if len(array_hand_d) >= 5:
        array_hand_d = card_ranks(array_hand_d, 5)
        return array_hand_d

    return []


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    """переделано на возврат готовой руки"""
    list_hand = []
    for i in range(4):
        if find_sequence(ranks, i, i + 5):
            for i in range(i, i + 5):
                list_hand.append(ranks[i])
            return list_hand

    return list_hand


def find_sequence(iter_ranks, init_pos, end_pos):
    for i in range(init_pos, end_pos):
        current = iter_ranks[i]['rank']
        next = iter_ranks[i + 1]['rank']
        if current != next + 1:
            return False
    return True


def kind(n, ranks, exclude_ranks=[]):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    """Переделано на возвращение готовой руки есть подойдет"""
    for i in range(7):
        rank = ranks[i]['rank']
        x = iter(ranks)
        list_with_rank = (xx for xx in x if xx['rank'] == rank and xx not in exclude_ranks)

        h = []
        for el_rank in list_with_rank:
            h.append(el_rank)

        if len(h) >= n:
            sorted_hand = card_ranks(hand=h, limit=n)
            return sorted_hand

    return []


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    x = kind(2, ranks)
    return x


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    ret_hand = []
    list_best_hand, ranks = hand_rank(make_numeric_hand(hand))
    x_1 = iter(list_best_hand)
    for xx_1 in x_1:
        ret_hand.append(xx_1)

    if len(ret_hand) < 5:
        x = (xx for xx in iter(ranks) if xx not in ret_hand)
        hh = []
        for xx in x:
            hh.append(xx)

        x_2 = card_ranks(hand=hh, reverse=True)
        for xx_2 in iter(x_2):
            if len(ret_hand) < 5:
                ret_hand.append(xx_2)

    sorted_hand = card_ranks(hand=ret_hand, reverse=False)

    true_hand = []
    for xx in iter(sorted_hand):
        true_hand.append(f"{rev_define_rank(xx['rank'])}{xx['suit']}")

    return true_hand


def make_numeric_hand(hand):
    only_numeric_hand = []
    for xx in iter(hand):
        card = {'rank': define_rank(xx[0]), 'suit': xx[1]}
        only_numeric_hand.append(card)

    return only_numeric_hand


def define_rank(letter):
    if letter == 'T':
        rank = 10
    elif letter == 'J':
        rank = 11
    elif letter == 'Q':
        rank = 12
    elif letter == 'K':
        rank = 13
    elif letter == 'A':
        rank = 14
    else:
        rank = int(letter)

    return rank


def rev_define_rank(letter):
    if letter == 10:
        rank = 'T'
    elif letter == 11:
        rank = 'J'
    elif letter == 12:
        rank = 'Q'
    elif letter == 13:
        rank = 'K'
    elif letter == 14:
        rank = 'A'
    else:
        rank = str(letter)

    return rank


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


# def test_best_wild_hand():
#     print("test_best_wild_hand...")
#     assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
#             == ['7C', '8C', '9C', 'JC', 'TC'])
#     assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
#             == ['7C', 'TC', 'TD', 'TH', 'TS'])
#     assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
#             == ['7C', '7D', '7S', '7H', 'JD'])
#     print('OK')


if __name__ == '__main__':

    # hand = "6C 7C 8C 9C TC 5C JS".split()
    # hand = "TD TC TH 7C 7D 8C 8S".split()
    hand = "JD TC TH 7C 7D 7S 7H".split()

    best_h = best_hand(hand)
    print(best_h)


