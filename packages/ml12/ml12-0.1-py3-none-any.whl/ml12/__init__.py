p1='''
1.ADA BOOST

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score

# Create a simple dataset with 2 features (both informative)
X, y = make_classification(
  n_samples=200,
  n_features=2, #Each data point has 2 features (columns).
  n_informative=2,  #Both features are informative
  n_redundant=0,   #no extra noise
  n_clusters_per_class=1,
  random_state=42 #Ensures reproducibility by fixing randomness.
)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Function to plot decision boundaries
def plot_decision_boundaries(X, y, model, title):
 x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
 y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
 xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))

 Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
 Z = Z.reshape(xx.shape)

 plt.contourf(xx, yy, Z, alpha=0.3)
 plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor='k')
 plt.title(title)
 plt.show()


# Bagging: Random Forest Classifier
bagging_model = RandomForestClassifier(n_estimators=10, random_state=42)
bagging_model.fit(X_train, y_train)
y_pred_bagging = bagging_model.predict(X_test)
bagging_accuracy = accuracy_score(y_test, y_pred_bagging)
plot_decision_boundaries(X, y, bagging_model, f"Bagging - Random Forest\nAccuracy: {bagging_accuracy:.2f}")



# Boosting: AdaBoost Classifier
boosting_model = AdaBoostClassifier(n_estimators=50, random_state=42)
boosting_model.fit(X_train, y_train)

y_pred_boosting = boosting_model.predict(X_test)
boosting_accuracy = accuracy_score(y_test, y_pred_boosting)
plot_decision_boundaries(X, y, boosting_model, f"Boosting - AdaBoost\nAccuracy: {boosting_accuracy:.2f}")


print(f"Bagging Accuracy (Random Forest): {bagging_accuracy:.2f}")
print(f"Boosting Accuracy (AdaBoost): {boosting_accuracy:.2f}")'''

p2='''
2.RANDOM FOREST CLASSIFIER

# Importing the libraries

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the datasets

datasets = pd.read_csv('Social_Network_Ads.csv')
X = datasets.iloc[:, [2,3]].values
Y = datasets.iloc[:, 4].values

# Splitting the dataset into the Training set and Test set

from sklearn.model_selection import train_test_split
X_Train, X_Test, Y_Train, Y_Test = train_test_split(X, Y, test_size = 0.25, random_state = 0)

# Feature Scaling

from sklearn.preprocessing import StandardScaler
sc_X = StandardScaler()
X_Train = sc_X.fit_transform(X_Train)
X_Test = sc_X.transform(X_Test)

# Fitting the classifier into the Training set

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators = 200, criterion = 'entropy', random_state = 0)
classifier.fit(X_Train,Y_Train)

# Predicting the test set results

Y_Pred = classifier.predict(X_Test)

# Making the Confusion Matrix 

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(Y_Test, Y_Pred)

# Visualising the Training set results

from matplotlib.colors import ListedColormap
X_Set, Y_Set = X_Train, Y_Train
X1, X2 = np.meshgrid(np.arange(start = X_Set[:, 0].min() - 1, stop = X_Set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_Set[:, 1].min() - 1, stop = X_Set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(Y_Set)):
    plt.scatter(X_Set[Y_Set == j, 0], X_Set[Y_Set == j, 1],
                c = ListedColormap(('red', 'green'))(i), label = j)
plt.title('Random Forest Classifier (Training set)')
plt.xlabel('Age')
plt.ylabel('Estimated Salary')
plt.legend()
plt.show()

# Visualising the Test set results

from matplotlib.colors import ListedColormap
X_Set, Y_Set = X_Test, Y_Test
X1, X2 = np.meshgrid(np.arange(start = X_Set[:, 0].min() - 1, stop = X_Set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_Set[:, 1].min() - 1, stop = X_Set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(Y_Set)):
    plt.scatter(X_Set[Y_Set == j, 0], X_Set[Y_Set == j, 1],
                c = ListedColormap(('red', 'green'))(i), label = j)
plt.title('Random Forest Classifier (Test set)')
plt.xlabel('Age')
plt.ylabel('Estimated Salary')
plt.legend()
plt.show()'''

