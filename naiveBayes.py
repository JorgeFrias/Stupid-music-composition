from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

def train(data, target, model="gnb", alpha=1.0):
	if(model == "gnb"):
		mdl = GaussianNB()
	elif(model == "mnb"):
		mdl = MultinomialNB(alpha=alpha)
	elif(model == "bnb"):
		mdl = BernoulliNB(alpha=alpha)
	else:
		print("Model not available...\nTry 'gnb', 'mnb' or 'bnb'")
	mdl.fit(data, target)
	return mdl

def predict(model, data):
	pred = model.predict(data)
	return pred