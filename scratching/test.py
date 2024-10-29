def divide_task(rows, threads):
    chunk_size = rows // threads
    remainder = rows % threads
    
    ranges = []
    start = 0
    
    for i in range(threads):
        if start >= rows :
            ranges.append(None)
        else:
            end = start + chunk_size + (1 if i < remainder else 0)
            ranges.append((start, end))
            start = end
    
    return ranges


rows = 5
threads = 8
thread_ranges = divide_task(rows, threads)

print(thread_ranges)
print(thread_ranges[7][1])
