import cPickle as pkl
import os

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from data import get as get_data, DATA_SOURCES

class Prediction(object):

    PKL = '.prediction.pkl'
    PKL_SOURCES = '.sources.pkl'

    def __init__(self):
        training_size = 1000 # not really
        num_iter = 10**6 / training_size # scikit recommendation
        self.classifier = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(
                loss='log', # logistic regression, which allows probability prediction
                penalty='l2',
                alpha=1e-3,
                n_iter=num_iter,
                random_state=42,
            )),
        ])
        self._train()

    @classmethod
    def get(cls):
        if os.path.exists(cls.PKL) and os.path.exists(cls.PKL_SOURCES):
            last_sources = pkl.load(open(cls.PKL_SOURCES, 'rb'))
            if last_sources == DATA_SOURCES:
                prediction = pkl.load(open(cls.PKL, 'rb'))
                return prediction
        print 'creating new classifier'
        prediction = cls()
        pkl.dump(prediction, open(cls.PKL, 'wb'))
        pkl.dump(DATA_SOURCES, open(cls.PKL_SOURCES, 'wb'))
        return prediction
        
    def _train(self):
        data, target = self._get_data()
        self.classifier.fit(data, target)

    def _get_data(self):
        data, target = get_data()
        return data, target

    def predict(self, x):
        return self.classifier.predict_proba([x])[0]

