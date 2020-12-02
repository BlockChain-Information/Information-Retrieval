# pip install vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Class_Sentiment:
    # pip install vaderSentiment
    # https://github.com/cjhutto/vaderSentiment

    def __init__(self):
        return

    def sentiment(self, sentence):
        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(sentence)
        # score is dictionary type
        return score


def main(args):
    lib_sent = Class_Sentiment()
    score = lib_sent.sentiment(args)
    score_neg = score['neg']
    score_neu = score['neu']
    score_pos = score['pos']
    score_compund = score['pos']
    print("{:-<40} {}".format(args, str(score)))
    print(score_neg , score_pos ,score_neu,score_compund )


if __name__ == '__main__':
    main("a boat is docked in a harbor with a city in the background .")


#sentiment_analyzer_scores("bitcoin is gonna be raised because US economy is being well")

#sentiment_analyzer_scores("a tennis player is playing a game of tennis.")

#sentiment_analyzer_scores("I hate you")

#sentiment_analyzer_scores("a boat is docked in a harbor with a city in the background .")

