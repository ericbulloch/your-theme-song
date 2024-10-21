import deezer


with deezer.Client() as client:
	results = client.search('sisqo thong song')
	print(dir(results))
	print(results.total)
	print(results)
	for r in results:
		print(dir(r))
		print(r.artist.name)
		exit()