def unbalanced_solve(X,y):
    使用RandomOverSampler从少数类的样本中进行随机采样来增加新的样本使各个分类均衡
    from imblearn.over_sampling import RandomOverSampler
    ros = RandomOverSampler(random_state=0)
    X_resampled, y_resampled = ros.fit_sample(X, y)

    [(0, 2532), (1, 2532), (2, 2532)]

    # SMOTE: 对于少数类样本a, 随机选择一个最近邻的样本b, 然后从a与b的连线上随机选取一个点c作为新的少数类样本
    from imblearn.over_sampling import SMOTE
    X_resampled_smote, y_resampled_smote = SMOTE().fit_sample(X, y)
    # [(0, 2532), (1, 2532), (2, 2532)]

    # ADASYN: 关注的是在那些基于K最近邻分类器被错误分类的原始样本附近生成新的少数类样本
    from imblearn.over_sampling import ADASYN
    X_resampled_adasyn, y_resampled_adasyn = ADASYN().fit_sample(X, y)
    # [(0, 2522), (1, 2520), (2, 2532)]

    # RandomUnderSampler函数是一种快速并十分简单的方式来平衡各个类别的数据: 随机选取数据的子集.
    from imblearn.under_sampling import RandomUnderSampler
    rus = RandomUnderSampler(random_state=0)
    X_resampled, y_resampled = rus.fit_sample(X, y)
    # [(0, 163), (1, 163), (2, 163)]

    # 在之前的SMOTE方法中, 当由边界的样本与其他样本进行过采样差值时, 很容易生成一些噪音数据. 因此, 在过采样之后需要对样本进行清洗.
    # 这样TomekLink 与 EditedNearestNeighbours方法就能实现上述的要求.
    from imblearn.combine import SMOTEENN
    smote_enn = SMOTEENN(random_state=0)
    X_resampled, y_resampled = smote_enn.fit_sample(X, y)
    sorted(Counter(y_resampled).items())
    # [(0, 2111), (1, 2099), (2, 1893)]

    from imblearn.combine import SMOTETomek
    smote_tomek = SMOTETomek(random_state=0)
    X_resampled, y_resampled = smote_tomek.fit_sample(X, y)
    sorted(Counter(y_resampled).items())
    # [(0, 2412), (1, 2414), (2, 2396)]

    # 使用SVM的权重调节处理不均衡样本 权重为balanced 意味着权重为各分类数据量的反比
    from sklearn.svm import SVC
    svm_model = SVC(class_weight='balanced')
    svm_model.fit(X, y)

    # # EasyEnsemble 通过对原始的数据集进行随机下采样实现对数据集进行集成.
    # EasyEnsemble 有两个很重要的参数: (i) n_subsets 控制的是子集的个数 and (ii) replacement 决定是有放回还是无放回的随机采样.
    from imblearn.ensemble import EasyEnsemble
    ee = EasyEnsemble(random_state=0, n_subsets=10)
    X_resampled, y_resampled = ee.fit_sample(X, y)
    # # [(0, 163), (1, 163), (2, 163)]
    print(sorted(Counter(y_resampled).items()))
    return X_resampled, y_resampled

    # BalanceCascade(级联平衡)的方法通过使用分类器(estimator参数)来确保那些被错分类的样本在下一次进行子集选取的时候也能被采样到. 同样, n_max_subset 参数控制子集的个数, 以及可以通过设置bootstrap=True来使用bootstraping(自助法).
    from imblearn.ensemble import BalanceCascade
    from sklearn.linear_model import LogisticRegression
    bc = BalanceCascade(random_state=0,
                        estimator=LogisticRegression(random_state=0),
                        n_max_subset=4)
    X_resampled, y_resampled = bc.fit_sample(X, y)
    sorted(Counter(y_resampled[0]).items())
    # [(0, 163), (1, 163), (2, 163)]

    # BalancedBaggingClassifier 允许在训练每个基学习器之前对每个子集进行重抽样. 简而言之, 该方法结合了EasyEnsemble采样器与分类器(如BaggingClassifier)的结果.
    from sklearn.tree import DecisionTreeClassifier
    from imblearn.ensemble import BalancedBaggingClassifier
    bbc = BalancedBaggingClassifier(base_estimator=DecisionTreeClassifier(),
                                    ratio='auto',
                                    replacement=False,
                                    random_state=0)
    bbc.fit(X, y)