p3='''
3.NAIVE BAYES

IRIS DATA SET

# -- coding: utf-8 --
"""
Created on Sun Nov  8 15:26:07 2020

@author: HP
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

iris=pd.read_csv('C:/Users/HP/Desktop/python prgrmg/Naive Bayes/iris.csv')
iris.columns=['sepal_length','sepal_width','petal_length','petal_width','species']

col_names=list(iris.columns)
predictors=col_names[0:4]
target=col_names[4]

from sklearn.model_selection import train_test_split
train,test=train_test_split(iris,test_size=0.3,random_state=0)

############# Naive Bayes ############

# Guassian Naive Bayes

from sklearn.naive_bayes import GaussianNB
Gmodel=GaussianNB()
Gmodel.fit(train[predictors],train[target])
train_Gpred=Gmodel.predict(train[predictors])
test_Gpred=Gmodel.predict(test[predictors])

train_acc_gau=np.mean(train_Gpred==train[target])
test_acc_gau=np.mean(test_Gpred==test[target])
train_acc_gau#0.942
test_acc_gau#1.0


#Multinomial Naive Bayes

from sklearn.naive_bayes import MultinomialNB
Mmodel=MultinomialNB()
Mmodel.fit(train[predictors],train[target])
train_Mpred=Mmodel.predict(train[predictors])
test_Mpred=Mmodel.predict(test[predictors])

train_acc_multi=np.mean(train_Mpred==train[target])
test_acc_multi=np.mean(test_Mpred==test[target])
train_acc_multi#0.704
test_acc_multi#0.6

SALARY DATA SET

# -- coding: utf-8 --
"""
Created on Sun Nov  8 16:50:03 2020

@author: HP
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

salary_train=pd.read_csv('C:/Users/HP/Desktop/assignments submission/Naive Bayes/SalaryData_Train.csv')
salary_test=pd.read_csv('C:/Users/HP/Desktop/assignments submission/Naive Bayes/SalaryData_Test.csv')
salary_train.columns
salary_test.columns
string_columns=['workclass','education','maritalstatus','occupation','relationship','race','sex','native']

from sklearn import preprocessing
label_encoder=preprocessing.LabelEncoder()
for i in string_columns:
    salary_train[i]=label_encoder.fit_transform(salary_train[i])
    salary_test[i]=label_encoder.fit_transform(salary_test[i])

col_names=list(salary_train.columns)
train_X=salary_train[col_names[0:13]]
train_Y=salary_train[col_names[13]]
test_x=salary_test[col_names[0:13]]
test_y=salary_test[col_names[13]]

######### Naive Bayes ##############

#Gaussian Naive Bayes

from sklearn.naive_bayes import GaussianNB
Gmodel=GaussianNB()
train_pred_gau=Gmodel.fit(train_X,train_Y).predict(train_X)
test_pred_gau=Gmodel.fit(train_X,train_Y).predict(test_x)

train_acc_gau=np.mean(train_pred_gau==train_Y)
test_acc_gau=np.mean(test_pred_gau==test_y)
train_acc_gau#0.795
test_acc_gau#0.794

#Multinomial Naive Bayes

from sklearn.naive_bayes import MultinomialNB
Mmodel=MultinomialNB()
train_pred_multi=Mmodel.fit(train_X,train_Y).predict(train_X)
test_pred_multi=Mmodel.fit(train_X,train_Y).predict(test_x)

train_acc_multi=np.mean(train_pred_multi==train_Y)
test_acc_multi=np.mean(test_pred_multi==test_y)
train_acc_multi#0.772
test_acc_multi#0.774'''

p4='''
4.FIND S 

#Load Libraries
import pandas as pd

#Load Dataset
df = pd.read_csv('/tennis.csv')

#Explore Dataset

df.head()

df.shape

df.info()

for i in df.columns:
    print(f'{i} : {df[i].unique()}')

# Split Dataset Into Attributes And Target
result=df['play'].values

attributes=df.drop('play',axis=1).values

#Initialization Of Specific Hypothesis
H=['0']*attributes.shape[1]

print(f'Initial Hypothesis is : {H}')

# Implement The Logic Of Find-S Algorithm
for i in range(attributes.shape[0]):
    if result[i]=='yes':
        for j in range(attributes.shape[1]):
            if H[j]=='0':
                H[j]=attributes[i][j]
            elif H[j]!=attributes[i][j]:
                H[j]='?'
    print(f'For Step-{i} : {H}')

#Final General Hypothesis

print(f'Final Hypothesis is : {H}')


LINEAR REGRESSION

# Import the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import the dataset
dataset = pd.read_csv('C:/Users/Susan/Desktop/Salary_Data.csv')
X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, 1].values

# split data into training set and test set
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/3, random_state = 0)


# Fitting simple linear regression to training set 
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)

LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

# Predicting the test set results
y_pred = regressor.predict(X_test)

# Visualizing the training set
plt.scatter(X_train, y_train, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (training set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()

# Visualizing the test set 
plt.scatter(X_test, y_test, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (test set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()'''

p4='''
4.FIND S 

#Load Libraries
import pandas as pd

#Load Dataset
df = pd.read_csv('/tennis.csv')

#Explore Dataset

df.head()

df.shape

df.info()

for i in df.columns:
    print(f'{i} : {df[i].unique()}')

# Split Dataset Into Attributes And Target
result=df['play'].values

attributes=df.drop('play',axis=1).values

#Initialization Of Specific Hypothesis
H=['0']*attributes.shape[1]

print(f'Initial Hypothesis is : {H}')

# Implement The Logic Of Find-S Algorithm
for i in range(attributes.shape[0]):
    if result[i]=='yes':
        for j in range(attributes.shape[1]):
            if H[j]=='0':
                H[j]=attributes[i][j]
            elif H[j]!=attributes[i][j]:
                H[j]='?'
    print(f'For Step-{i} : {H}')

#Final General Hypothesis

print(f'Final Hypothesis is : {H}')


LINEAR REGRESSION

# Import the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import the dataset
dataset = pd.read_csv('C:/Users/Susan/Desktop/Salary_Data.csv')
X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, 1].values

# split data into training set and test set
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/3, random_state = 0)


# Fitting simple linear regression to training set 
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)

LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)

# Predicting the test set results
y_pred = regressor.predict(X_test)

# Visualizing the training set
plt.scatter(X_train, y_train, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (training set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()

# Visualizing the test set 
plt.scatter(X_test, y_test, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (test set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()
'''

