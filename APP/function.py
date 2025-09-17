from rapidfuzz import fuzz
from rapidfuzz.fuzz import ratio as fuzz_ratio

def get_best_match(tc_name, df_candidates, radius_m):
    scores = []
    for _, row in df_candidates.iterrows():
        name_sim = fuzz.ratio(tc_name.upper(), row['Outlet Name'].upper())
        norm_dist = row['distance_m'] / radius_m
        final_score = 0.6 * name_sim + 0.4 * (1 - norm_dist) * 100
        scores.append((row["Outlet Name + Id"], final_score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0] if scores else None

def get_best_match_(tc_row, df_ra_nearby, radius):
    scores = []
    for _, ra_row in df_ra_nearby.iterrows():
        name_similarity = fuzz_ratio(tc_row['Outlet Name'].upper(), ra_row['Outlet Name'].upper())
        distance_m = ra_row['distance_m']
        proximity_score = max(0, (1 - distance_m / radius) * 100)
        total_score = 0.5 * name_similarity + 0.5 * proximity_score
        scores.append((ra_row, total_score))

    # Filtrer les scores > 50%
    filtered = [(row, score) for row, score in scores if score >= 65]
    if filtered:
        best_row, best_score = max(filtered, key=lambda x: x[1])
        return best_row["Outlet Name + Id"], best_score
    return None, 0

def get_best_match_t5(tc_row, df_ra_nearby, radius):
    scores = []
    for _, ra_row in df_ra_nearby.iterrows():
        # Mettre les noms en majuscules pour la comparaison
        tc_row['Outlet Name'] = tc_row['Outlet Name'].upper()
        ra_row['Outlet Name'] = ra_row['Outlet Name'].upper()

        # Remplacer "CAVE" er "CHEZ" par des espaces
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("CAVE", "").replace("CHEZ", "")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("CAVE", "").replace("CHEZ", "")
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("RESTAURANT ", "").replace("BAR ", "").replace("LOCAL ", "")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("RESTAURANT ", "").replace("BAR ", "").replace("LOCAL ", "")
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("TERRASSE ", "")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("TERRASSE ", "")

        # Remplacer "EST " par "ETS "
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("EST ", "ETS ")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("EST ", "ETS ")

        # Remplacer "EST " par "ETS "
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("ESPACE ", "")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("ESPACE ", "")

        # Remplacer les caractères spéciaux tels que "-", "'", ";" par des espaces
        ra_row['Outlet Name'] = ra_row['Outlet Name'].replace("-", " ").replace("'", " ").replace(";", " ")
        tc_row['Outlet Name'] = tc_row['Outlet Name'].replace("-", " ").replace("'", " ").replace(";", " ")

        # Calculer le score de similarité et la distance
        name_similarity = fuzz_ratio(tc_row['Outlet Name'].upper(), ra_row['Outlet Name'].upper())
        distance_m = ra_row['distance_m']
        proximity_score = max(0, (1 - distance_m / radius) * 100)
        total_score = 0.3 * name_similarity + 0.7 * proximity_score
        scores.append((ra_row, total_score))

    filtered = [(row, score) for row, score in scores if score >= 70]
    if filtered:
        best_row, best_score = max(filtered, key=lambda x: x[1])
        return best_row, best_score
    return None, 0