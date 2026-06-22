# -*- coding: utf-8 -*-
"""
机器学习课程知识图谱构建脚本
============================
基于 Neo4j 图数据库，构建涵盖机器学习课程核心知识点的知识图谱。
节点规模：200+  关系规模：400+

使用方法：
  1. 确保 Neo4j 已启动（默认 bolt://localhost:7687）
  2. pip install neo4j
  3. python build_kg.py
  4. 打开 Neo4j Browser (http://localhost:7474) 查看图谱

作者：QoderWork 自动生成
日期：2026-06-22
"""

from neo4j import GraphDatabase
import sys
import time

# ===================== 配置 =====================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # ← 改成你设置的密码

# ===================== 节点定义 =====================
# 格式: (标签, {属性字典})
# 标签说明:
#   Chapter   - 章节/主题（最高层级）
#   Concept   - 核心概念
#   Algorithm - 具体算法/模型
#   Technique - 技术方法/组件
#   Metric    - 评估指标
#   Application - 应用领域

CHAPTERS = [
    ("Chapter", {"id": "ch01", "name": "机器学习概述", "desc": "机器学习的基本概念、分类与发展历程"}),
    ("Chapter", {"id": "ch02", "name": "数学基础", "desc": "线性代数、概率统计、微积分与最优化理论"}),
    ("Chapter", {"id": "ch03", "name": "数据预处理与特征工程", "desc": "数据清洗、变换、特征选择与构造"}),
    ("Chapter", {"id": "ch04", "name": "模型评估与选择", "desc": "评估方法、性能度量与超参数调优"}),
    ("Chapter", {"id": "ch05", "name": "线性模型", "desc": "线性回归、逻辑回归与线性判别分析"}),
    ("Chapter", {"id": "ch06", "name": "决策树", "desc": "决策树学习算法与剪枝策略"}),
    ("Chapter", {"id": "ch07", "name": "支持向量机", "desc": "SVM原理、核技巧与多分类扩展"}),
    ("Chapter", {"id": "ch08", "name": "概率模型与贝叶斯方法", "desc": "贝叶斯分类器与概率图模型"}),
    ("Chapter", {"id": "ch09", "name": "集成学习", "desc": "Bagging、Boosting与Stacking方法"}),
    ("Chapter", {"id": "ch10", "name": "聚类", "desc": "无监督聚类算法与有效性评估"}),
    ("Chapter", {"id": "ch11", "name": "降维与流形学习", "desc": "特征降维与流形学习方法"}),
    ("Chapter", {"id": "ch12", "name": "半监督与自监督学习", "desc": "利用无标签数据的学习范式"}),
    ("Chapter", {"id": "ch13", "name": "神经网络基础", "desc": "感知机、激活函数与反向传播"}),
    ("Chapter", {"id": "ch14", "name": "深度学习", "desc": "CNN、RNN、Transformer等深度模型"}),
    ("Chapter", {"id": "ch15", "name": "生成模型", "desc": "GAN、VAE与扩散模型"}),
    ("Chapter", {"id": "ch16", "name": "强化学习", "desc": "MDP、值函数与策略优化"}),
    ("Chapter", {"id": "ch17", "name": "自然语言处理", "desc": "文本表示、预训练模型与NLP任务"}),
    ("Chapter", {"id": "ch18", "name": "计算机视觉", "desc": "经典CNN架构与视觉任务"}),
    ("Chapter", {"id": "ch19", "name": "大模型与知识图谱", "desc": "LLM、RAG、提示工程与知识图谱"}),
]

