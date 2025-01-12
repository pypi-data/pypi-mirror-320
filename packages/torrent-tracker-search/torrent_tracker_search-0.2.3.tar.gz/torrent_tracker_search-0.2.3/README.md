# Torrent Tracker Search Lib

## Integrations

- rutracker.org
- nnmclub.to

## Example

```python
from torrent_tracker_search.ClientBuilder import ClientBuilder
from torrent_tracker_search.source.rutracker.RuTrackerService import RuTrackerService
from torrent_tracker_search.source.rutracker.RuTrackerClient import RuTrackerClient
from torrent_tracker_search.source.nnmclub.NNMClubService import NNMClubService
from torrent_tracker_search.source.nnmclub.NNMClubClient import NNMClubClient
from torrent_tracker_search.TorrentTrackerSearch import TorrentTrackerSearch

builder = ClientBuilder()
rutracker_client, nnmclub_client = builder.build(clients=[RuTrackerClient(), NNMClubClient()])
rutracker_service = RuTrackerService(rutracker_client)
nnmclub_service = NNMClubService(rutracker_client)
rutracker_service.login_by_session(session_id="[YOUR_SESSION_ID]")
nnmclub_service.login(session_id="[YOUR_SESSION_ID]")
service = TorrentTrackerSearch(trackers=[nnmclub_service, rutracker_service])

async def main(query: str):
    result = await service.search(query)
    print(f"search results: {result}")
    torrent = await service.torrent(result[0])
    print(f"full torrent info: {torrent}")
    await builder.session.close()


```