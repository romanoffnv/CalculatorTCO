def assess_sup(sups_rating):
    statuses = ["Gold", "Silver", "Bronze"]
    # Sort by rating descending
    sorted_items = sorted(sups_rating.items(), key=lambda x: x[1], reverse=True)

    # Group suppliers by their rating
    rating_groups = {}
    for supplier, rating in sorted_items:
        rating_groups.setdefault(rating, []).append(supplier)

    result = {}
    status_index = 0
    for rating in sorted(rating_groups.keys(), reverse=True):
        suppliers = rating_groups[rating]
        # Assign same status to all suppliers with the same rating
        status = statuses[status_index] if status_index < len(statuses) else "No Status"
        for supplier in suppliers:
            result[supplier] = [rating, status]
        status_index += 1

    return result
