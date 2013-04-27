#!/usr/bin/env python
import os, re, sys, codecs, nltk, operator, string
from nltk.corpus import wordnet as wn
from collections import defaultdict
import cPickle as pickle
from pkg_resources import resource_string, resource_stream
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier

"""
Interface to SentiWordNet using the NLTK WordNet classes.

---Chris Potts

Sentiment Classifier & WSD Module

--Pulkit Kathuria
"""
__documentation__ = "http://www.jaist.ac.jp/~s1010205/sentiment_classifier"
__url__ = "http://www.jaist.ac.jp/~s1010205/"
__online_demo__ = "http://www.jaist.ac.jp/~s1010205/sentiment_classifier"

class SentiWordNetCorpusReader:
    def __init__(self, filename):
        """
        Argument:
        filename -- the name of the text file containing the
                    SentiWordNet database
        """        
        self.filename = filename
        self.db = {}
        self.parse_src_file()

    def parse_src_file(self):
        lines = codecs.open(self.filename, "r", "utf8").read().splitlines()
        lines = filter((lambda x : not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = re.split(r"\t+", line)
            fields = map(unicode.strip, fields)
            try:            
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                sys.stderr.write("Line %s formatted incorrectly: %s\n" % (i, line))
            if pos and offset:
                offset = int(offset)
                self.db[(pos, offset)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):        
        if tuple(vals) in self.db:
            pos_score, neg_score = self.db[tuple(vals)]
            pos, offset = vals
            synset = wn._synset_from_pos_and_offset(pos, offset)
            return SentiSynset(pos_score, neg_score, synset)
        else:
            synset = wn.synset(vals[0])
            pos = synset.pos
            offset = synset.offset
            if (pos, offset) in self.db:
                pos_score, neg_score = self.db[(pos, offset)]
                return SentiSynset(pos_score, neg_score, synset)
            else:
                return None

    def senti_synsets(self, string, pos=None):
        sentis = []
        synset_list = wn.synsets(string, pos)
        for synset in synset_list:
            sentis.append(self.senti_synset(synset.name))
        sentis = filter(lambda x : x, sentis)
        return sentis

    def all_senti_synsets(self):
        for key, fields in self.db.iteritems():
            pos, offset = key
            pos_score, neg_score = fields
            synset = wn._synset_from_pos_and_offset(pos, offset)
            yield SentiSynset(pos_score, neg_score, synset)

class SentiSynset:
    def __init__(self, pos_score, neg_score, synset):
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.obj_score = 1.0 - (self.pos_score + self.neg_score)
        self.synset = synset

    def __str__(self):
        """Prints just the Pos/Neg scores for now."""
        s = ""
        s += self.synset.name + "\t"
        s += "PosScore: %s\t" % self.pos_score
        s += "NegScore: %s" % self.neg_score
        return s

    def __repr__(self):
        return "Senti" + repr(self.synset)
def count_features(bag_of_words, features, polarity):
    for lst in features:
        for word in lst[0].keys():
            bag_of_words[polarity][word] += 1
    return bag_of_words
    
def train_bag_of_words():
    """
    @return: dictionary
      bag_of_words['neg']['word'] ==> count
      bag_of_words['pos']['word'] ==> count
    """
    def word_feats(words): return dict([(word, True) for word in words])
    bag_of_words = {}
    bag_of_words['neg'] = defaultdict(int)
    bag_of_words['pos'] = defaultdict(int)
    negids = movie_reviews.fileids('neg')
    posids = movie_reviews.fileids('pos')
    negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
    posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
    bag_of_words = count_features(bag_of_words, negfeats, 'neg')
    bag_of_words = count_features(bag_of_words, posfeats, 'pos')
    return bag_of_words

def classify_polarity(bag_of_words):
    """
    Pops word from bag_of_words['neg'/'pos'] if the word appears
    more in 'pos/'neg' respectively
    """
    for word, count in bag_of_words['neg'].items():
        if count > bag_of_words['pos'][word]: bag_of_words['pos'].pop(word)
        else: bag_of_words['neg'].pop(word)
    return bag_of_words
                    
"""
Word Disambiguator using nltk
Sentiment Classifier as a combination of
  -Bag of Words (nltk movie review corpus, words as features)
  -Heuristics
  
--KATHURIA Pulkit
"""
def word_similarity(word1, word2):
   w1synsets = wn.synsets(word1)
   w2synsets = wn.synsets(word2)
   maxsim = 0
   for w1s in w1synsets:
       for w2s in w2synsets:
           current = wn.path_similarity(w1s, w2s)
           if (current > maxsim and current > 0):
               maxsim = current
   return maxsim
def disambiguateWordSenses(sentence, word):
   wordsynsets = wn.synsets(word)
   bestScore = 0.0
   result = None
   for synset in wordsynsets:
       for w in nltk.word_tokenize(sentence):
           score = 0.0
           for wsynset in wn.synsets(w):
               sim = wn.path_similarity(wsynset, synset)
               if(sim == None):
                   continue
               else:
                   score += sim
           if (score > bestScore):
              bestScore = score
              result = synset
   return result

def SentiWordNet_to_pickle(swn):
    synsets_scores = defaultdict(list)
    for senti_synset in swn.all_senti_synsets():
        if not synsets_scores.has_key(senti_synset.synset.name):
            synsets_scores[senti_synset.synset.name] = defaultdict(float)
        synsets_scores[senti_synset.synset.name]['pos'] += senti_synset.pos_score
        synsets_scores[senti_synset.synset.name]['neg'] += senti_synset.neg_score
    return synsets_scores

def classify(text, synsets_scores, bag_of_words):
    #synsets_scores = pickled object in data/SentiWN.p
    pos = neg = 0
    for line in text:
        if not line.strip() or line.startswith('#'):continue
        for sentence in line.split('.'):
            sentence = sentence.strip()
            sent_score_pos = sent_score_neg = 0
            for word in sentence.split():
                if disambiguateWordSenses(sentence, word): 
                    disamb_syn = disambiguateWordSenses(sentence, word).name
                    if synsets_scores.has_key(disamb_syn):
                        #uncomment the disamb_syn.split... if also want to check synsets polarity
                        if bag_of_words['neg'].has_key(word.lower()):
                            sent_score_neg += synsets_scores[disamb_syn]['neg']
                        if bag_of_words['pos'].has_key(word.lower()):
                            sent_score_pos += synsets_scores[disamb_syn]['pos']
            pos += sent_score_pos
            neg += sent_score_neg
    return pos, neg

senti_pickle = resource_stream('senti_classifier', '../data/SentiWn.p')
bag_of_words_pickle = resource_stream('senti_classifier', '../data/bag_of_words.p')
synsets_scores = pickle.load(senti_pickle)
bag_of_words = pickle.load(bag_of_words_pickle)
bag_of_words = classify_polarity(bag_of_words)


def polarity_scores(lines_list):
    scorer = defaultdict(list)
    pos, neg = classify(lines_list, synsets_scores, bag_of_words)
    return pos, neg

def get_scores(tweet, ranges):  
	tweet = tweet.strip()
	r = re.compile("[,.?()\\d]+ *")
	words_list = r.split(tweet)
	pos, neg = polarity_scores(words_list)
	score = 0
	if(pos > 0 and neg > 0):
		score = pos * neg
		if(neg > pos):
			score = score * (-1)
	else:
		score = max(pos, neg)
		if(neg > pos):
			score = score * (-1)	
	return [score, ranges]
def createIndex(genre, genrefile, plotfile):
    ind = {}
    N = 0
    docs = []
    """
    # list of file numbers for this homework
    file1 = open("movie_data1.pkl", "r")
    genrefile = pickle.load(file1)
    print "loaded genres"
    file2 = open("movie_data2.pkl", "r")
    plotfile = pickle.load(file2)
    print "loaded plots"
    """
    titlelist = []
    plotlist = []

    count = 0
    for key in genrefile:
        if genre in genrefile[key]["genres"]:
            docind = {}
            #count += 1
            title = genrefile[key]["title"]
            title = title[0:len(title)-1]
            year = genrefile[key]["year"]
            newkey = title + year
            #print newkey
            if plotfile[newkey].has_key("plot"):
                count += 1
                movieplot = plotfile[newkey]["plot"]
                titlelist.append(title)
                plotlist.append(movieplot)
                words = movieplot.translate(None, string.punctuation)
                words = words.split()
                N += len(words)
                for word in words:
                    word = word.lower()
                    #print word
                    if word in ind:
                        ind[word] += 1
                    else:
                        ind[word] = 1
                    if word in docind:
                        docind[word] += 1
                    else:
                        docind[word] = 1
                docs.append(docind)

    print count
    return N, docs, ind, titlelist, plotlist
    
def mixture(numwords, docs, index, query):
    query = query.lower()
    tokens = query.translate(None, string.punctuation)
    tokens = tokens.split()
    #print tokens
    #print docs
    lamb = .5
    scores = [1.0] * len(docs)
    #print scores
    for a in range(len(docs)):
        #tokscores = [1.0] * len(tokens)
        #print docs[a]
        wordct = 0
        for tok in docs[a]:
            wordct += docs[a][tok]
        
        for b in range(len(tokens)):
            if tokens[b] in docs[a]:
                #print float(docs[a][tokens[b]])/wordct
                score1 = float(docs[a][tokens[b]])/wordct
            else:
                #print 0
                score1 = 0
            if tokens[b] in index:
                #print float(index[tokens[b]])/numwords
                score2 = float(index[tokens[b]])/numwords
            else:
                #print float(1)/numwords
                score2 = float(1)/numwords
                #score2 = 0

            scores[a] *= (lamb*score1 + (1-lamb)*score2)
    #print scores
    return scores

def notmain(query, score, ranges):
    index = {}
    docs = []
    N = 0
 
    # list of file numbers for this homework
    file1 = open("movie_data1.pkl", "r")
    genrefile = pickle.load(file1)
    print "loaded genres"
    file2 = open("movie_data2.pkl", "r")
    plotfile = pickle.load(file2)
    print "loaded plots"
    #N, docs, index, titlelist, plotlist = createIndex()
    

    print ranges
    if score < -.95:
        genre = ranges[0]
    if score >= .95 and score < -.125:
        genre = ranges[1]
    if score >= -.125 and score <= .125:
        genre = ranges[2]
    if score > .125 and score <= .95:
        genre = ranges[3]
    if score > .95:
        genre = ranges[4]
    print genre

    if genre == "C":
        genre = "Comedy"
    if genre == "R":
        genre = "Romance"
    if genre == "D":
        genre = "Drama"
    if genre == "H":
        genre = "Horror"
    if genre == "A":
        genre = "Action"
    #if query == "quit!":
    #    return
    N, docs, index, titlelist, plotlist = createIndex(genre, genrefile, plotfile)
    scores = mixture(N, docs, index, query)
        
    sortedscores = list(scores)
    sortedscores.sort()
    sortedscores.reverse()
        
    index = scores.index(sortedscores[0])
    print titlelist[index]
    print plotlist[index]
    #print docs[0]
    titleout = open("moodie_movie_results_title.txt", "w")
    plotout = open("moodie_movie_results_plot.txt", "w")

    titleout.write(str(titlelist[index]))
    plotout.write(str(plotlist[index]))
    return

if __name__ == "__main__":
	words_list = sys.argv[1: -1]
	status = ''
	for word in words_list:
		status = status + word + ' '

	[score, ranges] = get_scores(status, sys.argv[-1])
	print score
	print ranges
	#f = open('tttt.txt', 'w')
	#f.write(str(status) + '\r\n')
	#f.write(str(score) + '\r\n')
	#f.write(ranges)
	#f.close()

	# call my code's "main"
	notmain(status, score, ranges)
#	print pos
#	print neg
