import sys
import os
import re
import json
import fastText


def strip_formatting(string):
    string = string.lower()
    string = re.sub(r"([.!?,'/()])", r" \1 ", string)
    return string


def runFilter(args):

    print(args)

    # Pre-process the text of review so it matches the training format
    preprocessed_reviews = strip_formatting(args)

    # Load the model
    classifier = fastText.load_model('reviews_model_ngrams.bin')

    # Get fastText to classify each review with the model
    label, probability = classifier.predict(preprocessed_reviews, 1)

    data = {'results': int(label[0][-1]),
            'probability': int(probability[0] * 100)}

    return data
