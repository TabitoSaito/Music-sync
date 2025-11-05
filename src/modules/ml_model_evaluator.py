import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_fscore_support

import joblib

from utils.enums import ReturnCode

# Precision: High means few false-positives
# Recall: High means few false-negatives
# F Score: Precision and Recall together


class Eval:
    def __init__(self):
        pass

    def load_dataset_from_csv(self, dataset_name: str) -> ReturnCode | None:
        if not os.path.exists(os.path.abspath(f"data/processed/{dataset_name}.csv")):
            return ReturnCode.NO_DATASET
        self.dataset = pd.read_csv(
            os.path.abspath(f"data/processed/{dataset_name}.csv"), index_col=0
        )
        self.X = self.dataset.iloc[:, :-1].values
        self.y = self.dataset.iloc[:, -1].values
        self.split_dataset()
        self.feature_scaling()

    def split_dataset(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.20, random_state=0
        )

    def feature_scaling(self):
        self.sc = StandardScaler()
        self.X_train = self.sc.fit_transform(self.X_train)
        self.X_test = self.sc.transform(self.X_test)

    def eval_logistic_regression(self, matrix: bool = False, advanced: bool = False):
        self.lr = LogisticRegression(random_state=0)
        self.lr.fit(self.X_train, self.y_train)

        y_pred = self.lr.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("Logistic Regression:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.lr

    def eval_k_nearest_neighbors(self, matrix: bool = False, advanced: bool = False):
        self.knn = KNeighborsClassifier(n_neighbors=5, metric="minkowski", p=2)
        self.knn.fit(self.X_train, self.y_train)

        y_pred = self.knn.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("K-Nearest Neighbors::")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.knn

    def eval_svm(self, matrix: bool = False, advanced: bool = False):
        self.svm = SVC(kernel="linear", random_state=0)
        self.svm.fit(self.X_train, self.y_train)

        y_pred = self.svm.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("SVM:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.svm

    def eval_kernel_svm(self, matrix: bool = False, advanced: bool = False):
        self.ksvm = SVC(kernel="rbf", random_state=0)
        self.ksvm.fit(self.X_train, self.y_train)

        y_pred = self.ksvm.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("Kernel SVM:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.ksvm

    def eval_naive_bayes(self, matrix: bool = False, advanced: bool = False):
        self.nb = GaussianNB()
        self.nb.fit(self.X_train, self.y_train)

        y_pred = self.nb.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("Naive Bayes:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.nb

    def eval_decision_tree_classification(
        self, matrix: bool = False, advanced: bool = False
    ):
        self.dtc = DecisionTreeClassifier(criterion="entropy", random_state=0)
        self.dtc.fit(self.X_train, self.y_train)

        y_pred = self.dtc.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("Decision Tree Classification:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.dtc

    def eval_random_forest_classification(
        self, matrix: bool = False, advanced: bool = False
    ):
        self.rfc = RandomForestClassifier(
            n_estimators=10, criterion="entropy", random_state=0
        )
        self.rfc.fit(self.X_train, self.y_train)

        y_pred = self.rfc.predict(self.X_test)

        score = accuracy_score(self.y_test, y_pred)

        print("Random Forest Classification:")
        print(f"accuracy_score: {score:.4f}")

        if matrix:
            cm = confusion_matrix(self.y_test, y_pred)
            print("Confusion Matrix")
            print(cm)

        if advanced:
            ad = precision_recall_fscore_support(self.y_test, y_pred)

            print("Precision:")
            class_ = 0
            for i in ad[0]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Recall:")
            class_ = 0
            for i in ad[1]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("f_score:")
            class_ = 0
            for i in ad[2]:
                print(f"Class {class_}: {i:.4f}")
                class_ += 1

            print("Occurrences:")
            class_ = 0
            for i in ad[3]:
                print(f"Class {class_}: {i}")
                class_ += 1
        print("")

        return score, self.rfc

    def eval_all_classifier(self, matrix: bool = False, advanced: bool = False):
        result_dict = {
            "Logistic Regression": self.eval_logistic_regression(matrix, advanced),
            "K-Nearest Neighbors": self.eval_k_nearest_neighbors(matrix, advanced),
            "SVM": self.eval_svm(matrix, advanced),
            "Kernel SVM": self.eval_kernel_svm(matrix, advanced),
            "Naive Bayes": self.eval_naive_bayes(matrix, advanced),
            "Decision Tree Classification": self.eval_decision_tree_classification(
                matrix, advanced
            ),
            "Random Forest Classification": self.eval_random_forest_classification(
                matrix, advanced
            ),
        }

        return result_dict

    def print_results(self):
        results = self.eval_all_classifier(matrix=True, advanced=True)
        results_score = {k: v[0] for k, v in results.items()}

        best = max(results_score, key=results.get)

        print(f"\nbest Model: {best} with accuracy_score {results[best][0]:.4f}")
        save = input("Save Models (y/n):\n")
        if save.lower() == "y":
            name = input("Name to save run: ")

            joblib.dump(
                self.lr,
                os.path.abspath(
                    f"src/modules/ML_models/{name}_logistic_regression.pkl"
                ),
            )
            joblib.dump(
                self.knn,
                os.path.abspath(
                    f"src/modules/ML_models/{name}_k_nearest_neighbors.pkl"
                ),
            )
            joblib.dump(
                self.svm, os.path.abspath(f"src/modules/ML_models/{name}_svm.pkl")
            )
            joblib.dump(
                self.ksvm,
                os.path.abspath(f"src/modules/ML_models/{name}_kernel_svm.pkl"),
            )
            joblib.dump(
                self.nb,
                os.path.abspath(f"src/modules/ML_models/{name}_naive_bayes.pkl"),
            )
            joblib.dump(
                self.dtc,
                os.path.abspath(
                    f"src/modules/ML_models/{name}_decision_tree_classification.pkl"
                ),
            )
            joblib.dump(
                self.rfc,
                os.path.abspath(
                    f"src/modules/ML_models/{name}_random_forest_classification.pkl"
                ),
            )

            scaler = self.sc
            joblib.dump(
                scaler, os.path.abspath(f"src/modules/ML_scalers/{name}_scaler.pkl")
            )
