

total = 32

test_list = []

for i in range(total):
    test_list.append(f"nyan{i}")

total = 464
items_per_page = 100
current_page = 2


def get_pagination_ranges(total, items_per_page, current_page):
    page_count = (total + items_per_page - 1) // items_per_page

    def get_page_range(page):
        start_index = (page - 1) * items_per_page
        end_index = min(start_index + items_per_page, total)
        return start_index, end_index
   
    current_start, current_end = get_page_range(current_page)

    previous_page = current_page - 1 if current_page > 1 else page_count
    next_page = current_page + 1 if current_page < page_count else 1

    previous = get_page_range(previous_page)
    next_p = get_page_range(next_page)

    return {
        "previous_page": previous,
        "current_page": (current_start, current_end),
        "next_page": next_p
    }


pages = get_pagination_ranges(total, items_per_page, current_page)

for key, value in pages.items():
    if value:
        start, end = value
        print(f"{key}: {start} to {end - 1}")
    else:
        print(f"{key}: None")


pages = {
        "previous_page": [],
        "current_page": [],
        "next_page": []
    }




"""for i in range(len(test_list)):

    if i >= previous_start_index and  i <= previous_end_index:
        pages["previous_page"].append(test_list[i])


    elif i >= start_index and  i <= end_index:
        pages["current_page"].append(test_list[i])
    elif i >= next_start_index and i <= next_end_index:
        pages["next_page"].append(test_list[i])
    #else:
        #break

print(pages)"""







