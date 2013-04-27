#!/usr/bin/python -tt

# David Chawner
# Homework 1

import sys, string, pickle

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

def main():
    index = {}
    docs = []
    N = 0
    query = ""
    score = 0.0
    ranges = []    
    # list of file numbers for this homework
    file1 = open("movie_data1.pkl", "r")
    genrefile = pickle.load(file1)
    print "loaded genres"
    file2 = open("movie_data2.pkl", "r")
    plotfile = pickle.load(file2)
    print "loaded plots"
    #N, docs, index, titlelist, plotlist = createIndex()
    
    #query = "revenue down"
    queryfile = open("tttt.txt", "r")
    a = 0
    for line in queryfile:
        if a == 0:
	    query = line
	if a == 1:
	    score = float(line)
	if a == 2:
	    for char in line:
	        ranges.append(char)
	a += 1
    
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


if __name__ == "__main__":
    main()
