from reddit_img_parser.reddit import get_reddit_entry, get_submissions


def get_statistics(type, name, category, time_filter, limit):
    
    entry = get_reddit_entry(type, name)
    if not entry:
        return

    submissions = get_submissions(entry, type, category, limit, time_filter)
    if not submissions:
        return
    
    statistics_data = {}

    print('Processing... ')
    
    for sub in submissions:
        if type == 'redditor':
            key_entry = sub.subreddit
        else:
            key_entry = sub.author

        if not key_entry:
            continue
        
        if type == 'redditor':
            key_name = key_entry.display_name
        else:
            key_name = key_entry.name

        if not key_name in statistics_data:
            statistics_data[key_name] = 1
        else:
            statistics_data[key_name] += 1

    print(f"Statistics to: {name}")
    print((21 + len(name)) * '-')
    sorted_data = dict(sorted(statistics_data.items(), key=lambda item: -item[1]))
    for el in sorted_data: 
        print(f"{el}: {sorted_data[el]}")
