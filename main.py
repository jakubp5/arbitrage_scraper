import json
from collections import defaultdict
from fortuna_scraper import FortunaScraper
from doxxbet_scraper import DoxxbetScraper
from nike_scraper import NikeScraper
from etipos_scraper import EtiposScraper
from name_matcher import NameMatcher

def run_all_scrapers():
    scrapers = [
        FortunaScraper(),
        DoxxbetScraper(),
        NikeScraper(),
        EtiposScraper()
    ]

    all_matches = []

    for scraper in scrapers:
        print(f"Scraping from {scraper.name}...")
        raw_html = scraper.scrape()

        if raw_html:
            parsed_data = scraper.parse(raw_html)
            all_matches.extend(parsed_data)
            print(f"Successfully scraped data from {scraper.name}: {len(parsed_data)} matches found.")
        else:
            print(f"Failed to scrape data from {scraper.name}")

    return all_matches

def build_odds_dict(all_matches, matcher):
    odds_dict = defaultdict(lambda: defaultdict(list))

    for match in all_matches:
        try:
            participant1, odds1, participant2, odds2, bookmaker = match

            participant1 = matcher.match(participant1)
            participant2 = matcher.match(participant2)

            # Consistent event key order
            players = sorted([participant1, participant2])
            event_key = f"{players[0]} vs {players[1]}"

            odds_dict[event_key][participant1].append({
                "odds": float(odds1),
                "bookmaker": bookmaker
            })
            odds_dict[event_key][participant2].append({
                "odds": float(odds2),
                "bookmaker": bookmaker
            })
        except Exception as e:
            print(f"⚠️ Skipping bad data: {match} ({e})")

    return odds_dict

def find_arbitrage(odds_dict, min_profit_margin=0.0, verbose=False, find_closest_to_arbitrage=False):
    arbitrage_opportunities = []
    closest_to_arbitrage = None  # Stores the match closest to arbitrage (but not profitable)

    for event, participants in odds_dict.items():
        if len(participants) < 2:
            continue

        best_odds = {}
        for player, offers in participants.items():
            best_offer = max(offers, key=lambda o: o["odds"])
            best_odds[player] = best_offer

        if len(best_odds) < 2:
            continue

        inv_sum = sum(1 / offer["odds"] for offer in best_odds.values())
        profit_margin = (1 - inv_sum) * 100

        if inv_sum < 1 and profit_margin >= min_profit_margin:
            opportunity = {
                "event": event,
                "outcomes": best_odds,
                "profit_margin": profit_margin,
                "inv_sum": inv_sum,
            }
            arbitrage_opportunities.append(opportunity)
            print(f"✅ Arbitrage found in: {event}")
            for player, offer in best_odds.items():
                print(f"  → {player}: {offer['odds']} ({offer['bookmaker']})")
            print(f"  💰 Profit margin: {profit_margin:.2f}%\n")

        elif find_closest_to_arbitrage:
            # Track the match with the smallest inv_sum ≥ 1 (closest to arbitrage)
            if closest_to_arbitrage is None or inv_sum < closest_to_arbitrage["inv_sum"]:
                closest_to_arbitrage = {
                    "event": event,
                    "outcomes": best_odds,
                    "inv_sum": inv_sum,
                    "loss_margin": (inv_sum - 1) * 100,  # How much you lose
                }

        elif verbose:
            print(f"❌ No arbitrage in: {event}")
            for player, offer in best_odds.items():
                print(f"  → {player}: {offer['odds']} ({offer['bookmaker']})")
            print(f"  💰 Inverse sum: {inv_sum:.4f}\n")

    if find_closest_to_arbitrage and closest_to_arbitrage:
        print("\n🔍 Closest to arbitrage (but still a loss):")
        print(f"Event: {closest_to_arbitrage['event']}")
        for player, offer in closest_to_arbitrage["outcomes"].items():
            print(f"  → {player}: {offer['odds']} ({offer['bookmaker']})")
        print(f"  💸 Loss margin: {closest_to_arbitrage['loss_margin']:.2f}%")
        print(f"  📊 Inverse sum: {closest_to_arbitrage['inv_sum']:.4f}\n")

    return arbitrage_opportunities

if __name__ == "__main__":
    matcher = NameMatcher()
    matches = run_all_scrapers()
    dict_matches = build_odds_dict(matches, matcher)

    #save dict_matches to a file
    with open('odds_dict.json', 'w') as f:
        json.dump(dict_matches, f, indent=4)

    find_arbitrage(dict_matches, min_profit_margin=0.1, verbose=False, find_closest_to_arbitrage=True)




