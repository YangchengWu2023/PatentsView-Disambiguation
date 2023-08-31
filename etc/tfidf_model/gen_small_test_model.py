from sklearn.feature_extraction.text import TfidfVectorizer
import mysql.connector
 
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="aeolus"
)
 
mycursor = mydb.cursor()
 
mycursor.execute("USE granted")
mycursor.execute("SELECT organization FROM granted.rawassignee;")

corpus = []
for i in mycursor:
    if i[0] is not None:
        corpus.append(i[0])
vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(corpus)
X = vectorizer.fit(corpus)
# import pdb
# pdb.set_trace()
# import dill as dpickle
# dpickle.dump(X, open('./assignee_name_vectorizer.pkl', 'wb'))
# mycursor.close()
# mydb.close()