p5='''
5.SVM

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,accuracy_score
from sklearn.datasets import load_iris

iris=load_iris()
x=iris.data
y=iris.target

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)
clf=SVC(kernel='poly')

clf.fit(x_train,y_train)
y_pred=clf.predict(x_test)

accuracy=accuracy_score(y_test,y_pred)
print(f"accuracy is:{accuracy}")
clt=classification_report(y_test,y_pred)
print(f"classification :{clt}")
def plot_decision_boundary(x,y,model):
  x_min,x_max,y_min,y_max=x[:,0].min()-1,x[:,0].max()+1,x[:,1].min()-1,x[:,1].max()+1
  xx,yy=np.meshgrid(np.arange(x_min,x_max,0.01),np.arange(y_min,y_max,0.01))
  z=model.predict(np.c_[xx.ravel(),yy.ravel()])
  z=z.reshape(xx.shape)
  plt.contourf(xx,yy,z,alpha=0.3)
  plt.scatter(x[:,0],x[:,1],c=y,edgecolor='k')
  
  plt.show()
x_train_2D=x_train[:,:2]
x_test_2D=x_test[:,:2]
clf_2D=SVC(kernel='linear')
clf_2D.fit(x_train_2D,y_train)

plot_decision_boundary(x_train_2D,y_train,clf_2D)'''

p6='''
6.KNN

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris
import seaborn as sns

df = pd.read_csv('iris.csv')
df.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']

le = LabelEncoder()
df['class'] = le.fit_transform(df['class'])

X = df.drop('class', axis=1)
y = df['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_pred, y_test))
sns.heatmap(confusion_matrix(y_pred, y_test))'''

p7='''
7.ID3

#Load libraries
import numpy as np
import pandas as pd
from sklearn import metrics #Import scikit-learn metric module for accuracy calculation
#importing the dataset
df=pd.read_csv("Play Tennis.csv")
value=['Outlook','Temperature','Humidity','Wind']
df
len(df)#dataset length
df.shape #To see the number of rows and columns in our dataset
df.head()#to Inpect the first five records of the dataset
df.tail()#To inspect the last five records of the dataset
df.describe()#To see the statistical details of the dataset
#Data slicing
#machine learning algorithms can only learn from numbers(int,float,doubles..)
#so let us encode it to int
from sklearn import preprocessing
string_to_int=preprocessing.LabelEncoder()#encode your data
df=df.apply(string_to_int.fit_transform)#fit and transform it
df
#to divide our data into attribute set and label
feature_cols=['Outlook','Temprature','Humidity','Wind']
X=df[feature_cols]#contains the attribute
y=df.Play_Tennis #contains the label
#to divide our data into training and test set
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.30)
#performing the training
from sklearn.tree import DecisionTreeClassifier
classifier=DecisionTreeClassifier(criterion="entropy",random_state=100)
classifier.fit(X_train,y_train)
#Predict the response for the test dataset
y_pred=classifier.predict(X_test)
#Model Accuracy,how often is the classifier correct?
from sklearn.metrics import accuracy_score
print("Accuracy:",metrics.accuracy_score(y_test,y_pred))
data_p=pd.DataFrame({'Actual':y_test,'Predicted':y_pred})
data_p
#Evaluating the algorithm
from sklearn.metrics import classification_report,confusion_matrix
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
!pip install pydotplus
# Importing the necessary library to plot the decision tree
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

# Plotting the decision tree
plt.figure(figsize=(20, 10))  # Adjust the size of the plot
plot_tree(
    classifier,
    feature_names=feature_cols,  # Use the feature names from the dataset
    class_names=string_to_int.classes_,  # Map encoded labels back to original
    filled=True,  # Fill the nodes with colors for better readability
    rounded=True,  # Rounded corners for nodes
    fontsize=10,   # Font size for text in the tree
)
plt.title("Decision Tree Visualization", fontsize=16)
plt.show()'''

p8='''
8 LINEAR REGRESSION

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
dataset = pd.read_csv('C:/Users/Susan/Desktop/Salary_Data.csv')
X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, 1].values
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/3, random_state = 0)
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)
y_pred = regressor.predict(X_test)
# Visualizing the training set
plt.scatter(X_train, y_train, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (training set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()
# Visualizing the test set 
plt.scatter(X_test, y_test, color = 'red')
plt.plot(X_train, regressor.predict(X_train), color = 'blue')
plt.title('Salary vs Experience (test set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()'''