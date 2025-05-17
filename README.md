# Coordinated Twitter Narratives in the First Week of Russia’s Invasion of Ukraine

This repository contains the full codebase and supporting materials for the project “The Digital Artillery, Twitter: Analyzing Coordinated Twitter Narratives in the First Month of Russia’s Invasion of Ukraine” by Aram Bagdasarian (Harvard University, GOV 1430, Spring 2025).

## Project Summary

This project investigates how digital narratives emerged and evolved on Twitter during the early days of Russia’s full-scale invasion of Ukraine in February 2022. Drawing on approximately 950,000 tweets posted by 780,000 unique users over a 65-day period, the study combines computational methods with political analysis to uncover patterns in hashtag co-occurrence, emotional content, media use, engagement behavior, and linguistic trends.

The analysis reveals how Twitter served not merely as a commentary platform but as an active site of symbolic conflict, protest, and information warfare.


## Data Sources

- Main Dataset: [Kaggle – Russia-Ukraine War Tweets Dataset (65 Days)](https://www.kaggle.com/datasets/foklacu/ukraine-war-tweets-dataset-65-days/data)
- Supplementary Data: Collected via the Twitter API for the hashtags `#UkraineWar` and `#UkraineNATO` (January–March 2022)

All data use complies with the [Twitter Developer Agreement and Policy](https://developer.twitter.com/en/developer-terms/agreement-and-policy).

## Tools & Libraries

- Python 3.9
- `pandas`, `matplotlib`, `networkx`, `wordcloud`, `seaborn`
- `snscrape` (for supplementary data collection)
- JupyterLab / VS Code

## Key Findings

- 71% of all tweets were original content, not retweets.
- Hashtag use surged post-invasion, with #StandWithUkraine and #StopPutinNow dominating.
- Ukrainian-language tweets increased 540% after February 24, 2022.
- Hashtag diversity tripled within the first week, signaling a proliferation of narrative frames.
- Top influencers (i.e. @KyivIndependent) played a central role in shaping discourse.

For a detailed write-up of the findings and literature review, please refer to the full paper in the repository.

## Citation

If referencing this project in academic work:

> Bagdasarian, Aram. The Digital Artillery, Twitter: Analyzing Coordinated Twitter Narratives in the First Month of Russia’s Invasion of Ukraine. Harvard University, May 2025.

## Contact

For questions or collaboration, please contact abagdasarian@college.harvard.edu


