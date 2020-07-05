import sys, tweepy, csv
import re, time, json
import validators
from urllib.parse import urlparse
# Then proceed to load matplotlib
# os.environ["MATPLOTLIBDATA"] = os.path.join(os.path.split(sys.executable)[0], "Lib/site-packages/matplotlib/mpl-data")
import matplotlib.pyplot as plt
#import mpl_toolkits
#from mpl_toolkits.mplot3d import Axes3D
from textblob import TextBlob
import tkinter as tk
#import urllib
#import json as simplejson
from re import split
from functools import partial
from tkinter import filedialog, Text, END, HORIZONTAL, Menu, Toplevel
from tkinter import *
from datetime import datetime
import pandas as pd
import numpy as np
from tweepy import OAuthHandler 
from tkinter import messagebox as mb
from nltk import ngrams
import warnings
import threading
import concurrent.futures
# from pandas.plotting import register_matplotlib_converters
# register_matplotlib_converters()
def percentage(part, whole):
	temp = 100 * float(part) / float(whole)
	return (format(temp, '.2f'))

def call_readcsvP():
	with open('resultPositiveTweets.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter='\n')
		for row in csv_reader:
			print("\n".join(row))
		
	print("\n")

def call_readcsvNeg():
	with open('resultNegTweets.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter='\n')
		for row in csv_reader:
			print("\n".join(row))
	print("\n")

def call_readcsvN():
	with open('resultNeurtalTweets.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter='\n')
		for row in csv_reader:
			print("\n".join(row))
	print("\n")

def check_if_empty(string):
	#print('length of String', len(string))
	if len(string.strip()) == 0:
		#print('empty String')
		return 1
	else:
		return 0

def clean_tweet(tweet): 
		''' 
		Utility function to clean tweet text by removing links, special characters 
		using simple regex statements. 
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
		
def get_tweet_sentiment(tweet):
		# create TextBlob object of passed tweet text
		analysis = TextBlob(clean_tweet(tweet))
		# set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'
			
def get_tweets(query, count = 20): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET = reading_Keys()
		# access to Tweet APIs
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth, wait_on_rate_limit=True)
		# empty list to store parsed tweets 
		tweets = [] 
  
		try: 
			# call twitter api to fetch tweets 
			fetched_tweets = api.search(q = query, count = count) 
  
			# parsing tweets one by one 
			for tweet in fetched_tweets: 
				# empty dictionary to store required params of a tweet 
				parsed_tweet = {} 
  
				# saving text of tweet 
				parsed_tweet['text'] = tweet.text 
				# saving sentiment of tweet 
				parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text) 
  
				# appending parsed tweet to tweets list 
				if tweet.retweet_count > 0: 
					# if tweet has retweets, ensure that it is appended only once 
					if parsed_tweet not in tweets: 
						tweets.append(parsed_tweet) 
				else: 
					tweets.append(parsed_tweet) 
  
			# return parsed tweets 
			return tweets 
  
		except tweepy.TweepError as e: 
			# print error (if any) 
			print("Error : " + str(e))

def reading_Keys():
	with open('conf.json', 'r') as f: #options.credentials
			conf = json.load(f)
			CONSUMER_KEY = conf["consumer_key"]
			CONSUMER_SECRET = conf["consumer_secret"]
			ACCESS_KEY = conf["access_key"]
			ACCESS_SECRET = conf["access_secret"]
	return CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET
def getData_ScatterPlot(n1,n2):
	
	keyword = str(n1.get())
	numberOfTweets = str(n2.get())
	polarity_list = []
	numbers_list = []
	number = 1
	if check_if_empty(keyword)==1 and check_if_empty(numberOfTweets)==1:
		mb.showerror("Text field empty Error!", "Text fields should not be empty!" )
		#root.mainloop()
	else:
		#Where the tweets are stored to be plotted
		   
		CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET = reading_Keys()
		# access to Tweet APIs
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth, wait_on_rate_limit=True)
		valid=validators.url(keyword)
		if valid==True:
			print("Url is valid")
			keywordparse=urlparse(keyword)
			keywordstr=keywordparse.path
			nstrkeyword = keywordstr.replace('/','')
			tweetsdata = get_tweets(query = nstrkeyword, count = 100)
			streams_collection(nstrkeyword,numberOfTweets,tweetsdata,file_name = 'ExtractedInformation')
			for tweet in tweepy.Cursor(api.search, nstrkeyword, lang="en").items(int(numberOfTweets)):
				try:
					analysis = TextBlob(tweet.text)
					analysis = analysis.sentiment
					polarity = analysis.polarity
					polarity_list.append(polarity)
					numbers_list.append(number)
					number = number + 1

				except tweepy.TweepError as e:
					print(e.reason)

				except StopIteration:
					break
		
			#Plotting
			axes = plt.gca()
			axes.set_ylim([-1, 2])

			plt.scatter(numbers_list, polarity_list)

			averagePolarity = (sum(polarity_list))/(len(polarity_list))
			averagePolarity = "{0:.0f}%".format(averagePolarity * 100)
			time  = datetime.now().strftime("At: %H:%M\nOn: %m-%d-%y")

			plt.text(0, 1.25, "Average Sentiment:  " + str(averagePolarity) + "\n" + time, fontsize=12, bbox = dict(facecolor='none', edgecolor='black', boxstyle='square, pad = 1'))

			plt.title('Sentimental Analysis on ' + nstrkeyword + ' by analyzing ' + str(numberOfTweets) + ' Tweets.')
			plt.xlabel("Number of Tweets")
			plt.ylabel("Sentiment")
			plt.show(block=False)
			warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
		else:
			
			tweetsdata = get_tweets(query = keyword, count = 100)
			streams_collection(keyword,numberOfTweets,tweetsdata,file_name = 'ExtractedInformation')			
			for tweet in tweepy.Cursor(api.search, keyword, lang="en").items(int(numberOfTweets)):
				try:
					analysis = TextBlob(tweet.text)
					analysis = analysis.sentiment
					polarity = analysis.polarity
					polarity_list.append(polarity)
					numbers_list.append(number)
					number = number + 1

				except tweepy.TweepError as e:
					print(e.reason)

				except StopIteration:
					break

			#Plotting
			axes = plt.gca()
			axes.set_ylim([-1, 2])

			plt.scatter(numbers_list, polarity_list)

			averagePolarity = (sum(polarity_list))/(len(polarity_list))
			averagePolarity = "{0:.0f}%".format(averagePolarity * 100)
			time  = datetime.now().strftime("At: %H:%M\nOn: %m-%d-%y")

			plt.text(1, 1.3, "Average Sentiment:  " + str(averagePolarity) + "\n" + time, fontsize=12, bbox = dict(facecolor='none', edgecolor='black', boxstyle='square, pad = 0.5'))

			plt.title('Sentimental Analysis on ' + keyword + ' by analyzing ' + str(numberOfTweets) + ' Tweets.')
			plt.xlabel("Number of Tweets")
			plt.ylabel("Sentiment")
			plt.show(block=False)
			warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)        

def graph(positive,negative,neutral,topics):                 #plotting Graph
    #fig, ax = plt.subplots()
    index = np.arange(1)
    bar_width = 0.1
    opacity = 1

    plt.bar(index, positive, bar_width, alpha=opacity, color='g', edgecolor='w', label='positive')


    plt.bar(index + bar_width, negative, bar_width, alpha=opacity, color='r', edgecolor='w', label='negative')


    plt.bar(index + bar_width+ bar_width, neutral, bar_width, alpha=opacity, color='b', edgecolor='w', label='neutral')


    plt.xticks(index+bar_width, [topics],family='fantasy')
    plt.xlabel('Firm',fontweight='bold',fontsize='10')
    plt.ylabel('Sentiments',fontweight='bold',fontsize='10')
    plt.title('Twitter Sentiment Analysis',fontweight='bold', color = 'white', fontsize='17', horizontalalignment='center',backgroundcolor='black')
    plt.legend()
    
    plt.tight_layout()
    plt.show(block=False);	warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
	
def getData_BarChart(n1, n2):
	
		keyword = str(n1.get())
		numberOfTweets = str(n2.get())
		polarity_list = []
		numbers_list = []
		number = 1
		if check_if_empty(keyword)==1 and check_if_empty(numberOfTweets)==1:
				mb.showerror("Text field empty Error!", "Text fields should not be empty!" )
			#root.mainloop()
		else:
			
			#Where the tweets are stored to be plotted			
			CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET = reading_Keys()
			# access to Tweet APIs
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
			api = tweepy.API(auth, wait_on_rate_limit=True)
			valid=validators.url(keyword)
			if valid==True:
				try:
					print("Url is valid")
					keywordparse=urlparse(keyword)
					keywordstr=keywordparse.path
					nstrkeyword = keywordstr.replace('/','')
					tweetsdata = get_tweets(query = nstrkeyword, count = 100)
					streams_collection(nstrkeyword,numberOfTweets,tweetsdata,file_name = 'ExtractedInformation')			

					for tweet in tweepy.Cursor(api.search, nstrkeyword, lang="en").items(int(numberOfTweets)):
						try:
							analysis = TextBlob(tweet.text)
							analysis = analysis.sentiment
							polarity = analysis.polarity
							polarity_list.append(polarity)
							numbers_list.append(number)
							number = number + 1

						except tweepy.TweepError as e:
							print(e.reason)

						except StopIteration:
							break
					positive=0
					negative=0
					neutral=0
					for tweet in tweepy.Cursor(api.search, nstrkeyword, lang="en").items(int(numberOfTweets)):
						
						analysis=TextBlob(tweet.text)
								
						if analysis.sentiment.polarity>0:
							positive+=1
						elif analysis.sentiment.polarity<0:
							negative+=1
						elif analysis.sentiment.polarity==0:
							neutral+=1
			  
					total=positive+negative+neutral
					posperc=round((positive*100)/total,2)
					negperc=round((negative*100)/total,2)
					neuperc=round((neutral*100)/total,2)
					graph(positive,negative,neutral,nstrkeyword)
		
				except ZeroDivisionError:			
					mb.showerror("Error","OOPS!!!Twitter doesn't have any tweets regarding the entered topic")
				except tweepy.error.TweepError:		
					mb.showerror("Error","NO INTERNET!!! Check your internet connection")
			else:
				try:
					tweetsdata = get_tweets(query = keyword, count = 100)
					streams_collection(keyword,numberOfTweets,tweetsdata,file_name = 'ExtractedInformation')
					for tweet in tweepy.Cursor(api.search, keyword, lang="en").items(int(numberOfTweets)):
						try:
							analysis = TextBlob(tweet.text)
							analysis = analysis.sentiment
							polarity = analysis.polarity
							polarity_list.append(polarity)
							numbers_list.append(number)
							number = number + 1

						except tweepy.TweepError as e:
							print(e.reason)

						except StopIteration:
							break
				
					positive=0
					negative=0
					neutral=0
					for tweet in tweepy.Cursor(api.search, keyword, lang="en").items(int(numberOfTweets)):
						
						analysis=TextBlob(tweet.text)
								
						if analysis.sentiment.polarity>0:
							positive+=1
						elif analysis.sentiment.polarity<0:
							negative+=1
						elif analysis.sentiment.polarity==0:
							neutral+=1
			  
					total=positive+negative+neutral
					posperc=round((positive*100)/total,2)
					negperc=round((negative*100)/total,2)
					neuperc=round((neutral*100)/total,2)
					graph(positive,negative,neutral,keyword)
			
				except ZeroDivisionError:					
					mb.showerror("Error","OOPS!!!Twitter doesn't have any tweets regarding the entered topic")
				except tweepy.error.TweepError:					
					mb.showerror("Error","NO INTERNET!!! Check your internet connection")
			
def getData_PiChart(n1, n2):
	keyword = str(n1.get())
	NoOfTweets = str(n2.get())
	if check_if_empty(keyword)==1 and check_if_empty(NoOfTweets)==1:
		mb.showerror("Text field empty Error!", "Text fields should not be empty!" )
		#root.mainloop()
	else:
			
		CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET = reading_Keys()
		# access to Tweet APIs
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth, wait_on_rate_limit=True)
		valid=validators.url(keyword)
		if valid==True:
			
			print("Url is valid")
			keywordparse=urlparse(keyword)
			keywordstr=keywordparse.path
			nstrkeyword = keywordstr.replace('/','')
			tweetsdata = get_tweets(query = nstrkeyword, count = 100)
			streams_collection(nstrkeyword,NoOfTweets,tweetsdata,file_name = 'ExtractedInformation')
			tweets = tweepy.Cursor(api.search, q=nstrkeyword, lang="en").items(int(NoOfTweets))
			positive = 0
			negative = 0
			neutral = 0
			polarity = 0

			csvP = open('resultPositiveTweets.csv', 'w')
			csvNeg = open('resultNegTweets.csv', 'w')
			csvN = open('resultNeurtalTweets.csv', 'w')
			columnTitleRowP = "Positive_Tweets\n"
			columnTitleRowN = "Neutral_Tweets\n"
			columnTitleRowNeg = "Negative_Tweets\n"
			csvP.write(columnTitleRowP)
			csvNeg.write(columnTitleRowNeg)
			csvN.write(columnTitleRowN)

			positive = 0
			wpositive = 0
			spositive = 0
			negative = 0
			wnegative = 0
			snegative = 0
			neutral = 0

			for tweet in tweets:
				Tweet = str((tweet.text).encode('utf-8'))
				analysis = TextBlob(tweet.text)
				Polar = analysis.sentiment.polarity
				if (Polar == 0):
					row = Tweet + "\n"
					csvN.write(row)
				elif (Polar > 0):
					row = Tweet + "\n"
					csvP.write(row)
				else:
					row = Tweet + "\n"
					csvNeg.write(row)
				if (analysis.sentiment.polarity == 0):
					neutral += 1
				elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
					wpositive += 1
				elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
					positive += 1
				elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
					spositive += 1
				elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity < 0):
					wnegative += 1
				elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
					negative += 1
				elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
					snegative += 1

			csvP.close()
			csvNeg.close()
			csvN.close()

			positive = percentage(positive, NoOfTweets)
			wpositive = percentage(wpositive, NoOfTweets)
			spositive = percentage(spositive, NoOfTweets)
			negative = percentage(negative, NoOfTweets)
			wnegative = percentage(wnegative, NoOfTweets)
			snegative = percentage(snegative, NoOfTweets)
			neutral = percentage(neutral, NoOfTweets)

			labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]',
					  'Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
					  'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]',
					  'Strongly Negative [' + str(snegative) + '%]']
			sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
			color = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
			patches, texts = plt.pie(sizes, colors=color, startangle=90)
			plt.legend(patches, labels, loc="best")
			plt.title('Sentimental Analysis on ' + nstrkeyword + ' by analyzing ' + str(NoOfTweets) + ' Tweets.')
			plt.axis('equal')
			plt.tight_layout()
			plt.show(block=False)
			warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
		
		else:
			tweetsdata = get_tweets(query = keyword, count = 100)	
			streams_collection(keyword,NoOfTweets, tweetsdata, file_name = 'ExtractedInformation')
			tweets = tweepy.Cursor(api.search, q=keyword, lang="en").items(int(NoOfTweets))
		#bar()
			positive = 0
			negative = 0
			neutral = 0
			polarity = 0

			csvP = open('resultPositiveTweets.csv', 'w')
			csvNeg = open('resultNegTweets.csv', 'w')
			csvN = open('resultNeurtalTweets.csv', 'w')
			columnTitleRowP = "Positive_Tweets\n"
			columnTitleRowN = "Neutral_Tweets\n"
			columnTitleRowNeg = "Negative_Tweets\n"
			csvP.write(columnTitleRowP)
			csvNeg.write(columnTitleRowNeg)
			csvN.write(columnTitleRowN)

			positive = 0
			wpositive = 0
			spositive = 0
			negative = 0
			wnegative = 0
			snegative = 0
			neutral = 0

			for tweet in tweets:
				Tweet = str((tweet.text).encode('utf-8'))
				analysis = TextBlob(tweet.text)
				Polar = analysis.sentiment.polarity
				if (Polar == 0):
					row = Tweet + "\n"
					csvN.write(row)
				elif (Polar > 0):
					row = Tweet + "\n"
					csvP.write(row)
				else:
					row = Tweet + "\n"
					csvNeg.write(row)
				if (analysis.sentiment.polarity == 0):
					neutral += 1
				elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
					wpositive += 1
				elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
					positive += 1
				elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
					spositive += 1
				elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity < 0):
					wnegative += 1
				elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
					negative += 1
				elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
					snegative += 1

			csvP.close()
			csvNeg.close()
			csvN.close()

			positive = percentage(positive, NoOfTweets)
			wpositive = percentage(wpositive, NoOfTweets)
			spositive = percentage(spositive, NoOfTweets)
			negative = percentage(negative, NoOfTweets)
			wnegative = percentage(wnegative, NoOfTweets)
			snegative = percentage(snegative, NoOfTweets)
			neutral = percentage(neutral, NoOfTweets)

			labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]',
					  'Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
					  'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]',
					  'Strongly Negative [' + str(snegative) + '%]']
			sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
			color = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
			patches, texts = plt.pie(sizes, colors=color, startangle=90)
			plt.legend(patches, labels, loc="best")
			plt.title('Sentimental Analysis on ' + keyword + ' by analyzing ' + str(NoOfTweets) + ' Tweets.')
			plt.axis('equal')
			plt.tight_layout()
			plt.show(block=False)
			warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)

		#print('Workdone properly')

def streams_collection(n1,n2, tweetsdata, file_name):
	
	CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET = reading_Keys()
	# access to Tweet APIs
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth, wait_on_rate_limit=True)
	# picking first positive tweets from tweets 
	ptweets = [tweet for tweet in tweetsdata if tweet['sentiment'] == 'positive'] 
	# percentage of positive tweets 
	#print("Positive tweets percentage: {} %".format(str(round((100*len(ptweets)/len(tweetsdata)),2)))) 
	# picking negative tweets from tweets 
	ntweets = [tweet for tweet in tweetsdata if tweet['sentiment'] == 'negative'] 
	# percentage of negative tweets 
	#print("Negative tweets percentage: {} %".format(str(round((100*len(ntweets)/len(tweetsdata)),2)))) 
	# percentage of neutral tweets
	neutraltweets=[tweet for tweet in tweetsdata if tweet['sentiment'] == 'neutral']
	#print("Neutral tweets percentage: {} %".format(str(round((100*(len(tweetsdata) -(len(ntweets )+len(ptweets)))/len(tweetsdata)),2))))
	data = str(n1)
	numberOfTweets = str(n2)
	if check_if_empty(data)==1 and check_if_empty(numberOfTweets)==1:
		mb.showerror("Text field empty Error!", "Text fields should not be empty!" )
		#root.mainloop()
	else:
		i = 0
		df = pd.DataFrame(columns = ['User_Name','User_ID', 'Tweets_Content', 'Tweet_Length','#_of_+iv_Tweets','#_of_-iv_Tweets','#_of_Nutral_Tweets', 'Likes_count', 'RT_count', 'tweet_date', 'URL']) #'User_statuses_count','user_followers', 'User_location', 'User_verified',
		for tweet in limit_handled(tweepy.Cursor(api.search, q = data, count = 20,lang='en').items(int(numberOfTweets))): #since='2006-01-01', since='2006-01-01',
			print("Searching Tweets...",i+1, end='\r')
			
			df.loc[i, 'User_Name'] = tweet.author.name #
			df.loc[i, 'User_ID'] = str(tweet.author.id)
			df.loc[i, 'Tweets_Content'] = tweet.text
			df.loc[i, 'Tweet_Length'] = len(tweet.text)
			df.loc[i, '#_of_+iv_Tweets'] = len(ptweets)
			df.loc[i, '#_of_-iv_Tweets'] = len(ntweets)
			df.loc[i, '#_of_Nutral_Tweets'] = len(neutraltweets)			
			df.loc[i, 'Likes_count'] = tweet.favorite_count 
			df.loc[i, 'RT_count'] = tweet.retweet_count
			df.loc[i, 'tweet_date'] = str(tweet.author.created_at)
			df.loc[i, 'URL'] = tweet.author.url
			df.to_excel('{}.xlsx'.format(file_name))
			i += 1
			if i == int(numberOfTweets):
				progress(int(n2),int(numberOfTweets),status='Completed! Plz wait for the Results will show in a Chart...\n')
				time.sleep(0.5)
				break
			else:
				pass

# Function for handling pagination in our search
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print('Reached rate limite. Sleeping for > 15 minutes')
            time.sleep(15 * 61)
	
def donothing():
	print("Sentiment analysis software ver 1.1")
	# filewin = Toplevel(root)
	# button = Button(filewin, text="Do nothing button")
	# button.pack()

	
def main():		
	root = tk.Tk()
	root.title('Twitter Sentiment Analysis Software')
	root.resizable(0,0)
	#root.geometry('800x700')
	menubar = Menu(root)
	helpmenu = Menu(menubar, tearoff=0)
	helpmenu.add_command(label="Help Index", command=donothing)
	helpmenu.add_separator()
	helpmenu.add_command(label="About...", command=donothing)
	menubar.add_cascade(label="Help", menu=helpmenu)

	
	number1 = tk.StringVar()
	number2 = tk.StringVar()

	labelTitle = tk.Label(root, text=" Tweets Sentiment Analysis ",font='Helvetica 9 bold').grid(row=0, column=1)
	labelNum1 = tk.Label(root, text="Enter Firm Keyword/Tag/URL to search:",font='Helvetica 9 bold').grid(row=1, column=0)
	labelNum2 = tk.Label(root, text="Enter Sample Size:",font='Helvetica 9 bold').grid(row=2, column=0)

	entryNum1 = tk.Entry(root, textvariable=number1,bd=0,fg="#6E97ED",width="50").grid(row=1, column=1)
	entryNum2 = tk.Entry(root, textvariable=number2,bd=0,fg="#6E97ED",width="50").grid(row=2, column=1)
	#progress=Progressbar(root,orient=HORIZONTAL,length=100,mode='determinate')

	# Create a pool of processes. By default, one is created for each CPU in your machine.
	with concurrent.futures.ProcessPoolExecutor() as executor:
		getData_BarChart1 = partial(getData_BarChart, number1, number2)
		buttonCal = tk.Button(root, text="Tweets Analysis Results (BarChart) ",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command=getData_BarChart1).grid(row=3, column=0,padx=15)
		
		
		call_result1 = partial(getData_PiChart, number1, number2)
		buttonCal1 = tk.Button(root, text="Tweets Analysis Results (PiChart) ",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command=call_result1).grid(row=3, column=1,padx=15)
		
		
		getData_ScatterPlot1= partial(getData_ScatterPlot, number1,number2)
		submit = tk.Button(root, text ="Tweets Analysis Results (Scatterplot) ",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command = getData_ScatterPlot1).grid(row=3, column=2,pady=15)
		
		
		button1 = tk.Button(root, text="Read Positive Tweets",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command=call_readcsvP,width="21").grid(row=5, column=0,padx=15)
		button2 = tk.Button(root, text="Read Negative Tweets",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command=call_readcsvNeg,width="21").grid(row=5, column=1,pady=15)
		button3 = tk.Button(root, text="Read Neutral Tweets",background="#6E97ED",fg="white",bd=0,font='Helvetica 9 bold', command=call_readcsvN,width="21").grid(row=5, column=2,padx=15)
		root.config(menu=menubar)
		statusbar = tk.Label(root,text="@TSA ver 1",bd=3,relief=SUNKEN,font='Helvetica 9 bold')
		statusbar.grid(row=6,column=0,columnspan=6,rowspan=4)
		statusbar.config(width="100",anchor="w")
		root.mainloop()

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

	
if __name__ == "__main__": 
	# calling main function 
	main()
	
		