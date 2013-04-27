import re
import string
import json
from collections import defaultdict
import pickle
import sys

def is_ascii(s):
    return all(ord(c) < 128 for c in s)


full_list=['Drama', 'Comedy', 'Romance', 'Action', 'Thriller', 'Animation'\
             'Crime', 'Horror', 'Fantasy', 'Adventure', 'Sci-Fi', 'Mystery'\
             'Musical', 'War', 'Western', 'Family']
f = open( "genres.txt", "r" )
data = []
counter=0
all_movies=defaultdict(dict)
genres_list=[]
old_movie=""

for line in f:
  if (counter==140115):
    tokens=line.split()
    # get the movie genres
    genres=tokens[len(tokens)-1]
    years=re.findall(r'\([\d]+\)',line)
    if (len(years)>0):
      index=line.index(years[0][0])
      title=line[0:index]
      old_title=title
      #print title
      year=years[0][1:len(years[0])-1]
      old_year=year
      #print year
      old_movie=title+year


  if (counter>140115):
    tokens=line.split()
    # get the movie genres
    genres=tokens[len(tokens)-1]
    years=re.findall(r'\([\d]+\)',line)
    if (len(years)>0):
      index=line.index(years[0][0])
      title=line[0:index]
      #print title
      year=years[0][1:len(years[0])-1]
      #print year
      this_movie=title+year
      if (this_movie==old_movie):
        genres_list.append(genres)
      else:
        movie_dict={}
        movie_dict['title']=old_title
        movie_dict['year']=old_year
        movie_dict['genres']=genres_list
        if (set(genres_list).issubset(set(full_list)) and (len(genres_list)>0)):
          #data.append(movie_dict)
	  l=len(old_title)
          string1=old_title[0:l-1]+old_year
	  if (is_ascii(string1)):
	    all_movies[string1]=movie_dict
	  #print string1

        old_title=title
        old_year=year
        genres_list=[]
        genres_list.append(genres)
        old_movie=this_movie
      
  counter+=1
  
  #print tokens
  #for token in tokens:
  #print re.findall(r'',line)
  if (counter>10000+140115):
    break

f.close()

data_size=len(data)
#print data_size
#with open('movies_data1.json', 'wb') as fp:
#  for i in range(0,data_size):
#    line=unicode(data[i]).encode('utf-8')
#    json.dump(line, fp)
#    fp.write('\n')
    

#fp.close()

#with open('data1.json', 'wb') as fp:
#    line=unicode(all_movies).encode('utf-8')
#    json.dump(all_movies, fp)

#fp.close()

#with open('data1.json', 'rb') as fp:
#    movies_dict = json.load(fp)

#fp.close()
#string="A Bad Situationist2008"
#string2="A Couple of White Chicks at the Hairdresser2007"
#print movie_dict

output = open('movie_data1.pkl', 'wb')
pickle.dump(all_movies, output)
output.close()


#with open('movie_data1.pkl', 'rb') as fp:
#    my_movies = pickle.load(fp)

#fp.close()
 
#for s in my_movies.keys():
#  print my_movies[s]
#  print "------------------"

#for i in range(0,data_size):
#  title=data[i]['title']
#  l=len(title)
#  string1=title[0:l-1]+data[i]['year']
#  print string1
  #print set(data[i]['genres'])


#-----------------------------------


f = open( "plots.txt", "r" )
counter=0
plot=""
old=""
title=""
year=""
i=0

print "--------------------------------"

all_movies2=defaultdict(dict)

for line in f:
  if (counter > 1769555):
    if (line[0:3]=='MV:'):
      #title=re.findall(r'\"(.+?)\"',line)[0]
      ind=line.index("(")
      title=line[4:ind-1]
      #print title
      years=re.findall(r'\([\d]+\)',line)
      if (len(years)>0):
        year=years[0][1:len(years[0])-1]
	#print year

    if (old==title+year):
      #print old
      continue
 
    if (line[0:3]=='PL:'):
      plot=plot+line[3:]
    
    if (line[0:3]=='BY:'):
      movie_dict={}
      movie_dict['title']=title
      movie_dict['year']=year
      movie_dict['plot']=plot
      #print title
      #print year
      #print plot
      #print "-----------------------"
      old=title+year
      if (is_ascii(old)):
        all_movies2[old]=movie_dict
      #print old
      plot=""

     


    
    
      
  counter+=1
 # if (counter>3000+1769555):
 #   break

f.close()

output = open('movie_data2.pkl', 'wb')
pickle.dump(all_movies2, output)
output.close()