CONCEPTS = [
    # ch01 机器学习概述
    ("Concept", {"id": "c_ml", "name": "机器学习", "desc": "通过数据驱动的方式让计算机自动学习和改进的学科"}),
    ("Concept", {"id": "c_supervised", "name": "监督学习", "desc": "从有标签的训练数据中学习映射函数"}),
    ("Concept", {"id": "c_unsupervised", "name": "无监督学习", "desc": "从无标签数据中发现隐含结构"}),
    ("Concept", {"id": "c_semi_supervised", "name": "半监督学习", "desc": "同时利用有标签和无标签数据进行学习"}),
    ("Concept", {"id": "c_self_supervised", "name": "自监督学习", "desc": "从数据本身构造监督信号进行预训练"}),
    ("Concept", {"id": "c_reinforcement", "name": "强化学习", "desc": "智能体通过与环境交互学习最优策略"}),
    ("Concept", {"id": "c_transfer", "name": "迁移学习", "desc": "将源域知识迁移到目标域以提升学习效果"}),
    ("Concept", {"id": "c_active", "name": "主动学习", "desc": "主动选择最有价值的样本进行标注"}),
    ("Concept", {"id": "c_online", "name": "在线学习", "desc": "数据按序到达时持续更新模型"}),
    ("Concept", {"id": "c_meta", "name": "元学习", "desc": "学习如何学习，快速适应新任务"}),
    ("Concept", {"id": "c_few_shot", "name": "少样本学习", "desc": "仅用极少量标注样本完成学习"}),
    ("Concept", {"id": "c_overfit", "name": "过拟合", "desc": "模型在训练集上表现好但泛化能力差"}),
    ("Concept", {"id": "c_underfit", "name": "欠拟合", "desc": "模型过于简单无法拟合训练数据"}),
    ("Concept", {"id": "c_generalization", "name": "泛化能力", "desc": "模型在未见数据上的表现能力"}),
    ("Concept", {"id": "c_bias_variance", "name": "偏差-方差权衡", "desc": "模型复杂度与泛化之间的权衡关系"}),
    ("Concept", {"id": "c_train_test", "name": "训练集/验证集/测试集", "desc": "数据划分用于模型训练、调参和评估"}),
    ("Concept", {"id": "c_hypothesis", "name": "假设空间", "desc": "模型可能取值的集合"}),
    ("Concept", {"id": "c_inductive_bias", "name": "归纳偏好", "desc": "学习算法对假设空间的偏好约束"}),
    ("Concept", {"id": "c_nfl", "name": "没有免费午餐定理", "desc": "不存在对所有问题都最优的算法"}),

    # ch02 数学基础
    ("Concept", {"id": "c_linalg", "name": "线性代数", "desc": "向量、矩阵与线性变换的数学理论"}),
    ("Concept", {"id": "c_probability", "name": "概率论", "desc": "随机事件与不确定性的数学框架"}),
    ("Concept", {"id": "c_statistics", "name": "数理统计", "desc": "基于样本数据进行推断的理论"}),
    ("Concept", {"id": "c_calculus", "name": "微积分", "desc": "函数极限、导数与积分的理论"}),
    ("Concept", {"id": "c_optimization", "name": "最优化理论", "desc": "寻找目标函数最优解的理论"}),
    ("Concept", {"id": "c_convex", "name": "凸优化", "desc": "目标函数和约束均为凸的优化问题"}),
    ("Concept", {"id": "c_info_theory", "name": "信息论", "desc": "信息量化、存储和传输的数学理论"}),
    ("Concept", {"id": "c_matrix_decomp", "name": "矩阵分解", "desc": "将矩阵分解为特定结构矩阵的乘积"}),
    ("Concept", {"id": "c_eigenvalue", "name": "特征值与特征向量", "desc": "矩阵的固有特征及其几何意义"}),
    ("Concept", {"id": "c_svd_math", "name": "奇异值分解(SVD)", "desc": "任意矩阵分解为UΣV^T的形式"}),
    ("Concept", {"id": "c_bayes_theorem", "name": "贝叶斯定理", "desc": "描述先验、似然与后验概率关系"}),
    ("Concept", {"id": "c_mle", "name": "最大似然估计", "desc": "选择使似然函数最大的参数值"}),
    ("Concept", {"id": "c_map", "name": "最大后验估计", "desc": "在MLE基础上引入先验分布"}),
    ("Concept", {"id": "c_entropy", "name": "熵", "desc": "衡量随机变量不确定性的度量"}),
    ("Concept", {"id": "c_kl", "name": "KL散度", "desc": "衡量两个概率分布之间的差异"}),
    ("Concept", {"id": "c_cross_entropy", "name": "交叉熵", "desc": "衡量预测分布与真实分布的差异"}),
    ("Concept", {"id": "c_mutual_info", "name": "互信息", "desc": "衡量两个随机变量之间的相关性"}),
    ("Concept", {"id": "c_lagrange", "name": "拉格朗日乘子法", "desc": "求解带约束优化问题的方法"}),
    ("Concept", {"id": "c_kkt", "name": "KKT条件", "desc": "非线性规划最优性的必要条件"}),
    ("Concept", {"id": "c_gradient", "name": "梯度", "desc": "函数值增长最快的方向"}),
    ("Concept", {"id": "c_hessian", "name": "Hessian矩阵", "desc": "二阶偏导数构成的方阵，描述曲率"}),

    # ch03 数据预处理与特征工程
    ("Concept", {"id": "c_data_clean", "name": "数据清洗", "desc": "处理缺失值、异常值和重复数据"}),
    ("Concept", {"id": "c_missing", "name": "缺失值处理", "desc": "填充、删除或插补缺失数据"}),
    ("Concept", {"id": "c_outlier", "name": "异常值检测", "desc": "识别和处理偏离正常模式的数据点"}),
    ("Concept", {"id": "c_normalization", "name": "数据归一化", "desc": "将数据缩放到[0,1]区间"}),
    ("Concept", {"id": "c_standardization", "name": "数据标准化", "desc": "将数据转换为均值0方差1的分布"}),
    ("Concept", {"id": "c_encoding", "name": "类别编码", "desc": "将类别变量转换为数值表示"}),
    ("Concept", {"id": "c_onehot", "name": "独热编码", "desc": "用二进制向量表示类别"}),
    ("Concept", {"id": "c_label_encoding", "name": "标签编码", "desc": "将类别映射为整数"}),
    ("Concept", {"id": "c_feature_eng", "name": "特征工程", "desc": "从原始数据中构造有效特征的过程"}),
    ("Concept", {"id": "c_feature_select", "name": "特征选择", "desc": "从特征集中选取最有用的子集"}),
    ("Concept", {"id": "c_filter_method", "name": "过滤法", "desc": "基于统计指标筛选特征"}),
    ("Concept", {"id": "c_wrapper_method", "name": "包裹法", "desc": "用模型性能评估特征子集"}),
    ("Concept", {"id": "c_embedded_method", "name": "嵌入法", "desc": "在模型训练中自动进行特征选择"}),
    ("Concept", {"id": "c_pca_feature", "name": "PCA降维", "desc": "通过主成分分析降低特征维度"}),
    ("Concept", {"id": "c_feature_cross", "name": "特征交叉", "desc": "组合多个特征生成新特征"}),
    ("Concept", {"id": "c_feature_scale", "name": "特征缩放", "desc": "统一不同特征的数值范围"}),
    ("Concept", {"id": "c_imbalance", "name": "类别不平衡", "desc": "不同类别样本数量差异悬殊"}),
    ("Concept", {"id": "c_smote", "name": "SMOTE过采样", "desc": "通过插值生成少数类合成样本"}),
    ("Concept", {"id": "c_undersample", "name": "欠采样", "desc": "减少多数类样本以平衡数据"}),
    ("Concept", {"id": "c_data_augment", "name": "数据增强", "desc": "通过变换扩充训练数据量"}),

    # ch04 模型评估与选择
    ("Concept", {"id": "c_cv", "name": "交叉验证", "desc": "将数据多次划分以评估模型性能"}),
    ("Concept", {"id": "c_kfold", "name": "K折交叉验证", "desc": "将数据均分为K份轮流作为验证集"}),
    ("Concept", {"id": "c_loo", "name": "留一法", "desc": "每次留一个样本作为验证集"}),
    ("Concept", {"id": "c_bootstrap", "name": "自助法", "desc": "有放回抽样构造训练集"}),
    ("Concept", {"id": "c_confusion", "name": "混淆矩阵", "desc": "展示分类结果的TP/FP/TN/FN统计"}),
    ("Concept", {"id": "c_precision", "name": "精确率", "desc": "预测为正的样本中实际为正的比例"}),
    ("Concept", {"id": "c_recall", "name": "召回率", "desc": "实际为正的样本中被正确预测的比例"}),
    ("Concept", {"id": "c_f1", "name": "F1分数", "desc": "精确率与召回率的调和平均"}),
    ("Concept", {"id": "c_roc", "name": "ROC曲线", "desc": "TPR随FPR变化的曲线"}),
    ("Concept", {"id": "c_auc", "name": "AUC", "desc": "ROC曲线下面积，衡量分类器整体性能"}),
    ("Concept", {"id": "c_mse", "name": "均方误差(MSE)", "desc": "预测值与真实值差的平方的均值"}),
    ("Concept", {"id": "c_r2", "name": "R²分数", "desc": "回归模型的决定系数"}),
    ("Concept", {"id": "c_mae", "name": "平均绝对误差(MAE)", "desc": "预测误差绝对值的均值"}),
    ("Concept", {"id": "c_logloss", "name": "对数损失", "desc": "衡量概率预测的对数误差"}),
    ("Concept", {"id": "c_hyperparam", "name": "超参数调优", "desc": "搜索最优超参数组合的过程"}),
    ("Concept", {"id": "c_grid_search", "name": "网格搜索", "desc": "穷举搜索超参数空间"}),
    ("Concept", {"id": "c_random_search", "name": "随机搜索", "desc": "随机采样超参数空间"}),
    ("Concept", {"id": "c_bayes_opt", "name": "贝叶斯优化", "desc": "基于代理模型的高效超参数搜索"}),

    # ch16 强化学习概念
    ("Concept", {"id": "c_mdp", "name": "马尔可夫决策过程", "desc": "强化学习的数学框架：状态、动作、转移、奖励"}),
    ("Concept", {"id": "c_state", "name": "状态", "desc": "环境的当前情况描述"}),
    ("Concept", {"id": "c_action", "name": "动作", "desc": "智能体在某一状态下可采取的行为"}),
    ("Concept", {"id": "c_reward", "name": "奖励", "desc": "环境对智能体动作的反馈信号"}),
    ("Concept", {"id": "c_policy", "name": "策略", "desc": "状态到动作的映射规则"}),
    ("Concept", {"id": "c_value_func", "name": "价值函数", "desc": "评估状态或状态-动作对的长期收益"}),
    ("Concept", {"id": "c_q_func", "name": "Q函数", "desc": "状态-动作对的期望累积奖励"}),
    ("Concept", {"id": "c_explore", "name": "探索与利用", "desc": "尝试新动作与利用已知最优之间的权衡"}),
    ("Concept", {"id": "c_discount", "name": "折扣因子", "desc": "衡量未来奖励重要程度的参数γ"}),

    # ch19 大模型概念
    ("Concept", {"id": "c_llm", "name": "大语言模型", "desc": "基于海量数据训练的超大规模语言模型"}),
    ("Concept", {"id": "c_rag", "name": "RAG检索增强生成", "desc": "结合检索与生成的问答框架"}),
    ("Concept", {"id": "c_prompt_eng", "name": "提示工程", "desc": "设计有效提示词以引导模型输出"}),
    ("Concept", {"id": "c_fine_tune", "name": "微调", "desc": "在预训练模型上用特定任务数据继续训练"}),
    ("Concept", {"id": "c_kg", "name": "知识图谱", "desc": "以图结构组织知识，表示实体及其关系"}),
    ("Concept", {"id": "c_embedding", "name": "向量嵌入", "desc": "将离散对象映射为连续稠密向量"}),
    ("Concept", {"id": "c_vector_db", "name": "向量数据库", "desc": "存储和检索高维向量的专用数据库"}),
    ("Concept", {"id": "c_rlhf", "name": "RLHF", "desc": "基于人类反馈的强化学习对齐技术"}),
]

