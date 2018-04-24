from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier

def train(data, target, model="gnb", alpha=1.0):
	if(model == "gnb"):
		mdl = GaussianNB()
	elif(model == "mnb"):
		mdl = MultinomialNB(alpha=alpha)
	elif(model == "bnb"):
		mdl = BernoulliNB(alpha=alpha)
	elif(model == "dtg"):
		mdl = DecisionTreeClassifier(criterion="gini")
	elif(model == "dte"):
		mdl = DecisionTreeClassifier(criterion="entropy")
	elif(model == "rdm"):
		mdl = DummyClassifier(strategy="uniform")
	else:
		print("Model not available...\nTry 'gnb', 'mnb', 'bnb', 'dtg', 'dte' or 'rdm")
	mdl.fit(data, target)
	return mdl

def predict(model, data):
	pred = model.predict(data)
	return pred