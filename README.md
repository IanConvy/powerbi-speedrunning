# powerbi-speedrunning
This repository contains a PowerBI report that summarizes a variety of statistics about _speedrunning_, which 
which is the act of completing a video game as quickly as possible. The people who participate in speedrunning
(called _runners_) have formed a centralized community at www.speedrun.com, which hosts leadeboards that track
the fastest speedruns of over 30,000 games. The websites provides a REST API from which data about games, runners,
and speedruns can be requested. The PowerBI report, which can be fully viewed by opening `speedruns.pbix` in 
PowerBI Desktop or viewed in a static form from `speedruns.pdf`, is built atop an exhaustive dataset consisting of
all users, games, platforms, and speedruns hosted on www.speedrun.com. The code used to retrieve and store this data
can be found in `scrape.py`.