ALGORITHMS = [
    # ch05 线性模型
    ("Algorithm", {"id": "a_linreg", "name": "线性回归", "desc": "用线性函数拟合输入与输出的关系", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_ridge", "name": "岭回归", "desc": "带L2正则化的线性回归", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_lasso", "name": "LASSO回归", "desc": "带L1正则化的线性回归，可实现特征选择", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_polyreg", "name": "多项式回归", "desc": "用多项式特征扩展线性回归", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_logreg", "name": "逻辑回归", "desc": "用于二分类的广义线性模型", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_lda_algo", "name": "线性判别分析", "desc": "寻找最优投影方向以最大化类间分离", "chapter": "ch05"}),
    ("Algorithm", {"id": "a_softmax", "name": "Softmax回归", "desc": "逻辑回归在多分类上的推广", "chapter": "ch05"}),

    # ch06 决策树
    ("Algorithm", {"id": "a_id3", "name": "ID3", "desc": "基于信息增益构建决策树", "chapter": "ch06"}),
    ("Algorithm", {"id": "a_c45", "name": "C4.5", "desc": "基于信息增益比构建决策树", "chapter": "ch06"}),
    ("Algorithm", {"id": "a_cart", "name": "CART", "desc": "基于基尼指数构建二叉决策树", "chapter": "ch06"}),
    ("Algorithm", {"id": "a_preprune", "name": "预剪枝", "desc": "在树生长过程中提前停止分裂", "chapter": "ch06"}),
    ("Algorithm", {"id": "a_postprune", "name": "后剪枝", "desc": "先生成完整树再自底向上剪枝", "chapter": "ch06"}),

    # ch07 支持向量机
    ("Algorithm", {"id": "a_svm_linear", "name": "线性SVM", "desc": "寻找最大间隔超平面", "chapter": "ch07"}),
    ("Algorithm", {"id": "a_svm_kernel", "name": "核SVM", "desc": "利用核技巧在高维空间构建非线性分类面", "chapter": "ch07"}),
    ("Algorithm", {"id": "a_svr", "name": "支持向量回归(SVR)", "desc": "SVM在回归任务上的扩展", "chapter": "ch07"}),
    ("Algorithm", {"id": "a_rbf", "name": "RBF核", "desc": "高斯径向基核函数，最常用的SVM核", "chapter": "ch07"}),
    ("Algorithm", {"id": "a_poly_kernel", "name": "多项式核", "desc": "基于多项式映射的核函数", "chapter": "ch07"}),
    ("Algorithm", {"id": "a_sigmoid_kernel", "name": "Sigmoid核", "desc": "类似神经网络激活函数的核", "chapter": "ch07"}),

    # ch08 概率模型
    ("Algorithm", {"id": "a_naive_bayes", "name": "朴素贝叶斯", "desc": "基于特征条件独立假设的贝叶斯分类器", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_gnb", "name": "高斯朴素贝叶斯", "desc": "假设特征服从高斯分布", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_mnb", "name": "多项式朴素贝叶斯", "desc": "适用于离散特征（如文本）", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_bnb", "name": "伯努利朴素贝叶斯", "desc": "适用于二值特征", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_hmm", "name": "隐马尔可夫模型", "desc": "含有隐变量的马尔可夫过程模型", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_em", "name": "EM算法", "desc": "含隐变量模型的最大似然估计迭代算法", "chapter": "ch08"}),
    ("Algorithm", {"id": "a_gmm", "name": "高斯混合模型(GMM)", "desc": "用多个高斯分布的混合建模数据", "chapter": "ch08"}),

    # ch09 集成学习
    ("Algorithm", {"id": "a_bagging", "name": "Bagging", "desc": "自助采样训练多个基学习器并投票", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_rf", "name": "随机森林", "desc": "基于决策树的Bagging + 特征随机选择", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_adaboost", "name": "AdaBoost", "desc": "自适应提升，迭代加权训练弱学习器", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_gbdt", "name": "GBDT", "desc": "梯度提升决策树，拟合残差的集成方法", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_xgboost", "name": "XGBoost", "desc": "高效的梯度提升框架，支持正则化", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_lightgbm", "name": "LightGBM", "desc": "微软高效梯度提升框架，直方图加速", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_catboost", "name": "CatBoost", "desc": "Yandex的梯度提升框架，擅长类别特征", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_stacking", "name": "Stacking", "desc": "用元学习器融合多个基学习器的预测", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_voting", "name": "投票法", "desc": "多个学习器投票决定最终预测", "chapter": "ch09"}),
    ("Algorithm", {"id": "a_blending", "name": "Blending", "desc": "用验证集预测结果训练元模型", "chapter": "ch09"}),

    # ch10 聚类
    ("Algorithm", {"id": "a_kmeans", "name": "K-Means", "desc": "基于距离的迭代聚类算法", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_kmeanspp", "name": "K-Means++", "desc": "改进初始中心选择的K-Means", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_kmedoids", "name": "K-Medoids", "desc": "用实际样本点作为聚类中心", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_dbscan", "name": "DBSCAN", "desc": "基于密度的聚类，可发现任意形状簇", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_optics", "name": "OPTICS", "desc": "DBSCAN的扩展，适应不同密度", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_agglo", "name": "层次聚类", "desc": "自底向上或自顶向下构建聚类树", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_spectral", "name": "谱聚类", "desc": "基于图拉普拉斯矩阵特征进行聚类", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_meanshift", "name": "MeanShift", "desc": "基于密度峰值搜索的聚类算法", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_birch", "name": "BIRCH", "desc": "基于CF树的增量聚类算法", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_silhouette", "name": "轮廓系数", "desc": "衡量聚类内部紧密度与聚类间分离度", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_elbow", "name": "肘部法则", "desc": "通过误差平方和曲线选择最优K值", "chapter": "ch10"}),

    # ch11 降维
    ("Algorithm", {"id": "a_pca", "name": "PCA主成分分析", "desc": "线性降维，保留最大方差方向", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_kpca", "name": "核PCA", "desc": "利用核技巧进行非线性降维", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_lda_dim", "name": "LDA(降维)", "desc": "线性判别分析用于有监督降维", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_tsne", "name": "t-SNE", "desc": "基于概率分布的非线性降维与可视化", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_umap", "name": "UMAP", "desc": "基于流形学习的高效降维与可视化", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_isomap", "name": "Isomap", "desc": "基于测地距离的流形学习", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_le", "name": "拉普拉斯特征映射", "desc": "基于图拉普拉斯的流形学习", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_ica", "name": "独立成分分析(ICA)", "desc": "将信号分解为统计独立的成分", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_nmf", "name": "非负矩阵分解(NMF)", "desc": "将非负矩阵分解为两个非负矩阵乘积", "chapter": "ch11"}),
    ("Algorithm", {"id": "a_mds", "name": "多维缩放(MDS)", "desc": "保持样本间距离关系的降维方法", "chapter": "ch11"}),

    # ch12 半监督/自监督
    ("Algorithm", {"id": "a_label_prop", "name": "标签传播", "desc": "在图上传播标签到未标注节点", "chapter": "ch12"}),
    ("Algorithm", {"id": "a_self_train", "name": "自训练", "desc": "用模型预测高置信度样本加入训练", "chapter": "ch12"}),
    ("Algorithm", {"id": "a_co_train", "name": "协同训练", "desc": "两个视图的学习器互相标注", "chapter": "ch12"}),
    ("Algorithm", {"id": "a_contrastive", "name": "对比学习", "desc": "拉近正样本对、推远负样本对的自监督方法", "chapter": "ch12"}),
    ("Algorithm", {"id": "a_mlm", "name": "掩码语言建模", "desc": "预测被遮蔽的token，BERT预训练任务", "chapter": "ch12"}),
    ("Algorithm", {"id": "a_mae_algo", "name": "掩码自编码器(MAE)", "desc": "遮蔽部分输入并重建，ViT预训练方法", "chapter": "ch12"}),

    # ch13 神经网络基础
    ("Algorithm", {"id": "a_perceptron", "name": "感知机", "desc": "最简单的线性二分类器", "chapter": "ch13"}),
    ("Algorithm", {"id": "a_mlp", "name": "多层感知机(MLP)", "desc": "含隐藏层的前馈神经网络", "chapter": "ch13"}),
    ("Algorithm", {"id": "a_bp", "name": "反向传播", "desc": "基于链式法则计算梯度的训练算法", "chapter": "ch13"}),
    ("Algorithm", {"id": "a_xavier", "name": "Xavier初始化", "desc": "基于方差保持的权重初始化方法", "chapter": "ch13"}),
    ("Algorithm", {"id": "a_he_init", "name": "He初始化", "desc": "适用于ReLU激活的权重初始化", "chapter": "ch13"}),

    # ch14 深度学习架构
    ("Algorithm", {"id": "a_cnn", "name": "卷积神经网络(CNN)", "desc": "利用卷积核提取空间特征的深度网络", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_rnn", "name": "循环神经网络(RNN)", "desc": "处理序列数据的递归结构网络", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_lstm", "name": "长短期记忆网络(LSTM)", "desc": "通过门控机制解决长距离依赖", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_gru", "name": "门控循环单元(GRU)", "desc": "LSTM的简化变体，参数更少", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_transformer", "name": "Transformer", "desc": "基于自注意力机制的序列模型架构", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_attention", "name": "注意力机制", "desc": "动态加权关注输入的不同部分", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_self_attn", "name": "自注意力", "desc": "序列内部元素之间的注意力计算", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_mha", "name": "多头注意力", "desc": "并行计算多个注意力头并拼接", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_resnet", "name": "ResNet残差网络", "desc": "通过跳跃连接训练极深网络", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_gnn", "name": "图神经网络(GNN)", "desc": "处理图结构数据的神经网络", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_gcn", "name": "图卷积网络(GCN)", "desc": "在图上执行卷积操作", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_unet", "name": "U-Net", "desc": "编码器-解码器结构用于图像分割", "chapter": "ch14"}),
    ("Algorithm", {"id": "a_diffusion", "name": "扩散模型", "desc": "通过逐步去噪过程生成数据", "chapter": "ch14"}),

    # ch15 生成模型
    ("Algorithm", {"id": "a_gan", "name": "生成对抗网络(GAN)", "desc": "生成器与判别器的对抗训练框架", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_dcgan", "name": "DCGAN", "desc": "使用卷积结构的GAN", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_wgan", "name": "WGAN", "desc": "使用Wasserstein距离改进GAN训练", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_stylegan", "name": "StyleGAN", "desc": "风格控制的高质量图像生成模型", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_vae", "name": "变分自编码器(VAE)", "desc": "基于变分推断的生成模型", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_ae", "name": "自编码器(AE)", "desc": "学习数据压缩表示的网络", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_dae", "name": "去噪自编码器", "desc": "从加噪数据中恢复原始数据", "chapter": "ch15"}),
    ("Algorithm", {"id": "a_flow", "name": "归一化流", "desc": "通过可逆变换构建复杂分布", "chapter": "ch15"}),

    # ch16 强化学习算法
    ("Algorithm", {"id": "a_qlearning", "name": "Q-Learning", "desc": "基于值函数的无模型RL算法", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_sarsa", "name": "SARSA", "desc": "在线策略的TD控制算法", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_dqn", "name": "DQN", "desc": "用深度网络近似Q函数", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_pg", "name": "策略梯度", "desc": "直接优化策略参数的RL方法", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_a2c", "name": "A2C/A3C", "desc": "Actor-Critic架构的异步/同步版本", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_ppo", "name": "PPO", "desc": "近端策略优化，稳定高效的RL算法", "chapter": "ch16"}),
    ("Algorithm", {"id": "a_ddpg", "name": "DDPG", "desc": "深度确定性策略梯度，用于连续动作空间", "chapter": "ch16"}),

    # ch17 NLP算法
    ("Algorithm", {"id": "a_word2vec", "name": "Word2Vec", "desc": "将词映射为稠密向量的浅层模型", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_glove", "name": "GloVe", "desc": "基于全局共现矩阵的词嵌入方法", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_fasttext", "name": "FastText", "desc": "考虑子词信息的词嵌入方法", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_bert", "name": "BERT", "desc": "双向Transformer编码器预训练模型", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_gpt", "name": "GPT", "desc": "自回归Transformer解码器预训练模型", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_gpt2", "name": "GPT-2", "desc": "GPT的大规模版本，展示零样本能力", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_gpt3", "name": "GPT-3/GPT-4", "desc": "超大规模语言模型，涌现能力", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_seq2seq", "name": "Seq2Seq", "desc": "编码器-解码器的序列到序列框架", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_elmo", "name": "ELMo", "desc": "基于双向LSTM的上下文词嵌入", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_t5", "name": "T5", "desc": "统一文本到文本的Transformer框架", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_llama", "name": "LLaMA", "desc": "Meta开源的高效大语言模型", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_deepseek", "name": "DeepSeek", "desc": "国产高性能开源大语言模型", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_bow", "name": "词袋模型(BoW)", "desc": "基于词频的文本表示方法", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_tfidf", "name": "TF-IDF", "desc": "考虑词频和逆文档频率的文本加权", "chapter": "ch17"}),
    ("Algorithm", {"id": "a_ngram", "name": "N-gram模型", "desc": "基于n个连续词的统计语言模型", "chapter": "ch17"}),

    # ch18 计算机视觉架构
    ("Algorithm", {"id": "a_lenet", "name": "LeNet", "desc": "LeCun提出的早期CNN，用于手写数字识别", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_alexnet", "name": "AlexNet", "desc": "2012年ImageNet冠军，开启深度学习时代", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_vgg", "name": "VGG", "desc": "使用3×3小卷积核的深层网络", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_googlenet", "name": "GoogLeNet/Inception", "desc": "引入Inception模块的多尺度网络", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_mobilenet", "name": "MobileNet", "desc": "面向移动端的轻量级网络", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_yolo", "name": "YOLO", "desc": "单阶段实时目标检测算法", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_rcnn_family", "name": "R-CNN系列", "desc": "R-CNN → Fast R-CNN → Faster R-CNN", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_ssd", "name": "SSD", "desc": "多尺度特征图的单阶段检测器", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_vit", "name": "Vision Transformer(ViT)", "desc": "将Transformer应用于图像分类", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_swin", "name": "Swin Transformer", "desc": "分层移动窗口的视觉Transformer", "chapter": "ch18"}),
    ("Algorithm", {"id": "a_sam", "name": "SAM分割模型", "desc": "Segment Anything Model，通用图像分割", "chapter": "ch18"}),

    # 关联规则
    ("Algorithm", {"id": "a_apriori", "name": "Apriori", "desc": "基于频繁项集挖掘关联规则", "chapter": "ch10"}),
    ("Algorithm", {"id": "a_fpgrowth", "name": "FP-Growth", "desc": "基于FP树的频繁项集挖掘算法", "chapter": "ch10"}),
]

TECHNIQUES = [
    # 优化算法
    ("Technique", {"id": "t_gd", "name": "梯度下降法", "desc": "沿负梯度方向迭代更新参数", "category": "优化"}),
    ("Technique", {"id": "t_sgd", "name": "随机梯度下降(SGD)", "desc": "每次用一个样本更新参数", "category": "优化"}),
    ("Technique", {"id": "t_minibatch", "name": "小批量梯度下降", "desc": "每次用一小批数据更新", "category": "优化"}),
    ("Technique", {"id": "t_momentum", "name": "动量法", "desc": "累积历史梯度方向加速收敛", "category": "优化"}),
    ("Technique", {"id": "t_adagrad", "name": "AdaGrad", "desc": "自适应学习率，对稀疏特征友好", "category": "优化"}),
    ("Technique", {"id": "t_rmsprop", "name": "RMSProp", "desc": "用指数移动平均平滑梯度", "category": "优化"}),
    ("Technique", {"id": "t_adam", "name": "Adam", "desc": "结合动量和RMSProp的自适应优化器", "category": "优化"}),
    ("Technique", {"id": "t_adamw", "name": "AdamW", "desc": "Adam + 解耦权重衰减", "category": "优化"}),
    ("Technique", {"id": "t_newton", "name": "牛顿法", "desc": "利用二阶导数信息的优化方法", "category": "优化"}),
    ("Technique", {"id": "t_lbfgs", "name": "L-BFGS", "desc": "拟牛顿法，近似Hessian矩阵", "category": "优化"}),

    # 激活函数
    ("Technique", {"id": "t_sigmoid", "name": "Sigmoid", "desc": "σ(x)=1/(1+e^(-x))，输出(0,1)", "category": "激活函数"}),
    ("Technique", {"id": "t_tanh", "name": "Tanh", "desc": "双曲正切，输出(-1,1)", "category": "激活函数"}),
    ("Technique", {"id": "t_relu", "name": "ReLU", "desc": "max(0,x)，最常用的激活函数", "category": "激活函数"}),
    ("Technique", {"id": "t_leaky_relu", "name": "Leaky ReLU", "desc": "负半轴有小斜率的ReLU变体", "category": "激活函数"}),
    ("Technique", {"id": "t_elu", "name": "ELU", "desc": "指数线性单元，负半轴平滑", "category": "激活函数"}),
    ("Technique", {"id": "t_gelu", "name": "GELU", "desc": "高斯误差线性单元，BERT/GPT使用", "category": "激活函数"}),
    ("Technique", {"id": "t_swish", "name": "Swish", "desc": "x·σ(x)，自搜索激活函数", "category": "激活函数"}),
    ("Technique", {"id": "t_softmax_tech", "name": "Softmax", "desc": "将向量转换为概率分布", "category": "激活函数"}),

    # 损失函数
    ("Technique", {"id": "t_mse_loss", "name": "MSE损失", "desc": "均方误差，回归任务常用", "category": "损失函数"}),
    ("Technique", {"id": "t_mae_loss", "name": "MAE损失", "desc": "平均绝对误差，对异常值鲁棒", "category": "损失函数"}),
    ("Technique", {"id": "t_ce_loss", "name": "交叉熵损失", "desc": "分类任务的标准损失函数", "category": "损失函数"}),
    ("Technique", {"id": "t_hinge_loss", "name": "Hinge损失", "desc": "SVM使用的间隔损失", "category": "损失函数"}),
    ("Technique", {"id": "t_focal_loss", "name": "Focal Loss", "desc": "处理类别不平衡的改进交叉熵", "category": "损失函数"}),
    ("Technique", {"id": "t_triplet_loss", "name": "Triplet Loss", "desc": "度量学习中拉近正对推远负对", "category": "损失函数"}),
    ("Technique", {"id": "t_contrastive_loss", "name": "对比损失", "desc": "对比学习中的损失函数", "category": "损失函数"}),
    ("Technique", {"id": "t_huber_loss", "name": "Huber损失", "desc": "MSE与MAE的折中，对异常值鲁棒", "category": "损失函数"}),

    # 正则化
    ("Technique", {"id": "t_l1_reg", "name": "L1正则化", "desc": "权重绝对值惩罚，促进稀疏", "category": "正则化"}),
    ("Technique", {"id": "t_l2_reg", "name": "L2正则化", "desc": "权重平方惩罚，防止过大", "category": "正则化"}),
    ("Technique", {"id": "t_dropout", "name": "Dropout", "desc": "训练时随机丢弃神经元防止过拟合", "category": "正则化"}),
    ("Technique", {"id": "t_bn", "name": "Batch Normalization", "desc": "对每批数据进行归一化加速训练", "category": "正则化"}),
    ("Technique", {"id": "t_ln", "name": "Layer Normalization", "desc": "对单个样本进行归一化，适合RNN/Transformer", "category": "正则化"}),
    ("Technique", {"id": "t_early_stop", "name": "早停", "desc": "验证集性能不再提升时停止训练", "category": "正则化"}),
    ("Technique", {"id": "t_warmup", "name": "学习率预热", "desc": "训练初期逐步增大学习率", "category": "正则化"}),
    ("Technique", {"id": "t_cosine_decay", "name": "余弦退火", "desc": "学习率按余弦曲线衰减", "category": "正则化"}),
    ("Technique", {"id": "t_label_smooth", "name": "标签平滑", "desc": "软化硬标签防止过拟合", "category": "正则化"}),

    # 卷积组件
    ("Technique", {"id": "t_conv", "name": "卷积操作", "desc": "用卷积核在输入上滑动提取特征", "category": "网络组件"}),
    ("Technique", {"id": "t_pooling", "name": "池化操作", "desc": "下采样减少特征图尺寸", "category": "网络组件"}),
    ("Technique", {"id": "t_maxpool", "name": "最大池化", "desc": "取局部区域最大值", "category": "网络组件"}),
    ("Technique", {"id": "t_avgpool", "name": "平均池化", "desc": "取局部区域均值", "category": "网络组件"}),
    ("Technique", {"id": "t_gloabl_avgpool", "name": "全局平均池化", "desc": "对整个特征图取平均", "category": "网络组件"}),
    ("Technique", {"id": "t_skip_connect", "name": "跳跃连接", "desc": "残差网络中的恒等映射通路", "category": "网络组件"}),
    ("Technique", {"id": "t_pos_encoding", "name": "位置编码", "desc": "为Transformer提供序列位置信息", "category": "网络组件"}),
    ("Technique", {"id": "t_ffn", "name": "前馈网络层(FFN)", "desc": "Transformer中的两层全连接网络", "category": "网络组件"}),

    # NLP技术
    ("Technique", {"id": "t_tokenize", "name": "分词", "desc": "将文本切分为词或子词单元", "category": "NLP"}),
    ("Technique", {"id": "t_bpe", "name": "BPE子词分词", "desc": "基于字节对编码的子词分割", "category": "NLP"}),
    ("Technique", {"id": "t_stopword", "name": "停用词过滤", "desc": "去除无意义的高频词", "category": "NLP"}),
    ("Technique", {"id": "t_stemming", "name": "词干提取", "desc": "将词还原为词干形式", "category": "NLP"}),

    # 训练技术
    ("Technique", {"id": "t_transfer_tech", "name": "迁移训练", "desc": "在预训练模型基础上微调", "category": "训练"}),
    ("Technique", {"id": "t_freeze", "name": "冻结层训练", "desc": "固定部分层参数只训练特定层", "category": "训练"}),
    ("Technique", {"id": "t_lora", "name": "LoRA", "desc": "低秩适应，高效微调大模型", "category": "训练"}),
    ("Technique", {"id": "t_distillation", "name": "知识蒸馏", "desc": "将大模型知识迁移到小模型", "category": "训练"}),
    ("Technique", {"id": "t_mixup", "name": "Mixup", "desc": "线性混合样本和标签的数据增强", "category": "训练"}),
    ("Technique", {"id": "t_cutmix", "name": "CutMix", "desc": "裁剪拼接不同图像的数据增强", "category": "训练"}),
    ("Technique", {"id": "t_gradient_clip", "name": "梯度裁剪", "desc": "限制梯度大小防止梯度爆炸", "category": "训练"}),
]

APPLICATIONS = [
    ("Application", {"id": "app_img_cls", "name": "图像分类", "desc": "将图像分配到预定义类别"}),
    ("Application", {"id": "app_obj_det", "name": "目标检测", "desc": "定位并识别图像中的目标"}),
    ("Application", {"id": "app_seg", "name": "图像分割", "desc": "像素级别的图像区域分类"}),
    ("Application", {"id": "app_face", "name": "人脸识别", "desc": "基于面部特征的身份识别"}),
    ("Application", {"id": "app_text_cls", "name": "文本分类", "desc": "将文本分配到预定义类别"}),
    ("Application", {"id": "app_sentiment", "name": "情感分析", "desc": "判断文本表达的情感极性"}),
    ("Application", {"id": "app_mt", "name": "机器翻译", "desc": "自动将文本从一种语言翻译为另一种"}),
    ("Application", {"id": "app_qa", "name": "问答系统", "desc": "根据问题自动生成答案"}),
    ("Application", {"id": "app_summarize", "name": "文本摘要", "desc": "自动生成文本的简短摘要"}),
    ("Application", {"id": "app_rec", "name": "推荐系统", "desc": "为用户推荐感兴趣的物品"}),
    ("Application", {"id": "app_ad", "name": "异常检测", "desc": "识别偏离正常模式的数据"}),
    ("Application", {"id": "app_timeseries", "name": "时间序列预测", "desc": "预测时间序列的未来趋势"}),
    ("Application", {"id": "app_speech", "name": "语音识别", "desc": "将语音信号转换为文本"}),
    ("Application", {"id": "app_tts", "name": "语音合成(TTS)", "desc": "将文本转换为自然语音"}),
    ("Application", {"id": "app_img_gen", "name": "图像生成", "desc": "生成逼真的新图像"}),
    ("Application", {"id": "app_img_caption", "name": "图像描述", "desc": "自动为图像生成文字描述"}),
    ("Application", {"id": "app_ner", "name": "命名实体识别", "desc": "从文本中识别人名地名等实体"}),
    ("Application", {"id": "app_kg_app", "name": "知识图谱应用", "desc": "知识表示、推理和问答"}),
    ("Application", {"id": "app_autonomous", "name": "自动驾驶", "desc": "基于感知和决策的车辆自主行驶"}),
    ("Application", {"id": "app_medical", "name": "医学影像分析", "desc": "利用AI辅助医学图像诊断"}),
]


# ===================== 关系定义 =====================
# 格式: (起始节点id, 终止节点id, 关系类型, {属性})

RELATIONS = []

# --- 章节之间的前置关系 ---
CHAPTER_PREREQS = [
    ("ch01", "ch02", "HAS_PREREQ", {}),
    ("ch01", "ch03", "HAS_PREREQ", {}),
    ("ch02", "ch04", "HAS_PREREQ", {}),
    ("ch03", "ch04", "HAS_PREREQ", {}),
    ("ch03", "ch05", "HAS_PREREQ", {}),
    ("ch04", "ch05", "HAS_PREREQ", {}),
    ("ch05", "ch06", "HAS_PREREQ", {}),
    ("ch05", "ch07", "HAS_PREREQ", {}),
    ("ch05", "ch08", "HAS_PREREQ", {}),
    ("ch06", "ch09", "HAS_PREREQ", {}),
    ("ch07", "ch09", "HAS_PREREQ", {}),
    ("ch08", "ch09", "HAS_PREREQ", {}),
    ("ch03", "ch10", "HAS_PREREQ", {}),
    ("ch03", "ch11", "HAS_PREREQ", {}),
    ("ch05", "ch12", "HAS_PREREQ", {}),
    ("ch10", "ch12", "HAS_PREREQ", {}),
    ("ch02", "ch13", "HAS_PREREQ", {}),
    ("ch13", "ch14", "HAS_PREREQ", {}),
    ("ch14", "ch15", "HAS_PREREQ", {}),
    ("ch14", "ch16", "HAS_PREREQ", {}),
    ("ch14", "ch17", "HAS_PREREQ", {}),
    ("ch14", "ch18", "HAS_PREREQ", {}),
    ("ch14", "ch19", "HAS_PREREQ", {}),
    ("ch17", "ch19", "HAS_PREREQ", {}),
]
RELATIONS.extend([(s, t, r, p) for s, t, r, p in CHAPTER_PREREQS])

# --- 章节包含概念/算法 ---
CHAPTER_CONTAINS = [
    # ch01
    ("ch01", "c_ml"), ("ch01", "c_supervised"), ("ch01", "c_unsupervised"),
    ("ch01", "c_semi_supervised"), ("ch01", "c_self_supervised"), ("ch01", "c_reinforcement"),
    ("ch01", "c_transfer"), ("ch01", "c_active"), ("ch01", "c_online"), ("ch01", "c_meta"),
    ("ch01", "c_few_shot"), ("ch01", "c_overfit"), ("ch01", "c_underfit"),
    ("ch01", "c_generalization"), ("ch01", "c_bias_variance"), ("ch01", "c_train_test"),
    ("ch01", "c_hypothesis"), ("ch01", "c_inductive_bias"), ("ch01", "c_nfl"),
    # ch02
    ("ch02", "c_linalg"), ("ch02", "c_probability"), ("ch02", "c_statistics"),
    ("ch02", "c_calculus"), ("ch02", "c_optimization"), ("ch02", "c_convex"),
    ("ch02", "c_info_theory"), ("ch02", "c_matrix_decomp"), ("ch02", "c_eigenvalue"),
    ("ch02", "c_svd_math"), ("ch02", "c_bayes_theorem"), ("ch02", "c_mle"),
    ("ch02", "c_map"), ("ch02", "c_entropy"), ("ch02", "c_kl"), ("ch02", "c_cross_entropy"),
    ("ch02", "c_mutual_info"), ("ch02", "c_lagrange"), ("ch02", "c_kkt"),
    ("ch02", "c_gradient"), ("ch02", "c_hessian"),
    # ch03
    ("ch03", "c_data_clean"), ("ch03", "c_missing"), ("ch03", "c_outlier"),
    ("ch03", "c_normalization"), ("ch03", "c_standardization"), ("ch03", "c_encoding"),
    ("ch03", "c_onehot"), ("ch03", "c_label_encoding"), ("ch03", "c_feature_eng"),
    ("ch03", "c_feature_select"), ("ch03", "c_filter_method"), ("ch03", "c_wrapper_method"),
    ("ch03", "c_embedded_method"), ("ch03", "c_pca_feature"), ("ch03", "c_feature_cross"),
    ("ch03", "c_feature_scale"), ("ch03", "c_imbalance"), ("ch03", "c_smote"),
    ("ch03", "c_undersample"), ("ch03", "c_data_augment"),
    # ch04
    ("ch04", "c_cv"), ("ch04", "c_kfold"), ("ch04", "c_loo"), ("ch04", "c_bootstrap"),
    ("ch04", "c_confusion"), ("ch04", "c_precision"), ("ch04", "c_recall"),
    ("ch04", "c_f1"), ("ch04", "c_roc"), ("ch04", "c_auc"),
    ("ch04", "c_mse"), ("ch04", "c_r2"), ("ch04", "c_mae"), ("ch04", "c_logloss"),
    ("ch04", "c_hyperparam"), ("ch04", "c_grid_search"), ("ch04", "c_random_search"),
    ("ch04", "c_bayes_opt"),
    # ch16
    ("ch16", "c_mdp"), ("ch16", "c_state"), ("ch16", "c_action"),
    ("ch16", "c_reward"), ("ch16", "c_policy"), ("ch16", "c_value_func"),
    ("ch16", "c_q_func"), ("ch16", "c_explore"), ("ch16", "c_discount"),
    # ch19
    ("ch19", "c_llm"), ("ch19", "c_rag"), ("ch19", "c_prompt_eng"),
    ("ch19", "c_fine_tune"), ("ch19", "c_kg"), ("ch19", "c_embedding"),
    ("ch19", "c_vector_db"), ("ch19", "c_rlhf"),
]
RELATIONS.extend([(s, t, "CONTAINS", {}) for s, t in CHAPTER_CONTAINS])

# --- 概念之间的关联 ---
CONCEPT_RELATIONS = [
    ("c_ml", "c_supervised", "PARADIGM", {"weight": 1.0}),
    ("c_ml", "c_unsupervised", "PARADIGM", {"weight": 1.0}),
    ("c_ml", "c_reinforcement", "PARADIGM", {"weight": 1.0}),
    ("c_ml", "c_semi_supervised", "PARADIGM", {"weight": 0.8}),
    ("c_ml", "c_self_supervised", "PARADIGM", {"weight": 0.8}),
    ("c_supervised", "c_overfit", "CHALLENGE", {}),
    ("c_supervised", "c_underfit", "CHALLENGE", {}),
    ("c_overfit", "c_generalization", "RELATED_TO", {}),
    ("c_underfit", "c_generalization", "RELATED_TO", {}),
    ("c_overfit", "c_bias_variance", "EXPLAINS", {}),
    ("c_underfit", "c_bias_variance", "EXPLAINS", {}),
    ("c_entropy", "c_kl", "RELATED_TO", {}),
    ("c_entropy", "c_cross_entropy", "RELATED_TO", {}),
    ("c_entropy", "c_mutual_info", "RELATED_TO", {}),
    ("c_mle", "c_map", "EXTENDS", {}),
    ("c_bayes_theorem", "c_map", "BASED_ON", {}),
    ("c_mle", "c_bayes_theorem", "RELATED_TO", {}),
    ("c_optimization", "c_convex", "SPECIALIZATION", {}),
    ("c_optimization", "c_lagrange", "METHOD", {}),
    ("c_lagrange", "c_kkt", "EXTENDS", {}),
    ("c_gradient", "c_hessian", "RELATED_TO", {}),
    ("c_matrix_decomp", "c_eigenvalue", "RELATED_TO", {}),
    ("c_matrix_decomp", "c_svd_math", "INSTANCE", {}),
    ("c_data_clean", "c_missing", "INCLUDES", {}),
    ("c_data_clean", "c_outlier", "INCLUDES", {}),
    ("c_feature_eng", "c_feature_select", "INCLUDES", {}),
    ("c_feature_eng", "c_feature_cross", "INCLUDES", {}),
    ("c_feature_select", "c_filter_method", "METHOD", {}),
    ("c_feature_select", "c_wrapper_method", "METHOD", {}),
    ("c_feature_select", "c_embedded_method", "METHOD", {}),
    ("c_encoding", "c_onehot", "INSTANCE", {}),
    ("c_encoding", "c_label_encoding", "INSTANCE", {}),
    ("c_imbalance", "c_smote", "SOLUTION", {}),
    ("c_imbalance", "c_undersample", "SOLUTION", {}),
    ("c_normalization", "c_feature_scale", "INSTANCE", {}),
    ("c_standardization", "c_feature_scale", "INSTANCE", {}),
    ("c_cv", "c_kfold", "INSTANCE", {}),
    ("c_cv", "c_loo", "INSTANCE", {}),
    ("c_cv", "c_bootstrap", "INSTANCE", {}),
    ("c_hyperparam", "c_grid_search", "METHOD", {}),
    ("c_hyperparam", "c_random_search", "METHOD", {}),
    ("c_hyperparam", "c_bayes_opt", "METHOD", {}),
    ("c_mdp", "c_state", "COMPONENT", {}),
    ("c_mdp", "c_action", "COMPONENT", {}),
    ("c_mdp", "c_reward", "COMPONENT", {}),
    ("c_policy", "c_value_func", "RELATED_TO", {}),
    ("c_value_func", "c_q_func", "SPECIALIZATION", {}),
    ("c_llm", "c_rag", "APPLICATION", {}),
    ("c_llm", "c_prompt_eng", "TECHNIQUE", {}),
    ("c_llm", "c_fine_tune", "TECHNIQUE", {}),
    ("c_llm", "c_rlhf", "TRAINING", {}),
    ("c_rag", "c_vector_db", "USES", {}),
    ("c_rag", "c_kg", "USES", {}),
    ("c_embedding", "c_vector_db", "STORED_IN", {}),
]
RELATIONS.extend([(s, t, r, p) for s, t, r, p in CONCEPT_RELATIONS])

# --- 算法之间的关系 ---
ALGO_RELATIONS = [
    # 回归
    ("a_linreg", "a_ridge", "EXTENDS", {}),
    ("a_linreg", "a_lasso", "EXTENDS", {}),
    ("a_linreg", "a_polyreg", "EXTENDS", {}),
    ("a_logreg", "a_softmax", "EXTENDS", {}),
    ("a_linreg", "a_logreg", "RELATED_TO", {}),
    # 决策树
    ("a_id3", "a_c45", "IMPROVES", {}),
    ("a_c45", "a_cart", "RELATED_TO", {}),
    ("a_id3", "a_preprune", "USES", {}),
    ("a_id3", "a_postprune", "USES", {}),
    # SVM
    ("a_svm_linear", "a_svm_kernel", "EXTENDS", {}),
    ("a_svm_kernel", "a_rbf", "USES", {}),
    ("a_svm_kernel", "a_poly_kernel", "USES", {}),
    ("a_svm_kernel", "a_sigmoid_kernel", "USES", {}),
    ("a_svm_linear", "a_svr", "EXTENDS", {}),
    # 贝叶斯
    ("a_naive_bayes", "a_gnb", "SPECIALIZATION", {}),
    ("a_naive_bayes", "a_mnb", "SPECIALIZATION", {}),
    ("a_naive_bayes", "a_bnb", "SPECIALIZATION", {}),
    ("a_gmm", "a_em", "USES", {}),
    ("a_hmm", "a_em", "USES", {}),
    # 集成学习
    ("a_bagging", "a_rf", "BASED_ON", {}),
    ("a_rf", "a_cart", "USES", {}),
    ("a_gbdt", "a_xgboost", "IMPROVES", {}),
    ("a_gbdt", "a_lightgbm", "IMPROVES", {}),
    ("a_gbdt", "a_catboost", "IMPROVES", {}),
    ("a_adaboost", "a_gbdt", "RELATED_TO", {}),
    ("a_stacking", "a_voting", "RELATED_TO", {}),
    ("a_stacking", "a_blending", "RELATED_TO", {}),
    # 聚类
    ("a_kmeans", "a_kmeanspp", "IMPROVES", {}),
    ("a_kmeans", "a_kmedoids", "RELATED_TO", {}),
    ("a_dbscan", "a_optics", "IMPROVES", {}),
    ("a_kmeans", "a_elbow", "EVALUATED_BY", {}),
    ("a_kmeans", "a_silhouette", "EVALUATED_BY", {}),
    # 降维
    ("a_pca", "a_kpca", "EXTENDS", {}),
    ("a_tsne", "a_umap", "RELATED_TO", {}),
    ("a_isomap", "a_le", "RELATED_TO", {}),
    ("a_pca", "c_svd_math", "USES", {}),  # PCA uses SVD
    # 半监督/自监督
    ("a_label_prop", "a_self_train", "RELATED_TO", {}),
    ("a_self_train", "a_co_train", "RELATED_TO", {}),
    ("a_contrastive", "a_mlm", "RELATED_TO", {}),
    # 神经网络
    ("a_perceptron", "a_mlp", "EXTENDS", {}),
    ("a_mlp", "a_bp", "TRAINED_BY", {}),
    ("a_mlp", "a_xavier", "USES", {}),
    ("a_mlp", "a_he_init", "USES", {}),
    ("a_rnn", "a_lstm", "IMPROVES", {}),
    ("a_rnn", "a_gru", "IMPROVES", {}),
    ("a_attention", "a_self_attn", "SPECIALIZATION", {}),
    ("a_self_attn", "a_mha", "EXTENDS", {}),
    ("a_transformer", "a_self_attn", "BASED_ON", {}),
    ("a_transformer", "a_mha", "USES", {}),
    ("a_cnn", "a_resnet", "EXTENDS", {}),
    ("a_gnn", "a_gcn", "SPECIALIZATION", {}),
    # GAN
    ("a_gan", "a_dcgan", "EXTENDS", {}),
    ("a_gan", "a_wgan", "IMPROVES", {}),
    ("a_gan", "a_stylegan", "EXTENDS", {}),
    ("a_ae", "a_vae", "EXTENDS", {}),
    ("a_ae", "a_dae", "EXTENDS", {}),
    # RL
    ("a_qlearning", "a_sarsa", "RELATED_TO", {}),
    ("a_qlearning", "a_dqn", "EXTENDS", {}),
    ("a_pg", "a_a2c", "BASED_ON", {}),
    ("a_pg", "a_ppo", "IMPROVES", {}),
    ("a_a2c", "a_ddpg", "EXTENDS", {}),
    # NLP
    ("a_word2vec", "a_glove", "RELATED_TO", {}),
    ("a_word2vec", "a_fasttext", "RELATED_TO", {}),
    ("a_bert", "a_transformer", "BASED_ON", {}),
    ("a_gpt", "a_transformer", "BASED_ON", {}),
    ("a_gpt", "a_gpt2", "EXTENDS", {}),
    ("a_gpt2", "a_gpt3", "EXTENDS", {}),
    ("a_seq2seq", "a_attention", "USES", {}),
    ("a_bert", "a_mlm", "TRAINED_BY", {}),
    ("a_bert", "a_elmo", "RELATED_TO", {}),
    ("a_gpt3", "a_deepseek", "RELATED_TO", {}),
    ("a_gpt3", "a_llama", "RELATED_TO", {}),
    ("a_t5", "a_transformer", "BASED_ON", {}),
    # CV
    ("a_lenet", "a_alexnet", "PRECEDES", {}),
    ("a_alexnet", "a_vgg", "PRECEDES", {}),
    ("a_vgg", "a_googlenet", "RELATED_TO", {}),
    ("a_googlenet", "a_resnet", "PRECEDES", {}),
    ("a_resnet", "a_mobilenet", "RELATED_TO", {}),
    ("a_rcnn_family", "a_yolo", "RELATED_TO", {}),
    ("a_yolo", "a_ssd", "RELATED_TO", {}),
    ("a_vit", "a_transformer", "BASED_ON", {}),
    ("a_vit", "a_swin", "EXTENDS", {}),
    ("a_vit", "a_mae_algo", "TRAINED_BY", {}),
]
RELATIONS.extend([(s, t, r, p) for s, t, r, p in ALGO_RELATIONS])

# --- 算法使用技术 ---
ALGO_USES_TECH = [
    # 优化器使用
    ("a_mlp", "t_gd"), ("a_mlp", "t_sgd"), ("a_mlp", "t_adam"),
    ("a_cnn", "t_sgd"), ("a_cnn", "t_adam"), ("a_cnn", "t_momentum"),
    ("a_transformer", "t_adam"), ("a_transformer", "t_adamw"),
    ("a_bert", "t_adamw"), ("a_gpt", "t_adamw"),
    # 激活函数
    ("a_mlp", "t_relu"), ("a_mlp", "t_sigmoid"), ("a_mlp", "t_tanh"),
    ("a_cnn", "t_relu"), ("a_cnn", "t_leaky_relu"),
    ("a_lstm", "t_sigmoid"), ("a_lstm", "t_tanh"),
    ("a_transformer", "t_gelu"), ("a_bert", "t_gelu"),
    ("a_gpt", "t_gelu"), ("a_resnet", "t_relu"),
    ("a_gan", "t_leaky_relu"), ("a_vae", "t_relu"),
    ("a_logreg", "t_sigmoid"), ("a_mlp", "t_softmax_tech"),
    ("a_gpt3", "t_swish"),
    # 损失函数
    ("a_linreg", "t_mse_loss"), ("a_ridge", "t_mse_loss"), ("a_lasso", "t_mse_loss"),
    ("a_logreg", "t_ce_loss"), ("a_mlp", "t_ce_loss"), ("a_cnn", "t_ce_loss"),
    ("a_svm_linear", "t_hinge_loss"), ("a_svm_kernel", "t_hinge_loss"),
    ("a_gan", "t_ce_loss"), ("a_vae", "t_mse_loss"),
    ("a_dqn", "t_mse_loss"), ("a_transformer", "t_ce_loss"),
    # 正则化
    ("a_ridge", "t_l2_reg"), ("a_lasso", "t_l1_reg"),
    ("a_mlp", "t_dropout"), ("a_cnn", "t_dropout"), ("a_transformer", "t_dropout"),
    ("a_cnn", "t_bn"), ("a_resnet", "t_bn"),
    ("a_transformer", "t_ln"), ("a_bert", "t_ln"), ("a_gpt", "t_ln"),
    ("a_mlp", "t_early_stop"), ("a_cnn", "t_early_stop"),
    ("a_transformer", "t_warmup"), ("a_bert", "t_warmup"),
    ("a_transformer", "t_cosine_decay"), ("a_transformer", "t_label_smooth"),
    # 卷积组件
    ("a_cnn", "t_conv"), ("a_cnn", "t_pooling"),
    ("a_cnn", "t_maxpool"), ("a_resnet", "t_skip_connect"),
    ("a_unet", "t_skip_connect"), ("a_unet", "t_conv"),
    ("a_transformer", "t_pos_encoding"), ("a_transformer", "t_ffn"),
    ("a_vit", "t_pos_encoding"),
    # 训练技术
    ("a_resnet", "t_transfer_tech"), ("a_bert", "t_transfer_tech"),
    ("a_vgg", "t_transfer_tech"), ("a_bert", "t_freeze"),
    ("a_llama", "t_lora"), ("a_deepseek", "t_lora"),
    ("a_gpt3", "t_lora"),
    ("a_cnn", "t_mixup"), ("a_cnn", "t_cutmix"),
    ("a_rnn", "t_gradient_clip"), ("a_lstm", "t_gradient_clip"),
    ("a_transformer", "t_gradient_clip"),
    # 池化
    ("a_resnet", "t_gloabl_avgpool"), ("a_googlenet", "t_gloabl_avgpool"),
    ("a_vit", "t_gloabl_avgpool"),
    # NLP技术
    ("a_bert", "t_bpe"), ("a_gpt", "t_bpe"), ("a_gpt2", "t_bpe"),
    ("a_word2vec", "t_tokenize"), ("a_bow", "t_stopword"),
    ("a_tfidf", "t_stopword"), ("a_ngram", "t_tokenize"),
    # 知识蒸馏
    ("a_bert", "t_distillation"), ("a_mobilenet", "t_distillation"),
]
# Filter out None entries
ALGO_USES_TECH = [item for item in ALGO_USES_TECH if item is not None]
RELATIONS.extend([(s, t, "USES", {}) for s, t in ALGO_USES_TECH])

# --- 算法用于应用 ---
ALGO_FOR_APP = [
    ("a_cnn", "app_img_cls"), ("a_resnet", "app_img_cls"), ("a_vgg", "app_img_cls"),
    ("a_vit", "app_img_cls"), ("a_swin", "app_img_cls"),
    ("a_yolo", "app_obj_det"), ("a_rcnn_family", "app_obj_det"), ("a_ssd", "app_obj_det"),
    ("a_unet", "app_seg"), ("a_sam", "app_seg"),
    ("a_cnn", "app_face"), ("a_resnet", "app_face"),
    ("a_bert", "app_text_cls"), ("a_naive_bayes", "app_text_cls"),
    ("a_bert", "app_sentiment"), ("a_logreg", "app_sentiment"),
    ("a_transformer", "app_mt"), ("a_seq2seq", "app_mt"), ("a_t5", "app_mt"),
    ("a_bert", "app_qa"), ("a_gpt3", "app_qa"), ("a_deepseek", "app_qa"),
    ("a_t5", "app_summarize"), ("a_bert", "app_summarize"), ("a_gpt3", "app_summarize"),
    ("a_rf", "app_rec"), ("a_xgboost", "app_rec"), ("a_mlp", "app_rec"),
    ("a_dbscan", "app_ad"),
    ("a_lstm", "app_timeseries"), ("a_rnn", "app_timeseries"),
    ("a_lstm", "app_speech"), ("a_transformer", "app_speech"),
    ("a_gan", "app_img_gen"), ("a_stylegan", "app_img_gen"),
    ("a_vae", "app_img_gen"), ("a_diffusion", "app_img_gen"),
    ("a_transformer", "app_tts"),
    ("a_seq2seq", "app_img_caption"), ("a_transformer", "app_img_caption"),
    ("a_bert", "app_ner"), ("a_lstm", "app_ner"),
    ("c_kg", "app_kg_app"),
    ("a_yolo", "app_autonomous"), ("a_cnn", "app_autonomous"),
    ("a_cnn", "app_medical"), ("a_unet", "app_medical"), ("a_resnet", "app_medical"),
    ("a_xgboost", "app_ad"), ("a_kmeans", "app_ad"),
    ("a_linreg", "app_timeseries"), ("a_rf", "app_timeseries"),
]
ALGO_FOR_APP = [item for item in ALGO_FOR_APP if item is not None]
RELATIONS.extend([(s, t, "APPLIES_TO", {}) for s, t in ALGO_FOR_APP])

# --- 概念使用技术 ---
CONCEPT_USES_TECH = [
    ("c_optimization", "t_gd"), ("c_optimization", "t_sgd"),
    ("c_optimization", "t_momentum"), ("c_optimization", "t_adam"),
    ("c_overfit", "t_l1_reg"), ("c_overfit", "t_l2_reg"),
    ("c_overfit", "t_dropout"), ("c_overfit", "t_early_stop"),
    ("c_overfit", "t_bn"), ("c_data_augment", "t_mixup"),
    ("c_data_augment", "t_cutmix"),
    ("c_feature_eng", "c_pca_feature"),
    ("c_transfer", "t_transfer_tech"), ("c_transfer", "t_freeze"),
    ("c_transfer", "t_lora"),
]
RELATIONS.extend([(s, t, "USES", {}) for s, t in CONCEPT_USES_TECH])

# --- 算法属于概念/范式 ---
ALGO_BELONGS = [
    ("a_linreg", "c_supervised"), ("a_ridge", "c_supervised"), ("a_lasso", "c_supervised"),
    ("a_logreg", "c_supervised"), ("a_softmax", "c_supervised"),
    ("a_id3", "c_supervised"), ("a_c45", "c_supervised"), ("a_cart", "c_supervised"),
    ("a_svm_linear", "c_supervised"), ("a_svm_kernel", "c_supervised"),
    ("a_naive_bayes", "c_supervised"), ("a_mlp", "c_supervised"),
    ("a_cnn", "c_supervised"), ("a_rnn", "c_supervised"), ("a_lstm", "c_supervised"),
    ("a_transformer", "c_supervised"), ("a_resnet", "c_supervised"),
    ("a_kmeans", "c_unsupervised"), ("a_dbscan", "c_unsupervised"),
    ("a_agglo", "c_unsupervised"), ("a_spectral", "c_unsupervised"),
    ("a_pca", "c_unsupervised"), ("a_tsne", "c_unsupervised"), ("a_umap", "c_unsupervised"),
    ("a_gmm", "c_unsupervised"), ("a_apriori", "c_unsupervised"), ("a_fpgrowth", "c_unsupervised"),
    ("a_rf", "c_supervised"), ("a_xgboost", "c_supervised"), ("a_gbdt", "c_supervised"),
    ("a_adaboost", "c_supervised"), ("a_lightgbm", "c_supervised"),
    ("a_gan", "c_supervised"), ("a_vae", "c_supervised"), ("a_diffusion", "c_supervised"),
    ("a_qlearning", "c_reinforcement"), ("a_dqn", "c_reinforcement"),
    ("a_pg", "c_reinforcement"), ("a_ppo", "c_reinforcement"),
    ("a_label_prop", "c_semi_supervised"), ("a_self_train", "c_semi_supervised"),
    ("a_co_train", "c_semi_supervised"),
    ("a_contrastive", "c_self_supervised"), ("a_mlm", "c_self_supervised"),
    ("a_mae_algo", "c_self_supervised"),
    ("a_bert", "c_self_supervised"), ("a_gpt", "c_self_supervised"),
    ("a_bert", "c_transfer"), ("a_gpt", "c_transfer"),
    ("a_vgg", "c_transfer"), ("a_resnet", "c_transfer"),
]
RELATIONS.extend([(s, t, "BELONGS_TO", {}) for s, t in ALGO_BELONGS])


# ===================== 构建函数 =====================

def clear_graph(tx):
    """清空数据库"""
    tx.run("MATCH (n) DETACH DELETE n")
    print("[1/6] 已清空数据库")


def create_constraints(tx):
    """创建唯一性约束和索引"""
    tx.run("CREATE CONSTRAINT unique_id IF NOT EXISTS FOR (n:MLNode) REQUIRE n.id IS UNIQUE")
    tx.run("CREATE INDEX idx_name IF NOT EXISTS FOR (n:MLNode) ON (n.name)")
    print("[2/6] 已创建约束和索引")


def create_chapters(tx):
    """创建章节节点"""
    count = 0
    for label, props in CHAPTERS:
        tx.run(
            f"CREATE (n:{label}:MLNode $props)",
            props=props
        )
        count += 1
    print(f"[3/6] 已创建 {count} 个章节节点")


def create_nodes_batch(tx, nodes, label_name):
    """批量创建节点"""
    count = 0
    for label, props in nodes:
        tx.run(
            f"CREATE (n:{label}:MLNode $props)",
            props=props
        )
        count += 1
    print(f"  - {label_name}: {count} 个节点")
    return count


def create_all_nodes(tx):
    """创建所有非章节节点"""
    print("[4/6] 创建概念/算法/技术/应用节点:")
    total = 0
    total += create_nodes_batch(tx, CONCEPTS, "概念(Concept)")
    total += create_nodes_batch(tx, ALGORITHMS, "算法(Algorithm)")
    total += create_nodes_batch(tx, TECHNIQUES, "技术(Technique)")
    total += create_nodes_batch(tx, APPLICATIONS, "应用(Application)")
    print(f"  共创建 {total} 个节点")


def create_relations(tx):
    """创建所有关系"""
    count = 0
    for src_id, tgt_id, rel_type, props in RELATIONS:
        query = (
            f"MATCH (a:MLNode {{id: $src}}) "
            f"MATCH (b:MLNode {{id: $tgt}}) "
            f"CREATE (a)-[r:{rel_type}]->(b)"
        )
        if props:
            query = (
                f"MATCH (a:MLNode {{id: $src}}) "
                f"MATCH (b:MLNode {{id: $tgt}}) "
                f"CREATE (a)-[r:{rel_type} $props]->(b)"
            )
            tx.run(query, src=src_id, tgt=tgt_id, props=props)
        else:
            tx.run(query, src=src_id, tgt=tgt_id)
        count += 1
    print(f"[5/6] 已创建 {count} 条关系")


def verify_graph(tx):
    """验证图谱统计信息"""
    print("\n[6/6] ===== 图谱验证 =====")

    # 总节点数
    result = tx.run("MATCH (n:MLNode) RETURN count(n) AS total").single()
    print(f"  总节点数: {result['total']}")

    # 各标签节点数
    for label in ["Chapter", "Concept", "Algorithm", "Technique", "Application"]:
        result = tx.run(f"MATCH (n:{label}) RETURN count(n) AS cnt").single()
        print(f"  {label}: {result['cnt']}")

    # 总关系数
    result = tx.run("MATCH ()-[r]->() RETURN count(r) AS total").single()
    print(f"  总关系数: {result['total']}")

    # 各类型关系数
    rel_result = tx.run(
        "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS cnt "
        "ORDER BY cnt DESC"
    )
    print("  关系类型分布:")
    for record in rel_result:
        print(f"    {record['rel_type']}: {record['cnt']}")

    # 连通性检查：最大连通分量
    result = tx.run(
        "MATCH path = (a:MLNode)-[*..5]-(b:MLNode) "
        "RETURN max(length(path)) AS max_path_len"
    ).single()
    print(f"  最长路径长度(5跳内): {result['max_path_len']}")


def run_sample_queries(tx):
    """运行示例查询，展示图谱能力"""
    print("\n===== 示例查询 =====\n")

    # 查询1：某个章节下的所有算法
    print("Q1: 「集成学习」章节下的所有算法:")
    result = tx.run(
        "MATCH (ch:Chapter {id: 'ch09'})-[:CONTAINS]->(c:Concept)<-[:BELONGS_TO]-(a:Algorithm) "
        "RETURN a.name AS algo ORDER BY algo"
    )
    for r in result:
        print(f"  - {r['algo']}")

    # 查询2：Transformer 使用的所有技术
    print("\nQ2: Transformer 使用的所有技术:")
    result = tx.run(
        "MATCH (a:Algorithm {id: 'a_transformer'})-[:USES]->(t:Technique) "
        "RETURN t.name AS tech ORDER BY tech"
    )
    for r in result:
        print(f"  - {r['tech']}")

    # 查询3：图像分类可用哪些算法
    print("\nQ3: 图像分类任务可用的算法:")
    result = tx.run(
        "MATCH (a:Algorithm)-[:APPLIES_TO]->(app:Application {id: 'app_img_cls'}) "
        "RETURN a.name AS algo ORDER BY algo"
    )
    for r in result:
        print(f"  - {r['algo']}")

    # 查询4：从SVM到深度学习的学习路径
    print("\nQ4: 学习路径查询（SVM需要先学什么章节）:")
    result = tx.run(
        "MATCH (a:Algorithm {id: 'a_svm_linear'})-[:BELONGS_TO]->(c:Concept)<-[:CONTAINS]-(ch:Chapter) "
        "MATCH (ch)-[:HAS_PREREQ*0..3]->(pre_ch:Chapter) "
        "RETURN DISTINCT pre_ch.name AS chapter ORDER BY chapter"
    )
    for r in result:
        print(f"  - {r['chapter']}")

    # 查询5：统计各章节包含的算法数量
    print("\nQ5: 各章节关联的算法数量:")
    result = tx.run(
        "MATCH (ch:Chapter)-[:CONTAINS]->(c:Concept)<-[:BELONGS_TO]-(a:Algorithm) "
        "RETURN ch.name AS chapter, count(a) AS algo_cnt "
        "ORDER BY algo_cnt DESC"
    )
    for r in result:
        print(f"  {r['chapter']}: {r['algo_cnt']}个算法")


def main():
    print("=" * 60)
    print("  机器学习课程知识图谱构建")
    print("=" * 60)
    print(f"\n连接 Neo4j: {NEO4J_URI}")
    print(f"用户: {NEO4J_USER}\n")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        driver.verify_connectivity()
        print("已连接到 Neo4j!\n")
    except Exception as e:
        print(f"连接失败: {e}")
        print("请确保 Neo4j 已启动并检查连接参数。")
        sys.exit(1)

    start = time.time()

    with driver.session() as session:
        # 清空旧数据
        session.execute_write(clear_graph)
        # 创建约束
        session.execute_write(create_constraints)
        # 创建章节节点
        session.execute_write(create_chapters)
        # 创建其他节点
        session.execute_write(create_all_nodes)
        # 创建关系
        session.execute_write(create_relations)
        # 验证
        session.execute_write(verify_graph)
        # 示例查询
        session.execute_read(run_sample_queries)

    elapsed = time.time() - start
    print(f"\n构建完成! 耗时: {elapsed:.1f}秒")
    print(f"打开 Neo4j Browser (http://localhost:7474) 查看图谱")
    print("推荐查询: MATCH (n:MLNode) RETURN n LIMIT 100")

    driver.close()


if __name__ == "__main__":
    main()
